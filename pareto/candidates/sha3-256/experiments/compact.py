










from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


MASK256 = (1 << 256) - 1
MASK64 = (1 << 64) - 1
UNIT = 6_504
LNK = 3_528


class Op(IntEnum):
    XOR = 0
    AND = 1
    OR = 2
    NOT = 3
    ADD = 4
    SUB = 5
    SHL = 6
    SHR = 7
    EQ = 8
    LT = 9
    MOV = 10
    ADDI = 11
    SUBI = 12
    SHLI = 13
    SHRI = 14
    ANDI = 15
    EQI = 16
    LTI = 17
    MOVI = 18
    LD = 19
    ST = 20
    LDA = 21
    BNZ = 22
    BZ = 23
    JMP = 24
    JAL = 25
    JR = 26
    RND = 27
    PERM = 28
    HALT = 29


COMPARE_OPS = {Op.EQ, Op.LT, Op.EQI, Op.LTI}


R_COUNTER = LNK + 1
R_NEXT_ID = LNK + 2
R_RHO = LNK + 3
R_ONES = LNK + 4
R_PREFILTER = LNK + 5
R_HITS = LNK + 6
R_LINK = LNK + 7
R_LINK2 = LNK + 8
R_ZERO = LNK + 9


R_LANE = 256
R_DPM = 257
R_C1 = 258
R_ACC = 259
R_TMP = 260
R_RECORD = 261
R_SLOT = 262
R_WORD = 263
R_FLAG = 264
R_X = 265
R_Y = 266
R_POINT = 267
R_MASK = 268
R_PTR = 269
R_INDEX = 270
R_ID = 271
R_REPEATED = 272
R_ONEBIT = 273
R_P = 280
R_Q = 281
R_N = 282
R_MIN = 283
R_LA = 284
R_LB = 285
R_U = 286
R_F = 287
R_FP = 288
R_PD = 289
R_X0 = 290
R_X1 = 291
R_X2 = 292
R_X3 = 293
R_TQ = 294
R_STATE = 300
NREGS = LNK + 12


@dataclass(frozen=True)
class Layout:
    table_words: int
    slots_per_word: int = 5
    slot_bits: int = 51

    def __post_init__(self):
        if self.table_words < 264 or self.table_words % 8:
            raise ValueError("table_words must be a multiple of eight and at least 264")
        if self.slots_per_word * self.slot_bits > 256:
            raise ValueError("slots do not fit one word")
        if self.slot_bits < 2:
            raise ValueError("a slot needs a written bit and at least one key bit")

    @property
    def key_bits(self) -> int:
        return self.slot_bits - 1

    @property
    def capacity(self) -> int:
        return self.table_words * self.slots_per_word

    @property
    def home_bits(self) -> int:
        return self.table_words.bit_length()

    @property
    def scratch(self) -> int:
        return self.table_words

    @property
    def lane_ids(self) -> int:
        return self.scratch + 256

    @property
    def lane_starts(self) -> int:
        return self.lane_ids + 256

    @property
    def data(self) -> int:
        return self.lane_starts + 256

    @property
    def memory_words(self) -> int:
        return self.data + 16


def trail_number(index: int, layout: Layout) -> int:
    if not 0 <= index < layout.capacity:
        raise ValueError("trail index is outside the table capacity")
    word = index % layout.table_words
    slot = index // layout.table_words
    return word | ((layout.slot_bits * slot) << layout.home_bits)


def decode_trail_number(number: int, layout: Layout) -> tuple[int, int]:
    word = number & ((1 << layout.home_bits) - 1)
    shift = number >> layout.home_bits
    if word >= layout.table_words or shift % layout.slot_bits:
        raise ValueError("invalid encoded trail number")
    slot = shift // layout.slot_bits
    if slot >= layout.slots_per_word:
        raise ValueError("invalid encoded trail slot")
    return word, slot


def record_for_key(key: int, layout: Layout) -> int:
    if not 0 <= key < 1 << layout.key_bits:
        raise ValueError("key does not fit the record")
    return 1 | (key << 1)


def slot_value(word: int, slot: int, layout: Layout) -> int:
    if not 0 <= slot < layout.slots_per_word:
        raise ValueError("slot is outside the word")
    return (word >> (slot * layout.slot_bits)) & ((1 << layout.slot_bits) - 1)


@dataclass
class Instruction:
    op: Op
    d: int = 0
    a: int = 0
    b: int = 0
    imm: int = 0

    def encode(self) -> bytes:
        if not (0 <= self.d < 1 << 16 and 0 <= self.a < 1 << 16 and 0 <= self.b < 1 << 16):
            raise ValueError("register field does not fit 16 bits")
        if not 0 <= self.imm < 1 << 192:
            raise ValueError("immediate does not fit 192 bits")
        return (
            bytes([int(self.op)])
            + self.d.to_bytes(2, "little")
            + self.a.to_bytes(2, "little")
            + self.b.to_bytes(2, "little")
            + b"\0"
            + self.imm.to_bytes(24, "little")
        )


class Assembly:
    def __init__(self, layout: Layout):
        self.layout = layout
        self.instructions: list[Instruction] = []
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str]] = []

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"duplicate label {name}")
        self.labels[name] = len(self.instructions)

    def emit(self, op: Op, d=0, a=0, b=0, imm=0, target: Optional[str] = None):
        self.instructions.append(Instruction(op, d, a, b, imm))
        if target is not None:
            self.fixups.append((len(self.instructions) - 1, target))

    def binary(self, op: Op, d: int, a: int, b: int):
        self.emit(op, d, a, b)

    def immediate(self, op: Op, d: int, a: int, imm: int):
        self.emit(op, d, a, 0, imm)

    def mov(self, d, a): self.emit(Op.MOV, d, a)
    def movi(self, d, value): self.emit(Op.MOVI, d, imm=value)
    def add(self, d, a, b): self.binary(Op.ADD, d, a, b)
    def sub(self, d, a, b): self.binary(Op.SUB, d, a, b)
    def xor(self, d, a, b): self.binary(Op.XOR, d, a, b)
    def and_(self, d, a, b): self.binary(Op.AND, d, a, b)
    def or_(self, d, a, b): self.binary(Op.OR, d, a, b)
    def shl(self, d, a, b): self.binary(Op.SHL, d, a, b)
    def shr(self, d, a, b): self.binary(Op.SHR, d, a, b)
    def not_(self, d, a): self.emit(Op.NOT, d, a)
    def addi(self, d, a, value): self.immediate(Op.ADDI, d, a, value)
    def subi(self, d, a, value): self.immediate(Op.SUBI, d, a, value)
    def shli(self, d, a, value): self.immediate(Op.SHLI, d, a, value)
    def shri(self, d, a, value): self.immediate(Op.SHRI, d, a, value)
    def andi(self, d, a, value): self.immediate(Op.ANDI, d, a, value)
    def ld(self, d, base, offset=0): self.immediate(Op.LD, d, base, offset)
    def st(self, base, offset, source): self.emit(Op.ST, 0, base, source, offset)
    def lda(self, d, address): self.emit(Op.LDA, d, imm=address)
    def jmp(self, target): self.emit(Op.JMP, target=target)
    def jal(self, link, target): self.emit(Op.JAL, d=link, target=target)
    def jr(self, link): self.emit(Op.JR, a=link)
    def halt(self, code): self.emit(Op.HALT, imm=code)

    def _branch(self, op: Op, target: str):
        self.emit(op, a=R_FLAG, target=target)

    def jeqi(self, a, value, target):
        self.immediate(Op.EQI, R_FLAG, a, value); self._branch(Op.BNZ, target)

    def jnei(self, a, value, target):
        self.immediate(Op.EQI, R_FLAG, a, value); self._branch(Op.BZ, target)

    def jlti(self, a, value, target):
        self.immediate(Op.LTI, R_FLAG, a, value); self._branch(Op.BNZ, target)

    def jgei(self, a, value, target):
        self.immediate(Op.LTI, R_FLAG, a, value); self._branch(Op.BZ, target)

    def jeq(self, a, b, target):
        self.binary(Op.EQ, R_FLAG, a, b); self._branch(Op.BNZ, target)

    def jne(self, a, b, target):
        self.binary(Op.EQ, R_FLAG, a, b); self._branch(Op.BZ, target)

    def jlt(self, a, b, target):
        self.binary(Op.LT, R_FLAG, a, b); self._branch(Op.BNZ, target)

    def resolve(self):
        for index, target in self.fixups:
            if target == "@STEP":
                self.instructions[index].imm = (1 << 192) - 1
            else:
                self.instructions[index].imm = self.labels[target]
        for index, ins in enumerate(self.instructions):
            if max(ins.d, ins.a, ins.b) >= NREGS:
                raise ValueError(f"instruction {index} names register outside the file")
            if ins.op in {Op.BNZ, Op.BZ}:
                previous = self.instructions[index - 1]
                if previous.op not in COMPARE_OPS or previous.d != ins.a:
                    raise ValueError(f"branch {index} does not follow its comparison")


def _emit_message_state(a: Assembly, data: int):
    for word in range(7):
        a.ld(R_STATE + word, R_ZERO, data + word)
    a.andi(R_X0, R_U, MASK64)
    a.shri(R_X1, R_U, 64); a.andi(R_X1, R_X1, MASK64)
    a.shri(R_X2, R_U, 128); a.andi(R_X2, R_X2, MASK64)
    a.shri(R_X3, R_U, 192)
    a.shli(R_TQ, R_X0, 64); a.xor(R_STATE, R_STATE, R_TQ)
    a.shli(R_TQ, R_X1, 128); a.xor(R_STATE + 1, R_STATE + 1, R_TQ)
    a.xor(R_STATE + 1, R_STATE + 1, R_X2)
    a.shli(R_TQ, R_X3, 64); a.xor(R_STATE + 2, R_STATE + 2, R_TQ)
    a.xor(R_TQ, R_X0, R_X1); a.shli(R_TQ, R_TQ, 192); a.xor(R_STATE + 2, R_STATE + 2, R_TQ)
    a.xor(R_TQ, R_X2, R_X3); a.shli(R_TQ, R_TQ, 128); a.xor(R_STATE + 3, R_STATE + 3, R_TQ)


