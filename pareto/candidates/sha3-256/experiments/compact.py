










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
R=15;S=15736;U=78680;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 603, 'HF': 111, 'J': 74586, 'LRC': 47274493834311359070016552638087168, 'Tb': 1326538090728833141529042052043505664, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 164, 'dp_loop': 420, 'one_dp': 422, 'ctz_0': 429, 'ctz_1': 434, 'ctz_2': 439, 'ctz_3': 444, 'ctz_4': 449, 'ctz_5': 454, 'ctz_6': 459, 'ctz_7': 464, 'record': 467, 'probe': 480, 'insert': 504, 'insert_done': 511, 'match_0': 514, 'match_1': 517, 'match_2': 520, 'match_3': 523, 'match_4': 526, 'restore_after_hit': 529, 'continue': 530, 'deadline': 533, 'restart': 534, 'restart_ok': 537, 'restart_nowrap': 545, 'setwalk': 547, 'setwalk_loop': 552, 'gather': 564, 'gather_loop': 567, 'restore_planes': 577, 'eval_f': 834, 'output_message': 864, 'match': 891, 'measure': 900, 'measured': 908, 'advance_p': 912, 'advance_q': 919, 'advance_q_loop': 921, 'lock': 928, 'lock_loop': 930, 'found': 943, 'replay_fail': 956, 'end': 957};EXPECTED='7a65f3a36da712f53426f912eedbe790e053b5dc22ecc0aa4558fe9a314fe832';NI=957;NB=30624
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(3683110911064695666, 5524110257754215480, 5540121487813319684, 18827079337838596);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5181794358648984391410270064345089)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;IYLhzg++YZ3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<=BS=_3InBAMymZL~kU#%2r-FBka~_Rxu@87*<1YMc+5^l>*|d*jd%Km-pU%z2*9_TGh*g&YF05)cmidPwT@A{*D6XS2A4Zl|@hc1W0Lvu-;7=!13gEEFEgP%lr=EDY3puRek-+dO5x>%--MVUV!iq`$r5l7uTUIhPjgm9T=DNo2-(Dz0BWg=&a}sR{l3@u51Am>Z%1w#p4X3SMFt!+c;2I<%&xRo5t?V?NvY@z10Tczoy;hS(THwtX%0{5bw<CA{gNE1{uvC|6!D?*JM1jZ@yk~P<1Aw`6nQJAIR$?P_S%mq{T@AfHX2k|wS=(k&?m~3pHFy8Tw(bFr5B<K9mm`|AyU!qiKf!PqdE(@%X-W-xo7M9vcRz)p8kGB7W=LtWKBuLkkDyX%Y4+SqbGl(c7WAN5V|{asYvfYoUh@ScM=in3N}FiQw(^COy^pU6i_E?gBPghUQVeqi$19rnxj5!a;F&E~tRKe=Jh%&gKP{hjfRP&zPuLK4PXQtlw4P+T23+3@U>ezy@Mk?3-G=?7C{@?2PBJ*=sOqCMC%ws+@tE@&{oOQZdek{LMd#!M-PTEaR*!IpbK!g}AO$Q4SNo<UDeu$;Y^-abI}q~z9j|7w#QF?{s}?mt=!cHSx<Lc;fcvZ{+G<jqp6lt>zwb4(ahr?V)SgkLDmHO95NY+2;zq8W6RL-uR=)aO1iclqX-1C>xh@VEnSvY2kE-umIiKuiqo=<pEfM})$5ZR9++6#ZNb{D{s{-H@Lb>6o>ucIlA_5ae6$rk=y=cDtcVg;u>6rYnC!3w?t&B;f!w(#?nF7eNTFnoG?cNpv22}mhevej&<;F)|4NQfV@ZR4r8mqIY_7Mo;ZLao&r2z~D)j3HO74G+)A;PIB>W`Mr7!MWcx1P@uZen7pKkP=fZ+smfrll@|4nWob3;Xgg>ceG)wV0e_x`GD-6ettZDFP(pEY?Ba@e2|t)AnRr;{{oE_qs|k`^wp?T)O)+A&*q<lU+2ocUcpgd_JK~squCdoAp45DYVYQcxel^^qti-!x_U8-T=W<52N)cbC<UyPbE09SrTt!$51u_Rsf1blAgo1C1r7Kb^KlumCIFVD~D)C(7aEo?(_c#4lp)gq7aL4Wk&h*F7}C`>gm13RKu$>Sy&v&a4I?aN;<#G{c(W&Lx!ox-@tL`c#IPMl&2Evu({<mk~;nrC-oUBZtZd#P>t7&3Q{!__vhhFq=X@z<l_vn)^LyXk#k(=EhT<eNHR;V3w?VOl6IBlB@=@_i49=4xUc8GXM~r>lmtESv3FmP3gy?y0;55mh%0(@Nt`w=ZN;`qFflobPAt5yti_qS=2AI)m)JL6IVo*E=L7pGGi{lF6u>aC9E>jO&NMRz@~yyb7ysXHl)~22y8~gfb-HGoYS^y@ryAjuUHILr7wAww5rMP)*W{JA&Mk(1<qt3D{!x~lIl=5;4R!izfw8Y3N?Kv?68K{&@?$9e8@wDlke~yg9Vd;9Y?kSkv-klhj(5F!fYUt{5@1R4VNXF5^)XN%t8AOEAFvaIOiEn@khz_Ko{>n#dl_1qo-Er<XlQyu&u0FW<m{Q8J1tXe%$ab#^q_CAEgV3#x_*QB98AN&SXB2OJf3aFjew@&*Fj5LjQ?E1K*=~Ggu0|Sp}_>7cMUc-lUdKs@2Pt>+S;R4AS+8H|H7K*`~dWx@mP;?yfcCAC<yO#5gP8~c8t9YdTtQ7t3X(!2kUFwHb&7UKpT`{&!NqBQ?t)REp09F#_O^8wBo+wxo;*>{(7o0TUBhxp=$RWUif`uI%LTN-?0Lv0`R_Wu&n1wQDD+fDz95cp!(&42Qq-yNxX|al3zaL>Dv%}qilL#Og%YO4gtU&$lfv?=aYvxLXj5no5Z-aN73VgKI`0@J(%lK@0!L*3Ll^V)Z7mu3Z?XNkg)^jKE7N2(_K`O_37G+iK23@=P|1R%0gLme6{)nh<qCN2D{`AkuZ+3#xpn|3jxaBO#)&66?%|c`0h`#OM{~2IgWbmphRbQeU}Kz%5i~zAUg%xm3;f_sT$(_=`<+d0Z|?7R3rhC_l+?-CGP!GdFI_o8w!lXt9Kr;RZ%IQcoRxJr1pmQ#OT+cT(%}uf|nkhV|fXIOz`P!sJ=UW-*G(haqH)w!X9i~=VD<kO3)L$nom{MN|Fn7MLEaAh4ByLJc4H=T|sr1bsY+koz8J;b0}Vgvu@+Sw_o8oE^FP9d?&?Tgl0XgcSEu#j9?V*(VaS&ou;up#)f+RxoBNX!xS_<iQd!L(cakusA2=!^`wXOCEf(T_VHCIS>7M3|J4Ej=Mg;vmm_howjXJFjT_n#`$wY%uAP17o->GDmNBh#Z6^zntbC^-o~e7bBP}UHXFtVu>UV2PP28o7rGqC%8C&<}MYG3hLOC_A?JvdWje;7XG326})9se+On(_k<T`3tqXyjy&SKhKkYa5FLzkqst}HoX8FPpgRh#gX&)EH|!@95Lk~T+W9f|Z0|Km6HO6g*~-4#>|*>BaOj05%AR|GInRZV)g*JM&c&_B9)9Q(k28=K1!$s)wWmDQ@Yx=f&}437icyvTU-lV_}Llt6X}T3=#6=8`nj-6*l&VcQ(CPO=CvRSNaei7OvI!Hy`(2C14%ZoHb}?&0L*l`rzmw@{<fqdQa?&&$m*`GhBpR`=vu__pfnL>oO4KIk+~l0_5naFv>#tI2EWxrQnxN1aT3L9LW<M-&LobdcONql!_TeD3D6y{~}_UEDHqL-qjE&}9wk8fZ9_hoiNN6BIwA<;j{XW3y?)mbU}{#E`b}S9EEdZBT4%{JG92#yT)tHbm>sU-kgIKFGOz0~uVmy9Xll6;hGyevK-%IWs`7v%Vi6_MnyFCf<9)98{nQLID$MfG*g?kF964^ZvG2@?=ux1$NemVSV$~1kL_T2yGBO7w1vzOm@92B-=mb6B8knudQgd0JmNO93Aj&!@^rE+fxQ>4osw*&%aBO4T}?>lYmH;N<gb0%{b}EjJi*iNTT5V0-k`pwS;6nNDKXJ!LB^A7AH&iwe=5<P^e*VNdY@{P{DnXm870je^NEbV~az90~%w-K~&<XE(AANxAb~UoH(J((vI)pUNa1HD9Nszxs=H!#dD=x-&z(aeRS?e2P!j&iZd-bxrhZ{+sncuYWNzRc(%9CN1p#+E&}~=w&NMAPYPFR#a6u1?X5{ch%ZnPyw;N~75A(K6<n{s#mEh6sO#0RsNBp7%s~-Aetiok$ci74zp$*>4XUt<MAbioj-wEtETn+DTFH0{>wQo@bnu|VCI06m^6pEHeBICMni+0D4*6(B%2nA)Cdpr}o+*g4_b?q+*xkg3YWR?k<5q6ooYdWK5#bbpw_iRZjLl0ud)Fs`toY3@k&ed}zr-9=#mxmzNm`6R{uKe3=NLMJ_{v;Ig2yL9i@0j9NY5ofksTnt2Z~{PCAk-O+Q-Y&c2nhxO3J{M?LeU@wkK(G2v$m)#f2TP(K<?T*U5O5!V-5k%~z~inqE=Hc*FQUa5#%wCnrTWh9vU%sEDPU>BrN?!>3WCehvWg8NaCbM)q+baObRKf)GmiP;%5F{3~j8yQX1G<BI@s%5#1T0)(=xBbHL&)jHV4Wnnf{=67SPYOLWWU<m!O=cq4X(_^u=u~BzDiT{{9#-!ex6C8cP==|axEeqbvN1MJGK;C3T?@mnVU|-(%dg4AAJk9TSEpGAS!K|je>65NcTf8l7my&yat#CrtRi)&gIZ#mWWksdrd$W+Qhb5nABt(@Ph7y|bsId4%H<``Iob%Y97t43b&Vt|aIBgr~<^z>`_3@*%h0kn;ZN@*Rz&LCZM8mF-x^0Y3f(2_~<KDfGFe-gJ*Qf4|{LpnkA~H14SbqguhvmU43{GmjgQDn{KP;vyDv+`lEib~*>3yv#TLG#g;?LBQ)`T&TgD|EK%osqrKYYiBb74|~zRKKqlTN@HAG>!^)>mm8bv3q_vU*6?-_EKmtw`==DiB=I3rGsUNtj!{8phQ<0_bQYz3}-1O<xvEh9VAdEj<JOFEBdVwlb@@2N5w(^O_&1FV6icLuu1<SNa7$rs6fw+qM752kbjnSgRpxz?)_}`*xv)hc9gSs^%pI+*^9>0pE1}6ETpj*^!P|Qv%*9Mbh(rm9hatyuKR0*<Q&Tg_)+tCb_19LMH-%yz1qqTCaEcln3^Dn`Ac`iMhAJ=2MwENAHP*DvZtaOQPu~*kh?&X73GnTU@Swf-iyY<Vk_kz{W!FCA7|u=A4XuL#{_Sh@#<1-xnOHt`qezxiEG+^^#)Dzc)V$siyDamr10C^3@R_721GV@uq5hO`9gE_Q+_}71=H;ZfMS@MDK#5Y`o6x+HmHGAUVS!s{T5=JucS!8=9_2>-t~G)g%C{;K$vsc<<Mbo{xiIC71Zp=r;6!*Q8iL-d>e;d2MeZmGYz-sOp9`FoA2-;aE5Z=6D93zUE2pLO;&Lt$%@vX1>oB5s&cwQQR$M@;J1pk?U~0G^OShK4e0`mW}%vR{f2!JB+{V&n&X>v*0nm1zTu>?B@T#q+6jZRuc8)1V6|v_UMFSJLgB4prV8~J{X5K8Yc}#(|cS%8@0&n+hHt;xL8MM^@d<uHrL@&U>B0dV-^3d0$ua;z-D$vsQx<l5NqdR1=O>U#AjDU{_6K6o~|Nj=qJFr1o?iDvSTBVt+}ULuNc<IcA7sJkSv}?b=PrYf}A+4gb7~Mrl|aqODw8PLsj+u8BFDlK)2T?zJ&B})^aNq_y6<_n_%lUEq*idDLdMmULmJG6q9yDU}tux))i?qwM9X~64$Fq$3ob@wlG!l6M`hhzZlz~mKN94S^Pf?SLyWYv1!1mLpqag3y|_#KLfR26z&uT(JXIc#d-p{8;9NRzezu=<QVQDoDn~cQc)W<`F<e*AR)k+Bztp(KybmO&!tq?aA&blC@-Fbbq1JP2#Qekf^SfpIp*vc)a0^eBKX(8$yE9eC+<#pS3$JPy|N2fxnQY%Afi>)gF_D`V11{&XsmqX8GO)c-r&O1)?V3{mJ9eHP%!MZti#HUbp(s*>dW~7i$1QHaL=zSDt8Tx5f7~1xFbvZ(#&Zv=yw@nAwhX_(H!oeGHiX<#`HJ;;|KlU<V5O}8l4;-)7m&vTMAI|mXW_uz3B=RjcQHZD>FFgY}oH{QR2c4(OAb>r2!g)TvZBSC&hx1`WaDqjtLEI`dZMmuX5!78zvDjYLJ?>s;Hy47`kW_HXHg(+4TNTFM^Arcj2Z5{22!2o^RVvv>Xm6PJ;9%a*B3`>t9o|+E8w#&rX39Cx{61DthHEF>~zBrpc_I-=|^xd=nsSJU-R|5!^?{Y+|fRy7y_S0JfnHWlumY<%(R|+Jq=@pr1S8z0vurcQ5T%Nz6?QJT_L;9N0km)y4~3^$7L1t@)4TlHd_@9tBQR<_~*~{bw-&n6|+rsbM@ymY9&eV6QQ>o{e;Nn^z{(u^`|ZY*#2oB2|@_f#6nT5He&^BBa?c8orsLm}<m1zD1dFUE%bU^l{yf%MrzQ_V`?ZG?~QD?sZ73Gy9m$JU4smE~Y5>FSxuD)@<WdsFNr0t_bS(iV-5Z>=UP!_^{H_qkby5IH}>k?%~meMH6>$k>blLc<I-dQv(J*1QQYKDLI+X$TU6j;vQ7GezUvf^q(rXXk<|2oPWT1-??B0y<FE;e#uv~MvgwRr!l~PqIM=hs)OtA{B(M=fg7Gra)gz_mzu7tt93`4`3{KUrkMemZoRUp3;CXozh+Pd`LRFNkDWm3m8rjzg$G5sNFulp$w|+=wr^X8*dF_pRom-QNzw4`#DJBNdiH};9DmfiN%V%F_SnuwzD~bKIEAvZDB+w%UqISOKu9zWdjUAWezbiHTH5?mNoy4%t~I6=`7Cdt6&1eGZx0q!UD*dD%<@fHl~Ug8nMfX`^s1Bv)NFd9ST#z-#k43(5g~Tu4kLY7IyJU4H5ucf6&zVt87P)+phIozJsU=YXqIr7M_`)Dh6;;zRY29Gfkq-x9xQjw<W`f+s6*<_OoT*jmx;h*+6ZIgRkncUT*~`_d7SyQ(SrU9YX)6#wa1%)>VE7EVt+y2P;Ko%<5u#^kK2|9oh$1C7SgQ$bRM)~uZx_l@|--24Di$WT-7hY{kaB_1*9!8FjSyY;bqo)Au$t!wYa*&c-=yc8fQ4ae=mQ3rmS9MdJlfNy);LSWG%&=0c{jYiqWx1mhiS_2NNR?HB_C$<iGwo(&~985;pCj+rUKR(HOOz@Q6A&al6l(WM2WM+?KW=K0!18e`c7q!{}Aksm}*TvC~Pt6k0F6&%C1D<|lks;Jb%&_X;~qVA4uITu_e`&xHa!JG(ADKO8VKA*I7e{ax_I1gc5FRx)}n4h4nnu`lk*G#@=7x9`akbUnZseoIVqH6aXLus7w=9C4nJdIx1!h&64Ru0@s`f}=EYKw;m01TyT@?5Q$W&k<z<4O~#svN%SEuPj27b?F?ix6QieQYv85>p;C}*0yRgnr0Z)Ojzd`Xe(@8t4H#J>>wruPt?H9jGtPtM<x64=CTIz4d##mhiSQ&^dOgaonYuEf0e_-%i$M`gB{uBVdDdT+#2x7_)@dQ(i7oh=WVRv!xWt0_=eyvNE|%9&DbcwiDfq&9AH-io0l(q)_1h&*n8}!>gAta@>kY%bfY0w>O<RPl@_ADRg@193@~TVSUJOG2RMz&5KizotX*+<A3q47GSLHFO^nU3UoxVV;YoZo+eeZ<Ic8w*NufzbO(NM39%wjw#jy~JZSfwj^=b&7iWqOB<Qh(=$_qGLea&6B8X|wO>E4c9156B;v<Q%8zfeKdkBdQC`bNL^^;LFe>jf%U&>p}@UuPetSvGn=m|bowDEXh-RFePA70*gcl3w*uY)SkarL&fNkQQXGDj2*-=SrKan%gMyJj@jF6*F<P@*u+i2S(<T7Zk+*NkMy%bqfwePFcafFqcE#SonO6WJNHE>4?sO>|t-f!w<PCUK$;zXC~<P9ngv%r-o#*hva^npX$~YvvI%VHaIngKdk{|)4qOJ`9T59^yVt73;q${KLq~-spc?i5Yz_rIV_v2-dt+aS0O}ksRsSp&b?q#Rl@~^B2vEw4v6Ab&6#2I(Aw&T;pKq<j4upRh$N!hb?jdoR`qtqW|S{IH5u~P@aHeZIWwpj3=cZ*Uh(5?yl$`GJjiGGe+9~PyMUpUCV;-sF?Nn!4n@9?DUOX|u5hIpUY0~SMH?sZz*0l%;t&O$vujA6$Wg!-bL~<al@VPJ*!qZUDO1AgeL;V0H<~#@%0aa2`eBKp-^rE!5<|#uw}!75o)B5+%3dDI(*w;-SLmDROv%{gD#!$R=)4q<fBDKV&oBRtodcN@$2?ONRg@zp!Z>Qh<RD%w+q4~nFf2ua63<#M^iu^2=rmB3F;kzsFPn?^4k)LC#{#sj^n~+t$b5yd9oD<X20FWpoG*{Z`{6%I*kRl(GBZuh6E+BbZD(2pC($svD@XqyLP{#Ax>TNL+BWsh%I!Rkk>Uit%Hag44vQZQuU38-=7H&Dex>}A1ADz*l8c#_FJ*+VInlN#;MN{{AtnZ<8d_ryP|D%BrHmJHN~bpDjAL2&;bdX~%H_-zLsklwoyG6WjHt$-AO`nXKdFbV?Zvm*!m(>eI6)}E?so-+j9<SpSrTZ|S`Y%Mkb2y%6a3*VR4{*ktYRXu<+&2K1gEBPOpvD!(gfxXlneAGG`)eEAls0IX~dxrG?KN&@i@2!Ct#nM@O~JP!G;j!BO}icMrb(&&0yI9-<inpAT5td12x2`D34zjYbqJL3*VM98nm~<up=F=d`RY2{w-9D!nrAl@yq*1)v)_ASRnKtH_~AXqxr35)d5W*Gac&QTkf{p>*6uH0O9~N`M9Gy1|V7993kwWCLwxe6QLUQu&jGKkCt1}<?iZ}%(Q(}MfSAmt3axm>5G~MBTrQpA0g_sqV3_SdZ?8aTMGyNSNF~A(R;qJEs#|v1V(!c0dw-X3{~G4pOsJ@!o^P2F%{Jz@nE1+ZdXh6;+fV}fZU)z<S*dDa@RV|b4Nc014kB$JA)e0)*N;bcecB_*lx+_d<6GaR?HvP(hxT1CUrH{%W(s}zR4<@6+5u?5U*w##6e??W^nm)Dn?{gZsY>sf;aw|Bg?Pb(W**Xz3I(owCKe&vbvQZ3D3pq{k(~@q1{oJl}<u999f8Q1L=ITdQ-0U65=?<SLl9o1T}>-ErwDJnCnIbP`+r{Sdn_blC<~k`IlwRJAn?h;Zr&{{o-ba`0BL<BNMvaZrbosFb!VIRpq&jn*#{szqqbE;pWKA#4+LvAe?u?tX?|6Ym(GNu1R$B4Y`qce@?g_`@SRn7Qi{?+nlzd3+N`kY2|`~HhpzPi)qJzfmw$b&U_^N{cL4g3rS&8Yui%v)<OT-i51GAkl2nZ*?&?ys!(cj?Fw4hEP96sXGnW%M(9d1v7+*&lxkjb521K*PomKW>$IVlR_unUZAg{-MX>wjm3t%S)vncf>WiVKj2el0(12agtHL(@-f)Q7#&c9FgAtezz9%X*xpB;o2S{Ax_q4YV<RScO&gZ*8#{@b&B{MCnmV1e<bcE;$p<a~z<4}0O(v0PGsKHI<t`UVY)~4;@Q=JSDM92){`&aI-DX#+(;fr-yHPy78#nO=wRiRO#33@=tK3i~VKx_<e-%CJawoutVrZXp)AnT{-3{Il?77ArQ+sLnP3vex!La4KYDuGQy-1$0l8+ooZiOD#wHeOYg(CnXL>0}i<{}<ppGvt#)u6?Syj#W3J9rc}l8*Sg2i}f~n@yez?Yc=+_>}uri7TzZ~f{QQk+SG6}yM=}<1i!|Z2GQ-`UhB2-VE~QJkD#nQZg9fOt_wQ>UHoU*iEN7<B(&X_i|n4s_|b}MiQ3xBR@#G8i?)jyoL_y~xm;(ds?$f#H3Ko>erAL1qkBtriHOb3$J0!(vkF{jvE3qC-=*4ng4L1&jQ&bo{Ik#(f7`Ugc;Ud%mRnD0#5pq9p6TH{M0M8zn15qBUC(A~uL5yNgpuRIIT8=T=XMaF88xB{m#AZ7>J_*I2iobpolr7qszux|2NWrsK(t}<eo5)%gXw-*;S{D~g5Y#f6;H=3LG{TOgtqX=9Y^t%@C?<l3zp+XDyuf*vHNlghz4M#4**E1Si4<0r^ql#WdKZfG)kxtxGj%^SEdFm-1pOO{G3zlxM=mz+giLYR#CyBxx7K~P)8OJ>yWbyr<?SB?4^MwT-vV<$YnPQ&i4hxk&4&E7C^ei=u_)_SJ6^!T9dM5NAQ5p<46liekDV^XnvXjSE>9_YXeQGSs|>>t&yMS+8kUwWV}p3Uu@7%8_;&}Oo}I4!1SIKz?ACx`i-Iz>=4H7f8hx+rscQWh8&@+&ox#Vw!7kg5@9S0<7bZfu14&n0`$S{N?>xjLIT;)0rK%C#leQ{YO*AcK_>xSLx%H0OnY4o)1A-d&2_;mkZ|Y#1PhxImX&pM_All<A@lwj(5L_dIf)*C<tWE5S>=1;=I?V8^w(q7{arP^beP?Sm<c@Ys6pa3&^yhXC1*Opdc6MZeT88!uM?2~^o;p0t?8v4;hRKe2{W*;>+491tE_Mh@xdf8h-o}(c(emzQwj)W8Jl->%TXf!wF*^rG<ci9;xIH3T$-_i(lor@ES5rn^KK~mh}&2cMC3C;8y&Dj+5wQrN+$z0fDd15$YswnNM}5}P8TxfjK1v5(=R2Z;<O|)7Weam+cAM@Ug;RXkRN*D4z7TVYk?TsDrrlnZfIFPzrUkQ8fcnkDAU<Pgfn6EUF5184&nSQto|SyDFH{20=0*0BI{!=VSGf>1BWy|R&*XHC5P=KWxNNaiWKhM>_5n<BUTFSwZ(>w$3&xS;$19V*xa%?117BBqht5xTO@NGc7i2=eitR~K|<Y)9p(`jc;iX#8o~_wgZ%#+Cd7kl)yMMT&YN?Vr1JeeB=C@G%U$}2|E`}e0Cc&Mzfs%fChp#q;UEIZ6Vd0&<raIsmDxZkL7DKBawfwQtS!ByW&XX^#NK3LP9>RfgyvKgU?$o9nD|mUjgC<S4kkV(rM2xu8)0}r_jqh=nBWo8%%QKx9UHu-^orWnUrnMB`dJxGl8=A+F}RC9DUUIPpQ3)oCw6_90GUkU=|7}%_-|Z@bn)60@n!cZi=r@&+*MBOR^qNuc9=WYk{g`_#&eJ};z<y^XhWgGr;2K5KFjF(qDlqwfv7Cfro4sF|1DV6S$?{8GpZ83TvAe>FIFf#t9apFR30ZI3TVa)S#$K-4(;aXkB&e4^}x>@I#<Vz_#|Sv^_(SRL=8w_APIX73;kRy5Od{HA%lR&7JILhUy}o^l#@#P^~3L4b*apPuX#;>s}DA?rBPWkRBz~Bf@;S_YGS`VL2{-frPGMuFHXJ$*@%))#p_GZ4%;#g7TN9SrdW6EL%OEiBcQ+nuc0z(M?6(|bnQ1zcubpJ@KJlHEUvkC!SIO~icLJPzH>TlJK3^G<iO$BUP2A6O=8MOiRua#U%Y7b-+Pq|blkjB28s3nm;0w-9RAcW*@UI@kNl*c_dOVa%n#jfxnd;Sa3dwpG$D|Bu7VTPrwXb7p{I!(dEmj0XZF&6GOrhmqe&K2oJE_e^l44K&!{mKlJ(uUBn#3xFq2uVCH82WBG!2!#qRm;Zy$+Yi8S089T4l8vyv^XEU2lytD5AjP&NJ`qrN*3xJA{A?9Y0Wf+Mj;ZMrB?gX3w2ZGH=soLzD@s(>O_7K?h0b(X^>e72m(%HSP{zsJ8Wr?0y;H2=3H+!A<qMDR_fk60^?hgd9qQDL}t(1&{6oB?jnR{Z@psg8wZh}ymXr2S?iBcuQ(DDPB};PInbkqeN*9|)z2GIpE)xHPp|2o%rHV{7GOblD%~V7Mn~<62Z=>)Y*$2$08v+XCF7+n9rSR3~aX4~@4OypZaWC)6N<vI=n2{r-CVzKR%bQHjawb*U^OQ6TIwatswFD@a(uHD<#CZY;)D-c)GMcK%bvWm~S4(sZ$i;52hl0`*`@F6Rtxgub&ueTTpKLY_DHdm`@1-BC)Y%)8x7nbgqd`%i#9KC1muVet!>8O!o@A%@$GdN!0V<{4;uF2rmKLP=XUjSdh;5yhfWT~Z^c=Vh_)tW`x8#)!Upyf}NR)L6#30Q1U-HvZ+6Cu#bZHcg`bV&i`v*fto`0NziPQ0I*`lt3-PdEbOmdVmccx1I>0$Be)Q7B0dwzTa<H3wO@)VV1uqb-$frB!r~3syha(OKw2}+X_}oHAQ(P5A4SZp0Mc^nKSL?JC5ih7B>)_8fzV<*tg28DohTs$o)~=lY2$YOq?u-+ZiFh7g}T<hE3H2jR771kzu()Fl}$mv~mWb;+m{5+c9f$;Ai7biCYC>@m91FvW;cPDmyg^$)c>kgnU_qQWv#YfBm6N77Qw<*~W_G3Y9<@>_9;m)nSjGNOW@y^<X-b$a8cHwDKp*-GY+Yh4f94q&q9f8epcLK|6Hpc{S_7h0SyHkLb@)TLhdnZnG%7O;A^{<usg)TOL|d=rXVFHwN1PgfcO^;f}tgwD`qi^vh<`RVV<wE@6R?CWue06!bTUjR=}f$bDg-yfDe0CTu!nHZE?GIY4jSa}sryidRi@UQmcae8U^M1q#tu(*Fzd;X~Mhe}q5ZFxgZ{3NFvJkf1XWHJpghI0ZX6u*HC#l}k!DN4mlUWviB})xwc!W|q=C@758YMnP{EUAut&OJCBkR|U%v&0Y>8jv^8mE1^EWtMiyx!uE_M{IigEZ7)Cya5`<w=E=;)JzOH#)8(jBv$wQLxxa0X5^z&r36lA+y*TDOCggSfhZD7V$gOKgC+&%2<ZP*CPR1NUveco5m%$Zi^uwx%rfH|;f-A;GOM>Yh6*?ku{>itEjXvf%>?9b&4FinWqr==BXU(p%Hl%B_e|$rPrncW@s+Iu2vFbAZ4v~kbWb~fbt3>jfA+!ItP8o|7Qflm0AX}9~l4<M{KFN#eFNLR%0A!5snhp7TO~iZ|r9(}F`1PDH#*|9_)7sP+1h&XPe=#wjf~6!7ko&S|mx!y-+bsHwIvx;0-N+(S9WE4>vo2YY`($O+r4`ix97NGUD*Uz7E@mqvv4AUQS-4S2X2H+8Z2F`hOG`d9tTm%os()iQ$2Ct9lM~0M_9=d5sTJ2Gr=aA=Zko`O$>GP7&_@vt+f?Kv9kX^B&)~K0?N8H79nB|SP(AI<wdQ{%ks5(aSPW0T$679sB;=hMdp+~Rnt8E{{6ql!5O@-P-$oSZ&EuRM@CZ-prC);)!6Mo}zKHe$eu&9&1xr%;g`R+V+Bue8lC{^f@&}VrTRqJam#7h^7FJd)StaC91vj|fEH68dACn`&`;TJu(Cr~Jp^6l)`2p#CzUiJOczE(IhZ_R|znm)GC&~u1E02s}P_=iW9K4D6CUXB+5@|!urQosmM7UUEg?OXObMZjYr-iXhujrM}=2+UYFPi3OzMuxic}ip5rea_hon3T$9+-RHnSw{Z2EdJ50p)a<0bx#KD)QUO$;XPl*ijFW@<cL6!VKbQt&tmh;ycW>e)ZjgT;LVwk3zd6NB$_<95+cPMoky|#33T&CFmyhkJL-DCEQ-KwcSS_ya?%ln8#0e8ilu7l{>X?r9WZhVvKBjWg4I%42|-IrPC=csvkPsuT58&h^wHrQy39|2?-x=;rZD13tJqSKv&WULU1mq_8~<%e?T^c%RYW)H;|0>XShfUkl*i%#}y2%%-@OZnD}K$*6x=m9LbGJ@1Z9^D6`YViEkXYO3Jr29mb{G<msA-P&-*R@0G^c5$p;WvqY9kZcgE_vtqI^zHllQLDBPOq!s9#uW~at#pY~d|IS=G3ntyLCEOQhnUe?~aT>YB376%j5<@DBd7auS|1fZBq>QFGYMy+hxZLa2H^yjTDcFsXZ^YW%vsoz04}F2gw7!}>e!KgKo#taeX!R)3nU%SDyi<J<TR#LV<r8FjK4{0$0pa5XBcfyKY0>l9Uwe0)P)QPo`I>=2jJcl%>k}rko=uCgdNaZeS?)Xj0Fd5HLE?shpvk}rAsqjetxxMh98kOfaTxntFJr!We2Cv35_eJ2Ug3NK4U8;6ag&NAtI>s?D(4q6gt-YZbIbq$W0i1uv;p4N00G-k#^VA2>tkzlvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000006553047590082088201845808269946262354047882280999049646908117207671421006378873383935949949', 'computed_previous': '0.3899999995351906720733774390472236358114526246610642810986618013598713992828293917647595407902733397', 'covered_success': {'lower': '0.3902220321579504716216330651345778176530730253800149369450882232232050906656937872553240226753409154', 'upper': '0.3902220321579504716216330651345778176530730253800149369450882232232050906656937872553240226753409156'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000002749153082959310268051922321319580078124999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000002749153082959310268051922321319580078125000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002026275818926735264675267419159751658475001566625383086099799092105215078327656352686562189337083603', 'upper': '0.0002026275818926735264675267419159751658475001566625383086099799092105215078327656352686562189337083605'}, 'self_coincidence_F3': {'lower': '0.00001320717059739995434656457898456858878630616953925782915164366118550420919174167856131173870833780241', 'upper': '0.00001320717059739995434656457898456858878630616953925782915164366118550420919174167856131173870833780243'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000003447597072678954980362910578013171456529211461492717223535776633954629887622418841091324103874409945', 'upper': '0.000003447597072678954980362910578013171456529211461492717223535776633954629887622418841091324103874409947'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 603, 'HF': 111, 'J': 74586, 'LRC': 47274493834311359070016552638087168, 'Tb': 1326538090728833141529042052043505664, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '93c504e7e8c97da258b646915665ebb29d66a0544a5b7f095c870d05bf52102f', 'previous_grid_upper': '0.3899999995351906720733774390472236358114526246610642810986618013598713992828293917647595407902733399', 'round': 15, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 78680, 'union_lower': '0.3900000006553047590082088201845808269946262354047882280999049646908117207671421006378873383935949947'}
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
