










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
R=16;S=14736;U=73680;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 564, 'HF': 111, 'J': 79733, 'LRC': 50536792653998707434768318337122304, 'Tb': 1326843522722965866262746813366796288, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 156, 'dp_loop': 412, 'one_dp': 414, 'ctz_0': 421, 'ctz_1': 426, 'ctz_2': 431, 'ctz_3': 436, 'ctz_4': 441, 'ctz_5': 446, 'ctz_6': 451, 'ctz_7': 456, 'record': 459, 'probe': 472, 'insert': 496, 'insert_done': 503, 'match_0': 506, 'match_1': 509, 'match_2': 512, 'match_3': 515, 'match_4': 518, 'restore_after_hit': 521, 'continue': 522, 'deadline': 525, 'restart': 526, 'restart_ok': 529, 'restart_nowrap': 537, 'setwalk': 539, 'setwalk_loop': 544, 'gather': 556, 'gather_loop': 559, 'restore_planes': 569, 'eval_f': 826, 'output_message': 856, 'match': 883, 'measure': 892, 'measured': 900, 'advance_p': 904, 'advance_q': 911, 'advance_q_loop': 913, 'lock': 920, 'lock_loop': 922, 'found': 935, 'replay_fail': 948, 'end': 949};EXPECTED='c9b699fef75cb095ea0cdeda004d9df2471aca222bc577d86bfb6ac2da72640d';NI=949;NB=30368
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(5380962625456677870, 9154425112208607667, 4418870163701554226, 599104096108074016);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5182987453513888191983819996266497)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;JFPc-dz9%Z3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<=Gz}K4O4eujMgJ+D0u+d8cyIi8Zu)*ea`x#^<DoqXCIy0v^Ka7MY&&o&%^92fHt>HEuchzRmdpQ@67+D+RQ5+Qsgs6dQ+-s!XQC5*^OV@hl1FV+W!tHE_^2x_KeX5#8l>Ohw~&EQ)F(YKAkq-IP9&OgWMjU1NSe7kPMFk6kHT_vLdlmG4}*@qBLJ5gPvjEC)`6<sodEs)AD%y(W@Y}@1q3X5tivG9Gh&fmW=ng(=Tx3tJPdYgihBm~aU;<OLN&2Kgg<GCy8Y-9R_`iS+s=iq-;A0?6fq-T#l<4k_O{+`z7*EWHHuz_pdW7-L!gP;KI`!IbQ_uE2lN{BW0MFfmA3KP#zjjLd{#lVo>X(;%}Wb*&Z2}RwN5&tv-^#2SIOsFAn1N3y#^=6Yr_nR=(E*A)VHZ!>)3kfS$PQjbbwB8@XOYsOWGXq*m_<`b`sCC^s$!sOa^6F35Zk$hZJJ?W;%537SeqD7Cw!<R~aN8Xquh5)&Ae$K$@d-jMj&s%@)C8Gkmls3R$>XH*a|MP*`xdzlsmwGcA2r77|J<j#6@*8{W`;;pA<Qy#D^UZ4dZj&S+OF>LW5{k7u`yWVsj69F}g(EiMy_$b}D8TF%D~AnLGBKEy_<p<{$tB=HAnH&wbK6gUb>njElT_=eYu##tYd^8V^Z-GeD1oF!hU#79~TIJDLjp{CD}tLIw}zyfm_MS+g~#hDm~eq+f7-_BHh;;PK);U8Uj$!C(&F!QVC*r*NnYXK{S)|Kh{b-6<deE4u>vP(I3;SWV%;iO}u^Qn!wqsxHbhCU*r8Dk(s`hXq)gp;BKx3yQl+_RojXlja7S{k>;y`O3sst9W5_q<oERXsBE$d9QvhKUCcJPnB%IFM7!1OwXf^c~iQ!H}b!iubNBh@+ucv}iI;?mrS#aAJ-Ogy#)q13-Q`1ZJB?pH!P>aK<!p{0!9UDWRn$VrX^#g~R_CV>LLc6o&i*DvdRspNw(}rErN2ayibdwHKV?QcS}ww}^|Fu%OX!GLyH>NV^0?Y9%y}CuS-W{><F5f*ZWg<BA%umW#qrN1jO1XRGZadz2$p?2O>tkwY0773nw?>!w&o0`6?KCgE5b{E%amlfz0%UM(eDTN}-%(n*1qtW>Dry!#~o3jIM?D4u@n<oH``Chv1%9J@lTr&>#&@oJK9LsdVzSXq_Ty9O|Hc7R(BNj!QrYew1iB4!4>-BM{5WE-r8692v)K9puCYik7MuK3XmqTv7+KRw<1ImkosOPzxMB>uu+{mNcS*qm=D_$3sC<6&O`D60$KN|}<K>?s_T%A7j)P?L%gWUz=Pq8N7S9D_W2a0{jN{mF)3zn)+0;tQaiOifR&QuO3j5INL71=pxLVYbOWFL<?~3CA49H>kKy6GaJ|FGc@uD6sP4e$nTy6X<?iplO%ChbUb8Gm$`Gu<(Tr&n*6*Ku_??-G^_+&8e~2%E=r6!(>VVGKwUs{G{XRVzEnbcU$|a_m&>4vlX;w&LR|9BxI1p$$Z+s_cXB)e)cT#2KWfoR6%*ye@UhwYcMh%TELr-!=Z?0l1_YVzizy_mXeWXLi|HG4Ayd@s<-Et%^996LcMDzheT2TA|V>Qld~c%hSU0l8Ceyk&N+ElBaGoCm%hKu)n`rzwn!fU!Lf}M4@95^X>QCzlQ4a}u{z(Jx?hnjowMPJj{g_+a&gS#LX{dsD^@Z{0<w#NrC1V?T~zBl3S*gm^Cy!5kr_IPs)YteE=iwg-ASxdLbwJ<9gT>KYE$*zzxHbG6wc#r*6s*;ft*I{`g-|70*SXL3(0M?0FRJ^EI%~1sn8>t+yd3d04M#m=4?|ylsHCno_J`DASET7K@7(=nQT?_9{Gr*;A7W@Xj1wR`~Jw5w-majnQ!fm>?Vx@fAZ#!S@y>#F%k;38&6vP)%7-j*d;PRs7SME&`Az@&sE_<!6jL+#04++BTBgRTtuH2f-r%!r^*U>VG9(%fWkFNxTnp4C!6Yu;X!l*<{vnYf4ZArIG+)gll*WNU6MaMvp>zgGbhHkAt<SMDPm>nYp1)^X!CSX0l(}pT5hS#Wp5W{?A99h=%S->8Ei2i8ufi=Q`h=1{Jx5FC~RH5i_19lhuf^VkmRp01hQc}#8>kXBtu1`jVpZNTJiMixuQ4_kk^XPvu~{_v;6K(sT-!;aKN7gkzgL{h#aycKcMygy;{z%N$&`ox9^6-*M#{5Vlzy^+aHP<1!U;K`B;!gOBc4x8?-olaYG&uY;dbNl2fW!?7i;ekPVOiuef3V`IyB2GAkmQlZ#_%=^<yoo>Y^Aq4fCoN0_<zFkCYnlQ5RC+kx)UEHC`o46Z|On4Its*^fu(nQ)rYcr34&ydZ`)5we+gPzH+?_OSVB6_~@p++gQ7D5U=e5PuUJc}8%`;uwZRYQ3@%V^V=1!*o;fY>lVEZ|qV|5>DRQ%HiSkId-)gc0=g~-<e;)rUr6A+u~l~w#BRy{$qmDPXnh?=FBT}rdB>GpzwRNU?{g!sz;m>hk6z`bTuu8(XiNgoZvOJoOVmK&oRn<3{V2PX*{x8vu=@twMUeF#+{uBJN~)wc0H5o<>V)gHO`aFu`T=dLBlbQDXF$S_FrQz^_f;R!A0qV)o7i$isjsQ`vo#YUNPkmNrS9owm?c*w;FrmY^MMZ@+o1InN`_`JPyF#lL8^^jeKMo)A{W}8|k2WuWa!KdGxz&Mv61;2mBD%aodQ?m=;{2GO^W>WAOBt%N#GKWKnmj)Yh^~R{CTw(P8wl0Da9-iybwibBe?TicuC%&;npzVp|aOMK*V8p><_a6=ARqz$d0TIM~_<@tGFr=P+m66&bexpsgd-o2p}!mHcy8I6t;(A&PXTxg<&EKa+4tJU?KdrJSQv3>GTVrQ{}{K#J0@z*=mBttslKe`Tag{lJVrMT@-oPKCLl^Eu$F>3MP4kF5_skNr#q-U#(b+@J~M`;yHNery6^oV>Hkq0*plB14f*wzv#}c7e-|v(_~wHj-E8OcK44+yTAN<pI>)Q4tglmitCglB_jIKDiq!%avNHpHK)$^rkiEL*cDyRInjU#rP+T7Ca|V{3#Pa%&QY)c_jhRk}zuTtR=xVp_P-GPy9uX!TWpV)eecG!1jiH-PM?Y3574L7tE%~wBD+sRU+0UQi^f$6polyuI<#~$_W-#Apf`@!N3mWYnjOq@gF+9(dA>G%eVz$@)ZtCO7O%9qC1$RUiKG9r&!bZ(V9hdOe<oH*v4B)2;LX=Y%ovHpRFYKD#AyM25JmvV*O(>9n`k6?>UY+fO9`iHi_?pZLQWAP(kAEC6iA6mSo_p*Zhn*NJwPv@qO`+TxDdhNQ%Y5d^6_Qw!^eJzO{XE!K!CVA19(eb7R(chp;|3gg5ZHT*SfNql)z&0)e0^gp>BX=GHk9?SiSpq8NN2{?E3h?(a+XVY!d-s%2SO;zH_WU7K9ts+j?Ivl53x&Hpe0L0Ku$=jrWyCaKF9%-$;h`RAANBX6pMTD?9xPxDt25%?^BnUB+-{4s&8C}cSFeTE4*BQXd5lH~@G=-!W1r%u)S|4_()MT+;z2d*z5I2i{A*{FOd%YXVmE}A$Dyr<h5g<ejKk6ctapnUaqQ8KEo{L>yQ5V5tHoFF~lPOf~L1anl<XLedChyq0~BXCeNoqd6z<`Ui-x?1=gB9!P#9G*tKyU_4*I!VDM`EBVre8<lKE-clPjcFn$io3d^XoXnS`o19YD{izfe#vq@kCgSl>jByeIMnipbS}O^<m;=s5glPmYAu=*GqqNW?$<QJAud>D+~2VHtN<l_l^0rLx#j0c>Eh4<4kynmmZ=L#kKRv*<}<TIMqa4Zp=n8O+eYW8s;j&2S|QbapVYUYrKF@C%g{<3=N_ROXn?@`o;-Z@=Hy=dmMJ31fz7_%MI6~S-m}{w7k7j((L{qB<97G&$b}x<Y29=K3oX1C?%FN$b#{{$fU}h1&8=K18)g0*%t;sb&F|nv1}A7I?n44C{TeS2XhAnB5gq@{^Tb2X`<;~uhX?#$vlL?5R<fK>0YardmNK;2?+k3xCGt)KvknS0%m+ZrWnB|%7KOZYGt75Q3$I5cCehUJ=<ehepI+HLth+#8#CXgMMPIPAb0}g3r|XTgCuBzc_(6Ntv2!-|d%yuG*CPb4_@FV>*>=-nf1!4*ny}fp+PZ{!Duj)GIC0zM$u;1kJxDiXR4V$ui(H$#K{w|^F9Q#$L@LZYC&G7%QJ@P@OuHW9CfeN}H;T|QelW$eQr-mKG^({!mL9AL>;!rll%D{vn3_~=bLhpX(Z0pc3nMp=P{6+~3V!RHJ4HhF5%{vBB4NKWdSWqzDb}?LG;#yE3bNsboaBG_qkS=1EF^LZr+`7Bo1r1+ETdPzh-;*8n-}X?OjNKRg5Vj1_zKcNeDTYTJ!$EbHe*yowie=!GgD*mT+bB|aW$WFN2pS+lIIai7l@^T)De8<>ln*rr?~@#cmv`0m^x%-a5DRIRJNP^J4Fi6$%1~O^uBlAMqkuI<Y0a)_bCY;>Dx3vg}kSitk8-wqQ7&}t2M8v^TgTB-Ba-APa!yy?<;RW>=JSQ%nFbdZ%W+@foE-lq#AX?@0cr783g`*WbRdI5BsI#tTM``Y%%kbp&F4>QN1<pfU;{|U@Xq`3xF=~t$kensvNrE8`tq0G~p2hC6=XopW_}d)x_<@SU4Sl3KYaS32Dt=$63}qqL;fCSHxm_?c-_4noj}M)Vo_Z9g!Df=~*ls)y9e?>5U||b!xml`yvns>tj-l0D4pmR6vo2)X>k(mZ}N7@&)su%bIUe*Z`Vu)H1M|JsxqSAS|dm&FntUVWQX;UFcK&($)6%3tcCFJ_!#B*JI(1+qLFW<<<}RvdwB&H)<bR;=m2m_vZPjz>qbA^N9>B`)qTfHHW+w5P#4p=nW8UbS^GfxqqWb<L)eHjTpGI@xQ$!u!Hs22@vCAzLCpBhoUrkTV6-rsiOoXaQFgyvT5cQuNScs))T-So5pUEv8Qgz!v*j#>q2yz8C9w!wzFmN+a3lt-2I=F`^;4OX%<UOu_?DRu!PlE=;kRMZ-CTN2J1k_JhATOT&oUuDDVN2ildRre&ZGi;TrNg1fW3t-(0c}!4|?T^1=znBdesJLkEl!@6pfU(@yk#eZ&re9D{{{gS=&Txp82-P@-a|bCbOSCjPBQ4~1I#?BGOWl9=?}G#;H#`7wXv1vA`}H)v+;b9+O5-(v)!nu%S&lP_iQ(?UY-W+{0i%qD607Em;B!<c#ehk(DydL$DWyah9E)9P$hi$n2EphQKu^~tMAl#Mh(KtHO)<}t1Dk>|X+3?LjexMnK=p^wra%<QeTM5zhd8^>$gBgsgGL6-|AC`>=07wINzfmbpO7j!ltI2qV5nNdOYNhwNB`ygOaSRO!kHXqtxeH{qJtIErJaKyGqw)-9%I;bqozBy4rdiCP#@lFACD9O-0D>Qocq0P2$9)sR9UQ3kgY#>ZCq)zBto;k=(12nikMVLt`nOT(Nso%d*=NXmhM`mQS9cP7_1FL+b<fkpww9k_?RVWB8%E@QMwjczC!-^7pE+yr8KV%bwraHPMLOt!hq8(?$tj@kVY^e@q#4vPftF^>;(m%veK(G1&cdOkP1It<<JG$*t1lNx@51;pQ4?8>Sd#ysPm5iGzHXWOg;tartFAyukeO@`7_c7Ly)oI@1*{ojH1Qc=x30t<LUYzC7%_lnpZ>^!zyU-X<<Ev4ikb&$vYwE`#3r5EN*Ieix5Jrq~-=E&B4Bya%(bqV89+WEnq$sy|;dc?}v{8sZJ{*{0KWT4do=tQW@*DFs3zbM;{xnw68#kqczJ?B+U^d+v^g2Qu%1;q`@wjnJP#!i7v#rn`CNSG`T}u;y6q3cF93Io*!Bkk(-|f3h*|Ntfo|Hg*>*R2xb2?ddeT1YF{(s{OYX^+4Wy3<3ZE~fH(wcx;rT2z3D99fe*_c7(TAy`V?~gAx>(<Y7!<f*84irczl2;0$7+DLEuRPc_LZl|4-8%2MIh=a2;Khi`47n6!24%2YD%&ve(8rDE22q&3_Zblk8Hi0-AMMoK)?Pd5lbZr(xMbqkb`FXr-O>3r68RrJ1&jWgRJi3(&gHl9$9R8hYjTXb&oByX>I-YLYKtCqtqe2HxPflz1MDuzSwft8L)Aq9K(6s6(L}tzp9=teWboxWRSV)aofjM=f4pZ<bmx!Q(U_0n!rg>jt~&)S58eo}ZCi*5$~V3kb`hmNbHMzW!zhPAQhxaJ0nQez7n2JzGCSF2S=+>o%BZE)$4?m9&Tc)u8~eJabiX<}B~+#)26N}shxa0a@;On7nw?6j9}wB$+=)-lL@^BN#ap6@DqxuU4kjm{Qq(m>>T#{g4%*qDtFNwwDp-Wkmc;>2>*xR6(p2J3+Y)am1MN|bq_q(N(Orki^{>QeeLQtnkaI-#fu<8dAY~L?m){>Ji3=Mlsi=vgm}b;2N5&1{J7q)o@A1F%Hux)Cryy|lU@_^KZ?7BcRKkQS>=A;)%$XV3o1X;;T|pFCk*;m^!}lXnrlIoh^P8f^Yu?hCD4{!SE^zi?S>s^Tuxunv0ieGHEJb;|%5KtdtvanbHBw#HW(_aRX9N*Zv~TwQu8e)VzZ)H~0MWxrGO(+E%Kmm?xR<xiFzE^0s1wFwxVa6oQS72CHgM#phEG?)`kxtz@OA>9je>89ytodTbSm#gCQf30<_{WP80c25vK&@!w~Bkr>AzFiOi@YmRbyYP8>%B2?UnA==v2+*M`rZiV?hg60W7E@W)BULVl$BE3!X>^sUXNlq!(KTVc!G=nWcd{U`m;f9lFn1tKugL!vca-8ut$0z({B$Tp&we9H~?5pqkMrU2w=*xmF_-MjV;%{VEuMCDYjI%*M-vwZYIi1Z;4Hhq@6`A0p8)cfoH)-|^XU?-HVvZ`qk31!eN?KCOHLyf0TAt)9V4F^LET(p3lh^Rl%+Fg7@YbxCRP*8;kW*P~s9w><3WK&V7p53y**L&wR#@I@+5aM@u$%9v1`HDtW1KH+GfEPt1;FId-DRFW5Ez^-Nd%iWhl-j(~o-yU-GwV;FW&DjtoQb?%yr<pVj%}pqBCog;G`f5ykG7h;5;b^>V_R@v=DSnW`Y}=8|>je<8DZjaaXSTXvNX9-|9v+R@O(@w>c9}>>uf&rA6QlSPxeXSuf=WYUNPp^a9tQx4(A(fifHISo*NMv}IWmdD3lHu>eQcQ%?H<8VVppWWByr$%z|J9y`u!CK+YO_kcH$y-Ur;<pj}P+O^?4ucRndIxMNWDumg$<-t;Ked`1Mp>OI$KzTs)u{>qsSu0DKL&PgCaX)T2dQL@AHXJDA(H0TM|bo3ud8tlv=~pXg*N`y(x^@CWsyly^!{WfxOpt-~Ar@XottS^v2fH7c|%hzKbDsJ<3Xn?EU()5Z7a(5$__4~p`7hHkJ?!fTkOW3A~XXrl&>*j!OAhn38s->y%L#KMb5hAuCReDBtywfCU6S1r^>K5_g|qY59T1uARQVeCEEh9pA-7W5#{Ngit35c={|907<}F?Un_SHn+Ci;mc1_)97Ms=7BRK0T?uz&%y>gDN&7;))?X`xT|g$p)E+u4#JD_;_{FWdp;YJ-~k(hKT5WU1a@hm&Tj4^e+3nYd#yB$x-fYhi1a^asgfov!CeI!lCSILF_HYVZndti644J+sGdfv(&@Q1tAH;rdU{_f*F^XZI1IA(Gq<c{45903<!XqBu5{b5=47(oguws(saf+S|W}1z#7XH?tf-3GO0L-F7^sn!D$K)7_hyZF}}`-6R(7)x@ciaJHKY1^rwA#f>@7X8hiR_CRuD6y|Lqx8QzMT#$_=7Zh)ak6gwdCthC+(iUHTvz5HzY`LZ~(6|%T$gn>6vOG9m~#7Q3B21%q|;UcqVkmvU19lTFe9D|i>vr9pMKR^8C9qb;2q6~`75^JQfcnue5om(olN@NL1M15d{{+wN5XEcbjfvse0(IjOVN-33dtTMMn#?mOxSDKguf5RWXd{5?-tIlcfC+0T%KbK6OoWQrn%g9wwFq9W_03`e_pVLl=X2{Ab!~BF$q8IUbMx?y{bQsXncYrWsgW@QzFIV$4G?B$2;|w5SG5i7b8Fq~l9)-R)6Q$bjE+Ex6aognw8imnPRct_wo92gcH&mS~=fYA}MMzbRj!D|K;mnEGiEsVVyK6>CcJq-I%^^jV_6mM;j<}6CyfXHwLF^@ff?xHfl(0Ejr;%(-qQ!T_-lVP&IxftbGbNs#7q^gM_K~y;fau?oB%y!1CWyiC<`!?Nl2wIBMwQJ^U&XuKbv?JSC^T`EYG2dgBWbzuz>SRdVPiCG<f(y+B62&a#n8g?iFk_Vbm_bu^q%i1GLN@0Kk~SWk%6(>$TQGWXu{s>zT$LA-6F@NH3!D4!vDHFt6SLEZ5KARoj1464kHy|hnpHUaAwVG+ECUj0&MPRat&AQIUu0VE$lo^Eal2q{y4rUCb$#!r@81Uz#y_pm=J6=B4n22;K7J!2?a<IQVi<T;V0vqb!y#ht1MSYmw{9DlkAw0qzijnc5tv3DNbcDe~HY2HY=|HkADDbHfL2x(oXK6nWwHIB^;-6d^sMwWsT7a)(R8Xr|qik<>uz2YbIUBQHd@iK41}t<WnVYEsM1>NHUtGjrjJ@*pjx%wjxJThqEhIu<eSa=U%Lwj`s3**3edPUl6`078r88X;Nn{HV;E?g35XfGSF1IPQen8fKpk1J$pehtr&wC>{}4k0$I;E1~b=M>I53Y(?}k&w7SpMobLc6y)HP1NqPglT@$Ef96LRI1f(%cQvjIyfe9^^NOnhFB8}U;&)ROyFV0_5VZqLz6c2#;Dz9g3>w(`?0&IGqCrz%rqOEUqOu@A}e`XZHrcbUaYNU<iH#|et=(<08!fVIXiJ2zo|Lvh*4wt!%cgWt)ZmcOZ#si{5k_a@5V$~K$!=P#-0bp{eux+OT(9*=WrjcOt&KpuPl)r<Y4S^a56HSqv%Z@tct_))$#xIJNCf;+386zg3c&eRb&sed<CC!$gnnk0WAP>NoT~k`x*aNRHo#qmhkV@Jo)0uyCz=f(yXhOO<DG5=N&4$i4QJr0(dg+BMU@mcUYg*MDYBX^J#DWyWE-q-7*XLHaYtU<!r>KhkuX8=EUTfLxFUX2A1lEi|ST`P^;(qGQkY-aJb7m?c#$^z0=t)QQe-bvr6z-SmT5mvl-4ZV{BUAvG>o>2a4mE!E^&aP9o7^}BprM|~l!v(<EZNMjeW7bH*rgD!y+&L9D>`V<`vSOw?-cfnd&T2CYt9p6waASCiWd7-D`PNuF?Ul075;IeE^}(y8iUp?fB<ilk%Kc(JO%v*q|;Osk=(`^HUaJM`{txEHWbNdf`xjo<Nmw&OMvWqOe}{6mk>I;Bq@^}wX#ORYqhB$oV%CdKUa=#J^Jq*iCmb(oLy#<f4m7+Z*u?!I$ikI%=bC+f%Yu}!}+Hyn~GBlX_Rhe(;k<jKFLA<QOF!1Rc9E@y*V2e=O1d(qxBKn>(LsAqTl$D4C!}@P)QrZq{=1Sza*(;QXPs-M~I!r;lS@VrayPpD7KPdQDaiU%%~!K&02G2o>3YcX<k&O6W2~;=Qe!fQK<wH??rvg8m)apxd<Cc=!bB(+(4-BW<Iqit*g*ufS@6Af*lrht3=M1>^+|$_1=qTcp};e{{8+?<@`90%0l=E9o<NOR`^O~KD+_mp^}tkapEvFhL~SSzg2nmxKH&S9+mrk=?kdG>_SqusK9KMJ&|1uJwi)`fRuFAk+h3J#pFD&`5Zci`lu~wLkWyppHawE%S=>4!vZ@5b}c_hI8g<Qv%3<Fxl(-s)>Ia)B1GX2PLeZtTW+5f@Y(yjp>J}+;XwA&j(mR97q(c^k)h_!ABnirVMNYULL6ltSyh}FdB@M=R|Gkste;Md|9W^n+l1BCbfmu01tS1*^z~WU?kQUDl4(oubJOhe17a0*6U%Umeo`{=0?R0UTQ&Zu2Y9FHR+$_gIO3kX<sy{1K8`0vIh8yXGpx<UL)1d$5P3V*zN@QEHBRcEdhGgKk1P%3D6pEb&8ekvxK)tg{J<x?hgAmqkT`x$IyHCiTIV$BE30{wUZ<`esSK;9&d~obZ3`I=DA~>n^<THeM=t*lSC1Pb0rOnsfg_SB<;g1^{L$`Rw+IPl0ZA!;2i-SQ_d&T9VcB^wjRV_fU4BV;cA|37P6ScVHQde?l@ga~>+F1&ij7WPPpF6d;F9pGC?e<5#+cewcvQXi>2VTTpJ=d3_;NE<rl_g{+(}crg&Wd2EWNWvkCW?VUKK0j8NtrV3~|PX0{ya98%jHZsqHj1bn$&*m9Im{O>SI)gR}I&dp=4e-fp4?B|d9#F`&1+iLxbO=K=Agqov7iCJgFScz`o}KZX6*l~g$PL!u_Bk!Cu)I@D(?4=_r-6sTpBaTKXWEueRoUM-R+>~P;MsK^}J;fKXr!o?28tQ)clUFyM=vxCx~v{)bOf;F$fV8BWP)m<=KPr5%5=Rto@F7)uAr&y-?`JJwxb!32&i`0u<^VCo^o%=kx2jFwrOGy0o5lXtn9A;f%ZC<1bDKQxWw8|!*0)ycExUV4)FnZzGf3dIl^DjJw+Bqs&-a0sA$aE~)hUJwPw-w{Dyi8+`X3S?Ykw<fr!0aB0mC)tx9cXm-GP;TRRGwp#$a%D9*#Zp`i*w4Rw!MFE@t!S{KlY-7b5?7<S}WvayLS*mV88}IR!7q#Kf|wC#MXg&KZx2B{z-pAne6ZJ_F*-o>_u3zxh7jeO`gL<&2OQFF^PGgk^S-*p22%$^{oy?0>Sxk1*Jj1063PT-a9t70S}N1(?@k|X6G7>Nw5^x1xo*@WWXYE<n?FDpy~wIdELv|5){`=&6?g_STGs-n`d41li25SU9@SLC1KoiehiLlLK`Qx#Yw#dljYa{JVgNDWYfJ2OBUFuBLOQ-7+rD?;}I~Z%_L#^2%2lYQnR`;dgdHg&CBF6m*NuvSZ6NBy6%ye{W?uQA}b^a;Ue||^GWc3suT1KMRYP<ukjb9w!`k-5CIy)DrrVNz-_jeXtF>Hf?Jaq-b%5PY82QO1{f&NU+Tw4Yo6<~XB<*~J^dR-?>U4MxIe4SD>xIvTK!QOfF`A&;X(ZQCMqSQ?W)D+1~*36yE5akg_I8tAzD87SM>4nv3yy_hZ@zkJ(VIPL1xk~H-gMJ02c8E+p+N?yQ#g}eW!UX$gBdXWdNrDs>7d6>RQ7DF7_xt6DcfjB5z=g&(-$ZVl#A&1d+(_C~r>Wgh-0}Pr@%>#G|J5mZi_#E^hPMwPL-*aF+8x!W2Ko7=&+2=7QFdL4j_ZRs|m8cB2ghjRRFjTPGX{nKE<O&*<jD>6=I{GQN|)V8=qwz{Ft#2Ui?xf@r6-kfsZhk?|V`TY|SI7BMz8bIc$iSl+L(qJB+gfh1i-IRhexOTn_Kxy@i*`f-QnUle?QUo~(HP>%i_5$i0<2xGtg%9?W%%zTz%654}GPa9BJU=d!z@cV+T-I0F5Mm9}iwWtnVHT`3GWsfV6p_2aY51?Y#gWXTnnQ?oBSR#JaQ4Ht~WgJL-rTlh5hZm3{3Ix1C8$NKpylE74dJUXgr5}E9vjAWaR|IDmLf~Yx?kqi2u>=Csz6(ws>0l~uE*HgnGIdCC9!I{xZk>-gVeV~ds9P~5{)dOVyG5PsyZ{}xey}nv;6djtP9bhwp>wGH13}oo4AHfr0nSncH6fSJZ}bxYtK#5I<grZ>#*M{AOA5ddd59l8-V<C}a#+8`<ge4yJv&6A@tvg|I!F#i%u_u77OnaygE6+ud^|?Xn9#otc3dm0=>Dh~0;gCL0DDPMLf@mz<jK(u?#F?{)lOVq-24-{1-@<50n=WZ2g!6ILtlmdvu>m>+~BhC@eeKIPYkEQGG7RUVn;x<JxN9F)omY11Z6a~%sVY;^Q=<IU6B-;prJb1(Z0YB&Xwx=G^PMKC}3I{^x8!%p3gr{Y45+=i6pwT!Q&y6U~1)|in*VUhrT@bl63t!-^vv$IQr>+DTLFMXM}Q>?{gqo9_{RJd__jj_yt9_J@wpWO$y|H5tSNuYs*Q0fP;Mz0ES0*e+ylf#f%OiZax!12E_!Kd*S4s0v97u<Y`6WRsY=hR@$jpj4Y4tb~`S2IZt;J|H-{%KfmDtc4)s!1y)jP$Dy_-QL5)cX|EtRL@Ug-%gy~UwXv72b-CAC0J@TPF~z07nyv_w&p&bQPLqzMd<P^|qEyFuWcm<UBG`Gd7z}K0)1D$z6QzTkG}lm4dmlslVrWbxz3iH8jn_AYd_xkX(X8m?c!SB`Fm#oFbYP-3Yk<#AW(&{GdnKo*^Oki{U!%knQRs{Ap6lW0?T>JQCykbJ7ya)7r^4zQcqV^WRJt*f>SPGZEg{9O=A$V$AKhFq$dypclgy2$c+ov5F(=Q(J72?$-MDsUe03jID-W8b4P51k&U%`iPXAPGax1G>&3#Sdm!<LEJVfSvAZG<r)49+MUvoy4K7izxUfR{9^k@sAmK>7DwEom5?|ujVR%IorPt&e@4nPvqStJ*Hamv)^9fWE`ludNE!#5q{$kKeJ_eF0ev)sOecd5mWCOYX2LQ<_9|DXh$2@{jaD!BWOYmewOpfMPeBX-~U#yY75gC{6S>ermP$*-+11&K$5c9f}FIUk$)CwSknA(Yaa+!HuUhWgtvwV3Ejb8N<rTC^=F6m#$IwqOJ%1pz$1heN|{4{BU^5)p!bR^accn~ujdFYCwcg~Ke;c**!V^JO09KBtxDmxPErEOkQfBASDT{_JHh@X1A;Z&8hKQx=19I*Y#sjRhw;r%r4$SJ!tW1-#a~b67{9-zrjnd;E@M4XE}Y7uGkTv?wG+B#iY7R$+>lgGfyqOv%`!{*|aFOwy>`B|^EHcpmFXl#~Bmcf%$v_GPV((wp(+0Y{x7O}{<q8*9%3uuFd{Dv~!x^M`_mhqv@0+WEifMPSrq)&{b4q<+}#JvyMn1~20TvIAXIu#+9i4?InX!=%blv>Thy-lS4SU9H#e^>ktUS$VC6+Xf)A#Z&}tW!ZZYNdc$@|3lbUCzxqjU1PI6A^IS%xIb<@Ns4zivqToTBpV1-$$GOI3ndP3hb$sN(peZ<FGdWpdfD&LNw&Qp6vhoAM7o=~{8OXG233a6Vy{9kB|Mysx$7wdT=}ih;&Q*ZXlV>oLD`*Y0b%J{cl^UWQ$%RyP#5ZqI>El!xclQEA#`@s|Fhh6+#dfo%O{M7GLU3qVQFp@P`L=56f|${4%AJh)d&0FV~CS&g(t>L)xBtix4<qfL^`_gjPQq<N5M@?!AE+Y8#_aI5`l!uW1?C2sxZ>r-S}2`i$T!^)XHsDah=<~KNQ>mie>jzj2d>uas*`&?MBd$Q$({DaxA5fsiSR*UrNLKLLaQ!epu=2K+{i<$++RvtyOF6?#gO;b^LDVzD|F3zuXD6l#DHUHkaC=zyJUMZRU0nj&GIi00H__j`9Kkjb9&uvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000003706359388395390950576610126096547297174375793313676235838158117210937124893023205240570404', 'computed_previous': '0.3899999992486855639687012632976256082338468549548913731136746930078235642711950991207117958021092227', 'covered_success': {'lower': '0.3902223237182248417840431290375858257892816257582978200800292965404606695972669543478650068775920785', 'upper': '0.3902223237182248417840431290375858257892816257582978200800292965404606695972669543478650068775920787'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000002410845922895532567054033279418945312499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000002410845922895532567054033279418945312500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002029625895901952665761331542201133633062976908439598639446069312258100921517604642077311666990988021', 'upper': '0.0002029625895901952665761331542201133633062976908439598639446069312258100921517604642077311666990988023'}, 'self_coincidence_F3': {'lower': '0.00001413746262920627735023389165534932850460238418590614154217594688395955937830089029726874905688848648', 'upper': '0.00001413746262920627735023389165534932850460238418590614154217594688395955937830089029726874905688848650'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000002812449446605000648874104572817390225166528266954752976790893171698673003623619292061437779050903339', 'upper': '0.000002812449446605000648874104572817390225166528266954752976790893171698673003623619292061437779050903341'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 564, 'HF': 111, 'J': 79733, 'LRC': 50536792653998707434768318337122304, 'Tb': 1326843522722965866262746813366796288, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '45369acd51bf8b3239928d02dc004f7a2a8f31a556822248be7f7a26146285aa', 'previous_grid_upper': '0.3899999992486855639687012632976256082338468549548913731136746930078235642711950991207117958021092229', 'round': 16, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 73680, 'union_lower': '0.3900000003706359388395390950576610126096547297174375793313676235838158117210937124893023205240570402'}
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
