










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
R=23;S=18296;U=91480;SPW=5;KEY=50;LINK=3584;NREG=3596
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 703, 'HF': 111, 'J': 63999, 'LRC': 40564185382003226733193754220429312, 'Tb': 1325914782967292795419109243400224768, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 168, 'dp_loop': 424, 'one_dp': 426, 'ctz_0': 433, 'ctz_1': 438, 'ctz_2': 443, 'ctz_3': 448, 'ctz_4': 453, 'ctz_5': 458, 'ctz_6': 463, 'ctz_7': 468, 'record': 471, 'probe': 484, 'insert': 508, 'insert_done': 515, 'match_0': 518, 'match_1': 521, 'match_2': 524, 'match_3': 527, 'match_4': 530, 'restore_after_hit': 533, 'continue': 534, 'deadline': 537, 'restart': 538, 'restart_ok': 541, 'restart_nowrap': 549, 'setwalk': 551, 'setwalk_loop': 556, 'gather': 568, 'gather_loop': 571, 'restore_planes': 581, 'eval_f': 838, 'output_message': 868, 'match': 895, 'measure': 904, 'measured': 912, 'advance_p': 916, 'advance_q': 923, 'advance_q_loop': 925, 'lock': 932, 'lock_loop': 934, 'found': 947, 'replay_fail': 960, 'end': 961};EXPECTED='2e3ab1dfbd729907b36db892aa605186e1b6268d693f2fc5ecead1a17b44d2de';NI=961;NB=30752
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(18281444912654326458, 9403882246296077292, 20902500145947972, 165228708557841408);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5179359560383465057396081511366657)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;Kv#(6<q)YZAm86ne7%kd*Ba<guF=!PzC0_E3&fBjOcm0L5T5uC_NV!R2=#GqLl$b*3z_a<{@J}<UiO9?*(4$H`wE&qeQoI!2TX{U*#wh3ro(9$)*5Gm^YBsAK&zmX~cTI_=F);u7l?`H;Q|og|`Zfd}R6(p`1W*(JdqLqIQcT+vN<Jq=Q?Qx(54eaDulJJs%}H8Iwdy=-N2eLoU-AGL2yHZ%6(r^7f5N9hiszPTxfNLO@k_NmdeK-wlk9wAr8{LSH?oirAN~#)^g~p5S@MS^OnfeVXVaj|=l5oNvoQs3tFxFAxSrz*tQ?i+pNug$?|}MSts{K~T8TG%)nv=q;*{z#;s}iy#D2o@>2-gxUef6uA?84{9uh`J&<i!<b!Yu@G7!F`l@TqLachU;JCIQb8)ML5whg<2!9;{p*=QjK{;<_>)h=K_Tl!H~v%KQdou1Up{|(ur00_;snL`aM=MIM@*O|AX-K@HNbj36lFu10_z5|_zM^C7TKUStK>&@dxkhMc7m;AI8R-awfvw%u%5I;e)&8%w<a^a<cXu3@~$<XN?im+w<0!b%C(j%Nu^ln#Qfshz*7*!*}o&XYfon%2#+053&fa#M^OylK75m5x{I(5AY1<xqSOpp21}SRRlX|giCWYg<O)lrcn_P48B<7YC)He{<Pt4zcbLdKNxdgI^kIE4&4u1C^z^^lFSrSWmA0*4&fs`_)eL4S7^q?v)$$KQPe@<D_<(DKcA_;xa3rA<Ce5M_B2C_Ho~cyW-Pq3bi?DaidsXmai2i!OG5|4L4k9;N1)afY@b2)fEBBfDq84uoVu7G+W`2@8B;P=BFu(_2MZ*D^IY=+76b{xv<AEHm2CuEs_qx&_W+I_&jGBBmgO}nu07A-;A6qQNsjf1^WO{DCsY)(|nfFy}nS92T@<@}C_Y~?PxjuptP(3KTSs<~_Ecz2aKPwd~=qRmWh_->_cXQYSLYpZjRq~xZUGYWhb7UBFqWiPSY^EMeKG|4hWa5m1(xU;^VZerKpHNTJ^VwBq90d%@(nk|DR)#Gpi0Q|sevv&<J?2IpwvImrc2m%$3LhUZ_!D6pYFI&Uq{6ewG;LE9wC5i)oQ!b+^LD>KSpWbxOS(u+<B)A8TyQ)3`E%=4Hv|$JqA|wwBve(dwt6+#lg&t9Y$by=4rt6boM{7Y&6{QcV8Nr&7`O!j3u}_|g~f~azb~A(GnQ@2rrfDs<9k84VK`Wn-C5mA*q4KVIV{RWJ+xHBr(wcs7by8p$qVCU794~wosrJ4DG;i(!85I?A;+2bu)Go8{>G0l*-Y<5?mvR5&Win3q^d;n<$wOnj6{VOlzXYPCa65Q>-+<p()>CD`ZLouF5SN<NwP_|#?FikG(fjz5YcW?IRv#=9_8&gDhBAP_<{Fb?rEA$dDIH?VP(2MkmyHnQy-DU<pD@EBSt?L-(|kzurU<{zwSZuNcqfQ{V8Zg$7yhmJGcT|cKX_LAIe=h2jyebV6DAzPr`u@d(zW!&+A4%r$5g3L1}MkmLWgG%mwH5HFhy3=vookU;`O=0eyxdx(o^;m^Hoy6Uz4>mKpxc5*`e&;>uf)6`kAEf|y_87rujHS;jmt-t-W}FIi~%9GH#g1V`d(`<mPqBk`|(o*-FAcc~OO$Iyo@H*nvqdx*Qi(1r63-q{BO(xU{l;CXI7I&YG~ugG7>-@Uqa`L9(Ta6qrRPyEK`>L9E(Lwveqh43qa*~5C6lY7Y3H$Hq;DR5~99@OM_Cek)}9HJD1e}J^iCq*b+(3W!y_kIGC+xw?a^K%uCm^xYIiL-m@^tuJs(mW-e**EIDCbdAFrG#i;i<~gemORe~zJ|k%G?TGbkBbD=(vSL)D{~GUVh=WWc9rZR5INK*rWD55Gmi7oB1gn55g8O6DrWSL8{kC-UhjT$h&m1t)3gHEohi|x<lRNmw-TfRd@aG8Q08J`GD;zgyzaVgvtMmM^IBbo<Pe4SxtC|zHryaWb7H}CU?WV{ms&M+d^YiEXoBn!DK}O(v_#zLMdm>Hbp1XRHN?XVy_)et4_^her+G_==$sXvU-I0K6mWy$<18GD1M;|c1MGpfb8-)sIvhF{2!HZ2%g_B>ieaD=Z_Q)|yQ!9!7Aqt;cufS7Jk@yHcqHuU-K7EC7<Tr`oYhYmI*Zd*RQirN$ZKxx3803Ig+Td1gIS*uXY>oC7<y|)8Da(Eji3>_QHKlyFWl2ETX&9I<f*(X^?N_!HP~iii0{k0G^;2G=$KCgr@~}1__Evj!Lvu9PkpriNnWx8bF@rq7HrYNpHOBwLPMO*`-<#7LaVO`d4)LK=~J!wdo6=eVVgSj=2Ii;Hb<)I=kV8KGRF<B^u)>d0mICQ6}V#&3EIrpk{~FOeOKqeqnhD4Tsk?^#&b)T9Z}pyriD1|wM#-}G@*rk4po|>xTv+h)jJcw2VP;fwGLSv!C-Kmx~h8sO8Hv>!Jf|-+kbW+&);^@K79qvI42BR3VQ1(Z!fYME!s;^4uN#E%H~07_D}VBoN#NKaap8i|E5TC+}w$ds`Mjbym=UJhH5%HtE<S^L(HFZH#&~MpF8pDz4x32HeDLKL-U$pn|`TaRXgB#(mzG(l)^Lzj#pVsTq`v0`=1on85(iAICfE6Vdpu<&5g~NePJO%M*^R;i=I@2(YhRS*9%D!5JS8a0tvB*m#EsbH#`Sk=WjkhSwp>;k*rRLmG&4Y4hIzH9@F+1Lv1KQ@~8W5^u5N@5_lPGH-?J<5T#>Xkw|U`H6?0I&+f2@{k?FV$t-JC9hJ?L<<)_sE-Cxca}n|U^#42b%48GE9xD_ScZg8gw_Ss<nsI}_S}LzQmy7%0b%#P=?&zRZ1*49^ote@*T))^Ba^ByBy7McZo@hpt6FwHYo|n&<tWdd&9%?a}b%>se-2xZ6%{?SFh!Ru_(<{F)uomfOP7ap@f5(R-KVN-wAh}>jp$|;T2#Vf8eXQ5II9bhC?)U8-Pn{5YYV;fcaY~be%2BK!l_fufjipb6g(!Z7Q_@1mb{Ny)!!Mcd9eH?|Z4*@!?avG6hl9(ILSMV{k7^vxHSh0=q+@+-G8}lDubV-atyWS3#JlyjyG3Sgg0*tgKX7RU)nuvs*VV{?-_04X^^d|aqM<0s1-~)<cBk|lV4IjhQSam9LS+>l62*LvqoW#1J_iDy?ZvQ@&qJlU^wFaCD6O30NUPItT1oUS&{YCh!Qz6;5N>7$LRB3=p!F&L>nP|D0E3eTiIB&_7Q{g7E)fdx+lWJBK{D5;nkEcG)B6?pOeMfe=ZSEky$}@dRvs+qp@_9xmKTs@<s-2G!d!9bqbrXAExrsJE{p0OIOLkrd1=o)G=y|F9q-%EP2j_Zgvf#sznhAnmFXtK<nn!P^u*1afr$X|>MjlxTG&#r89>|e-`8%uVW<9_R834bT0p>DG;1h&sk;Odff;^D)KytX_)IcZqR(9ms}`EBn_ka#37coC#G;e~*NKGYqwfvZP4Sjix#HSHu7d84CFzpTj9f0`H}I0D6{DUEvM>tvVT<nlE5LqE8WQ>|H3V$$L$SDFO7~9|u|@bF1s6kZ`%bYedX9ACV5iQ1zNSQf0J%kP&e3`$#>2DIYk<roUQfM>d1II5aDfs|H?=>OP(`d<Wn97&lSET4yd1`$q;h&T!xDxgDJ6i8VdPol2_<?fE`ebwM9W(up*h8H5ZB*Ed1NW5=LVhNKLo5ln?+t7;E+AgwiwOGvE`I0WoqzreRNl!*E$^Ts2V<&gI|tOSzS12DFE0F<SrzB9lMz@aIH=RmXbmV3^)TKi&3$%J3%Q=mk7*-_4p-l@rW@H?y3QCHNQMZ(J_AOQc|rkT7fj85PdNUf(4PqWw#Xug(fa4zFbdMrfm{R$yD;kmuX@zR2TrhptE+PIR@~ehLofJUL9h{F-|=uUX1HO<0Ta)Cwe(-SnYi``h9P6m<&pP^xzDF#)>Qtm>&X_0+avOLh0;svBLR9xW_?*h{B4YCSg*STlPo-bik;G^K^W5VTx{*0unv5l_<4x7&HK}xJS$7PHrGlvn+)>l3CXheG$PzO>Ek{R*V5`QYS-6z<CYHP2QOa*9IY`*I+TR+yOCzGlYw>rg1xhtxwx6Fv+2P7jVMl9A0vd?DdmjjQ#y}v=wT}Ev&dfDdAmtYsbtvor&e2JM7>N*R?$qhE_CL*lHwvjmO+^_QI*oKeS}r$;Zy=T5F|>xyeudHISq`egzi0#jxy$-RMe~Ptzv8R3|Fn9dQs%sQCfTfBadB0SQ?eiJE}+oy99%^OG*1MIR&cyuA=z???WT_cH1bOl>~5uq3pFUx|H?<o1I``LKXVw|Utg=axD(3PdR&OtApWbglwQ^Ef#{m|YKobm5T!T)1a(fC3%uX0p?7`PE8|g8;2}vJ5NDDWN&~AWGawp!b43xOHvp9oLSwTfN6?0?C~&5WJuQd~bQpy*+A;A2`dVWET~)+P@1Xsb!~pkqp^PjMt#-AIi{+c-!qP@LuTl6_UID<@#or4e8^^@_6=lvu6G|hT+T?fT-zAi&~k8TNm}`t<G~5gCq<J%n|SiV@|tYC%OAr|J0-7>2+xZ9VH$rQj6+gCBYG`gc79*8KHFGALThty8szeaWW<wK-6%lE#im3=~0C8BF`Bwm~)F(Xs3XV)ZMAmEY)D4h_1bz+ihcG=clZ5``Z|GO>P>J`bJ+(J6_yh9rZ{X;cl34hM@*}VE${z4`E|33h}pb$LrTwkpA}yc6@8}9kHWzgD3TeoUXZONSzZv#(UxFZm&P}&%mW?K#_rCSvh4If+!sur=!KcS`Rgf+$woH3tzGR#a41?pUYdPSb3RbsFS*k(ocu+Hl=`fRzI+3pJN3NvuU#X*Gwzeg<p3={>F+2xHK<~B7=v$zKx@uk)tg-%Pay60T=^jS-6A6G)7jRL93z=v$@~5LS5bp4NYH^9T|(xZ%Xk3t8r6d1L#i#F$48r;ZMiyt}>xO(a^m^JqxKX*Rkzv-VxM#IN>dA&6$z*qOX!}B4}7AF16l7LIiYDCF%OvfN-1D9|RLCf+|FgN%3nVv{!0<6AWqrkv8;K^{Zyqp?WBxj{r8gaL_W`T8d#07wph`55|IE-sNQ;VHr^104KW~ZK3bm8D3Gs?XIpudh`+Qy<40MPYjaCG_xe+hq9#fsBv0+(sCJjfWHEJH7u)b3VXm5E*Y6Y<!@dYN=JP*%S0<$@mjNlYu7QmOne3~UZw_-eaQ!MIp>m-*{@AaybJ%Vl3d3Q%cE?;yes$<8ul~+&yTZA5hy;tL*XRpo`~C)WNmA5HUj&4t^&P#tYerhhCb}4VFM%D+vFtlz0Z7B2^UlVEbZVK#3EY`qpMm!ut;x6-_lBhB(xlf7ux)!-vSBc-inS)nmYZcv&GYdP5_blH-~6M_G$PsZmlB-6fxBa>gZA9-y@M}M~Du9l>V8MLo>U%ZAbO$ASp_ny4*^Fv9VW3kYKK8?=9db)RL6WnZz-zQ;=J-4--(nTrLEwfS7)EzvP+IA94Q1KaPsE`tbC*8@(H#s9vSg)~y6P`M-Q3;}#W2mv+duJ@B&VQtcx+cbf2orVtn-pebf~sSOa_y~QhgG4=WJJdg`*uP6=$Py*;<a{x7NH+YFmvgHc~b=x4e@rS?2orul`{At`@!e=v(DVl~mBP9^;8@U-XEOje*a3>Qa!&fA=Q7Fi;!CEq04{nN4<_l>&sa8>3YqXK`>{N7+A_Rh14+e1(FVIU2%`qU&adiG>QdJ`Dw;y<}w>0%r0m8P`#)Rv+D<!NRP7?_s_F*ZLuW2muv_F5G6CuqR*ao($LGgZ50(Ov{u#ooX|6G|Xw6gGn7evnqHU7uLkFT>eAKsr_^lb9ZkUa@3|El)L;x8e6C$^z@80Sm~#07K&Y91BaII{?{8!LM3Q!yw50kX^p!l(&~tKfTY;cz^WddIFp%l4_gUR-Xhk+{HUol;?IaIKlU-0>#k=eym$3&Kc7gkdNGhSUA)Hv7o^NYp-sG;phN*xcYyo9#fOs??8(X9Unt(piLX)Z7U)01oA*U&0c39IhU?fufQnMVI#rXUNpkYQX8kRXnb*1X6ZcH(q1~CdNMzPTvuGMv~%t#4X7{YPr6340K>W!Iid|)<#-fqxe~QK(uCGP;@S9{<TheUimHL_*SkayPn~i?l;l9=wCK;v?o;-hKX$!Qv#|~SL;8qox|&_e4Gy;lV{3?nJ?Z%3KV|wLNJfD==DNd#D`AVnWs=4u5oN`a&(b$E@%9YNm_U{H^41ieh+JlfGGL9w_+B+iwoxHu)46hc}g$7VO`y^I>N887c!MUckWI2*zIo=<GwYm!3sry433#yuHR-@0A#z+UfZp^-0N0S6wXu%0qJbFf>u^5owq&v^!@}~v2Pm8r1~f!MpLvBm)I#$Kf#Qx+H+4}(GNwr;4;#2sPpnLOm>954o+y3#TEvH?{a9f<a5_oArUroYJs%s2B;xFsU3g?fb-Y`n9<6LnmvK4Qsi@myI`TGyeh`Pu~%B8*H5CL0;Fwg!}pQ!h*vxwxD7Ww+#*+YXUV91+txGZkIsaLSk%Ct@ZzESBg-bV$&NBaiX9s)Co%6vF(?HSsJTN#QKzx$4<n=z7ug+^YH<SjPmE!tNK3tcxdM8iFH*F(F1U_<O8bANr0`z>O^ma|fcmE)QwsN-e6s*K63GDFvqkoD1Fbc`OKUov-43LZ(qs`3YAvVLqvMeDJt%uEGCX0Ja1HOxu{!mhhT*=J0mmM#%D$}p4Z#)z^5uD)P>X3eFnp!E^Zm)Min3@}Nt6g(3=9v#&(M0tA;OLrGXHT4k?@}WwimxKUpPRq1~6_<Hn6mHtNqL`%In%$7VF+RjkO9Mp72?)iGSKja}~`I4od|tPongQ_xK#hO`wRpuLq&EW$pn#g2*SVP+AA+p%|{~u-RKX*WhH2t^qX2l~B=rr2MqtrXBG+SpfefA{Rd1r8-2!0%9_Y#Xm@c;)L-gmEy>R0ZIU`D(5mQXkba(jp{$>Sl33(P%;j{bCy5sITGztJmX&w&a9=t)v1^sgU-mzBMtn)9I@U!UkK~+7-@szI*Ol~@~I7Z^%$a?>4Y)9V@5qx{c8pHpWdZAbtwzHzxkSI^CUv8loigoPR!A@n{ETRhTj0ps%+cP>;5y-CG|0hZ`zm(cUd55>)YqSQygx2PnDNZY_ege_H|>CI(xs?Lr3fFNEa0$-Y)}wQaQWO@xe11Jle57a{;az!F0fJGEoQsoE$csL8BwMiv|T($Y183UXa?W)^fPm0@MK|7)61A@SqY+KHiTGEO$v=E4`ONO*~Co)#HBT6Rf6nN3#jM9_S`evFfQ&U*TkHo_{$wv5D_zMU_556IHJ#7D5L|2QFf#!s~K&pM*~>87zw!V^KWH)SV)cb3*do0LD#rz{WzPDT1vOkxyuE`ap%5b1GAV%vWJpQOI_2z?rKO<E*M!0vS9?bU4|W65quc&q6{6FD~1wMf$J2>uX$jdh2%qJAL{Qa0+jrdy{u^{I?@zrVUzykHa+w(-AqSeLC5S<xeY&l4^TES?+qt;Et}z5R1$sYaJSPD{J3yLJp>FB;QMSB#SJ!GM-Td_+kLL7MZY?Uk<ol&J6`Y&;?fZt0x^iJV?dq8MJ;r@!B+(HyH*Qa)B>k-_u^zLOqsYI>rTAJS2&fl`9`?euzVc&5O=9P+L--7ZL9`+D}`gW2L}T1XfUjMA8#ID1WT3)RUDtjw;k61t(1-QlDaH#KZtT7_zf*R=|JAY+Cf_o8rpRUFcA(g}8l{ZRm%yuIn!kBK&C4Pv3(r=A$N5L|Z<lhGO8Sre;Hq_GVWhVg-jkPckoVmBqy+E985PpL*!CPr==}WadVetd<0|5M)u%=|H$RV3IMl$dKAP*f5#VPcMT`_nAx)Ih9943VFLZ_Ns6vpvdvJyPm`19gP`CSepe2Wau*vO8}3evQKT$<1WtPqB(?rCjOcKP(l7=`Rs11+K#CF_Slg7*N&AoXmC!;ksUZ3qnH)l2!Q`4qD?f*7yj0Yp{sq1#nhtdtbEYBAVTQ)iJ+2I<!>FxSfL+KF>5K*vok=nlDh*DDM;4X%LJ^*ndgsN8V$%GWMN_;TCa#ws%RuFM}F-t$x~efT3_x8K;=W6eBG`5S0h-KbG*!!JHmyTW(gRkqyFz0UMok=A+jI{uJD76tTL@M%oUa7Z`kT(I>{6QuWsr?+`oQ^P|Xm5ibFmU6V^NGiJ7CjG&gC2RT_5$%%}%+lwrCpynafs<xyMU3uCHevrYer{2NM3(+Zt^StzJ;-;zp(g;gCPlY+;#(DI2P<n{Rdy0#4;cDo`1keD8!l3Fa};ymZn61C-Ps8>dxNFOzuVdYqg6C6seAskC=ICxkB*WHKs5TNsEL1SF(Kw{r1hbbLMgXTjL^kXn#{hO!YQ2D+4t7w3<>LVd}8G483;3Rk=uu<Rk=2-ya;{&Qyg{Ek&S@9I=8{Ai;PdG^CYY0UZk1rr*W;z3fZ23KS)5Xp|e^00eq)R@^-6s0aA2J`Y*@aPfSKj2kiU3;tV)=(X$E%9dYX<(;|G`E7Uv0y-CzxwzBjwO1C(2ccTPf7Zl(bf(oD1z$0)oH?GfQF}^@S-f{bKv^N|wI)&<XAq7-`v#1)Wz=Km;$aP?7Cds<%$C^V|r&71_N8qN@}hb-@}l7j;Nt%dIy7)uk)ho+cOiI&7(M1S{M*Fyk3kCb3Wjj8o|#4`ZVOomWaAT4$J#tVww00^7k#jXa5VH~z$zM9`5)TYvb5&_g4*SP42g2NdH)2h{HQFMvGq@=2y2gQ`3Q@cXg>kZSD`76X?8V0x1gF2F~Sec77wK^YQ6ecu`lLU(P+j~)p-;(9|JaSl@@UqXS#K4l_E?}bUU|DbOENr7^!Ri~jjwrRZM_Hdg45>&CS8xL&W5q&yzGwBou5P^<6ba?do<iv%zLRdf1KePg}H=wYtJZ<=)dU7-<ITBI()z81FXGL>%B^QJ#N(a32TbrwU`#N|UO;O(ow1@Ya*6Pkarz$b=9${h{iEO5fK~cFRWt4PnK@xktFUoNzk=~3IN0^67Tz`#5mtq9DTGT;uEL&=L)pwuC(qYZueewn&+v%0#&_2teD+!XE&B8u|7rOzumeTov2+ns)xnwx-AnqchlL-;eCkr!xkaV*(N4I=mI15e&(|ChfuJ9O`XVQK&N;>S+{9a@WJMv#9&{m+`B$LUfP~*G<JokHMIgG@-KDwh**aKRVOTp?oTQ}wKaxZuUb~~Uh|A88Yzg;2yuZ9D+sj{fk3XWISa*`)e!sbd3MBJDog@Al`pd9J`BlQ#JC>*^5jRoQ3Z=O~QR+CbG)a6AU!L!Z-{5jyGpJhJE_2ooOP^}?EY}<@9iPH-Rwi1BdxqNtMYWLh@V;}e;m}=;QjE=YR63u#2<;5-s8O>wI>hox~%`;<&GPK^eTyAL1{=+9cIxQ>Xmp}kU{JXfWb@Pk@9J=^Qy)O#&KI$hSCJRQAMn!i23M>ROr`tRV3A4itMdsuT-qC+^xn7<Y$}gPkT^fW4OhRP3_MMA6I;hwJCq`I`YKM&PD0qS;Q*T(KnG)xrZ&R-Zo%Z>)FQE(ejKLDVkEY}i8J$;&kQer))=2=3lw3sZ0<?4uL>bRAty(y(AqURxm1>P{4>H%JM@cn~mb+#r3AB9fzAB;!<XSpnSY}>2>h1P3;Kg!HJZijOZ(Ix#Crcw#$)Rj&kt{XwH%Hd`P3X5vKgP~8B0<|-zIv-!`SgCDc*s>p8!_cRaf6CPX=zgdOu3iZs1?C-|CP}%#SeWQSlFqXb@-_uUV=llJD0z3_K=vNu+l1UChuZHZBXYTGNNR?cfW%_e0#g9YKIOCp?x5tmiHvE!Lb`%Dm26-?SH}tb+K06<lshEvI-gi)~;Jtu`fXi?F0p%uL6s&*uf3@#jCxS${!|22hhlHJ>tuewEvO_btT0t50L+i)7Z$m;s=}<5hJZtrVgsOa^_JMwIBld=KJs7j(iXC5iC6_UhMO<&_4CkVFT3^vFA@Ocj1R-Nxh;9x35o&$Trt!9B>9fu^sZys4L0((<L*G7j#;F+!=^JBxC>1E@k`{)O1@{1WmOytms3KBgTu5JAW@?YAk1)lQ(uGvmVQ~;bzSU7P+a|__D99x%LGFXm}r85P|CY0|KQ<cNqP@*|ChCf2P@60l9Ma>x@oDq>h5Liy{e5(Y}hdXQs#aSKux6&R5hywoYtl^{pGs<>>cx--7G%4F2o9aEz6R_k(idf1QyrxzW4drUB*7tj4dIRq!1lIqC7WTypaV2IT-sH<Qxjs0b$H5Oi+keuCuXJ+5O_o)SeI%neLcfuVrKHE@%oV!F)6+^3k^4}jW*WK57@_;^pCT#W*bK+R@>`@a47Ol_1znNTdtWZa4ZFKIOgoN$}?3*JOIf1m%jBJi2DNz%(=Ny^>R{}-tQlNC4gn1gR(XdOH)AITrAq-y|XO+r6hJ(>pz@AEXjrUhs=G6pfqzEUtTAtHXjVrFcr#Z)kK*Qu69@jH*)c7IC+WPAOqRD>5;2)3;6@q#=hpymfmW$lcmY$RCNG{6_4hj_q<!&_QEO&>-z0s#+9S$_u%2kpt`pU`GcKW4q6WoyFXmHd;2!VH&`dN=AjqO#m2Sq%Uj^+llN=AluWFj7%P4(YHWPE<sDxzjjpqprq`@r`>Fe_w2?r8J)M>USX}^vglIJZqBQ8*kXO4FQiV!J?ub$*JiN@#o<6seH1tK|glF)-}~m1Aiii6J}!xOvG()HYGp#e$7Ty+IDdv^unVNAf-gWH)Eac=1+?%GSATp^E(W9T+sSGHcd`|y+U@iIjKJZjM!_sK^b}w-{|e~QqjFvDpom7>hn}0#)xmXvWXeBFchjpXD7h~Cc+!e>z&eB)Ng!`SN7mItrNJ^=QkF{nAn}ri`SS&wj#L$-jm+bJl^)k{kh0K$?3GjVAU;=$BBH5F;yCry(nF(l;G5o$^ud#YGA7Qzzr+9Red_$+EPV*(6G$FUmki9kFesOY~;t%;p9@wOx_`|$Z9yH9A8lGub9~A7a~4?wMMv@<U^6~faX1g?Q-5**Oh9gc>ksZPCx)Pp0x0w!HgeT=)%^TT^VSE^A*{fk;(C^cY78mR*O5Sw`ZtI3Gscph|8S(W<bDBp=3}m)P#=bR__@FD_@ljjB_BeiqJIh0^Pz4L7GmDo4fOnsMl-nDE&k9IR8)NftPf)wt$HO4XsuimfR#R|40Oj@JkkbN%S49`mnMDF9V4fpE>6CxFZuSWtrFq`(rCXx#fr(7)7A{R9n^*GQf*t196GQfDNi7?4i_?4viLb!1(7`Uk5z}FXBKQ63lE&P7%=WyqPp1&QD=vOIOmvX%?tzx}}B?ZGYVYO;Y$P$dM?zrH;4?XZyhD|CP2bgoH;>tK9%8!Cu8aQdP&nfIxp%E<Jq)CT|Wd{vq8fM6`*J^TKTRNbrj_D6Wxe7Lqa12PPCHaK(Vt<(Y)ZwoUietWPQ05x-^2CP&c|+8+D*b{dw`=MuCT%KwOde(i9_$LC!@hmfFz|0y0<Z@YjP9;qZ#*%sKM>mT$Fq71{XwysIL@Ts-Rt5B>&h)Mx%cBMI{c;qRqw8;@n$UR6kB)CEekH)(k>#EQG`qZ5#wT0xdlEZ<Q&fh}zr&A2PlmsDKT^Txsw6NBv^*Tn5XS6@Die}=q7ke=D%1sb{yz<eT<B%rIo?!s@uLiWBV{dIPL<D%+VdN(Zt|}H^0_Vm6%!akw|I_TA2Wh}AMbH)N>RD|Rw5(}4zb3jsZ69xc2gM8NwlJpw7Kge3%8qjK9J-O*LASI_(*{rHYPPvJZeGLX>Sq}20gP6Ab=ugevY7-?xqhVn2Vbfd@x4qGlXMGP@-%)E`lmy$hdX0r8tv|)zUXj*fXa&{Ux%``k@7NL#*-;P`GC!+l>p=*tTWum-wzH(v^kjE^wu<%U>kd2KoN+9cgwe3^Tu|n3%M_V>#@i4JQ)PxIXB!R$V{#J@FfgJnI^O+)59$vvqd9TA4<0(^G#VKzK%AZRi@Woe4-P9?0A)LzOst@chGUL2Y7g~S=eHLJQCQEutZ`Zusn#T<SR;A;QQegkvMeoByNzD#nKE&#7(I`2k5QBbZE!J67}(pAz_#(R?pX*LQ+DDSL4z6r)+;s%D4ZP`%`<@rz$a0;l1ivS};2Ofu{RK2plFg<f-QRzYJ|bPjq9Db2*2GRTvNP{#)!s&phBh`WyYDBR-V-z*i1uKiwhafVyZEb%@pIbn(a@0eBwqN>K7gbWxx1`V3QGHDv2yil5Wdo`gAS*#Vp%{O#>tmifAP{kAY$-@E5G<Du}?jnM@!8d_Fc;-~v|r?SZp7(z87RK3ZJpi^i=aYrsXEX5*qvoL~#)Seh-Drf%*w-L^J7>HzT-la2ZWr?k2QoUv~awC@Fu?~u6VLBOBz2T(f8rJseQ0ZA0c)YpPz1L58K$QC~J|&qkX2=AlT(`dHc!=0|XyMtu|3qVoc7}f)Mbt|x4hkQ!@=xLtG<;QZT7s3_r^h{W^vu-{ItB$zNG_5B_h5uG(JmACvWQX=4K`JR4=kYh5;fb@*v5ja&v){A6FLMZxX&Y~XmGK^qv|=jC?s5YXjK#$x+5^FbJP?lY9F)bE@L4V&6*QF`*K!TsLEYunw<6)MubD~-FOSyEK8qjrG&GtIdqzD{=O679N1MG|L%3tP{pBI$phQ}%+@DeC{;$M8nl-0`um%fmH97gy$G!KU|bF<TGz_;k`dcJJaQn@(NLMvv`<q(hwXPiASIeQkaZzqm`wThrxbJz<P29`vTLWG-}Vi~*?nR_P90Dy0+ygoI-N>hi_9h)Mj(DpqnT|NlG81{ZvV_vp;O$(Hp>LzWAf!$r?*wnqN=lFUg(7qdN8MYSzxVM{Vl?2A&vMpqpl)ANuOz)=#7^I`xFbO_zg~0N{N};yxen;_unfG-PHV3MR9t$Jq(kRO_9k5#nXduW`fQlgIE>~yGIB}U7x1k{9qCMdDq-_u5yA9@b=$OniX2S<)NX!uCCoChF<Vph=#2cHkZtF#{g+H4P(LA-(mAPi%Fg0x(x8__;XR)rvW=#TB%~Hl734X$I^4L!`LT+fawUnV6sv>PC0;g?f{!Lnww*%G!&L=?`84y4g%EA9K6jEWs=gsO%f$*!={w5DuulyfZRCkdCTRYG#)iHoZ9x5_Q4K$Gu-k`3v63mC#<_RT_`<mi<#y8)MS}NDasN`HYKRWzoj4zN^Uagd6xelE#6v`>S-~^Glz#e(MN)ssstyB?-FKs2XzcB6u?+tdH!akH>T;>_5xD5QPHu&HN7ZCiXL{IFy2)vO-5*>Z61fse8TzH99Ifl$5l|cPZvt%T#Of3TY);PLRm*8&nB;M+9rU<%0(@)Nd?PNw{sNl#?A|tbaW^sI6)4PR2%C;GxF^5>#)Q5IeHZ5+D?QINSGz;D~t}7tP4n(+b^Cw_%7np2v^Kl)h0@i!M)MPV0Mc*(*C=(hTWx=o1<!mk4E=x+>>s3AB_L#HfT$VK%04uAiOI=AB8PB7~wx#c&I^?=qd>IlMoed^iXp2dl-4#ixF7#KvV&KJqm7THfFzRLdsqnLzEWaMiY9ey>gjc{$*J4-3vjQuGGpc&B%Wx^kXf@yf)sDxg{96#+n~3(jd|TlS`y9yeP|Qz1`X@psNCIx2!JS#GU|aU}-8*o38oECjr!Wtq^ZzbMZrMCwFn$Xe$~Cr;7AGQ4Q%V2nh;;HX_ICDaoV$Bb${6_8C6lBkJ25KdKP}%}EyAM-j;vjNaSPk1*V6eHw3i0i$^laZHz&t5`u_y{K&j`cZOJhSeuKqa%>c<Ub%*=6HHixvGt5?D$5s9PO8`Yv{Ee&^+arVFg;MmYSuJzLrsr`BL_A!w>PyT$LhE#*7%VQ^sD+*Yd6bNO?vLJa)%QY&jviHe4q=cr{g$xV)upmDymKjeRhW6QvHzCIJeTO_dbKgZ&lwY)hK!<;a#T-Pe0l)QW`(MIcg<3`34Wq@GuZp?{Lo_(=8|gRCLfmdk^mm0YO)%Km?L#`k>-dtN8X0x2g$IBAabZ)Stab@wh0DUljQ-fCXV`;9ExYpk3S*nrJS3U`iWRw8au$)5Jnz)fSKd4+RY9#Q68?jWg>I*#hhsI^T$h81BRp(6Cdghumt00000J{7Cg$e@9T00FU9n~nnjiY-?UvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000005920301699291685808790087575075447906825541973677197145095917255777770338654740143957368885', 'computed_previous': '0.3899999994818793145981678525453677411363907159834555654303139992498463309818573609469081020806494221', 'covered_success': {'lower': '0.3902237244338266925760508573304269752646662852847654736993021666859942154839223285017837906978656905', 'upper': '0.3902237244338266925760508573304269752646662852847654736993021666859942154839223285017837906978656907'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000003716400698294819449074566364288330078124999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000003716400698294819449074566364288330078125000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002017780464679887171019410782340670003163706148087826778216112663466702337541980103704219306060775877', 'upper': '0.0002017780464679887171019410782340670003163706148087826778216112663466702337541980103704219306060775879'}, 'self_coincidence_F3': {'lower': '0.00001129784381456023666100779224983761930681149068511500195261518912039238459841888755566976724422258598', 'upper': '0.00001129784381456023666100779224983761930681149068511500195261518912039238459841888755566976724422258600'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000006931550815678006308514218372910655141858059153958661610126535572037736153120853618059604278501957052', 'upper': '0.000006931550815678006308514218372910655141858059153958661610126535572037736153120853618059604278501957054'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 703, 'HF': 111, 'J': 63999, 'LRC': 40564185382003226733193754220429312, 'Tb': 1325914782967292795419109243400224768, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': 'c3f60192dcb337e7eb845e81ed9ab7b688ad1ec7c248374780291fb9cb7998b8', 'previous_grid_upper': '0.3899999994818793145981678525453677411363907159834555654303139992498463309818573609469081020806494223', 'round': 23, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 91480, 'union_lower': '0.3900000005920301699291685808790087575075447906825541973677197145095917255777770338654740143957368883'}
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