def build_program(
    layout: Layout,
    *,
    replay_cap: int = 43_210_406_009_979_655_608_818_122_161_651_712,
    tb: int = 1_326_345_234_525_992_950_706_776_067_278_897_152,
    hit_limit: int = 48_391_447_023_367_850_163_390_149_816_221_697,
    dplo: int = 145,
    dk: int = 10,
    dt: int = 646,
) -> Assembly:
    a = Assembly(layout)
    home_mask = (1 << layout.home_bits) - 1
    slot_mask = (1 << layout.slot_bits) - 1
    limit = trail_number(layout.capacity - 1, layout)
    limit += 1
    if layout.capacity % layout.table_words == 0:
        limit = layout.slot_bits * layout.slots_per_word << layout.home_bits
    threshold = dt << (dplo - dk)

    a.label("start")
    a.emit(Op.RND, d=R_RHO)
    a.movi(R_NEXT_ID, trail_number(256, layout))
    a.movi(R_HITS, 0); a.movi(R_COUNTER, 0); a.movi(R_ZERO, 0); a.not_(R_ONES, R_ZERO)
    a.movi(R_PTR, 0)
    a.label("clear")
    for offset in range(8):
        a.st(R_PTR, offset, R_ZERO)
    a.addi(R_PTR, R_PTR, 8); a.jlti(R_PTR, layout.table_words + 256, "clear")
    a.movi(R_LANE, 0)
    a.label("initial_walks")
    a.add(R_POINT, R_RHO, R_LANE)
    a.st(R_LANE, layout.lane_ids, R_LANE)
    a.st(R_LANE, layout.lane_starts, R_ZERO)
    a.jal(R_LINK, "setwalk")
    a.addi(R_LANE, R_LANE, 1); a.jlti(R_LANE, 256, "initial_walks")
    a.jal(R_LINK, "restore_planes")
    a.jmp("@STEP")

    a.label("loop")
    a.jeq(R_PREFILTER, R_ONES, "continue")
    a.label("hit")
    a.addi(R_HITS, R_HITS, 1); a.jlti(R_HITS, hit_limit + 1, "hit_ok"); a.halt(10)
    a.label("hit_ok")
    a.or_(R_TMP, dplo, dplo + 1)
    for plane in range(dplo + 2, 240):
        a.or_(R_TMP, R_TMP, plane)
    a.or_(R_DPM, R_PREFILTER, R_TMP); a.not_(R_DPM, R_DPM)
    bits = [(dt >> (dk - 1 - i)) & 1 for i in range(dk)]
    last_one = max(i for i, bit in enumerate(bits) if bit)
    first = True
    for i in range(last_one + 1):
        plane = dplo - 1 - i
        a.not_(R_X, plane)
        if bits[i]:
            if first:
                a.and_(R_Y, R_DPM, R_X); first = False
            else:
                a.and_(R_X, R_DPM, R_X); a.or_(R_Y, R_Y, R_X)
            if i < last_one:
                a.and_(R_DPM, R_DPM, plane)
        else:
            a.and_(R_DPM, R_DPM, R_X)
    a.mov(R_DPM, R_Y)
    a.addi(R_C1, R_COUNTER, 1)
    a.jeqi(R_DPM, 0, "continue")

    a.label("save_planes")
    for plane in range(256):
        a.st(R_ZERO, layout.scratch + plane, plane)
    a.label("dp_loop")
    a.jeqi(R_DPM, 0, "restore_after_hit")
    a.label("one_dp")
    a.movi(R_LANE, 0); a.mov(R_X, R_DPM)
    for i, shift in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        a.andi(R_Y, R_X, (1 << shift) - 1)
        a.jnei(R_Y, 0, f"ctz_{i}")
        a.shri(R_X, R_X, shift); a.addi(R_LANE, R_LANE, shift)
        a.label(f"ctz_{i}")
    a.subi(R_Y, R_DPM, 1); a.and_(R_DPM, R_DPM, R_Y)
    a.jal(R_LINK, "gather")

    a.label("record")
    a.andi(R_RECORD, R_ACC, (1 << layout.key_bits) - 1)
    a.shli(R_RECORD, R_RECORD, 1); a.addi(R_RECORD, R_RECORD, 1)
    a.mov(R_REPEATED, R_RECORD)
    for slot in range(1, layout.slots_per_word):
        a.shli(R_X, R_RECORD, layout.slot_bits * slot); a.or_(R_REPEATED, R_REPEATED, R_X)
    a.movi(R_SLOT, 0)
    a.label("probe")
    a.ld(R_WORD, R_SLOT); a.xor(R_WORD, R_WORD, R_REPEATED)
    for slot in range(layout.slots_per_word):
        if slot:
            a.shri(R_Y, R_WORD, layout.slot_bits * slot); a.andi(R_X, R_Y, slot_mask)
        else:
            a.andi(R_X, R_WORD, slot_mask)
        a.jeqi(R_X, 0, f"match_{slot}")
    a.addi(R_SLOT, R_SLOT, 1); a.jnei(R_SLOT, layout.table_words, "probe")

    a.label("insert")
    a.ld(R_ID, R_LANE, layout.lane_ids)
    a.andi(R_SLOT, R_ID, home_mask); a.shri(R_Y, R_ID, layout.home_bits)
    a.shl(R_X, R_RECORD, R_Y)
    a.ld(R_WORD, R_SLOT); a.or_(R_WORD, R_WORD, R_X); a.st(R_SLOT, 0, R_WORD)
    a.label("insert_done")
    a.mov(R_TMP, R_C1); a.jal(R_LINK2, "restart"); a.jmp("dp_loop")

    for slot in range(layout.slots_per_word):
        a.label(f"match_{slot}")
        a.movi(R_X, (layout.slot_bits * slot) << layout.home_bits)
        a.or_(R_X, R_X, R_SLOT); a.jmp("match")

    a.label("restore_after_hit")
    a.jal(R_LINK, "restore_planes")
    a.label("continue")
    a.addi(R_COUNTER, R_COUNTER, 1); a.jnei(R_COUNTER, tb, "@STEP")
    a.label("deadline")
    a.halt(12)

    a.label("restart")
    a.jnei(R_NEXT_ID, limit, "restart_ok"); a.halt(11)
    a.label("restart_ok")
    a.st(R_LANE, layout.lane_ids, R_NEXT_ID); a.st(R_LANE, layout.lane_starts, R_TMP)
    a.add(R_POINT, R_RHO, R_NEXT_ID); a.addi(R_NEXT_ID, R_NEXT_ID, 1)
    a.andi(R_X, R_NEXT_ID, home_mask); a.jnei(R_X, layout.table_words, "restart_nowrap")
    a.addi(R_NEXT_ID, R_NEXT_ID, (layout.slot_bits << layout.home_bits) - layout.table_words)
    a.label("restart_nowrap")
    a.jal(R_LINK, "setwalk"); a.jr(R_LINK2)

    a.label("setwalk")
    a.movi(R_ONEBIT, 1); a.shl(R_ONEBIT, R_ONEBIT, R_LANE); a.not_(R_MASK, R_ONEBIT)
    a.lda(R_PTR, layout.scratch); a.movi(R_INDEX, 0)
    a.label("setwalk_loop")
    a.ld(R_X, R_PTR); a.and_(R_X, R_X, R_MASK)
    a.shr(R_Y, R_POINT, R_INDEX); a.andi(R_Y, R_Y, 1); a.shl(R_Y, R_Y, R_LANE)
    a.or_(R_X, R_X, R_Y); a.st(R_PTR, 0, R_X)
    a.addi(R_PTR, R_PTR, 1); a.addi(R_INDEX, R_INDEX, 1)
    a.jnei(R_INDEX, 256, "setwalk_loop"); a.jr(R_LINK)

    a.label("gather")
    a.movi(R_ACC, 0); a.lda(R_PTR, layout.scratch); a.movi(R_INDEX, 0)
    a.label("gather_loop")
    a.ld(R_X, R_PTR); a.shr(R_X, R_X, R_LANE); a.andi(R_X, R_X, 1)
    a.shl(R_X, R_X, R_INDEX); a.or_(R_ACC, R_ACC, R_X)
    a.addi(R_PTR, R_PTR, 1); a.addi(R_INDEX, R_INDEX, 1)
    a.jnei(R_INDEX, 256, "gather_loop"); a.jr(R_LINK)

    a.label("restore_planes")
    for plane in range(256):
        a.ld(plane, R_ZERO, layout.scratch + plane)
    a.jr(R_LINK)

    a.label("eval_f")
    _emit_message_state(a, layout.data)
    a.emit(Op.PERM, a=R_STATE); a.ld(R_PD, R_ZERO, layout.data + 7); a.xor(R_F, R_STATE, R_PD); a.jr(R_LINK2)
    a.label("output_message")
    _emit_message_state(a, layout.data); a.jr(R_LINK2)

    a.label("match")
    a.ld(R_Y, R_LANE, layout.lane_ids); a.ld(R_LB, R_LANE, layout.lane_starts); a.sub(R_LB, R_C1, R_LB)
    a.jgei(R_LB, replay_cap + 1, "replay_fail")
    a.add(R_P, R_RHO, R_X); a.add(R_Q, R_RHO, R_Y)
    a.mov(R_U, R_P); a.movi(R_LA, 0)
    a.label("measure")
    a.jal(R_LINK2, "eval_f"); a.addi(R_LA, R_LA, 1); a.jlti(R_F, threshold, "measured")
    a.jgei(R_LA, replay_cap, "replay_fail"); a.mov(R_U, R_F); a.jmp("measure")
    a.label("measured")
    a.jlt(R_LA, R_LB, "advance_q"); a.sub(R_N, R_LA, R_LB); a.mov(R_MIN, R_LB)
    a.label("advance_p")
    a.jeqi(R_N, 0, "lock"); a.mov(R_U, R_P); a.jal(R_LINK2, "eval_f"); a.mov(R_P, R_F); a.subi(R_N, R_N, 1); a.jmp("advance_p")
    a.label("advance_q")
    a.sub(R_N, R_LB, R_LA); a.mov(R_MIN, R_LA)
    a.label("advance_q_loop")
    a.jeqi(R_N, 0, "lock"); a.mov(R_U, R_Q); a.jal(R_LINK2, "eval_f"); a.mov(R_Q, R_F); a.subi(R_N, R_N, 1); a.jmp("advance_q_loop")
    a.label("lock")
    a.jeq(R_P, R_Q, "replay_fail")
    a.label("lock_loop")
    a.jeqi(R_MIN, 0, "replay_fail")
    a.mov(R_U, R_P); a.jal(R_LINK2, "eval_f"); a.mov(R_FP, R_F)
    a.mov(R_U, R_Q); a.jal(R_LINK2, "eval_f"); a.jeq(R_FP, R_F, "found")
    a.mov(R_P, R_FP); a.mov(R_Q, R_F); a.subi(R_MIN, R_MIN, 1); a.jmp("lock_loop")
    a.label("found")
    a.mov(R_U, R_P); a.jal(R_LINK2, "output_message")
    for word in range(4): a.st(R_ZERO, layout.data + 8 + word, R_STATE + word)
    a.mov(R_U, R_Q); a.jal(R_LINK2, "output_message")
    for word in range(4): a.st(R_ZERO, layout.data + 12 + word, R_STATE + word)
    a.halt(1)
    a.label("replay_fail")
    a.halt(13)
    a.label("end")
    a.resolve()
    return a


