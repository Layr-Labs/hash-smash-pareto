










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
R=11;S=19760;U=98800;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 759, 'HF': 111, 'J': 59289, 'LRC': 37578868218465746492669018171768832, 'Tb': 1325620839056724639014355545949732864, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 168, 'dp_loop': 424, 'one_dp': 426, 'ctz_0': 433, 'ctz_1': 438, 'ctz_2': 443, 'ctz_3': 448, 'ctz_4': 453, 'ctz_5': 458, 'ctz_6': 463, 'ctz_7': 468, 'record': 471, 'probe': 484, 'insert': 508, 'insert_done': 515, 'match_0': 518, 'match_1': 521, 'match_2': 524, 'match_3': 527, 'match_4': 530, 'restore_after_hit': 533, 'continue': 534, 'deadline': 537, 'restart': 538, 'restart_ok': 541, 'restart_nowrap': 549, 'setwalk': 551, 'setwalk_loop': 556, 'gather': 568, 'gather_loop': 571, 'restore_planes': 581, 'eval_f': 838, 'output_message': 868, 'match': 895, 'measure': 904, 'measured': 912, 'advance_p': 916, 'advance_q': 923, 'advance_q_loop': 925, 'lock': 932, 'lock_loop': 934, 'found': 947, 'replay_fail': 960, 'end': 961};EXPECTED='09e0dccd3a22e25e278363de8c8f78e4c3f59b35659f7529c4680dc850307585';NI=961;NB=30752
K=(0, 0, 13265668776992266707, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 7928103212675454578, 0, 8575737624765115194, 2590537648358642454, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(8779690472602585590, 9377898425489954449, 9667194340742837760, 290484375670267904);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5178211340887781798108502832447489)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;FP5#CtUyqZ3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<<&w2vtJ*lXKl4f^~&kDS;`Tv#S*}Y!)F9*Li2gZ;z=9K8Ujp--l&*#=c(1Rk4Dgo<;)27lp^MCuo*Pf~72=KI^Yf>d#hkNFYR=%khwb0_9E>s0mRHBR(@Z1Q|p<DN+|D2unWW5>RHy+`cMh6c?toh_?92xwqDBZ<F#m_qSCja3No#zJsw{x!brIgMqT@j4AyAKn?XL8sEQm322v7pJy{2$J!w_bA+$ga5%Um^pPz4J&C#{kE!XwdbL-Qr^Q6ke5T#3MD^>b?IO{25HYRY}at`aB~HdN)ct2U>3E=Pe(`blIee(tE{7F)j3pt5JuoPcdLS(8P^{siTM#-Ld`W8N&!bTkI*LijvU<7GHuwh!A0vq~*j9ATZ@Yk`?x2#WGShn<U^J?9ThBghMt%o}{2H%?~5*lIYYT%p9Gd4O#Zp^cEA2l(4aSBEfZoa{`4UtCQga{6&g#7u<K^6AjM0MJ(&J3eebmNb05BCGWW|lZDG*+h~_me<iWuH_Ngtt*s@F%d-``cch6WZc~I!P><R7QaTHtcykmJ+@~FLxn$|)H}D{#{snU@3lsFzO0zJwdufeSZX3?9Orfnp=IcU(7JU%zKzbXNrx&95QEd4#6%l&Xk<q2<Jtn~DHB&d^tF`J;5<Z&8Pi|*rWI((!^?EWxWN9Y{^dEX?jU#D{ciqKPnrVXHxcVr%lS|5ji%nV<4>#&_t@H#IXaBAXC;FG^BRzB>ODf?HsLzS)I_sbq?$jITe)sKYXLdm1w3BcVrMeb;HT$Egb#LsRIS$D1rtLQw!Imzz7Yg(l?7^-VHIR3EGCQ#}fLzQ+5h&Wojix4v5;}$e5wFxyNd$1qRN}8Tqbo|;j~liE)iqW{3nawT(#zTvq#3w*?x&M2kaakW0z-c0{XY18NWTRBdd(8Sm1bIr&Fs2t{=P+$(12k8NU#DzN)zKeX}i2dOZhxZ!#MJO^7XOiLoIX13`wRo16>|m<Hhl}C=ly;Sdj8ui&VYNcW)CM>n*N&K8=dF0D!djW7A}82)3t*APG%GNz-$_%dIB-b&SnOOhAJY+Sv;pvz(`UGD#|c4;F+m?N(PWPTal^t{0iE9ZG#JZbwcPEeqR~OQ^&N^FuQ2AM1|?5VR~SXi%^)<Ig6_Qu_*=bsVL1EO1>=UOrJ6hSEAwz=$$%O4*#-^d&aTZ(1XfLcECM1kd=S5^RLGs^;d3#@bAV<1uTjrcQp4m;z>Rgxqi-A$xL^c7sa2i2S;Iu=uA3U2a9j-<kH!{sB%wk!6;y>#+Lx#Ve!hboJ83u&*>Y<R_^3cHO;VQdIHrpzELWic%1)O7MSd(W9hixzYU2J=dYHWe&A?gw>GP(`iB7!k8(o3%@c6e3`R@T<gD})}I89`R{ZI?UFEr*sThyu_Ib*L-!SKFhjgGa1aHKtZHX&zqmCssn+`!3jVG{YEf_&S(W0iXlfsrbGihUWOb=;?@yaCTvok<UMAp(-KPcRE1oApIxd+HcP3KCT|pN=_IJ{i2jhCKH3#2lr+=CMxT^3b3UbFd;S0bV1IKlb{`1sKQsYIj<Ch2B&cBiwAm3wKs=28dABh5vCzaYx{-w_nlsHS-jS@jsIY4Vl61FgU?y0R&G>pa$7$X@P+&c~H)C#@)9(RZfn7_OZo*?GxA^2;_r>c0pzRmzVA+_md>S*3uuCVJ=S39{8{hlz_jT{ruq1q@r5WF$5<?|$Fb@-`kYP4gi^){M;bVxpK_FtBxsK4G{-S$3;_MIBg5ig_S!NIKArHEg0DrXx|x2#;^U}+{VlpyXkN8f0t*&_krjs7zO;y7-g5)wo8BM<`!mSiB;_H1Xo<TxlEJglI4JMd*H7-WriWL-d;e1JwrtxCTNO};e>*luS&rir$6-w!<5T_MSOkx+?j&g$*he9+FO7)-NXUntLQ68O>sQsS5qfH1&WOk>xwHFsOHA4RYXR;e!qSmUBQwbX%SByp3xd%s^>+v@};yY2EvYi7QF1O%q*sg>(!rIe)|=nM@^Rr<=(_0QEb|M4NFy%r2}*bDB>7_KFY{!}S!T%0GiW1AVxSW?c*;aZmICm3u7*_&)o^;7z6aJyI>0P)7$;uY>4fA^$4y<w1lz8<ax3x{WLbol|*)N4fDot?mfVkr6&WyA<~Hla?j0&N!Qcnd@r)O;xz7oq}~ttT<F+hmdIf(EHYv!%2(G|Qf~IKbK=<Ne`*ZWcp*jX_%6O#-YEYb}|oH`yUi-dC3RZvwf)H7kh$A(3%&c<`FVP>$j=lbE_F$Pmj8D&hsWil6;nVuMH3$sj9DTL_(rdu?%tjLpkJ8ZeY!y9dGJDf^mo#*%M2987=<8u^%@hin8Xvrfh`WYiKkD5GBv%hR3q=<bsU2d#qM=ZB0!FWHw2C<Ou<{GcG(cVM4U4b%suAsT^ULIhVwYh9KAVWFl8NJ9tfuu;e<M0q|`k6Qy5R8+Pv#fw=pxAkN(8gDIZ1lS*m5T}|X=I7Wzv>IesA#u}qb|Hfze~T&gr>F&c+tpph*NR+2bt$B`TTvn5timNCtL~j<!4{tk@PK{G*m5Fh{#7i=v`nZF4xIU@H9{SUBK+~@N4%wzqCvw&kS{c%fUSkS<U}7iJiuRFZPTI%352wM0U2oxx<Mb2$EVi)MQ1}hk44Rpi>8<ujV7#=wX=ik|Ca){EdeH_%B6P8CG{7bv|+rPc-e>2sCMzix;^i9Wr&t+RdPldi-`)jxK-|<%14Gz-tZGVs)t(d9*y_dJ+u$MJK}!-b||u<l8BmrEa-q)DX!|CRO9qyjc!Fo^_j$cas4%?d>mVfrt5<fYMAG^bAU+!82Dl$B0KQ}&d&NVp(9aPl9uY(Tg2+v`aIYNZosQSvDCddF+$tQB`+ZqfW~hFNEEKS2lllR@h#ab4^AYX7s_Q%<6@tiNzRAU%KL2aKk@Wi7E(|N5;&<DbH!<t2NI_<3GDO1!Ndx~<Xk<ALgQg!_nva?x+q7$fVJW>sotXB0_s6=woT}O^m)0hRdAy<BWUB2VW+0X6%kX5MN;4ZW&0Wr;INWKE)kQbsNymNNfQ2e5>O|2{)sl~0NAZ>QK?<r9tx8+<epLd0KzNm){H_fD>}%cQQbHhInDR*b}DJFbp0sIqh$;fzp8HqLb6;2KS6%SZUU5`c?~_fTc{m?lf03^)Qv!!_mLJuI)P|fo5{U!rpkM@7AMvi@TOOlpW7rERjRIvl8F=D6Uj}7_`A*8(r&=otfJ5Qhi*CXln3`}H-<jg^NtpP>6Mf}v4ml&uQ<g7N-UXH9n$&TwQLC7k@Wf2ITs7rO=sO+VT3S2?rhz~05k?5q7)Mx54k%p2|3PLLj3k48|W10Dsgge-r$cMX}pHO4y()>k=D(T8d@m<ZQ%@c0U&%Nqryv`ITfgV80Jk|@cD{b(65q_h~54B+M(0oa$xCCjP`dObj6Z9D$@?=)}8*~_g1|m7mS@GW78!ATcfh0x-y3ROElET<LRf&1GthKBLm%xej0}MIPOV5QRe^Xl_^hUX5%ZYK!q6Kl8~#4bH|vC$AlLe!lgws0H9B8K`38yO$@`vUSp|YY7(d<H}&W+c5P$*!`ewf^USiUfD|$Rz_bH(bot?Dx0DU^<<x>?EaLR*J87Nkj`&a~xlngB3AMoIlyG4n5Lc!mv>;vNY%iqB1Z)xm`aWo>={YA%_a5j~oK^)w+^X<LUAr!J##{)hwpHmzw;9&aYzBm1Y=Urua|jQ%U{1D?9M!el)5MTp)TC+rX<bCb<Xu}u&99pWPVTx0l9dUq_-@|PA~#g`9v4z;)_t@hta4wj#9a@i?C|p^0^D+vn&3yg-<>fN>!hU7rb9;7M8_3SRLLb~YVk}IAZ!(h@@!7Q+uNpG7$vY)bM?Qqt@&PP)nUOG)yzfx|6E2M{?7jDfK(6Si?w!-L+7<j3sA0aUAz`P&I84V>N)|nOOgWPx1ZUnyacAZQIe(2g3>dJK2uVd-73G2wmH4@vNT^;OBK0XA0P*96fNM?dN0-HdSAyr2Kt36Rc`u&Lq0h&RGaG1D)Hkn$WnIaXslI-fx9AjLBza#Gw|#&&kTnA!^AnvXar#|R21j_!jJ{-np9uUY;c9kI|WL;OjXMzLwnIjUe+*m>W3s?UDfFkLY-CinBzh{uN2Q^U=zJCWs1Z@5zf?e^5WSP$C1LkJ61v-c#Kd?j$*_agJ(s8IidIfn@KnjqhSGhdFvVQX7m>_#+()y(AN1L;f;2$HE1S&!f-8<klKT|$rF#78J~?yqw>=c&B1nE97$B79#iQ=IwGgBUQ>fp4E9vQRA0Ruhb;BP+{DVU$UzLh4s2ZshWOpT>?$q7G#el}i}c&TAOuM1I*a&Zite2?*MEjWtuKde0^8SE6XRn}SApJ+X{5N%8_DFW$X(OX@kMwvo;HM_qB(Zh>YMfN&Z}HIVd$rrE;KB@YUiwr?FvNLInI_qiTPa^JE16rM8FuFQUCqIxbygtzBLRc$`-D^riESj6dx~Ie1ERQ_<{bhsjG+PE4^n@1fI{_8VjDMpo1L3TnX(Z>E{@4kUm|7aQqaO@1jj$kw&u`s(S3XFk29_WVV%}6D;W&adwth;mAG^9-_1^@l>7`3gl(`k4%_h-X1x&M<=#CfIQ}@E)d}^gjC%rvCMR_L-DTmxA--A!7jS+VvN|I5ZKG`aGL5Bu8j|ENZEE33@2^zN$(M8{13IU(>yZkSbzjUqs6FTrcxBR$!?Cm>_9#@<|#!nsta^g0N|Gv1d~*k{O6rEbhh+=Gi19!vog;@F;4spdzc+Fh2g@O2(F*xI48Sv2$?P4%U7v+tdhJo664PdC|LYFP2!sT_6&imQhwZ;^eH5`rZlHhQ$A99w8qDEI2EG&`<>J`6e}z%g*&p{vTIjxL(sdfhD45p$0{UjOPkYWM-Bazk?VFpjnoK-Me7W6IU0O8N*gVqGOh!zmv(HGG4^Gepj0j(jqQDFIb5C0W1amaA<q`rga~JDK~BccR*2P)tg=hJ#II9k61Q?vI^#aIlrt;o@Da#ukY%IR0zLw~$GGfVOfr}X-97qg+2>MaX%n{v*Z1i(cqja+83+n-#8Q39uCf9RWQA|p$-T}%tjUhJ>}AapBb1iQ@!8H{1dpZ=Mzp`*kHVSA@C_ug2(>fE!EeEwAs7PoMno6CvtQ4O+&3m;sgR-%FxNnTCN6Cm##V%g^?g6%5PhpwbOWYqXJa<BNZ9@<q`bH{yhV%3<ox(A*^Q-u*WP>GCmQe?Kl+pM@%e|!O5v`~Z&JFV1uJ5R*0F7L%##k*o3Z_I#ib?nP|Axrjh#@H^6jhDm?WO%PP6UFQPV0cLGf-Gq)V^W0LKV2?0aQ-6lrhN)J&vtk9Lr=hyYr?K*C|wzZOV7)|IX#<eL7Wd@N+<(mIbabpI6Mn7Ps^YkK|QZyLd^2LgC`VH?un)+j!8IMQ$#E~YQ=LdYlYKlhrKNLdzbQ%OfSg!{BJdCr!5j0(lxDN!^G+O@}BRM8#FJBTe<dwIrm17>5(LaUY+X8t<xk`;Tl?@yR!{nbb60)4G&sh|x_+vxyOu#K!&`C|D3{N5#>qGRImhDRH;o;5WgSB!Bh3;pt6Og+54aoipRIL2OIk!%}%vOs{dqQd3{MY$&Ql|wpa?0Q-)98sG}kC|({AHu#<UOp)p`L$=UDoWO|T1V(PYXWUaKj|kwI7c5}JfQDEB5T(A#r8}_MQar~*jjeFn}^?=Z&Aq;rVDTwBTg{$hyt%SlPJQlDv-n!1>p6lIUz&giY#FZnY0>59VE7^{fh`$^0ib^JI!lH>BS;gRMtZ?SUc2A5`_C3b(Zf|*He{?Js1DGmm#@ul0Xy{112Fr>#V-w{Y&VUK)Q5O30-l<g}1!<h89W!4?DS=DTNI4U*?*BUkQlMDG@XUJlPJ<0CB-npAvZXHut!jllj$@OMNu4n$``2wOql*_!&(V<dzbjF!975F%Tl1#o+oWsJWY7C-;MBizoU5@}_C(WuPhB-J3NpZe9v?`ZY@jWT*Ei4U}9LR<*ZMqI?H+53jk$n?5IaYTG(63r?A7Z1#)-yCvbp;~jrsi8%=Zy}o4x_}$-lTVLo9jR5}Z18b^?9t}lX#q3CYcuO=h!hxD`g4HfD)4`9n$+nZY7iEKUaB*>=1&EY<HYcc~U4bR7iTGey_ZH>w8f0fUCu-KZ4%&n=VcnNMGfeKLZ4YJ6`*Uva@Ubx{GJGx{*kZXp6%J{f44F(;x0P9Gmsg9vdX8yA&-Eb<aSr(=%G1kor@;&f4edyFkaVF^w$?Q&aXed#9+e7y(EG6c-SmX@N*!gDn?Hw_OlRCTq%#v0F7}Y_dD7%&5HD^J*ns7<O$J~29O7T9unk@{{Q<#GwKZsAeizM_E`=vPNu!_I8rlvjRTKST+v6+cfITSxyG&?Gb6|X+r3H5xfub7lG`;o*parf3n_Hh0k0s()o9ae`>+u^d8FS`mN$-T_E#yeVqfb{$BjdX>{Jd{xkLh@HHn^-4{@Vr<6+W`qD?JtHvwV7-)I<tzKnK*zn=m{c7Nq{~(yX~+BQ^fAZ1Q!b<=9@|3Tb@q&hI%NT&t7l`lgX@`XSMgMd%E(uC=8239HIB2B0Zu+2od`;?qky$?)d#5v&wq5I^`EmvJb`sKMh=FZP8N950K(_K)fD9p%0>e~*MW>deeZ`CLtJal4SRX87r+Xz)Q1VHn)9@rx1`va4)NQ1J;BaCn=XKEsHA4X-dcgUH4r)%U}vY`pp?fQk=orGP+WQN35a&fY%45|n&0Ubvn4YSHoxe=BXk-#_%)i!)&aARj%aYA$W|WQat`jR58#ggBrZu@#rp5;0!2tM13BvTLKoA;@Y#QX3VVT~7}g4j~2yXN}!Gr(_QJ+bhPn`%pFw%kUa^Wdu|;Sz)R$zI@A>=vg=djT-c%a*(&0m;{Vd9&hNB47bVZ<BR3M(%WgJ+?dPm1Mpv)0}r6jE5KULdrFo5FY0CbY<XR0dX^Es2G;>mFqMd%Ayc>Z8L}7Z9Mf(Xo6}0Y&IDu{mJ2^h`Get6eu^i5^rF){B(^#oVlSkNOE|5&@ER+Fe*0<<qGT)QNH%Gdo#bs~&M2|RylN^bzDHxXUb!F|K!QPMnHEdJmda0*C*QG)czdufMbz2c!!7XnVW<q3gs2t&JttHaCjV%UgNm%@e@($Fbi_oj(q?88^tTecx%ql6$RnNx14xx*k}wvWkThX^Xf>e#!K8Zgnb13(K0L$j*;dm>j8uLSD>4QPB-dsgBzJ!A@0AJtUTNL50J9WZ7f;1BnTsW@JS4!95<at=hLNvhjn$s|UF|xXaFU{0b-;2<WUKyF){aB3bYKwvWbX21a5_OYG3pOi0!T&_@OLD2Nu}P3zrFQJ;4TG<v-Ih+Q&h{sZO~5t6V_Tbvk=YHQegr#OFj=s<EQaEv>{ME1;_>E%O*^3Eao9pj6On9`=X&D)5%)Iw@D5-ld|C>5+*vWFniwG50J*w)qYZrh|gq8sD1a`Ir{7v9xh$wc=ADHE5*SLAy2o^)cij(Q+vHSZ1^r9#^Wv&{~?C`GR?nJHGg~tNPMW)$G`=4z2@jWP%VxN`~z}+A%R2kon>}^6HFSpY8<;g;Xu6_48cCUNv#MSQsY(m+Hw*><1)D=ux}2;21^Q@g@U3EUwDOP{lqbl1wFH9P%#O)G7V8u0c<)R$6cXwbYgUDrcqb96z8Qs3#V%#e@uRiBmyPDYC<UnV~%#UhVO#(vF-?$<G8d|C`2U;Z|cz8OS5G;d}v7BR7)l<;o%7fq6mol4bTNakaQZ`nE)@OXi@C3nWR5FeMF*9t>re{D13ot0Xt(k1?~H{*`P?vCw)qeD16<}B&8?w09w8}P3>Y4;le2+{^Kv`<jroAM+`;X-C59+e}SHFX_SrkkJGVGio;V5&^{JCFh(&?tY=gkya=O)u2H;q$Ow3!FC)#mKHknR+wjgH8k{`_rFYlXkm$^W#W@Lng+b(px{y^ef;D=>G3Fz%E2goP9b7j!IA65vUH~8nP<F)f1ap0)ieCYJ;D(^iNF@Mp%oO?#n0P^e=nq9~Cl^gnDvvr>felW{%)^2mZVvSe6Ji;8D0bvS52t8@bp=`ga!oOe6=ME~Rt9ru9T0Tg51c5N)nu^`w?|&@E=#vVD{{6%cYXZ)p#-Kq?fJqNU8|ewIE())qEt3{KPW+29HVSODeE~juir}8_H1ucTnx{KlX#<fjCQZKNRvg%(W>MHDo_CklD#i4+r^01joK&L;2twmX&STXV~ifu5sURl!rv9@rSjnsBmQ-0>N<ef*p<=HR_$m}gDc+}!Bh>;Tx^&?!7BW=eI`F_<qy19_!sX@>+tfI120VM3zw4M&oQKzzy}!0quygFV60hYP2Swr2oYgcMkUywme6AE<3gx_D!qS7@NT>2gl<_q_FSt}fy)(jjkCIgXwKib07woOm+(qermM<Mf|5qG*~D1AnkgK~!)%1ampb5xVYt5{gzV)5pr2t!*)FK$6Ysa?L7zyO2(wN7A>4r+C)QG<2rU}Wvib|`AmD*S=eq115qw0!MzIKUd^&k9HrRDwIo{!R$mABX+V2vy>t`N$R6ceRNOI<sRcnl(HGtq%QE-G?6AN=zH?3aW{rt8eAUcePor*rk(VXYH$}RlMIr+1tzt;q5@*K$gZnfr>QJaZ@#8V%WR4aM_N!+;owLBZ4!@eJQ%r9T$W?G~CA~5M}rZ?_(nsk??cKE?8a9k-vlipMjvsE_IL*L2$faxI6Mjy7{vE%UmnluVMS_cWRCD4W@n7u&82D^-y6>ld^NPT2_>aq2-0MF<)@R+7-7y>3yWolhzUV-q<?^}J}4!vFV4{dA5-so#X3cj0*E#apd>){MF3Z+D`HPuLp<=ZFxVY~#WaeFwWXhv7!z(CbPGOn%;DINb6)vKh2W)teDfx2wMW5FX#`k&dYAExz@f5hzo-Wj#(v6_BRhBpf<n<W@W0nj-c{gM`4Xwm3-I3gH1e?rbe<YrWLaME5?&RtCxxZ5jyo1yq`HPwA|4>7R};6+?ug%n`&E~YZc{3mP;WDnqQ=h9y^1+}}h0X=Y?0NQD}1;Rb3iD~;ksj&0mm8no_j>*&emzkM$vb(N8fg}Q#$$xYy7eYuvIFqVGqk?mFuMAk8*4YXjG$Kr$Pk~rAyoCV8#0dphIcDw$@J;h&N&93FHKtEJ@oXheu30G68OndO%mgib%6C#wDGI=Dz5i&jef!PUxBPSb9!H=M#*Q-|ED4aw67~OoFqDLM;@*Sq4jH~2W1-l&3`4H!y3C1!7ZOr}BLgrqv@nd$MYb82!a74sppK77+@CGweMW^h;;6Vz*|V&<9v7zEYE1)TK~v!PA0>Du9i(a;@)m{d;djvkHUz+k>7J0u6kUzr&g;PhT_&023c4zuGo>794(B^o#gi_zsf(Bmm963ESkJ@nSw~R;*Wpp-xNR#o{el8nIpW7OaagsA39C-|C7p0DOjVpCnj1Np^GX=>_s0b)XFe6I)#uV5`j<MDUQK9K?r+tWeCzhq-lMW#xln5_0+M|nfsYMiRk=EO8`=i0)o8Jh?T+U7Kvtzs)-#NVVWz<Gr5v(o<0erGtLnW!g;wBh)>C_xZaM1wcMr0?#EUV;<Gp<PaO3!F<Q5GP;&2)(yAM~}DgS|LO*zE2>9hrvF92*RUASTw+F>s>E8t*+aqmL+J9l9Zxa@D-4Xou$s$mC-c}w=DR;PdM7^bS+NNKWMAFWHy;921Cp5>wg#c@M*a0T3*qgOEe?atJPSB2l>L2?RHF8)Md4^-??eC7})KpAf`X(j;FP@#uR8zx?6)hx}bf{k!ULDN04e-YW065f_x>14&l+|>_Q<ZFpb2X{D7hWd<LtL|d*(6RK@i5$=_{v3}H>ZkZ}ZkDHW!uh{jtg;TX2XIq-GjRA`yHkLb=Q@wRQbq2V+Z3i$c35d}vU+LsT4x1b1C(Rz;6vudS^5hLImmDCElAfCd41<b_aJ9F#`^&DTd%ow>PW@$a)^)t!)nX<RuQr~;3~GIA}ZHMq0E2#J18S)sE#ILqhcF3#uFz7s4FVUR1QvyKKg8OcIhkbr<0Z<ffrLQ_FBV#Zu;bh7av6+W=fr?y))W2v5XEnY?m(v{mDGmTdXEeN4(9~j`#?{ZzF?%xmW|X&{3iqk#w9D{qePeWE%AZ_b|e5EqFYJwqZEswr9<tAnD8R(Mb?$cuB^+WUPvq{4C)e9PgdQW+Ijwi;~$~^`_Qm)H48L;rMBEeYugK=Q8=_+8PcM*U+#nY2YVjU$>w~xN6yIl!BKW8_>5ZivO|iwwNz1?-GvsvMsDqLCL3jY!h9l)UPDMvlJg7|0xX{6EKnrgOhIkLUx7_Pg<W3rl8;r2eIU{AZLY>TJi4me<hV=?RQGA@G=LXvybEQ$M{xoFQma6!ISW3OLcv@0s-44Nt@Hf9sUiFDb|9{+EKcdCgzTl5K%Cn>lK>UFVJ7f7cg`BUH!&9gpY*PqvaMHk_}TkXp6_9X?h<)mJ-XOFxD)InZq}q<$E>3wbqz|X_ID2fYM-*&U0O%Oy}q!*RKc&mjNfG_9VMJ2K=4g;mu80_4H2@+JieO^)(X>P2HjDvlr)IJa7YwF4eI(a~Ue`DKdg+>-0jgS5@Td2=+VCil7URA(*G4ptinHa5isy2#f*!W_s@pgZ$<kg+2--40RYOdLzVcdA+>G>JID~k4cX85XcQSujSDuhHCNj6)ru~7f{&HMde}C^+=u=P#4{w`S9|lXk6h5_*+H^wK3fUXp#=~$AS@o@NUq3OSvCtQ1_are+!{`jYCxues3Iir^m7lPMrjA@Q4l~HQ4jKwC_FnfeGP)mavgSdmaD=oK1f{zC4u2SweDK*PAjN$l4O5RCwBam2<5Uq?`5~>pGDxi~!`hn5?S}KeR09*#ZMG9mG}5MPa(5X<3QFJO1o!3T~X$ULio&Pd5Q)HR-^b9eXphFk7<iSu@-&lLBB6gduiPd0nttpe5&(&+_7bIH7~C2ul{`oa$ta-JYZ4uPB~^uB&$i0!rk;4)N(WTd|%rSv32meAAf8<C9RdK^NDYA#ESn#CKjHss|iWa~K{{9*S=7w-Bxw@&HM|K=9!TQeQ=C>)w<gW!!5G^<6!HZ5!Fhz$Hbq7B-WF*RC3GBYF;J(dSSH5Bg29g6%aRSG_-puQs*Sh-*s%$yMkDV+QaeRC$PDq<6PVoD`m6(8z&WM<T(;nh1NSyi1M1llp7wHCX|m&GScB2=tTv7#Rj`>)p5HtY;hYSSm0mCa)Mlq!%c^qP(h6ZZkIe>UQ!yp42wz%zfFUBg1JT7gw2Bvb*arJVV1}Gq{~d#x|}5C8&pYCuo4laKq|k?SVkrE+B@`e$!uWT76x(GULN!s54LTQU;(V2;pNZdPHn=Hr=G-miKfdW_rWLTj3~-8BNYitelfJDNhUjwB96FY>9obr$>*eZyp<Jlw*tNLDl&{>x<iSL04^?H6y$OD6--H3zjRQnFq2v3+s|uo2ASf>@&OouR`rjmf5`vpAvQ`l(<7cI|`^AB;*gEfQN|Z)~E+l>+lYjS%ECoMKIRDgx{kyv}4c~pu@Ea(5Rl`bh>k6^}wY0$N&HUD(p!)j`|gR00F~Drl|q|`{^~XvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000005746944984047803679116802106194260980931961105818710236951929941029351531685024826357678383', 'computed_previous': '0.3899999994479954876058851645944667215542113397599142740562988391396291744708064673904448472725693077', 'covered_success': {'lower': '0.3902168927546248272013421441901542415164173564781697128392582850780298174342038839288627531525908798', 'upper': '0.3902168927546248272013421441901542415164173564781697128392582850780298174342038839288627531525908800'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000004334950176598795223981142044067382812499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000004334950176598795223981142044067382812500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002013111010041717163859450775621387379217012401596181929598439799337514501521961258986653638339127387', 'upper': '0.0002013111010041717163859450775621387379217012401596181929598439799337514501521961258986653638339127389'}, 'self_coincidence_F3': {'lower': '0.00001046775269015989070981337693831249424994054655508513559725108101117724764399450771679676989867744292', 'upper': '0.00001046775269015989070981337693831249424994054655508513559725108101117724764399450771679676989867744294'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '7.783760593975268802978857323981297287871606954789386320671365285050818329832419791833830904513924010E-7', 'upper': '7.783760593975268802978857323981297287871606954789386320671365285050818329832419791833830904513924012E-7'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 759, 'HF': 111, 'J': 59289, 'LRC': 37578868218465746492669018171768832, 'Tb': 1325620839056724639014355545949732864, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '1bb25a4f3d291b06392fb4342e41b25c34ccb4dcd128c12884774cc85022f791', 'previous_grid_upper': '0.3899999994479954876058851645944667215542113397599142740562988391396291744708064673904448472725693079', 'round': 11, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 98800, 'union_lower': '0.3900000005746944984047803679116802106194260980931961105818710236951929941029351531685024826357678381'}
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
