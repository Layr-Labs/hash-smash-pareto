










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
R=18;S=14640;U=73200;SPW=5;KEY=50;LINK=1924;NREG=1936
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 560, 'HF': 111, 'J': 80301, 'LRC': 50896805424463524584793382047449088, 'Tb': 1326874505886269100760266988647874560, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 150, 'dp_loop': 406, 'one_dp': 408, 'ctz_0': 415, 'ctz_1': 420, 'ctz_2': 425, 'ctz_3': 430, 'ctz_4': 435, 'ctz_5': 440, 'ctz_6': 445, 'ctz_7': 450, 'record': 453, 'probe': 466, 'insert': 490, 'insert_done': 497, 'match_0': 500, 'match_1': 503, 'match_2': 506, 'match_3': 509, 'match_4': 512, 'restore_after_hit': 515, 'continue': 516, 'deadline': 519, 'restart': 520, 'restart_ok': 523, 'restart_nowrap': 531, 'setwalk': 533, 'setwalk_loop': 538, 'gather': 550, 'gather_loop': 553, 'restore_planes': 563, 'eval_f': 820, 'output_message': 850, 'match': 877, 'measure': 886, 'measured': 894, 'advance_p': 898, 'advance_q': 905, 'advance_q_loop': 907, 'lock': 914, 'lock_loop': 916, 'found': 929, 'replay_fail': 942, 'end': 943};EXPECTED='8e0ae6b85d3240287d9bd14a262628541cbcfc8e2313f3852b0b9a7c73b786d7';NI=943;NB=30176
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(18415722230335311330, 23441265891514909, 9254393875900494493, 9235809724234031232);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5183108481610962729408958845419521)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;L1oW*j)exZ3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+4t@_iHHeN8MmGr+MEc{s~F95n)$oi_2w@dYdNooRfQsG$z>8x6ee6*}>&2f7wfQh69oTB}8#IHx2W?~OUvyOJoo{JZ`kQ?$jN*9H}Z>p5ixOA4CkPYlc?s6l0&=4m)5nzm1rOy_DnB2as0JqB2s1D5nlTnb}oK&P5OGRdpBz&SpLey6<@gBVb?8=@<%$@llC#)h8>OJf|Xgz^O1wC~Gh5jgeJ_j>11k=?e;X6F)98zxFEf*eQOA6sjw19V^NezfuKRTa@%lte-s-lK|`HIaAbvXxrT-IuK0k<`!^^r+C4G^grzSYZhwEbq3?KNz6+#wvvy;J^MtN^Mm&Rt8;r^@(C2nxZL*`*8N5cuQvO}y~hn$MgvvG+3{%5bvIY?b2<im?_T6GT_tY(|w{UHf_^=M#O7cjWRiZr322P|wktNWJZHCfw|w1~j4rv+Q;0z@POSxp$}oMSnlS;f~%DZ42B((i_-lzjg-13xko%RBxceyVB`t;&U_?l#|b&Rq(T_jv-fD)HZI$?|S*AJ11jfmi8nYD|w;KR^9D9A;F_6m%-5N(W%c?!>G2->>SmBRF;Z2zPRb25_K8+?)zDi@2*~DQR3)U!}1axJfqg8|FD9mMMA2E;;8j}?4c92Y*1b__ZBn+YjPkd=3@MijKg`ADie@_Pb2C;bv%e#ZFP_1vI((%040}|)<fji{^1Bd^HN9IuT6Vj`%Dlh9gsi}2y~?D`j%3j`LPDZhRNPHvZdaz+ScY;?>n0Z+%b@}2*nDWRa*)|3QWoL^=Q*y%CiebcAoBVWgy&6GI43Y@}dt>gAu%vF5FBG;k^>g@P_Bb?)QA{{ALKUZ}OP+mrF62OxL(Y%1Kx>RI?rMUEiWM31)%{qT5F)K4bx}YR_ei2XEERcn|JBXbl-|RDteYXj|DxRb!8<!s_S}X9aMuWrgMVN54nJ*1XZ`K(Vz(-8X@#9G+bx9eQ5wlBN|;oderM=4_o&&zX2OP!v@v8TD3H9_i-rUI9HA0E`gWCd5<dLWk1zqu6*7k#CCDHyE~qi~*(NIchE$B_E<^oX}ByP;)#i#%8HYA4D<<*i7SgJK`-Jh5DH~eOA<wym{%iKqfy`?kt8{O<Ss;v@ND&r*D^0XpI`OM!O9ySh(eYA}Hp(<$wi8uRJ%HHtn=y`0%E;J9Y4>`;I;*>HL_Q&Yp7QSTc#JSJ1|zR3Ol<o!LE)=qKp3?n$3gVPhHOOjFE8w+Z!JUK$CSUmNFAwDx8Z|EUWQrb4Iyia|j9;*$H}rTM<uAUDbU8i@LzCZ1KbuvX>Xx7ATv!Q|UH<@1LUthp{Z3}Uf-l%oBS?WI312rNUL*PLH(p6Y&7pz_}s8K&H0J`SqKP8Wktly5@nwwjB~Q0kjmG11)$7q3MYfMu8MG~FT^VKFLgMZ7bhsP_*SHMTw#&3gxejYic{bLlL%R2%Z8{P){u<}G!RvC|vbH&@|q<t9a7!fbSNfAg5VEczyqFZwmIp#_ZyV(kdKM|1$7XttUON)h;Qkho6*2Kv=SQU(NsjbJ<5e;-5T2BIDc`b=qL1W1_hKT?`xF$mj4XNk)>-+mAZC80xs-JM0^*6OLMz#jn#!g<14Z{j=%An&by7je^;m^9rdS`Ly-MVh&EYbZd>Uwz9bM5&%sHN!59kLCER(-NI+&77a?Q6<9X-E9Zj0ZxFmnC$5};UJ7EX!ey)ad}%_cKmvq&%73sp}B>bg1*}&*oLZkel(USUUH62XsRZe@=FPY{kNr@C&)#B%9NFGZ1DDhcgVsNScC(sFnc8$YU^!tm@3#-lYLMk?n=^bU!~`5JhW@f1?0v)W7`&A?tJsFIAMGkq|wK0(CXB7s7NHaYMevSvK>Go_6zw7TcWv`MJSwe6$P1gy5Gbn{{ucM4!<PjP&Ey5*f<|wA%|L(m>#`t@d31|viW`Ez6i7TSs%h3wwf^t>qS%paKgPjyAnyV;~HbpCX;UFe%C|<5L#YPoH1QMry!%%37A8vGKo;ZxU!OqXIW$94IW(&6$Y*aC=3aHdy~HqB(;5}YRv2QXw>t?gePOH(<Ug{c3u~I*}N@k*oL|pa*g%$McGjrh22h8jU4ieQs7tSR-<I0Ba&-zXLZ)V;YoQD)(H-6zUbAzFuTz&rke|ii|0$LP_tA92M#(pI)mQ(Q#X(7KP~vtf*3oAc^yEy=!GUZ0AVlN7bae45tQ-M?~O?>mu@=;53VTBDkkezSYwaWVEWPTD|8T}dKADb(9*>EGG$v!n+=CJ%LHn(cJ$Q<?-A(H;9YeSkP~fGa3)!dk8J(?e>i9^f=fmPis@p64wqNQQKjGH1n5$M?5AWly6;KYYjPVZ0SB#laa&EZ4I5iib8s#bfvB*aVD|9n<_EVEbymNU;RKgyG+wV=(4#Kl@?=CHIVIt3loiu5+{!``EP&Y7-6e*&@qi(;H2rb-bJW50f(QlfbrhZPB(j$4pyVXRNM72qf(}fm=tG7xw3JSlpaBn>MGecH#6j;#QE(2#OK!>+&$ab+18n3qJ@%J2mD-??HEspB{Ta)Hj9%9h4pX&$=#=<_OV-p0=6Y3tip!&{xg{Mu6N!FnC*Bof`FZv=b_{CvY+%SyrAd_s$k{cSRs10#GXvkpo_uR?PmH=72<??~%$PLw9jxiT+Fv5e)+X&G6zmEAxf~=X8g)!4uc%eJ1Cvw%gF^lHBK#P2>M;?9B%6uHR7aksU-Sjovm*e;gI3;7*;wj|ZcqC5Ksk-8j{zy@0+v)(d1#X|vXqrYO2_pYowp9d{owjfA+Q7BaE6Ce0J~vjaLJQlR@SPLwM?N!0kwT9z*6C34#bVaWe?+{jB}_}d&bxfaq}sQ>+aAVADKu|TFWY+csTaB*?w9#OwpXJgpqc9dJf_pH^Urzj5R=1KP2qEYDX1RtP6fwII}r@Oy<|evZpDfzuSfUn0^wHQxTNh5axMi9XmJ=7_r&j&96wy3%^?zZcT8AUuOr^{g~6^4@KB!Bwk1#79>zPvWGxRZ`}Eat)yhbGfP3$^RA5>2yTPBp|(5+ntB7(sn@QQGNv(fI0$U&pD%b0S{Z0XU8~pWeOND6k6~`gb`_n(5Fovgf4}%rd2cIru^fipsftdOL`S*0q7Kg&VSjJ}i|z3q-X3E5-lb%g!X0P-@Al-RC%24$Y~I2oPmmy1sWs2Ll_CYVCw56Hu3(6#hgQK1Y2<x6;{v1hE;tQk!U$4D&$OwzLMntFWT~R4T*irdBaVi6#kyLe%~8R&fUCxn_^N@E^etyz=s&76(9-J9BYWlGC62#me#Z`5^b)o6vDDJvaX3hF`{AEW!w&5zjB+o}-qMXLCgy{-xBrZ~3}!C6FQmPXOLsyzntc9NOeuC{Mnox^W}z_AsU#GThhK{+*`SPZqi#6LLwFpzGk8=ZAeCJ#V+DRt-*oJPNtquvyrob)b3m5vCOoz!dQRkSu0A<;i59!tJqZ{cfSgPW+2n!uJDoIm&Fdl`S+DM7(Y9U1ENYpovciJUO$XC@4=p;C2sBdqJK_%6y_|?^PmuJ+(T)T3e;aCEBe)73#`>h#g~qBn?yaNVe4q#6Tr@ON8;D+0OaY41E>Q}n>cOePZ@Ld3t8ha<Mx|THLk`Z<aWWH9%p{)_0_Kk{GfzIauAOuwTQNpLrD~{k7YJzdabMgp=TT8nM<2tQXji+c*gGt$b~%V07}i=HeX~R#`f-obxntI-n&D2A0%sm`+;;>Fg6t0%0=XQ{<ya6o*JY{Hz`8bK2*gsWl~~f8APxwA_i4{jN5RkrL0Qqsyllhy$b8o<d8%CEO7GxnKhqQ~3pH%m(VTY^`k0>X1^F5z{8*F&pC>Lx`fR@O+X|nR^$@@!nYtnD^1q+kRbhg&(DE^*0Wv-=BkQXI&$m5!yRtR^T5H(a4BauukT!@_^r#Kb#vsRi^<bfnb9axy`$I`Ou%amzfR1v8{oeN9KNTPbkX1qT5UIU)Bf5#zG6>_sOm&OF5vzG1p>S5^k0F>G7YM8S*$Iy9LNYFFWq5JBbHC~NVn1~8_5DsXU{-<5Ed56-M@pa`pDpF%OM^kZ1TvS5w|i}>b*Z1U;W%Ny)(}NRSFC*#)N%l+FIytpCs95}K_e*Pk%YL9+eRSY>a1$xUo5elgp-*KWCxYa&fsrP&3fJ#m-_}VRF+cYUtR161WiK&*JX@3x5{@E+M7VQheHQE`8saimhZLU_DIfl<pu8$q{H#c;B$_v@`l#DO+_{`&pl4l4_n2YUC)f#l;l7r!1%O>HTnN&+nG%+tP@U+h(i|Cv}aHQ!qn#P1;z$#vA6L}T<&>d7^UeULgL$ji}7o^$xK>05iY|99ZbCM1;Gf@4jBl{r!QM<QR2I^G0OGo-pJl;TCzKe-&F-QA!r->hXA};{Z`X8A!-yN--N<qpgi^6rsMh-fP@e$*TZ3*gP#EI_#GX?Ml;awf@X#6>PDZU?owaS#}VRN{Pc4O5$e*+9SUsuVu@knZZSi8&7g4~iLZy4thsNulH+sy7e_4EYz~@PGOM|#M&-yt6opd^-4&58DcqXzB;eOV(ApGqap`7R?CDOFTYpp8Wv>J}4?O5G*{n<UHO7)?gv!ZRwyHlthCg8u&S*?K%oT1n@|@o?v*si__dlowrR)$oN_Vm{=azg;n45M`oA(%VHiqLT!@cxwOA)oOMMx|QRtMi_VDmv9Au|<wa#UgATMFI(RU!Lj1~1|Ln|zf0C1mbPn`nG4=S?Q0Er1RBmaxueaSaWY{b#+(=Y#WM+;(g$h0U8?oP@7QDrJ^nptb`V*!@eAgm#EP*U`)Gx{~Ij6YQrBkE#0pX+{uvnq>CSMS9Sq!+LR8x0=^5cC_jb`dq+<Kysh7mlwa@3~jMN5t{3IoIK8I5J(UYF&-`G6J#F~sr~~jy-L(sh?zBfi)paewwB9jP-UPk)Cmmb>f=?=(A1Tf$vDFVht@}(M&b7r+0uMBS#jD7rObE8={D;@g9h%=W!t1d=7RKbm)s&Tt@V*Y0qTa-%XpLhQ1tDG1yj3V#02+AkO=Xwi(;|2jV&6Xvmlr4WtICG<JxmOCD_jtc^o4!ut2EC=Y?(%=Ce9e-c5|?hi+hdSwhynS)XZGza?upqSMd0F$YyueX2Px22U$)N$DY_LKt@|AUhGqWyWz@RPWzYp~s53#JWviYj2G3rtuusGwshrEu55AKdz`+OW<D#W6c74nYbH@6klC$U&TDWjhgGJ(k;=aWEnD90U{xCU=UW>D#E2xV|(LoIF?^s^_+yJL<!HSndmZ3yKhR~%>#^_kgCNvHM1Ha>r1Q9Gq`X7*%_;yh&)ro-pj<j;yAcb$W!6MJGyCZOy07QDb~=`_m!-)!iBlquoRuNR7M-1F|{T(^e38CBCj#LIm=_&c3qq~etnzw_`_~*__4m@Z0q-~Oni);fX3v9up{<f9K}+^x>!o~J~k$qa|(qM{aSgKb$4-9IoOu`c-I~nyA1IN#7NO`Q%SmI00%y1#d~GE3|~;-(&?;}O&hNx&fOhk9XWqXUB>LX_65N^T_P&riNeScW2aU$$<*K<8Ze*|upfDYGkLF|-g7H0!>;lBSVJ3t8wh5WM7Ih<%fyX{KZ97HRi|TAc*-+<+N;P&EN=E>$xAA}zjV^{(R~^rISK_3vGf(MKXScW)5(0w$SW|SE7Y0;qwCYiF!Z|gtzJ@xlSF3|c5)5OD}2I%ijzl@-*#m()sB&T>@8l4iu2ZdHV`)n3n6ig0tjfVV8HAxh#!oIMH!_L*NV2qS#~wC@fCCScs#S2gl<7re^Ng#t(OuqCNIVk<q+V{Cv~~qfUc?_=PJj=V@1295kW$gJ8zd-$fXL+i%Y)4bhG|og%m3!pJIP22bEogz=Y*Cq}Jf<@rcb^7qd;WK9NQ~4nc%y#uN!a2t=umj7(SNrH>kusUAb8%X+yuDh~v_ZUG46*Fu5Rhj{1x)~E(6CYc-^r_f%n&g>vaYyof0x8Dhw(FAH)*>hIE1mtJArsWhgw4i2#lJ7zrTD^t^i2NUESJ~XMTGToM(efzY-M%58MsR_J)T!VLVrlNb{h@A}M{H|F(up@Y#n$q)qW)_8+jtJvFucc7x&ZKLB3F&r4FE;5sJ-34@7L<~fu{&A`CJQ)d=?Z-fwq|B|C{)BYSR-)>qX~^!|{|WVdFGgP`WEft&B`@D;`$%EeWccH5?LNsX8FyYLQTr><lQWq|FSPb2bPU{i&g$=^AntmL1#>MLe{>+gCsSV41)m+haDB;+!(Hnx9D^b-`p%@DESvMUm_9I?&hv<op1$C6L1PP~t1)Raz#4oUDN>C6_qTQf3PQB2fv|;5Uc>py2LtEL9C08BB`Vra&N{nor6CxniC;Z%%6~R}BBf3{2t&P?Gdov}u2=0}=WRjxac#NMT^KP<K}PywrWlPfD>&m<nAI4u($Nc8hzlZmcw9G<vt&q`W1zd}ACng2FZYa-w0mFe_J%j9oq=+)^FJw+c#Q56mrPMLW&1pArfp2P_G(p$s@{IxP1mt#a#D)kcNLdgz+|u%Q$l*{Vgc(rUYDTc@D~K!SEPufSC_%S#vB1Hbw1=_nF&95&}~;l2um68za|`G1XI5p2^T)HmC@WG3u+%52A>Ntnbq-{fxI?SD+lbO0a8HH-t_KB--rmqf*1^R0(kkEF+~HFAPk9?XC`6(qVh6heE0S)?T{+5;Iy^hS`yI#i}2*zP|7hE=ct5t(Gum3@bS71Xe=&v&rWLo6>6;>h*jHqJt;VGq4ww>_X7%#CzjD{~icmm>Pz3H%Lt%ok0?aZMzc&+%X?B5{32cfuURdl8DtnSmwQZCqgX)TahmA!#%`-9EW7c-8QEqf5f@o%OO!*tmi$7FPP@-_L0L;vW{3#Nca}oOPrlYQqDku3H!VqK0ivCEAwkHxLWt(~n7qe*@eYDe@eTl^=>8F_H$8<7qiI+kS}-rzc;u-+iCOO~~F@J4!hWqcqCJ?|Mf-j|to{S5vV0w~A;7VNYeSeKDBNdJ?}4W>KD~10?-=N7eYKi+i1hL$&$)-%PW8?Mo<$OC>?3A%uD@XZyL)62}4Ut9G;)-y%zc=h7pH${kfy8(h5;udHLyJO1KBv+-dKr?Xh1!4Is=My4X(R#jMcY8I^m`ktO?uiiND4yc#n0PJ!?C{C3$+(ezdOV24%Qm=VroXq%+cF!Vq`|nx4+IUj52Rg8EU=rX?j2l)^!)HT8g2ZSHC8RjU05Z*fx*JtOl0#i%EQQIUTnIiPkgw0^nub(gwbA|U4z<GO`H*pM%jR-&)UU6RpeG*k!KQ|>3Gj!dP}<KVXA$DS3X6e@I<P6bs21Kw6yZJbI3{sp699xA7FJR$0N#kHHTbq|IUTPxcdIDFr3HI;PI`uYweg;y6!zUw(1OgtxDC~;(%vdj^*dj(@-$U`&eCchVUKGlyg&i&qT@dyOLaqas|tGQ@A0ie1L$tB*1p8m;Nvo5sr;C=!}^d$l`J~}!t)a7_Jty2pHYb#Z??79=mHEHA2$fuIv>k*FGZh)*GbF1Jstl_RSN?VTDrG`FG`P~-ZS%kQ9;6nUbrfrpK|x<LWv_|kDjGY-iE9S8l!#1KZd?4p&0T?B1mKUzD3a5_#m(^kYfZ$a4dUus75y(RuZW`7RLqS+hJAy+?9I|LasdXKV}FSXeO?^ePG75P7rXd>1q4pHF~_c*NiPqKy9R?xa<`9m+I+W*~$ZECbl;<Lmh8l6qigSF-VI``T;0@C=8dj!oHiWLh4g1hSmrh?KRPq+rd*TZ58-S5OtTa{H9BX=~m2&ec;@VDn`D56jn?Aa8uede`Y;Oh%-+M-K6Di?FxywV$I$DN&xgR#Rt`L8-gn^oJnD&vpt)sA{dDE|MoAj-q!`!xvnq<q6{iLg@akVJatdi8Hv*cDDnm>Y+K&<d4<5@=&yfDn~)=D!^c3~mXNhYG<0?|dB|@ybdX9PqnQ|!&}s0XR`3P2k$vXW#(v=YlyNwG_1oq*tJx*pzr4@gO+l<)xKWvxyYqN)luU2M9Fl6w_E*plP|3I?h1hmLlU9gCE7Pma!~@A}O=Ax;Kqak}gp87IAC6`7b?zlKH^;?HJaO~N(OOUbEGT=o@pbMNy_5)!9V7C~IZXH1O*GM_JijnCh`heQfk&q3UlIEbAKes3%+MRQ#d7A48qH$R8vU8k`r%@J3{Qs6BSIm8(f6g{nwN|SHv|T4f9*}B>J(LE(^Kb@7L9w<O0jH9LUo`}F1S9X>5jf2h1}PFPGJ1^Yr0pcwencssn`uU^^LHbr*o<3{;HY<md~B5BAI8L9AI`z?3*qhZ52%WlJ%A|j59Z5o6d7!i|Mq<f&Fv#3df!0IzIR+{yA1v=e#HE5N87J>w?pHE&X<vMI|LRb^zA7?!f940%41J2*H9Jn|d{#33*=Xapb?5>FVrctn`Sju4lUQHAG@*Wr;q%_d8xO>pZvs`j6q5l2Z)VhGNQ8>ZFqO%-oKQ`47XMBqWJ!Dy8TsyW>vl9XMdRU|YPI^gEu%iP)&OzDA=)gI{jrBC{m6t{Mvc4Ll!SANpugUD(R!&4qJNH?$HW^l{I{@KMUgF2j>vJ9yGGW1b-ydyluiT#;10uu{$$47CYZaOw?Z25n3ux3m2wsTt8q5fIBj<0Sl^x=sJJ#KqL2=+n1^D-Ad$+|R4*lfu-UycfekLy>8z_O{d@FJXMRxtijlPQj6r60XY&pMQ`q>o55YzgOwMN0bgEoh<3|4*c4GU)U7-+IsUQ8H==_M(61ZGzQ9(XpDpj;;{&=wWBbtQ3~^XZ+_)_HhSI$SC)}w%|y7K{8#qv;pu37z18gkE-Alci%t_^3TN<LF2q;e)UvVLj|h#D_XHOORqbKKU&y0CTbvRFx<F|f%l4q$1`tEX$l6nDUY#oVLtPF!HrH5~%s-yr%hnHUS#QIQVl{gYe|nwLq-v|N)s=^lIc#e^zrw|}TU)U-L(uoY#Zf3ws;D@aioN2f9729=z+^4FnX&TFNLwVCiHO&tfl{hljcq_Byjv0HLX0?6a+8YIZ$!1Tn5>bJY32IbQR4Jf<Mfod!()aRrcS8qlX}%&dfCm0K9?|{^H9jStt#a|kre=W^L2VA><c$Jmp88Nt_xN!L+6tgi6;$n7A4!A89NT;tr<siFztTjjsws-A6jP{!sRm%2^$WbY#+<toKP$|pFvW~&&NFEF~FzSZW2d1sj~ihIow2RR*o#t?>;|WwaoKQc&#l-B&r}$wF}~aLu^jn<2$P2{SF`B9@8v>n$v{2arh^W9g38A;PsdLO<U6&*EqDE7q(X)T_lSeymL;7ftZmymu&|^YdSp8>Li;npEg298htSGVwsq`_d#qHiHVd1wuneQ?LYtlC{|UA&`ZA76*4Bk6C(Goaq!9{<$;q1dk~+kA%D}^CSd~A@n(#K7KJpMt^XgwR{9f{ySn>jIXn^V#U7k#u?KvGpeUHhOdZInuaWuGQBN{nLEV<XX_vK7xk8l}H1E5@{x7UMKQ(_;$YqOxmX@l2_Z3F0TCgy+!%^R4p6$O>tY#x2ZPb^>wo3|>PIB#BFE8u~4ASlT)&3zH$r_yG;I9+d)=O4sc_SP%kj;#~z=Zo+qL&YA?>X-xZgng5I_xXl^=``Fa+R^|TlB7n-lqfPlYki(f8*!iu~DHEOi{81`GSh20TMD~z_z1U>d429{Sk0A+SE!d3ftp3oJvmy&hVaPZl=}+7HMSlO_^_Vk-?1v3EKbqx&JDeo$q1v8Da)#xXqDQAvr=roqzt!Qb{MZ*<c^)kCn|FZ6g_Q7E#8-(VY0oluOJ~tPz#D>h0c6Ozp;L*FpEah31<-g9nOWlA*N470dXh<BPSJ^J)#Et<AEUb8Y0#(9Q$pr}9Q{UIt`kD758JEWhLIFPA@eXvZAw_Kr{a*nR0RpipD1i~5ZEFYvbN355KlY5})-TBcJ<^)dM$kaX>~!LXsBUNsSWQ<?W@I27_nS3?^u<)*f#)-(?+$P)G#vO|@}93c{sWH8>J#i~i)U1Z_TUQ^AaL2bknn+{7#|Cf{?2BnIl)FW4_G{Y%h{O#uK3gJK|Q14(PB?Ho!DS%;lb0b~@E|0}dhAJH-QvDKt*oq8MWL+)`PN+(+?f@rCZwlqxwi>`RjT>khS((H#4&7UWpX>n1ZjO28ugL~j`bhV3TGD#~1Pg9pf78quyUFG~z{1tz45lpe69GU@jOtKlDIZbx3~leu-k1BkSZ}frBE+<X=JBlD-K|*L{X@!C0oE3F=(=-XE6RF4;bSTiw~EF@XVL<OJ1|C{VoV>&T9w+L-;u((?{VleQ0JCesVCQ-onbT+S`&U%P;9hHNv>|xLzcv#YMhu>Zv<#@oB6gE{bKoR>!+d(A^-i*u4P6Yju=yWs;UEcAxAiMIZc%zA%f?C*6xl4;<j4dGC^%)5E|eJO&B5)>^s1HW?4%8#_IOdF4+pOj!Yj&;y*@p#B<E`ho+ON?JXKVL}6jsUG>H9CG2I&phv35<E+F8`@Ei05c^`Q8}D`W@k|z|=@x2dM73}Yj<jzQK>*pvxmPNF`9yMEDO6gWY)Pcc;T&Q@ezh&)9({Q`1g^5ch<;g#@(D$@M~>YWl*+yIfOgDn-WNC|{dz{Si1kLH)`9AAveWN_96ILf{985FW+W2|8BUiJRV1N|v%8zLjO&0jH)}DdC<gQ+O!^0LJ_^Ui8zXmL9o4mM;^zY&KGmrL1TRSzXvh!lM6OZnr;PPCW3)*E5cJtpC~uNERp7(Z`&o{dxw4Cl-}D3e>Wy-yEsx<vRw2*$F<7&MKdB$wSfQB$S2T6F#ZnN_1*_C)2HPc&A~L#U_owQ~Mw!0XCNJV8&fIWk6{pN7{a;vmsL$Z;!7_WZOWT#kIkirNsAqFFVg9H?yDmo?L?NWl<|qnpd!y*1gpQ^^#NT3D_~4pQSMjOlwOZS_=%9`^)eBA4cTMN&ku>@eMR^5Z#7gq2Si8eMeVxc-g9}iSLYzl>r!nHF!SZ;((23HQtuG_qUcL}I1EUSlov&^*zc3*G;8g}_XOh}xAQHWGiZE(9p7Y4B=O><HPZmpcd>1WFrO8kQ?=bCE0fqK9%_5qM6-_BX#RC4y#l0^>t+lp)%JDmb?9N`4r88-hA}C#tzy5uCopRZ*yxzSR1z+wh;oln^tRH5S!10j191zJm-JdaAm%kLt?*{GIp$X``x5^;#!V4k*q+r(9Sgl@c9g(5Jc9aC=Z1L2N-CX}&^+4@*yB!%@o^*>;1Nuyq3sz5|>USm;t|hU%5ApTwREI$_&(TsU<L<bw!%8$$laAx%%ny0K2;y#ulI0oNSCVC!%xRr${QF1}i@(d=k#r}kd_{>m1mi)OJ~Oa#0G|XOjbi3rlGncaPlo$*vyi~7C}Mw}>DAiI5a|K(l;CQr9=h}SE7uK~-QyzD5DnKW45R>zgI3M2UX$40{lOsF%{1m4^HX#Hg#FYR=Tyx&b4me2tJHivw3UIo$x#w{IK_XKL9d8Sjbaq%iLSf+8AZej_ui@yPaOU*@K^QDZUID3cqz;-aWmUO$cNYfnIoE;Cw(yKi8n+~r1QU`{35;B+n|dd4dBLv+1e7sT_*yUe_od|21pl_hGDi1>q^#mc<i@@UMw5Ia=5+^rfGh86cpsbkP88FIu<DqvkP4HFFnVTJB-bHPi7I9!^JV{M2<`$xF(J=S=e?Uq^+MrGjvyX6#O|_;x=ZLUG?xe=&QsIH`k`hK#g-dTs1vJVtoeemU`rgVv@=zEhUZ<<^OD5$l~2l3R@_Vx8oZD2zQqj=P8x>eJ}snaCtECZAI(8o{3wB8a*66YulNDB0^bDZ%yo-lS$_N9am2B_ZxY0Yd~^uvM>2!+la35=hzD$d<Zydl8hCkjiNokRcGIz+rXNufw%Cj5ICMw1g>Cm;W;w_^wR-G<IV5P<I7VteVF~nnTLOjqcpg*yDzA|2ld(lJg4m$F6J`F?M>g!)X@*ohJ0}INRf5w_7Fnb#yc&19Ro@jG$(`f^b|52@rU;fcWp10#O9Rz(73Vqrp7Zoxzo7P<$omnqc)UNE7V(I%F#7ydHFb^tufBix<ENr%XV|wO=y*`1B(7iSiUteuO<U6gA&z8Z53qHKJdl#ZkS!Tp%Wk8^yFR`_f?|nagk3GBmb1f3eBnRqt!7NkpBe%+DX`C0B9fjzwz$5*+|?w2+UBBi>Y?h#v=;C`VO#}3L2ik0lPxN8NjXj)7=$X+{RguUII=@6N(2uX7y0h@*JoVJs$TFSgAnJ*z(J~N`k65M)g5r)N<HZU2M0Aytbp)P#~K*F<o9sK;zFxQ99u44-Z(XF%c$bSHMiGdF_-xH}>S}Gq(;gGrG)3gPMalYy?&Zs6k|xM#g4xe<`=s&Za2+5tB8`3IdjM#w9;@B#2k4^zcUp2>&3~NL_=!&p`HHD@rtbyl<8)gtFcVdy-3ofagDUWMTfT03?tO_hy`H0fV{B!F})M^rtkim)1is3CaI%=SWrdpnEZ$YVS*)_l#Ne>*)C+&sPN>n<iFsP%0Y2CJ{CS*i&lAwS#?UZN2}&mCECT%=*$s^ZMNc+1skmeBmFGzjcA?PmZeQP=(#jdFp1(=5fD`AUd*aVPC$8=%JdJw)LKYzJPEUvM6@ybod|jRD9%^wrL+xg}sU{>Yoco6b5z+L|aW;(WJ|`ELL;5m5@G?9wEwuy^7ET34LREyE;-dwmsxhSVRijDT`&^QUemZmDVYs2f7g;2!0*so_Y!KYn|Lzoqw79#BWqr+iPS5lM?j~+vFCerT^}M5=V9(5{qvagMet;_d*{}HPtyl%xxL4kCR^O09*svU;>0zmMtz3=e>hBh)|diKT@+x?iX?Xw(`j>LpKqWev!5}tEZ!yo6Z7?#>bZUUGH1V!|vwVo#l!QJ;5iS-_&ybNi7%XZhU6BwUPMGR$8tGV5F&O@hf&1o7cceOJ7tdUxWKEj%HNYCn}Zg_uL?^O&Ls|P3vaM6X;v5r6*{QS*Voqb=7@|mS4I-6%PyaKYut#0c$7*{4p$nw&LI7=UerFan6E`+f{iJT7CvrJ~)E5eQbD7@+~Hdk5)A7X%tl+E)=X;ZzZ<DuWa2+zw1a+`RpTjtCNhN+uD~2&d3~ddUr`CPIPl87c-3{x|w2-s@rwjw&3HSs>oJqo-lpBsMjF7_Q)bcFCTB0V`gKI9X5zwuc<mL-sS0h^df;U3_sH2K(o5$4v!uQ(teQpfZ8@x$gbY2Z>*}T%$L6u|Evp&ezE*R`v8;Nv~d3Ky1zYjf=Pp$Y+M-VaI5{b9jgt_P;9XPoSPd<vNnOeaZ~Y@{eO0PG#Z{8`o^9MEVRTV7U1hLdQ#n5h)!bTp-)N#MAfPrGxgS7<6pg0X!iOm$3Vh*7o+H#D*be#x;e=Wcs0E%mko?3ufSEg<P!ozW~Ex}r|`li)?Jl92NmTR!}Dk$AI1@DqvhJgg2TXkOhI1`estP`*Ip(Z(?6k*N3sR4gD*yD35(HCT3l&S2D9bkhHuC4E>?h6E3P9Aq(MF?DYqV@A#ybJ1w7o}!N|##HSiEt6k`!?FJhp#+QhDr=5hk3_!67V)gh;)XlADcA0&e^0r>YDNVS`-P9*TaSCoB4-N(M88KFi&0Xx&)f5{RPE<;OZgy9+E_u<fl@@ok!jn6$1K<YZl16+!`Dg2rXAVEV9=Je=mnH=Ej#2qYwV(ppbd?d7V6YTJ+4YurHr&Ghb)*U?L+W4&^L)PYPApI;F>rEr7b2`fVG~iz&z4PhesO8j-Sw_2q1x{atN!hjdfQC^kt32=Y!xXF{Z>b%OMN}#JBk+A6rDgt(rbG&s?g`~P$Z_Yps^HJRX5svG&{(aK3Id%5ac<$Fr*_1V$%OY%tk{uzEdgn4+c3YqmrVez=iUMUe^v>tLz|Y&(<s_g0;VxKY$&ol9`b8Afdvr)+5cqCJ<!S)u*khJ{dn`sB*iu65~MdEwP%F?@nCUT{WLhME94UY-yqNMw#<*|GkfiQ{qd&sS+As%8{zHsoUb7t;U0`Y!A4m2w_f!e_#~C1>gTzFCaE<NviY0yoQEB0N;;`5=%j>2f>@*|K!Q&><%~ru4X>yerMtv0hkjhtj78Mmv_eR6<9Md8uQvIe3c+)<0T(crRsGtQT-`kV7wktS*+}x+p#5@lOA?+arTm!`eTc~TRhvnLvF|Q&FhEh5Joa{S&v66XjEp<cY&IOBE1g;+=vqG#$qm6HC<6;euf*WDM<UrM1x4WL)G*tk%@bV?38eJdw1sXV&){<|r8XbiJFCOsilQA2i8e=B*cG?N>v`5%bvzUx4oM19yg@#SjQYxhiCFJh!f901d(mEWzX(3s((_YT0*_|vy357HfnUI$?d)T2SJ1EYB$Rr?J;tEgX&`U^Qa85_4?siiAb`*-%DWkmv9PaegU+lP<%gZj0t5{sixh1|QjBX+W``wlSd?<#wA)KgQx|D-9~oKCh)?UHF8YOd8q~WGnm`v18=_0DI0glb;{B$)#MS-(VCzryj~0~R(Mh&ZPuib4M0CeiCB78_0fCat7d-~!tI0a#PKGYkm{t9=p|D&J8CqG*8<{EWnnOexvZu%Y-F>j;hO6d_{;VD@kwGXP1M``B=jMK3C;QYM1|4S0L0vLiu~ZtMT4b^g{0C2N+m`XOgeTN9Mr?i?7@f>tz1r`~*pgBZ)lXgK2l*%KPaAIT(sDVQZpo^#u`s6q0UON&yGL=T00Hz_$&>>C3&1C$vBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000004226015760976887013627824479990829080379709968572539334108567504700455144868061578373834618', 'computed_previous': '0.3899999992973142120659795223710886725631001281287604378217955888491344750160738434103955184631658954', 'covered_success': {'lower': '0.3902211014706578304467084915835217492365575420491186907217594216845444570596026026587985933601132972', 'upper': '0.3902211014706578304467084915835217492365575420491186907217594216845444570596026026587985933601132974'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000002379536567786999512463808059692382812499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000002379536567786999512463808059692382812500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002030076182625783014693555938381085300838403301691854417470440608522757917432499643728689573413057599', 'upper': '0.0002030076182625783014693555938381085300838403301691854417470440608522757917432499643728689573413057601'}, 'self_coincidence_F3': {'lower': '0.00001424672652264030612244897959183673469387755102040816326530612244897959183673469387755102040816326530', 'upper': '0.00001424672652264030612244897959183673469387755102040816326530612244897959183673469387755102040816326532'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000001467166703247874553783043052549437606086692394680269295038905023061654337546628976390544980366428842', 'upper': '0.000001467166703247874553783043052549437606086692394680269295038905023061654337546628976390544980366428844'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 560, 'HF': 111, 'J': 80301, 'LRC': 50896805424463524584793382047449088, 'Tb': 1326874505886269100760266988647874560, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '346c210dc2aa38174abb7c3802cb14b21286b8220eab082d557ac5f174fa92f8', 'previous_grid_upper': '0.3899999992973142120659795223710886725631001281287604378217955888491344750160738434103955184631658956', 'round': 18, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 73200, 'union_lower': '0.3900000004226015760976887013627824479990829080379709968572539334108567504700455144868061578373834616'}
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