@dataclass(frozen=True)
class Counts:
    instructions: int
    setwalk: int
    gather: int
    restore: int
    restart: int
    restart_halt: int
    hit: int
    ctz_clear: int
    record_slot: int
    probe_word: int
    insert: int
    dp_fixed: int
    deadline_final: int
    eval_f: int
    output_message: int
    measure_iter: int
    replay_iter: int
    replay_const: int
    setup: int


def counts(a: Assembly, layout: Layout) -> Counts:
    labels = a.labels
    segment = lambda first, last: labels[last] - labels[first]
    setwalk_prefix = segment("setwalk", "setwalk_loop")
    setwalk_body = labels["gather"] - 1 - labels["setwalk_loop"]
    setwalk = setwalk_prefix + 256 * setwalk_body + 1
    gather_prefix = segment("gather", "gather_loop")
    gather_body = labels["restore_planes"] - 1 - labels["gather_loop"]
    gather = gather_prefix + 256 * gather_body + 1
    restore = segment("restore_planes", "eval_f")
    restart_halt = segment("restart", "restart_ok") - 1 + 1
    restart = (segment("restart", "restart_ok") - 1) + segment("restart_ok", "setwalk") + setwalk
    hit = (segment("hit", "hit_ok") - 1) + segment("hit_ok", "save_planes")
    ctz_clear = segment("one_dp", "record") - 1  
    record_slot = segment("record", "probe")
    probe_word = segment("probe", "insert")
    insert = segment("insert", "insert_done")
    
    
    dp_fixed = 2 + 256 + ctz_clear + 1 + gather + record_slot + insert + 3 + 1 + restore
    eval_f = segment("eval_f", "output_message") - 1 + UNIT
    output_message = segment("output_message", "match")
    measure_iter = eval_f + 8
    replay_iter = 2 * eval_f + 13
    replay_const = 79
    
    
    clear_iterations = (layout.table_words + 256) // 8
    setup = segment("start", "clear") + clear_iterations * 11 + 1
    setup += 256 * (7 + setwalk) + 1 + restore + 1
    return Counts(
        instructions=len(a.instructions),
        setwalk=setwalk,
        gather=gather,
        restore=restore,
        restart=restart,
        restart_halt=restart_halt,
        hit=hit,
        ctz_clear=ctz_clear,
        record_slot=record_slot,
        probe_word=probe_word,
        insert=insert,
        dp_fixed=dp_fixed,
        deadline_final=segment("deadline", "restart"),
        eval_f=eval_f,
        output_message=output_message,
        measure_iter=measure_iter,
        replay_iter=replay_iter,
        replay_const=replay_const,
        setup=setup,
    )


class Machine:


    def __init__(self, assembly: Assembly):
        self.assembly = assembly
        self.reg = [0] * NREGS
        self.mem = [0] * assembly.layout.memory_words
        self.pc = 0

    def call_subroutine(self, label: str, *, max_steps: int = 20_000):
        self.reg[R_LINK] = len(self.assembly.instructions)
        self.pc = self.assembly.labels[label]
        steps = 0
        while self.pc != len(self.assembly.instructions):
            if steps >= max_steps:
                raise RuntimeError("subroutine step limit exceeded")
            self.step(); steps += 1
        return steps

    def step(self):
        ins = self.assembly.instructions[self.pc]
        self.pc += 1
        r = self.reg
        op = ins.op
        if op == Op.MOV: r[ins.d] = r[ins.a]
        elif op == Op.MOVI: r[ins.d] = ins.imm
        elif op == Op.XOR: r[ins.d] = r[ins.a] ^ r[ins.b]
        elif op == Op.AND: r[ins.d] = r[ins.a] & r[ins.b]
        elif op == Op.OR: r[ins.d] = r[ins.a] | r[ins.b]
        elif op == Op.NOT: r[ins.d] = r[ins.a] ^ MASK256
        elif op == Op.ADD: r[ins.d] = (r[ins.a] + r[ins.b]) & MASK256
        elif op == Op.SUB: r[ins.d] = (r[ins.a] - r[ins.b]) & MASK256
        elif op == Op.SHL: r[ins.d] = (r[ins.a] << (r[ins.b] & 255)) & MASK256
        elif op == Op.SHR: r[ins.d] = r[ins.a] >> (r[ins.b] & 255)
        elif op == Op.ADDI: r[ins.d] = (r[ins.a] + ins.imm) & MASK256
        elif op == Op.SUBI: r[ins.d] = (r[ins.a] - ins.imm) & MASK256
        elif op == Op.SHLI: r[ins.d] = (r[ins.a] << (ins.imm & 255)) & MASK256
        elif op == Op.SHRI: r[ins.d] = r[ins.a] >> (ins.imm & 255)
        elif op == Op.ANDI: r[ins.d] = r[ins.a] & ins.imm
        elif op == Op.EQ: r[ins.d] = int(r[ins.a] == r[ins.b])
        elif op == Op.LT: r[ins.d] = int(r[ins.a] < r[ins.b])
        elif op == Op.EQI: r[ins.d] = int(r[ins.a] == ins.imm)
        elif op == Op.LTI: r[ins.d] = int(r[ins.a] < ins.imm)
        elif op in {Op.LD, Op.LDA}:
            if op == Op.LDA: r[ins.d] = ins.imm
            else: r[ins.d] = self.mem[r[ins.a] + ins.imm]
        elif op == Op.ST: self.mem[r[ins.a] + ins.imm] = r[ins.b]
        elif op == Op.BNZ:
            if r[ins.a] != 0: self.pc = ins.imm
        elif op == Op.BZ:
            if r[ins.a] == 0: self.pc = ins.imm
        elif op == Op.JMP: self.pc = ins.imm
        elif op == Op.JAL: r[ins.d] = self.pc; self.pc = ins.imm
        elif op == Op.JR: self.pc = r[ins.a]
        else:
            raise RuntimeError(f"unsupported test opcode {op.name}")
        if op not in {Op.ST, Op.BNZ, Op.BZ, Op.JMP, Op.JAL, Op.JR} and ins.d:
            r[ins.d] &= MASK256


import hashlib,json,sys
from dataclasses import asdict
base=sys.modules[__name__]

MASK256 = (1 << 256) - 1


def configure(link: int, unit: int) -> None:

    base.UNIT = unit
    base.LNK = link
    names = (
        "R_COUNTER", "R_NEXT_ID", "R_RHO", "R_ONES", "R_PREFILTER",
        "R_HITS", "R_LINK", "R_LINK2", "R_ZERO",
    )
    for offset, name in enumerate(names, 1):
        setattr(base, name, link + offset)
    base.NREGS = link + 12


@dataclass(frozen=True)
class StoredLayout:
    table_words: int
    id_bits: int = 17
    slots_per_word: int = 4
    slot_bits: int = 64

    def __post_init__(self):
        if self.table_words < 264 or self.table_words % 8:
            raise ValueError("table_words must be an aligned positive table")
        if 4 * self.table_words > 1 << self.id_bits:
            raise ValueError("stored trail number does not fit")

    @property
    def key_bits(self): return 63 - self.id_bits
    @property
    def capacity(self): return 4 * self.table_words
    @property
    def scratch(self): return self.table_words
    @property
    def lane_ids(self): return self.scratch + 256
    @property
    def lane_starts(self): return self.lane_ids + 256
    @property
    def data(self): return self.lane_starts + 256
    @property
    def memory_words(self): return self.data + 16


def _emit_dp_mask(a, dplo: int, dk: int, dt: int):
    b = base
    a.or_(b.R_TMP, dplo, dplo + 1)
    for plane in range(dplo + 2, 240):
        a.or_(b.R_TMP, b.R_TMP, plane)
    a.or_(b.R_DPM, b.R_PREFILTER, b.R_TMP); a.not_(b.R_DPM, b.R_DPM)
    bits = [(dt >> (dk - 1 - i)) & 1 for i in range(dk)]
    last_one = max(i for i, bit in enumerate(bits) if bit)
    first = True
    for i in range(last_one + 1):
        plane = dplo - 1 - i
        a.not_(b.R_X, plane)
        if bits[i]:
            if first:
                a.and_(b.R_Y, b.R_DPM, b.R_X); first = False
            else:
                a.and_(b.R_X, b.R_DPM, b.R_X); a.or_(b.R_Y, b.R_Y, b.R_X)
            if i < last_one: a.and_(b.R_DPM, b.R_DPM, plane)
        else:
            a.and_(b.R_DPM, b.R_DPM, b.R_X)
    a.mov(b.R_DPM, b.R_Y)


def _emit_ctz(a):
    b = base
    a.movi(b.R_LANE, 0); a.mov(b.R_X, b.R_DPM)
    for i, shift in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        a.andi(b.R_Y, b.R_X, (1 << shift) - 1)
        a.jnei(b.R_Y, 0, f"ctz_{i}")
        a.shri(b.R_X, b.R_X, shift); a.addi(b.R_LANE, b.R_LANE, shift)
        a.label(f"ctz_{i}")
    a.subi(b.R_Y, b.R_DPM, 1); a.and_(b.R_DPM, b.R_DPM, b.R_Y)


def _emit_scratch_routines(a, layout):
    b = base
    a.label("setwalk")
    a.movi(b.R_ONEBIT, 1); a.shl(b.R_ONEBIT, b.R_ONEBIT, b.R_LANE); a.not_(b.R_MASK, b.R_ONEBIT)
    a.lda(b.R_PTR, layout.scratch); a.movi(b.R_INDEX, 0)
    a.label("setwalk_loop")
    a.ld(b.R_X, b.R_PTR); a.and_(b.R_X, b.R_X, b.R_MASK)
    a.shr(b.R_Y, b.R_POINT, b.R_INDEX); a.andi(b.R_Y, b.R_Y, 1); a.shl(b.R_Y, b.R_Y, b.R_LANE)
    a.or_(b.R_X, b.R_X, b.R_Y); a.st(b.R_PTR, 0, b.R_X)
    a.addi(b.R_PTR, b.R_PTR, 1); a.addi(b.R_INDEX, b.R_INDEX, 1)
    a.jnei(b.R_INDEX, 256, "setwalk_loop"); a.jr(b.R_LINK)

    a.label("gather")
    a.movi(b.R_ACC, 0); a.lda(b.R_PTR, layout.scratch); a.movi(b.R_INDEX, 0)
    a.label("gather_loop")
    a.ld(b.R_X, b.R_PTR); a.shr(b.R_X, b.R_X, b.R_LANE); a.andi(b.R_X, b.R_X, 1)
    a.shl(b.R_X, b.R_X, b.R_INDEX); a.or_(b.R_ACC, b.R_ACC, b.R_X)
    a.addi(b.R_PTR, b.R_PTR, 1); a.addi(b.R_INDEX, b.R_INDEX, 1)
    a.jnei(b.R_INDEX, 256, "gather_loop"); a.jr(b.R_LINK)

    a.label("restore_planes")
    for plane in range(256): a.ld(plane, b.R_ZERO, layout.scratch + plane)
    a.jr(b.R_LINK)


def _emit_replay(a, layout, replay_cap: int, threshold: int):
    b = base
    a.label("eval_f")
    b._emit_message_state(a, layout.data)
    a.emit(b.Op.PERM, a=b.R_STATE); a.ld(b.R_PD, b.R_ZERO, layout.data + 7)
    a.xor(b.R_F, b.R_STATE, b.R_PD); a.jr(b.R_LINK2)
    a.label("output_message")
    b._emit_message_state(a, layout.data); a.jr(b.R_LINK2)

    a.label("match")
    a.ld(b.R_Y, b.R_LANE, layout.lane_ids); a.ld(b.R_LB, b.R_LANE, layout.lane_starts)
    a.sub(b.R_LB, b.R_C1, b.R_LB); a.jgei(b.R_LB, replay_cap + 1, "replay_fail")
    a.add(b.R_P, b.R_RHO, b.R_X); a.add(b.R_Q, b.R_RHO, b.R_Y)
    a.mov(b.R_U, b.R_P); a.movi(b.R_LA, 0)
    a.label("measure")
    a.jal(b.R_LINK2, "eval_f"); a.addi(b.R_LA, b.R_LA, 1); a.jlti(b.R_F, threshold, "measured")
    a.jgei(b.R_LA, replay_cap, "replay_fail"); a.mov(b.R_U, b.R_F); a.jmp("measure")
    a.label("measured")
    a.jlt(b.R_LA, b.R_LB, "advance_q"); a.sub(b.R_N, b.R_LA, b.R_LB); a.mov(b.R_MIN, b.R_LB)
    a.label("advance_p")
    a.jeqi(b.R_N, 0, "lock"); a.mov(b.R_U, b.R_P); a.jal(b.R_LINK2, "eval_f")
    a.mov(b.R_P, b.R_F); a.subi(b.R_N, b.R_N, 1); a.jmp("advance_p")
    a.label("advance_q")
    a.sub(b.R_N, b.R_LB, b.R_LA); a.mov(b.R_MIN, b.R_LA)
    a.label("advance_q_loop")
    a.jeqi(b.R_N, 0, "lock"); a.mov(b.R_U, b.R_Q); a.jal(b.R_LINK2, "eval_f")
    a.mov(b.R_Q, b.R_F); a.subi(b.R_N, b.R_N, 1); a.jmp("advance_q_loop")
    a.label("lock")
    a.jeq(b.R_P, b.R_Q, "replay_fail")
    a.label("lock_loop")
    a.jeqi(b.R_MIN, 0, "replay_fail")
    a.mov(b.R_U, b.R_P); a.jal(b.R_LINK2, "eval_f"); a.mov(b.R_FP, b.R_F)
    a.mov(b.R_U, b.R_Q); a.jal(b.R_LINK2, "eval_f"); a.jeq(b.R_FP, b.R_F, "found")
    a.mov(b.R_P, b.R_FP); a.mov(b.R_Q, b.R_F); a.subi(b.R_MIN, b.R_MIN, 1); a.jmp("lock_loop")
    a.label("found")
    a.mov(b.R_U, b.R_P); a.jal(b.R_LINK2, "output_message")
    for word in range(4): a.st(b.R_ZERO, layout.data + 8 + word, b.R_STATE + word)
    a.mov(b.R_U, b.R_Q); a.jal(b.R_LINK2, "output_message")
    for word in range(4): a.st(b.R_ZERO, layout.data + 12 + word, b.R_STATE + word)
    a.halt(1)
    a.label("replay_fail"); a.halt(13); a.label("end")


def build_stored(layout: StoredLayout, *, replay_cap: int, tb: int,
                 hit_limit: int, dplo: int, dk: int, dt: int):

    b = base
    a = b.Assembly(layout)
    threshold = dt << (dplo - dk)
    record_mask = (1 << 64) - 1
    match_mask = (1 << (layout.key_bits + 1)) - 1

    a.label("start")
    a.emit(b.Op.RND, d=b.R_RHO); a.movi(b.R_NEXT_ID, 256); a.movi(b.R_HITS, 0)
    a.movi(b.R_COUNTER, 0); a.movi(b.R_ZERO, 0); a.not_(b.R_ONES, b.R_ZERO); a.movi(b.R_PTR, 0)
    a.label("clear")
    for offset in range(8): a.st(b.R_PTR, offset, b.R_ZERO)
    a.addi(b.R_PTR, b.R_PTR, 8); a.jlti(b.R_PTR, layout.table_words + 256, "clear")
    a.movi(b.R_LANE, 0)
    a.label("initial_walks")
    a.add(b.R_POINT, b.R_RHO, b.R_LANE); a.st(b.R_LANE, layout.lane_ids, b.R_LANE)
    a.st(b.R_LANE, layout.lane_starts, b.R_ZERO); a.jal(b.R_LINK, "setwalk")
    a.addi(b.R_LANE, b.R_LANE, 1); a.jlti(b.R_LANE, 256, "initial_walks")
    a.jal(b.R_LINK, "restore_planes"); a.jmp("@STEP")

    a.label("loop"); a.jeq(b.R_PREFILTER, b.R_ONES, "continue")
    a.label("hit")
    a.addi(b.R_HITS, b.R_HITS, 1); a.jlti(b.R_HITS, hit_limit + 1, "hit_ok"); a.halt(10)
    a.label("hit_ok"); _emit_dp_mask(a, dplo, dk, dt); a.addi(b.R_C1, b.R_COUNTER, 1)
    a.label("save_planes")
    for plane in range(256): a.st(b.R_ZERO, layout.scratch + plane, plane)
    a.label("dp_loop"); a.jeqi(b.R_DPM, 0, "restore_after_hit")
    a.label("one_dp"); _emit_ctz(a); a.jal(b.R_LINK, "gather")

    a.label("record")
    a.andi(b.R_RECORD, b.R_ACC, (1 << layout.key_bits) - 1)
    a.shli(b.R_RECORD, b.R_RECORD, 1); a.addi(b.R_RECORD, b.R_RECORD, 1)
    a.ld(b.R_ID, b.R_LANE, layout.lane_ids); a.shli(b.R_ID, b.R_ID, layout.key_bits + 1)
    a.or_(b.R_RECORD, b.R_RECORD, b.R_ID)
    
    sb = (2 * layout.table_words - 1).bit_length() - 1
    a.andi(b.R_SLOT, b.R_ACC, (1 << sb) - 1); a.jlti(b.R_SLOT, layout.table_words, "slot_ok")
    a.subi(b.R_SLOT, b.R_SLOT, layout.table_words); a.label("slot_ok")
    a.label("probe")
    a.ld(b.R_WORD, b.R_SLOT)
    for slot in range(4):
        if slot:
            a.shri(b.R_Y, b.R_WORD, 64 * slot); a.andi(b.R_X, b.R_Y, record_mask)
        else: a.andi(b.R_X, b.R_WORD, record_mask)
        a.jeqi(b.R_X, 0, f"empty_{slot}")
        a.xor(b.R_X, b.R_X, b.R_RECORD); a.andi(b.R_X, b.R_X, match_mask)
        a.jeqi(b.R_X, 0, f"match_{slot}")
    a.label("probe_next")
    a.addi(b.R_SLOT, b.R_SLOT, 1); a.jnei(b.R_SLOT, layout.table_words, "probe")
    a.movi(b.R_SLOT, 0); a.jmp("probe")
    for slot in range(4):
        a.label(f"empty_{slot}")
        if slot:
            a.shli(b.R_X, b.R_RECORD, 64 * slot); a.or_(b.R_WORD, b.R_WORD, b.R_X)
        else: a.or_(b.R_WORD, b.R_WORD, b.R_RECORD)
        a.st(b.R_SLOT, 0, b.R_WORD); a.jmp("insert_done")
    a.label("insert_done")
    a.mov(b.R_TMP, b.R_C1); a.jal(b.R_LINK2, "restart"); a.jmp("dp_loop")
    for slot in range(4):
        a.label(f"match_{slot}")
        a.shri(b.R_X, b.R_WORD, 64 * slot + layout.key_bits + 1)
        a.andi(b.R_X, b.R_X, (1 << layout.id_bits) - 1); a.jmp("match")

    a.label("restore_after_hit"); a.jal(b.R_LINK, "restore_planes")
    a.label("continue")
    a.addi(b.R_COUNTER, b.R_COUNTER, 1); a.jnei(b.R_COUNTER, tb, "@STEP")
    a.label("deadline"); a.halt(12)

    a.label("restart")
    a.jnei(b.R_NEXT_ID, layout.capacity, "restart_ok"); a.halt(11)
    a.label("restart_ok")
    a.st(b.R_LANE, layout.lane_ids, b.R_NEXT_ID); a.st(b.R_LANE, layout.lane_starts, b.R_TMP)
    a.add(b.R_POINT, b.R_RHO, b.R_NEXT_ID); a.addi(b.R_NEXT_ID, b.R_NEXT_ID, 1)
    a.jal(b.R_LINK, "setwalk"); a.jr(b.R_LINK2)

    _emit_scratch_routines(a, layout)
    _emit_replay(a, layout, replay_cap, threshold)
    a.resolve()
    return a


@dataclass(frozen=True)
class ExactCounts:
    instructions: int
    setwalk: int
    gather: int
    restore: int
    restart: int
    restart_halt: int
    hit: int
    ctz_clear: int
    record_slot: int
    probe_word: int
    probe_wrap: int
    probe_end: int
    insert: int
    dp_fixed: int
    deadline_final: int
    eval_f: int
    output_message: int
    measure_iter: int
    replay_iter: int
    replay_const: int
    setup: int


def counts_stored(a, layout: StoredLayout) -> ExactCounts:
    L = a.labels; seg = lambda first, last: L[last] - L[first]
    setwalk_prefix = seg("setwalk", "setwalk_loop")
    setwalk_body = L["gather"] - 1 - L["setwalk_loop"]
    setwalk = setwalk_prefix + 256 * setwalk_body + 1
    gather_prefix = seg("gather", "gather_loop")
    gather_body = L["restore_planes"] - 1 - L["gather_loop"]
    gather = gather_prefix + 256 * gather_body + 1
    restore = seg("restore_planes", "eval_f")
    restart_halt = seg("restart", "restart_ok") - 1 + 1
    restart = seg("restart", "restart_ok") - 1 + seg("restart_ok", "setwalk") + setwalk
    hit = seg("hit", "hit_ok") - 1 + seg("hit_ok", "save_planes")
    ctz_clear = seg("one_dp", "record") - 1
    record_slot = seg("record", "probe")
    probe_word = seg("probe", "probe_next") + 3
    probe_wrap = 2
    probe_end = 1 + 7 + 8 * 2 + 4
    
    insert = 4
    dp_fixed = 2 + 256 + ctz_clear + 1 + gather + record_slot + probe_end + probe_wrap + insert + 3 + 1 + restore
    eval_f = seg("eval_f", "output_message") - 1 + base.UNIT
    output_message = seg("output_message", "match")
    measure_iter = eval_f + 8
    replay_iter = 2 * eval_f + 13
    replay_const = 79
    clear_iterations = (layout.table_words + 256) // 8
    setup = seg("start", "clear") + clear_iterations * 11 + 1
    setup += 256 * (7 + setwalk) + 1 + restore + 1
    return ExactCounts(len(a.instructions), setwalk, gather, restore, restart,
                       restart_halt, hit, ctz_clear, record_slot, probe_word,
                       probe_wrap, probe_end, insert, dp_fixed,
                       seg("deadline", "restart"), eval_f, output_message,
                       measure_iter, replay_iter, replay_const, setup)


def build(rounds: int, slots: int, table_words: int, link: int, parameters: dict,
          hit_limit: int):
    configure(link, 271 * rounds)
    if slots == 5:
        layout = base.Layout(table_words, 5, 51)
        assembly = base.build_program(
            layout, replay_cap=parameters["LRC"], tb=parameters["Tb"],
            hit_limit=hit_limit, dplo=parameters["DPLO"],
            dk=parameters["DK"], dt=parameters["DT"],
        )
        counts = base.counts(assembly, layout)
    elif slots == 4:
        layout = StoredLayout(table_words)
        assembly = build_stored(
            layout, replay_cap=parameters["LRC"], tb=parameters["Tb"],
            hit_limit=hit_limit, dplo=parameters["DPLO"],
            dk=parameters["DK"], dt=parameters["DT"],
        )
        counts = counts_stored(assembly, layout)
    else:
        raise ValueError("unsupported table layout")
    binary = b"".join(instruction.encode() for instruction in assembly.instructions)
    return layout, assembly, counts, binary


def manifest(rounds: int, slots: int, table_words: int, link: int,
             parameters: dict, hit_limit: int) -> dict:
    layout, assembly, counts, binary = build(
        rounds, slots, table_words, link, parameters, hit_limit,
    )
    return {
        "round": rounds, "slots": slots, "table_words": table_words,
        "capacity": layout.capacity, "link_register": link,
        "register_words": base.NREGS, "instructions": len(assembly.instructions),
        "bytes": len(binary), "sha256": hashlib.sha256(binary).hexdigest(),
        "labels": assembly.labels, "counts": asdict(counts),
    }


import base64,hashlib,io,json,lzma,sys
R=10;S=20512;U=82048;SPW=4;KEY=46;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 629, 'HF': 111, 'J': 71510, 'LRC': 45324847211160342250514623108218880, 'Tb': 1326450541133374800865240636180135936, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 162, 'dp_loop': 418, 'one_dp': 420, 'ctz_0': 427, 'ctz_1': 432, 'ctz_2': 437, 'ctz_3': 442, 'ctz_4': 447, 'ctz_5': 452, 'ctz_6': 457, 'ctz_7': 462, 'record': 465, 'slot_ok': 475, 'probe': 475, 'probe_next': 507, 'empty_0': 512, 'empty_1': 515, 'empty_2': 519, 'empty_3': 523, 'insert_done': 527, 'match_0': 530, 'match_1': 533, 'match_2': 536, 'match_3': 539, 'restore_after_hit': 542, 'continue': 543, 'deadline': 546, 'restart': 547, 'restart_ok': 550, 'setwalk': 556, 'setwalk_loop': 561, 'gather': 573, 'gather_loop': 576, 'restore_planes': 586, 'eval_f': 843, 'output_message': 873, 'match': 900, 'measure': 909, 'measured': 917, 'advance_p': 921, 'advance_q': 928, 'advance_q_loop': 930, 'lock': 937, 'lock_loop': 939, 'found': 952, 'replay_fail': 965, 'end': 966};EXPECTED='176970960e7521916df812adfcfbfe95cfda8372d4af876748a7bc520c2c6305';NI=966;NB=30912
K=(0, 0, 14296593545235584991, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 8185834404736284145, 0, 17927975257650305787, 2075075264236983312, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(3911089904694572841, 9806839383433692426, 14497373572058597470, 4731312883675170900);M64=(1<<64)-1;M256=(1<<256)-1
RC=(1,32898,9223372036854808714,9223372039002292224,32907,2147483649,9223372039002292353,9223372036854808585,138,136,2147516425,2147483658,2147516555,9223372036854775947,9223372036854808713,9223372036854808579,9223372036854808578,9223372036854775936,32778,9223372039002259466,9223372039002292353,9223372036854808704,2147483649,9223372039002292232)
ROT=(0,1,62,28,27,36,44,6,55,20,3,10,43,25,39,41,45,15,21,8,18,2,61,56,14)
COUNTER,NEXT,RHO,ONES,PF,HITS,LR,LR2,ZERO=range(LINK+1,LINK+10)
LANE,C1,TMP,REC,SLOT,WORD,X,Y,POINT=256,258,260,261,262,263,265,266,267
ACC,ONEBIT,MASK,PTR,INDEX,ID,REPEATED=259,273,268,269,270,271,272
PA,QA,N,MIN,LA,LB,UU,FF,FP,PDR=280,281,282,283,284,285,286,287,288,289
STATE=300
def rol(x,n):return ((x<<n)|(x>>(64-n)))&M64 if n else x
def perm(a):
 for rc in RC[:R]:
  c=[a[x]^a[x+5]^a[x+10]^a[x+15]^a[x+20] for x in range(5)];d=[c[(x-1)%5]^rol(c[(x+1)%5],1) for x in range(5)];b=[0]*25
  for y in range(5):
   for x in range(5):i=x+5*y;b[y+5*((2*x+3*y)%5)]=rol(a[i]^d[x],ROT[i])
  for y in range(5):
   for x in range(5):i=x+5*y;a[i]=(b[i]^((~b[(x+1)%5+5*y])&b[(x+2)%5+5*y]))&M64
  a[0]^=rc
def message(u):
 q=[(u>>(64*i))&M64 for i in range(4)];a=list(K[:16]);a[1]^=q[0];a[6]^=q[1];a[11]^=q[0]^q[1];a[4]^=q[2];a[9]^=q[3];a[14]^=q[2]^q[3]
 return b''.join(x.to_bytes(8,'little') for x in a)
def chain(u):
 a=list(K);m=message(u)
 for i in range(16):a[i]=int.from_bytes(m[8*i:8*i+8],'little')
 perm(a);return sum((a[i]^PD[i])<<(64*i) for i in range(4))
def decode(raw):
 if len(raw)!=NB or len(raw)//32!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('controller bytes')
 out=[]
 for i in range(NI):
  x=raw[32*i:32*i+32]
  if x[7]:raise AssertionError('reserved byte')
  out.append((x[0],int.from_bytes(x[1:3],'little'),int.from_bytes(x[3:5],'little'),int.from_bytes(x[5:7],'little'),int.from_bytes(x[8:],'little')))
 return out
class VM:
 def __init__(s,code):
  s.c=code;s.r=[0]*NREG;s.m=[0]*(DATA+16);s.pc=0;s.halt=None;s.hook=None
  for w in range(7):s.m[DATA+w]=sum(K[4*w+k]<<(64*k) for k in range(min(4,25-4*w)))
  s.m[DATA+7]=sum(PD[k]<<(64*k) for k in range(4))
 def run(s,start,stops=(),limit=1500000):
  s.pc=start;n=0
  while s.halt is None and s.pc not in stops:
   if n>=limit:raise AssertionError('step limit')
   s.step();n+=1
  return s.pc
 def step(s):
  if s.pc==LABEL['eval_f'] and s.hook is not None:s.r[FF]=s.hook(s.r[UU])&M256;s.pc=s.r[LR2];return
  op,d,a,b,im=s.c[s.pc];s.pc+=1;r=s.r
  if op==0:r[d]=r[a]^r[b]
  elif op==1:r[d]=r[a]&r[b]
  elif op==2:r[d]=r[a]|r[b]
  elif op==3:r[d]=r[a]^M256
  elif op==4:r[d]=(r[a]+r[b])&M256
  elif op==5:r[d]=(r[a]-r[b])&M256
  elif op==6:r[d]=(r[a]<<(r[b]&255))&M256
  elif op==7:r[d]=r[a]>>(r[b]&255)
  elif op==8:r[d]=int(r[a]==r[b])
  elif op==9:r[d]=int(r[a]<r[b])
  elif op==10:r[d]=r[a]
  elif op==11:r[d]=(r[a]+im)&M256
  elif op==12:r[d]=(r[a]-im)&M256
  elif op==13:r[d]=(r[a]<<(im&255))&M256
  elif op==14:r[d]=r[a]>>(im&255)
  elif op==15:r[d]=r[a]&im
  elif op==16:r[d]=int(r[a]==im)
  elif op==17:r[d]=int(r[a]<im)
  elif op==18:r[d]=im
  elif op==19:r[d]=s.m[r[a]+im]
  elif op==20:s.m[r[a]+im]=r[b]
  elif op==21:r[d]=im
  elif op==22:
   if r[a]:s.pc=im
  elif op==23:
   if not r[a]:s.pc=im
  elif op==24:s.pc=im
  elif op==25:r[d]=s.pc;s.pc=im
  elif op==26:s.pc=r[a]
  elif op==27:r[d]=0xC0DEC0DE
  elif op==28:
   st=[(r[STATE+i//4]>>(64*(i%4)))&M64 for i in range(25)];perm(st)
   for w in range(7):r[STATE+w]=sum(st[4*w+k]<<(64*k) for k in range(min(4,25-4*w)))
  elif op==29:s.halt=im
  else:raise AssertionError('opcode')
def checks(code):
 v=VM(code);u=0x123456789abcdef0123456789abcdef;v.r[UU]=u;v.r[LR2]=NI;v.run(LABEL['eval_f'],(NI,));assert v.r[FF]==chain(u)
 pts=(1,2,3,(1<<255)|5);v=VM(code)
 for bit in range(256):v.m[SCR+bit]=sum(((p>>bit)&1)<<j for j,p in enumerate(pts))
 v.r[LANE]=3;v.r[LR]=NI;v.run(LABEL['gather'],(NI,));assert v.r[ACC]==pts[3]
 v.r[POINT]=0xdeadbeef;v.r[LR]=NI;v.run(LABEL['setwalk'],(NI,));v.r[LR]=NI;v.run(LABEL['gather'],(NI,));assert v.r[ACC]==0xdeadbeef
 sentinel=(1<<192)-1;v=VM(code);v.run(LABEL['start'],(sentinel,));assert v.pc==sentinel
 v=VM(code);v.r[LANE]=0;v.r[C1]=1;v.r[RHO]=0;v.r[X]=2;v.m[LID]=3;v.m[LST]=0;v.hook=lambda x:5;v.run(LABEL['match']);assert v.halt==1
 assert b''.join(v.m[DATA+8+i].to_bytes(32,'little') for i in range(4))==message(2) and b''.join(v.m[DATA+12+i].to_bytes(32,'little') for i in range(4))==message(3)
 v=VM(code);v.r[LANE]=0;v.r[C1]=1;v.r[X]=2;v.m[LID]=3;v.m[LST]=0;v.hook=lambda x:x;v.run(LABEL['match']);assert v.halt==13
 if SPW==5:
  rec=1|(0x12345<<1);v=VM(code);v.r[SLOT]=0;v.r[REPEATED]=sum(rec<<(51*k) for k in range(5));v.m[0]=rec<<(51*3);v.run(LABEL['probe'],(LABEL['match'],));assert v.r[X]==((51*3)<<S.bit_length())
  last=(S-1)|((51*4)<<S.bit_length());limit=51*5<<S.bit_length()
 else:
  key=0x12345;sid=U-7;rec=1|(key<<1)|(sid<<(KEY+1));other=1|(0x54321<<1);v=VM(code);v.r[SLOT]=0;v.r[REC]=1|(key<<1)|(17<<(KEY+1));v.m[0]=other|(other<<64)|(rec<<128)|(other<<192);v.run(LABEL['probe'],(LABEL['match'],));assert v.r[X]==sid
  last=U-1;limit=U
 v=VM(code);v.r[NEXT]=last;v.r[LANE]=5;v.r[TMP]=7;v.r[RHO]=9;v.r[LR2]=NI;v.run(LABEL['restart'],(NI,));assert v.m[LID+5]==last and v.r[NEXT]==limit
 v=VM(code);v.r[NEXT]=limit;v.run(LABEL['restart']);assert v.halt==11
def projection(seed):
 raw=hashlib.shake_256(b'hashsmash-sha3-exact-controller-v1'+bytes.fromhex(seed)).digest(17*32);pts=[int.from_bytes(raw[32*i:32*i+32],'little') for i in range(17)];seen={};n=0
 for _ in range(4):
  nxt=[]
  for p in pts:
   f=chain(p);n+=1;k=f&4095
   if k in seen and seen[k]!=p:return message(seen[k]).hex(),message(p).hex(),n
   seen.setdefault(k,p);nxt.append(f)
  pts=nxt
 return None,None,n
def controller_main():
 q=json.load(sys.stdin);event={'kind':'digest-xor-mask','mask_hex':'ff0f'+'00'*30,'expected_hex':'00'*32}
 if q.get('schema_version')!=1 or q.get('experiment_id')!='exact-controller' or q.get('target_profile')!=f'sha3-256-r{R}-prefix-v1' or q.get('event')!=event:raise ValueError('request')
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5181452367715577589597074056282113)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;AGevXk7pWZ3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<<x^oeSa{pZ43czJFUMO0;0aB$p+#d?|vkW-4i2F!aK(U!MC$GJ2*G<R!6)i>bucyl0eI_QZrv(gTSIy|KH5aAWcdHxgk5Y+`*aHz7MmV$XFx(WDTr=+?u#^kuchLLo_6XS*q&CBYZw0aqtYq!pM@yQnDX6O_>&9}>ee83;CLb+b<O|`2uBu1#@=EN%2kc^%SwR%9hwIGLsiw>5I>i2s2kV2KEbm6dSb4W>(<pvPL%F3sp3TVjDM$)Cds~C0Axx>(DJPiD6IOs_m~#m!f(I7LH%m-9N9%PeR@&r|k=Ov-2=bNU?KVJJ>aIU8mt})76J@sj(>C!2JkyM(jdP#(WA5Q3QDn|*Y~;26DF>Pd-YwN4C~q6}dX5)GQSGlOhtpHLUoUUOPr+UY$ZdjmTbZ{2kktHsW9bk%AYt0{Or}UQ`%Hn=+kaeeU(+>sxEYv0*Q?^q*70oiDkNZ*H^~J*X%7{rM0q9%e-g!2QZYg=M@Z5&L^KH*Op_dxU?V^3U>TAPOZCZ4*#=&e*e-(9(U9F^=Z_wKFq5%4jP5LS;0}gayJtZNfIxQw-(K+oa9Pm!h38eu%iC6b`SvwN8wHPtL$*N#GiFp}Y0c4|E`00kHOE>>nhu;Rp`W;+RwYJ{-wgc>iMlczPnK18eq|O}z1kp~)x@3c_FI{jlNTem6-6vWL;n}4Hr3(ihnXem74U8zBxzK~h2QDj=+jn&BU-;qW;$QG?&kegVaX%;FYfxK!r*$gjwX&qQ~tM~7e6s7I-zBIa7wlGjTHuZA97a)f$(D2+zxSPrL|0%?nlh+GOjhWGuCmB-_H8JQtj+-BSg{pQkn3ockJ3ry}sN`K5U?Sfa1w4=)0|;Ds`5=(;WS@s6rwjPP5$+qFFH!u>!EwKzB+IJD03OVK0*}fn4YlD!i9td>R^(kTkRmtz0<(x{kl+-aS{O+4SkOLGO23Ait!KO%6W&CwgvQ^G}vh6542*FSJ#|H>RQCc!XA@>kTrd<ks$;NMy+%z!IDIL@(`AU5K==%o6Pp<S&qK3PRV!glWTmUa4r^$U+~E&7+*XO_%=e?pXx#;>sz6DDvWaWc0W*TTeJpN_3Hod1<|iCZ5AHqvWh{j2L5W2nO(&33!PtsghAy6cdDbQq4&>j9^Q(waEQJOK^4Xy0<Xlp&GrDyd99xXK!eY8r^?9Sl+!X&<s1rJ*jg?ky6d3S}qForE9+_kKG4UbWC+wjCX^q@BhFsA#GNDk6FTV6>BX?M*rDf2>+}KnYtjxITj>6--eLli;^%|`&0R3liO0`=mJE^!QV5t9q4}a`6~4V?AsRz3`o$uxi0pWyI>%4*bA(f#oBKsZuC?8OSBBA{pw+@W)p%L@|5$Hp*NwMw=7BEeTNl$JWip<kiNXX?LHuEd%bmaheUu4&FL^3=GEJ#S&O|>PGrIzH1opJkRP_G@)<?*yhjq{-xjShlo7|Vdd;Owo1VZA$%Lt>X48-ZEiF;z_0#lY227_Ib=7nZr=s%P^tSE#72#M-hVAQtyEv&K+|ZtpHeu*a-%c*<24E02R6y0bZ(@ygm*;^X0ASROl1l#=EoUaj8}SEZRC8n%ir18V0M8%kC<ExD=<-{r3^~8G)4DW#ukn)7fy8LnKyz-+wIwj_6Cy~kjJm{Z+5(Dqh~<2a=%`{I3R&UGKCNiP#Q!4e)7m^`wVM;*CcO^cK6`FDhC53Vqc+%xc^wqz0_-}hn0J8tHlJd$U%WejB}b58UmyH-a$n8T6SzMyimslU>E!BC1ejPEe{?0xM>*CRz(b6cb^6>sht$y2refb=p*V2WwUdnjz785g$bE){&TaT2Qc=sa(|hFWaj<j6`!!qR-{8b{JJ{sjBoDJl;|7fI2(1abB0z!%6?s7PgXxRXPZswdlHGi`n^%UMKT(b)Hj0I_vac<Yg<}imb%%8e)8QM<pCrH#ErGV9&U&v~8GGDRJxdCy!Px*zVkBk|>4BJZ;DF+j-(bfovO6q)px|Ngz_9f9@VyST)oz2pxlKDR^PH4=OkiAG=kDAs<a$8!*G6L~wJHR=qZ-8Hk^M*%dlutKdFTF=rl>NGlQK)M8pt~(QCFOf#Bm`ft0-uJUv#-#xw0oTu`XS6gB?nT#kYPVDG;i8ztD~m4mdN&0e?R6$DV2~>Gr(h_si05cA}*)ihv$6NCUJ+t7D3BEn$rj!1n!waDsCS@4rT1H+rMUQPF?+WGt}ea)noQQhk{-|KlqBMD^a@sD}7Nmq_hZ{WvY;VVT&L_?byJ-yU1WM$3JUU=jHLaJjQ0(34*beIt`CO77m!(uW`xmf;TO=Y8Mv-%Xx2q`UOYa%n9{Z!Rmy1oUnda-p?lbS-9HO(+Bim|aNz(hYfVg{*E68~?T%Ehv<Zw@5}Lwk6LvtG`NMMmh~-d`X~d1J%%}B6kvc!pO^?^!Ab=_3x&SehhoGFkB{ZBM+39qhZqrtw-oB0A&xa4^t_D#vcz%*x!Kw2eu8ACHH-PBp@JSLc@NVs59$)0nJ0hzkDmfkjMB1WvyH4>oc_=@~nSGuh=Z3dEFj+(<Kp@+2tzEg<X8OQ9%HoQxbTmgF(!hK25@wq#<I;&2o7$@WXF3gtj%PfTFp`&Px_}uM567A<htJN|nX8vGOgs86Ek1O~g*xV>Or{JjP^REx7fJ49m%D*<3`eJcX`$?oM-AEB(5g`-FY>=e-FKawAc65jx;UJU0LycVQx`rJIc)s*;-gAS}m_x$I<2%r&4Q>jE~uLtUs52>2*PHEMRMx2UT;58Eo*mZo%ubYq2&xpe#sxZbTN^U8p|#@c$i%QsQqm|nntad*oN;Xh0^0A_j;{hi~<3UprXw;8KHzeUgmp>VDecmNUsfZ;Gx<D>CLYl{?E_F@3qiqED?Ta#;!4%#tn>Do)Dtv~LSqi|B1DU+Q2?#2(=ADIS{Ar8B^n|Yndq!q{2KjE@7yvp{fK4GP>Al3HtNCO|i5@wecT7Cc?nmRV@mZ|w#4FP0vz`$q{8`JcZt~bNSJdMflx{joj&qJoH8SHo+wItmmzwaTA^|saOKZ~(RUM^9vmy={Cg_$}c^Ti6D9wWw>>R6B$@FMT<d=wy92I4(}^<|dN%_pTH&3VFY={pF%Wbd&POkjR#G@_>LMh6j9{8pES+)87Sv6;@drZD}Wlv{3(t45Q^3bV|dXXQL|`^ZB<x5yh7K)7Al?c4ezMJ~5Gxs>E}kirfPFmCF|i@>z{gT@ZLI7P!LI<92Yak-I$#rPc}0=Q+*c|iKyp+JA4H7q)H%cg5=>9r_<vr$l!fB@%1hX$-ZM0BLq;$1Og=d)12KsD9>k}sg+LieY<S+2n_?-OS=oSh2+0)*=O8C5=NUO3jiZQ`HV>D8+^CKsVLpTm}Wf-x@!k~)R`;eRB$ZCF9Shb|`kP;6+<j9-GTaHR|@;?CnrtDfF9Deq9GU8cI>y3goBT;1(hOd+2(R$*@x-RRJ&6{K<FlN#pG+4M#90TevNGF~GyiX{|V*=3>fG4SXEnNu>{I{;^Ocq=PDOXoG<^V*E$ks7V~Xw+=_tamDrLqKma>5=pC?sRgH0wEm9xIxC?*({;x!;waE?Z-Pg`jCikSmu*)+=Xio`Z)Jt%a@crZJ+g%WfBPaKW$y@5BP)i)qfN`^1%9Q1{ei+@t(0PCOeX^Ly*`k2Qsf`<XK<06JK3UXWFM|?bp?aPH)OMWJm`#b^7dzY|n@DcqMQ}O2<~{KvBO>{ZiW<Vv8o$?aw&E3XAb``zgcHMZD0(!%zfvi*RwWzv_R@u<&s1A5U|X{vp2zb>HT5ojFKa(mHo=z9TT`D;ozE&gIX1Hc%`!f)9SpD#Flx-ue+;KmGGs6FpUz!GA_z(>S^zscKF3R!ha#Ad=kjlCy?%%Yc`J-<#haM_9q9iqIn%cM0FLOHi?vzP@RVU-VH;?DwckiloE}C<IG|Gq~D_oDf>nh#{BWb$+$HD=*ez$7cnn?6a|WCWqZ_POff3NWD|ku{#|F8|aw&@Ctu#og;CyH%`bTc}R~A$OBx5>8ay;C~(m;7-ortBKf`&4a9^pfuSFCG*}*Mf3gB|4xYO0?vWKTpJ<$!L79XRiOA!n4D`ZStmlH~c@DZ57V1tadsWY2kn8j(z_Ce_91NWM2Ya3$cj3;!S9#yU{lqAnc6>^hm!qe44_&~m(wab6n?p`zRt&YBYhTy}@grac2jb`e%S!Ve@ZW`&+g&WZCotJ*D_8h$%5Y=*pPX;Vuc+#tFUI~mUv#r_2lMWi?DdEh6w+osPfrL?FU&mGhde9%yKeyy${U`%LhtMsP1y6=v3fSnt+YJh!1Bn^8yLvAvNK0QEbC*xI<f@k8A;WG9Io&qlW;$1oXe63K@96AK4e)<|L^0`ULJJ2sAj0y_-tU5KjJ7pIUW*RFXp$xVkdy7!+1@m@AVNedTnjCN_t&bAg2x9Ox>K_4JRrih~H;)o03uX?LoMLz`Pb_oF#L`gy2FbGK29l1)MYOGd}5BU_5kdtTHlyZhPpgX0E^=Hm9J4Pms-Fd&sLgFNw|7c7vTp1+l;tbTqOmB~2%!MSYC0VKt%IsLs#EfE?w)okV6YHWB;selx-B#OC52Q|GGI>ixif*>Mu;p5{>ffc6WR1JUn<Gd|t>b@4QWjOcP#L(`%MC2#+@=U;&8lIuunVZ-F!Z*?0OI8)?Jy<->t<f7;mq<MLv0VvBxi#~R1k6ZJefcu&u;s2&KMWToCzB%p?u+)#<kL#gwN+=dTAYNG?=!im;4f+D=EW>Qz4*q(Q=eZDaabn%y>e9o;#$>Mv2CrUPv?bNHC)Fq*OE#w}*+Kc1dtv#Ex02UXRBU(;3yFJk8~>zgSJsIH8Prt*rH~=8HU2sjZ>L^+mWLlv%MGcW2$;0T^|xL`ZUITK$PR<(swmT*{#%nX`rlq+RRb*Y|H&Wx_9Fs?dG?6{MC^bqsp3Hm?l;rd#JPz`Th#IZXEoQFL!d93w3aB4KSz~z2;Gmjew<dCgKF1!x269&1j;mOmJd{m>7qzRk>t)3<Poxmokk)!<6HJKPLijZ(uYK50izr3J2;=T%@i}S^NGeqkW8x9THY4_S7--AbrZGFsa_NEP%ZZNpXDvq9g^6}heJ4eq+cTUYuf}?<*9ght{vz_^xDIo1IdgnUKo{Dl;sv@a04D?(z2OP%$OXz(RiuT+Jg6n4&bLmbN(ekytU^BS(kDq|A|T(<z=t@<Dhqe`DPj2^jZ7y_(0H=)qq4bsQ*Rp?X*ginUfP6-fn5%Ntp?5ISgTNw$6M5&!3bgQEt9qUSV24?LV)_I9FMXu#}zzjP)LdP}$hE)$u|Pv3fU2qI&|@B&ozx=F#%`I)%qELL~dRT96cwGDT)GN5_M||5aKs$3_L7+}hoZZYeN4Cl|q%$bH-XuwncPwNT?k!VM(z-2y^LGXG&CzKbBO?QFgotC!QQB6*2M(p|$R4gP3Q>%L`0U-bIP4T=G1KGZW*8R;c`z73S6g040!m8*$RQ4;h%^g#)n9BElAQE4rScG+Y+q@GIcsfJc}*V)g?1)YuAU}>wQ><vXmw7ZDl?Aav~_zL*bt)n7c2i+O1uMy_f5PngXMB*~0N!l+4jshMY*M}EEKZjo*COXmmsr1kdsjw7dqWvRM@%%Da;om&`ZAs~Kl!>HyK21?S-z9T6Qri43U_REBvw`a7Rh8u@NO3oK62fTr8j%HbB$+m^FlE|qoAr5YAascn0xa&Cwl1kg_au1a#?cGz;4{^tg1$pwUs0@s1n7;PQ}XHCIy-xr*-r{3F~y!HmcOVMrIr9S;Fdx<L!e<X6@X7bK#mWji?;P*OFWnKAf?SPk!XQSutikK0khjVwVzo@k?3s9e=ekdY16Bioy`*YRfu=~*lzp>SJS_M`A1vBqbG1%&JKO_KSbKclIDQ=LXOkQtWjT9?t}lTnW`q>i?`xv&_sMa47ni<yEq_IDRXNU55gK|b}vDRrhoji9+~YZn+_P=A0)x<j>_6zrQCmiS6<$C|7%l?hH5@1hO?$D@1j`|1kEK4iQUT&CISKUl`$=QAhc@z5R!`#RI(e*otyp~a1rxVkYVX|5c{3p>+n2D<}?bf%k6ReU}&VfV+75g>+k+PL~gE455CB()dAx}H-L2_9U!Vcw=`R=^8(5*mV|zxbV0v>AMGZ)u9YB>8NKjgvKH@@o|7#{9Pc#yz;=Avm4DRLSkY0Q{pHg*Cic6lnYg&ujh+$IJTBp|o?N@I64#??q$af3t18c49O+v2kSLMmaD+E8`Tr4|LEdx&YB}vR&>uL%LAbaEi^>=^S>Is^L4}4nSUFdjT>OM4UU>abvf1bG4yWB8U2VK1(~1ph#8l2DP+<&kyK0$6HTnlRl=OIo_XnGQ9;Aj^$PkQs-eg)6RI23-uY_h1PZ(?<^aFrEVNx-AQ(iXsc=>ri7G#5K%#~>@j)RD3vBI<1KT=JG$r#ITf^mf@u?QT&;eGkt63NrRzBI*hZX`$F9YhfKvP!mKbmNb`m~d!fVc#kJgN52kfE!$I2TD6sz<O?`cxLVXDO_Ma+GwNWl*g6^4k(?g%+CmUx($PrSG)PW?vhiDZWtfR{wt6NBezVPA0WfJkRTPmI2NIoywvA&@RMo-2P1%-pBcE}g>8GB3~QA1V2Uw{%0E}T!4juXCH4vR>28(byg(2WZ!1sGbDC`hQ_F=q{OgF}#9$1ej*VQTgV90ATa@vXyscJUx9^~pa~8+%3A-KnvjI^;VH9ccA?Y1!K(!>rULT`?nmGdi_2?vE{&fTzXXSJ-Y?7fr0S91v+ba$RSwE#n<4&PNk~79JgfY0Oj$tf2Sed#H=UE@`;gL^;9P&?C7MRAxKC9#u3LOl)CFGPnZ?!xqh`qe9N&E5G2pJp8pLLAO?StFthBz^+c(UK8SF@!w?$;rP?G$+Ea*^zEcYK#2!N6;MBYtRBv}eQ~c+vyAg4vYwpB|PR0auMJ<r~S!|EXF$-lZB1IH*Hzo8Z*z355=(rh4b3zn%5-0oB__&)s^;7q@;N&YM780DVfa<yT+=#4;*IYxwEO4c?~ssIRMTYHJ=`*p;<blN)eKy&4tGZgwfkvsGZG69(5bp{58R+*jITVnutuJt@Tv^XetLB$G!J(OOrxe4sIzW5(F&0JUAvFRTIosS;`2>Pm<+oixD~zKSuRJ$*Y~{y)TYQa3ZC1qV1fi<p0eI{o?iPR!It^K@j8R5Db9U6G`u?o!4~F8R&_3KvtwoDN#ojgo!fY(apfv(ThT)qCs=KkAgtKPix;TLpO#+n^gkPLWR{NmA{xA#vi<;*`Fco5TABU$*fER$4vS;?ijFQ50!Re?EI|<m~UJ2Qlcr(zGEdbf>>5y*bh+*(Xvdei0S2;@5`@X5rXch&P3t+T3Q7d~E>0atHF0&u<>j7EC&jhdhJW>TS2)T@GbrOi82Zq3RtvH??_){YV|O#pOz+H!NvW4Ae~mUlU@!esidPqz@o20hv||5zVgQsRjG#s}E-%#W3<poY$)?=)B9fUBLPhyF|N*KQCct8NX~65n;~CM+E0wENNK(C*5jZHoM2;3bJ_j16q3#!-5x`P4h>k-KmS?Kv#kT<?$r8c9Eq+^xf&to7{S!eE3PxK(aT5!y-g<(u*zASx%iYTr+blP1xZhm|&04xDsSog#}qo3V3x3g-y)f+JMsqTqPZ7duxY(uy7W{Xu*d)`mzkpSUIZAJaE8zyE+!fO#-fW4i_nyTS?=91}x3ho-b+}O;__JJ!f`gl989X@?=H|N@+v={AYGRa}99H=KkASPNX_fCv#`(O}X~Qa7>E*K<HKJy}Wtr-v`eKQ8p)=iLhOFqh!FQ7RmChg$ypU00kXiE9g!gp?1>@w6{dPCi8?TS=_>l3<(;ct&@=%i90uG+os1iJv<@>rAnFTMwy}H9&DT0bcy{rvDH(LiiB6WT*sonlHTyu!$ATw(D$)e3yaI{S}Xbp{o-wJm}3F&@2GvrRxiY@2Vmq&>9sEJ3PBR}?046R#;?Z~XI$p!n=&kGVabBiIs$K-GEHWw2)VO+--$0AFn<FG2Jxx-KQry5^Zs+U+=RY&$ofIrCxcZ%ifp}jR(rso|4LCrb=lL#nlp=ph`j8Z-pq5RmJA5ddjn?(bl--i%J+REDb8I0tM(QDA53M|xNp^^^Fl}9)!RG`CE)MqF;0DlKR*M`5o8cvx`^+5=KD-jB50NypL5M9)5?{2@KuL`esq`{n5w10T{AvLj40$RbO3Gx20}9>H{v}!HTeix^oZgDM+oYT7x*PQBr1^}i!4jj<lT***bWoKwdLDVHK2mkb*!(W*cUT+4uQr7VQ<&Z0tr*90N$0#eeZN3Kew1n{uR~fwDywG`?uGEwFzN$@yxc}BdoWPOSGPF>+pnmzWo);t_ab;a-_S#fpQ`o>==1F!z`OhB**Q6k1Du-Oj`m?6)1@(q;^aS=S7|BY+4Tkq`T0GD7KZog&$(PXV17PxeC~!3sM$F^BLyN+6dy`D=Eh=bn9H|a^-SdO%OOmX!upa2Jsz!L;iKp_COI81@kdUvC_Kh+pI$aDo}LvR|gA$WG}e70v8-OF*;D9a-;yV^P-5#HRmC)=O^J6!CucrvmVTL#=$5x_8aWHDM9wV9u$0Z!!R=?3MpS3j7P55iM00g_!~>no=@5C2ZA$awbe`{WA@xd(HSTp%J=v1-c$qI4H;kyhl%nFIg;(tG>geRxxyO&4gFVD!=Fj^00D$I*~tL_7>rDbvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000001564205788233026912997989249361118820637431392383226006826858519914010829893081005536578660', 'computed_previous': '0.3899999990335861322387924335268122874678445596142059294554662087820565894948200682684776973583692395', 'covered_success': {'lower': '0.3902652197342516299371174845441050124146067166821932722778908754252395100678707866847240402814196366', 'upper': '0.3902652197342516299371174845441050124146067166821932722778908754252395100678707866847240402814196368'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.00004783284384757280349731445312499999999999999999999999999999999999999999999999999999999999999999999999', 'upper': '0.00004783284384757280349731445312500000000000000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002024112119535294685333204356883809053653728274944283137977920386123374187643964822984227855759572850', 'upper': '0.0002024112119535294685333204356883809053653728274944283137977920386123374187643964822984227855759572852'}, 'self_coincidence_F3': {'lower': '0.00001265746598557783445092899876403102812903617168089252630541324079152565077936816457343905206993208489', 'upper': '0.00001265746598557783445092899876403102812903617168089252630541324079152565077936816457343905206993208491'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000002318056044370139971490560531561392722096181711392209266970277786405455286382163778452890115881361410', 'upper': '0.000002318056044370139971490560531561392722096181711392209266970277786405455286382163778452890115881361412'}}, 'key_bits': 46, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 629, 'HF': 111, 'J': 71510, 'LRC': 45324847211160342250514623108218880, 'Tb': 1326450541133374800865240636180135936, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '3d734148eac4dcba4dc004892b76db8c913809b93971b99174b55a907b5c3abe', 'previous_grid_upper': '0.3899999990335861322387924335268122874678445596142059294554662087820565894948200682684776973583692397', 'round': 10, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 82048, 'union_lower': '0.3900000001564205788233026912997989249361118820637431392383226006826858519914010829893081005536578658'}
def certify():
 getcontext().prec=100;p=CERT['parameters'];n=D(2)**256;theta=D(p['DT'])/D(2)**(p['HF']+10);logq=(D(1)-theta).ln();tb=p['Tb'];covered=D(0);prev=D(1)
 for j in range(1,p['J']+1):
  cur=(D(p['W']*j)*logq).exp();ev=256*(tb-j*p['W'])
  if ev>1:covered+=(prev-cur)*(D(1)-(-D(ev)*(ev-1)/(2*n)).exp())
  prev=cur
 ev=256*tb;g6=(D(p['LRC'])*logq).exp()*(D(1)+p['LRC']*theta);co=D(1)-(-D(ev)**2/(2*n)-D(ev)**3/(3*n*n)).exp();infl=(-D(U)*(D(1)-D(ev)/n).ln()).exp();mean=D(ev)*theta;avail=U-256
 vals={'replay_cap_F6':2*g6*co*infl,'table_exhaustion_F2':(-mean+avail*(D(1)+(mean/avail).ln())).exp(),'self_coincidence_F3':D(U)/(theta*theta*n),'start_replay_collision':D(2)**-90,'endpoint_alias':D(U)**2*D(2)**-(KEY+1),'hit_cap_F5':D(2)**-1000,'numeric_rounding':D(2)**-60}
 assert hashlib.sha256(PLAN_TEXT.encode()).hexdigest()==CERT['plan_sha256']
 lo=D(CERT['covered_success']['lower']);hi=D(CERT['covered_success']['upper']);assert lo<=covered<=hi
 for name,value in vals.items():
  interval=CERT['failure_intervals'][name];assert D(interval['lower'])<=value<=D(interval['upper'])
 union=covered-sum(vals.values());assert union>=D(CERT['union_lower'])>=D('0.39')

STEP_TEXT=lzma.decompress(base64.b85decode(STEP_SOURCE)).decode()
PLAN_TEXT=__import__('re').search(r'^PLAN\s*=\s*"""(.*?)"""',STEP_TEXT,__import__('re').M|__import__('re').S).group(1).strip()+'\n'
def embedded_step(request):
 namespace={'__name__':'embedded_step'};exec(compile(STEP_TEXT,'embedded-step','exec'),namespace);sys.stdin=io.StringIO(json.dumps(request));namespace['main']()
def main():
 raw=sys.stdin.read();request=json.loads(raw);kind=request.get('experiment_id')
 if kind in ('exact-controller','success-certificate'):
  if kind=='success-certificate':certify()
  request['experiment_id']='exact-controller';sys.stdin=io.StringIO(json.dumps(request));controller_main()
 else:embedded_step(request)
if __name__=='__main__':main()
