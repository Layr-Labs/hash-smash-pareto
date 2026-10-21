










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
R=14;S=16752;U=83760;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 642, 'HF': 111, 'J': 70065, 'LRC': 44408969652495446507933255042334720, 'Tb': 1326263181384309037131395203527081984, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 156, 'dp_loop': 412, 'one_dp': 414, 'ctz_0': 421, 'ctz_1': 426, 'ctz_2': 431, 'ctz_3': 436, 'ctz_4': 441, 'ctz_5': 446, 'ctz_6': 451, 'ctz_7': 456, 'record': 459, 'probe': 472, 'insert': 496, 'insert_done': 503, 'match_0': 506, 'match_1': 509, 'match_2': 512, 'match_3': 515, 'match_4': 518, 'restore_after_hit': 521, 'continue': 522, 'deadline': 525, 'restart': 526, 'restart_ok': 529, 'restart_nowrap': 537, 'setwalk': 539, 'setwalk_loop': 544, 'gather': 556, 'gather_loop': 559, 'restore_planes': 569, 'eval_f': 826, 'output_message': 856, 'match': 883, 'measure': 892, 'measured': 900, 'advance_p': 904, 'advance_q': 911, 'advance_q_loop': 913, 'lock': 920, 'lock_loop': 922, 'found': 935, 'replay_fail': 948, 'end': 949};EXPECTED='cebe9b54759e720320305cc93b328f8bcc1b142ce9a0540c5feacbec6bfe96da';NI=949;NB=30368
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(6477630067258275675, 12682966089671427414, 2745741419840686127, 439106461336602665);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5180720492997819994494792030486529)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;HrHmvRwcLZ3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxyy@iYDw+=UDVjA6#4!l2qagxHmgadt+YM)E{S$k;t1|D2t5lDZKE}21Vn7^-TXLIi2xeVSq;%7Yj1B|T3-6LNtlH?wK&;!YzX(1Uiwia_GK+bcMxiz5h&O-oNIP^}_ltwy<`>z%ny+c?s#2BwI)_}|n(Xqz@p_%9zKGJT+puPQbT&|w%4tFe=a#&vr1R^;g|$lL^zC<b&dCmJzRkXXw82ptbF%AJTp_9_O=X}ZF_$Bluobx^m7!UsKO3SiRXR-&<D6RqDNWo8poe(0W2Acfx))!_9H0!vzN9wpEc@rY=6AdSy)wOYgE<XEHypCpt)IsZagJ0k^i$U#al<Ma#lM3aeyt(tYUk!=2I!x&y&u<nm9u+9ul0M#W;DAxr6X}euZHffxASyZHYB|T+7}D1UI(_NPrOw9KT=4Bf~BL$uxj3?NPO6$-%suOhi%B82}egyAU7TI5wH9L<UqT6KQM3`)AGVqw$^G>_N}Y-!$o6(q8Xp8I$A5e9xyeVkm%=ima;kbQ>4+Nq6xEo!7O0?+R>Jp;4G$O@ZX7Y;T=<6YLIcg>0Jc6PfsH_6yVQ>KpGXdkS93aN*;!MO?7>n1mnIjv$zE~pbAl06F!<NPH+mC(M|dp_zF97LTYQywa)ijS0>=bAGCoyK#!70UNq6PasF3i36CU*j^E{cR*-H8nVAPgg+90!_B@GbRtEKJ;x3!C(v$-~WkgeHkm044Wp#;cYpi^J`n_8$Q~&ed<2n!N7_>xwv>uHa`?96=y>RF)p73wwt8(?}PlJS6>Gvhn7OC_#fUmAYk_a>EKLn)xyirD52xBOaLxrsjF$*_iA{?@7@d15u=01=+&}*cdS+7O{jIEEz@v{06|Jnu{Xzi69v^C_?P~*zJ8KF)jiM53Iu<MLm%E)YfNo*x$6A2Oy!@YUuY}*)%WfRY=OkHDP&u&qvm;n;zUPBD`vt2zEZPDorka@a9y)B;F=4Lv@YN=&LCD;~WMMUa>xx7SV2~t(A`#p2pTX1b*N@$3}NQ<|z?7WMTm=k!O#_~CyeH7rf84bX}xSVf82laNV8^tMcuev(b?H;1YdSz(Ji=6gqOCKg;bd}KyL0gX&!VgrGiJmY5&_3)hsVioECjjS&`+?E#2Vi{KN1A7xlD#NfvJ7=({i4g~&41kQyh48NN;6Y4OrGKxat-%x8o@h~iphS&U;7pL@hVWTGnX(buvZqtavRhLu)=|#lt0LpwL$}9MX%-aBn~5SW0t2&A?q^Ks%4+n$Y&`X41%yU3tf+cN0+=r$c{hsSS%YdBJ-=9_t0KM49h8T!Tf!o@Ml13aJ+TwQc9*&6~47oZlHwix^K;kbyDQEV$8?MDOB##!xav4#KGu;fr<_T1#4CsvS!i%I%TtqEg>o!5o=7#r8kbW#cGP|9`}CT648#hUb$cP31=ys?=YL!&?D$g?`v)!q1K9-I@+ePik-^FDVEqjksql7qx1DtT&u#r4-<~d90F9U$xG(E4&a#hG`-i=vfQN-YD>%gzYU5<rReYVr1-_XRqYeXbja4TPR`4MIjz+NUd<zkFXLbhFtT;0Lj6lGkz^n<nx!l3M-^S@PehxmNTK`KQ1q+YIr~MNIN3FcwA73nQr{71Vpuuw+$F#zX6zzId+dEEFfJr|Lr5KHjV2dMZYujME=TWr88;tMC$ETU=N6Zee)_k=0wBy$Ck5YIb7#nSBj(r%DkOWTrE0X8XyO)ZUn?;3&m2M#2QC7OHLyk8`*jtgw5S)VQqqZ~<2!m~r8uYN_%C+vkQ>$U=M!l}@|(|u8@%#SFYWsQ;B%sYtnu#cP#ds*VQS%rj%C@O0R&z28N_3{tjZnvM=8knj%U$3{uEzxerA4&|37l77b(bmMOMRCOZQfLO2+ag>K3M(7YAq+rJ|tsGgNU|x7({@b<W@jPQEC%o#wY5Y1UJ6D~l+#_7f5`^VU!n{3p>0zzIkiU5P1gP@3;C<%0<T<*rd!gQl3p*ohUcs`$esidT~o$K6#}7XPKmjlF+W^M*PXCv~E*y0@xKn;mOu;BJKa3`JYZ#GC1lG44i`;L2-~IwdbWunYVc%9%L&@fjc7y)cZ%Z9^XIz}QwK1;n%&NKN+sgCmRUP4bJ1bK8=aK{5!3d~d%=V=O2=OWRWXsX3Izj6{3o&Uk;|i^_o6C3(<00y1#IYU>#WS)r_%P-F726&6mAveu9<Ce96-5ZW$4#G5^|RH7QODgC?R>)pW=KeV;RhtdoYPh@Ky$igIF)F6hjSls!iLll#nfKNlKNCfU}>3i?0@--mopMf5D<FFW|2c4HGaV@qyrD4*-@fR^pn*~j-)CQdB1u;i>>FVrA{2*ZCl@0TD<bO%8b}&`zP^8y0fWdn3Lo^uTB&X{q_d)<!q!7QzbC4}hf2Yk+%Fnn<yoJj;uL_(TFlLJ@T+5wE*XCTfBxgS)64;~cRf^|T0dHqD#bVkgfZKOU6@44j=N}CLkkG@*7CW4C57Hbgi8m$!{DZ5su2DY3o>0g1C(dbq)McN_0WQHML*&2VvsKOf;P@-%+z8`C`wa3$)m7EJVN_V96HM9A*}zEM(UipEk-}Sq6?X;9R1(R#8CjFFKczmqnL1)5)%#fxB}Cj-=sZ#mUDE;8s1UmIzH^uDM;Bb2|NF@I%mhg|R)a(b4d$&s?m|E;Y*O6*O<L@>(utU{&*3@BHb*==HVCJg#zIX279GDnVspe1Dn%6!?9Hss6bzEaq)}zbC@oH`_EpG?2->Eb2ua-($2Yp96o#iFAuQp8p?dO<J+1$z-yR{0$_)vj!i3tqm9IZ0e=MJX`Erc(D+A?RUJ=uH^o0+Y`L88r=bXR;NnNe)1GAOr)c9ysD!b)8m}$YsSoCdhw^+j?kYC+NG2*>vJ(ULPu#lk2vtS+<*7;jpWx38WRc8|_2gbhAv72Y;p=B<f<~||qZIHtSRXq0atS3wyos>$Xd;Q)A=Ehy+sWCs5v(~@W9_?tJuy>Nw?smg@ZWd+4#_g*w{LE@8ttXwqt=gO-eBeoqT26*1d{v9k#D$h-?+5EvXoCC7aqX$kjMz(0fw<pS);hb~G%(Pbh>y&3k)yLmuuEt%tDr@R*lE34wHCDB4kCD|k61xCtxM^PaSroMrYzFN9$~8NmjcQX|HyTgQ(%NJdSE2<bK)puNRv?wtFKGVZjt_X%njt8kP7`ZPE1?I{J+|fy10!2X3+^bPFHBmTpSO5(!`J;txtuT6RT}$EhXFST{q0)9bZq%o8F@KCPFZfSlHF|lo~#zzWVGGr_^^>1;>eWvs@-*8R&0gNX%@08Yl@9Te_YZB}0mhGEmtb(73IlNVx#}(ARGk=07FjY#DB3rUElrcm#ZgvgY(5eb?%VzVubNJ>qekvGES$@rE7okQNw}(2tfy%Eb?fy#0BA=>zpZ3apH3N1C8bjr@63mAWvR(Hn1~2wEqa?n+ik_#jH)L%Dels{(PrctDCz(nRsnQ(@P2)(c~K8xFXt^&VZ%G5uJ3Yz<3+n%v;`)8Hs#f2t%g9ANaBjqfaY=y_7&5$uAjD8cYri38@`hy-Aqhvk51U;~9(ypU~JqkYiVP!f9H#;Avb5;#Y*oVHRbfbT2>aJU=^Z+uq~!~0BaeXWcH8(I<hS1`n#d)P*dV%r4IF54L!&Pz{!gLI8L;2{5>Rs~?SUMpu?42sKc@Y^K6SOwHCxI*l;BLYg#u7_*-UU(B5ExO$J5aD=fst^5E2%MnH0Xo$=u^uuH6{cQe4Ln)o%W0UeJV5rnL8FS^dERC-I<se7;;xTd`udrVeRog<wM<srW~Ar$Ko&RFnCQ(Uz(p8BP_*RhrK2P?xG80=BUFd?98!HfYa?O*h5whqy<k^9#C~U2onlptz#KAEt4%A()I-$ba>oS@{YAuDSW?bWi8!!h7|0E%`BHBx4Vhp>oW_Ry$C{Sew-V}}{fhU>-w@oKXnYa?3Mlq}Ku&fuy29#b=IQkJewzNKZ%%y_vGJXfN*RFEEo*Vq(D^<>?X~j4u2tl?<2>jozEw5}94R;JOl|Qn+BVW={qpx8_L2+5<Ca$P9bE9-BLpMYm6mfjpN3CxQ-r-DDmg6rivb((!CE$E{jEP;CLyZgqtG-k%n1eCa$AaSi>CYYA^I_$jRtjhE5@N>-jf(m-AZ{Uo%&m<=GM__n!ha3gWtl(_5(*k^RHM3*Ws&W!EjKRN+rE;q7W`$6;Qnb28eKsT52F(9VXB$XPX+TO(rzjz9u>zjB7AXuc_|5G54f3h&niyyF!uT?bjOabt2@PAMAYPft^9V%&yqil4<qi;#*cDX3$UQ{^lA(6ml{!TV&w2mkt847&5mf=!z$zS0{XBCBnQ74T6A)(Es)dPDJCSpa!?LLtNfkp(=NXnRP%ChDgTr4jSOA{N{9z`$2pQ!FzU=k+Sj9eKMbP?t(|UM{iLrY?-yoYiS-}2IbZQm>ho$S^&8MHT6L&Q}Q^Ou3TdVi0YLXd$0BY55`5MNg#k)ap$pn*^T*0O_~e+c+o9x;2<^s!;>#`;kIVV1nUq8OgN9=AnQ_eF}2O4ABaU{-%YkCj>Fipldwr#HcX|!{EWV~LZQz%j+Qn<l%Duu*S-(768#`lU~!OFA7rZsvx&(8-2X3m$6Yfx^-kJZ!IC|0Nm!3d;@RRq!N|`>HAHD|^ug<+dh4K)6y{h4XfZ$tI#W%Y#7Fs@r47+D?=6&>o+jBm6}J{lC+KtxAo72tDwK94MpMtiAC<#c%Pu+Ydo1@(lRQo<@f4`A2XHj+pU5-9Gphn`CH>k;|D_*A=1PcPo6dWS8%n?=Nc-jYPJ$aS2F<>-wLIcy6|9^K4D67ZOjC0$J~G_}Nc3_4_1OV>7}RRPnpe#71reGv(7KfEMyuQ0o=phBBoWfz6k#-1=l>({EmuI`H@kbFKm5M1ZHREhwN8sNXpAUOO6EUIzB59A{NdWim<R3byFZSwyLYusp3|@FrE->~dkSK*Rxf}Zsy1@-Uv~87EAh1dlE%(o8Gme2wlP}Cw@V<o)}GESm()!?>h}1r@Odd*>2Mhr6uCq*zWzvnse@etbfLb2$QW0SZ+di}s*xHFxlngZqc-Yw5Uobu@+9^1h{bCAdCSH9ioTNn`$4HL<;5sB6##R{O-a8FI_CoipR9ZM*`m;mE&4x|fDl?}cCrvE+{GO_K&q2f>45aM$@xyW2~au0){pM>1odc?7%9Oc$d*9L6uyN*>HoJH)~2hGNI2S8w_i@isS~>vdH9Tj;vxlWor8e=;%ka=XgH^7ZoIakwA_#p%%v2I2Rw&+O^03cY_)N+A@QcKpEy{E+(Nh;%`*=2x_5~JV!#u>CYs0#2tI<_{BdRN<~!PsILZUza7{C3nsB7zp1W0=70BVdZsl2_#Ge)<fRn&vEGTh_uq8o7#Q=P|##gpvlX>o8P#T6~8q#A?NeQ8`gqwj#zM5P4mE4u4t(AW|%a`$bY#)<EhK?>Ig;l9PxUdd{1EjE^{>f_1arj|ln(gztZ5Maj^k{|7Y2mI9A0f@m`>3xes1f{Ob)%vEYBPA)6I0Hj(mgsb`F&7fmX}^1c40N_FG^S9Uz3=1$Y=xgsmm8uGSFYk9kjl}Wf86qWbMvJQAwA0tLX*VuX{*gn#`PXIUBEzFA<jM#B+|g3hDBl(6J(nvmF$zobvF|b!qTQ1UIORCd@CR!yX(|%5<n8=mESEfp9a3zy<#8Z#GnrqVX&aX*E2<Y@d--?-nCs7Z;_%ujR()d>dxQ06lE6>L=7DhaFE&A7qFMyCx~uK~e2OYx|=$x!c&^0hnwAym9U$w%O+%aQZb<tScb^JFzRcux9E?BN<GO4j$ock)1w+-a8dbFMakwi;geXgBSosG}w-`cc-R^`Da%`3C#CJ@SLD_CrMvn`(88-P)RS1kcOP}BB7u}$n65*BStPO&PTnM*OR_R)eAH;o$J0se^t6~f_S!&AzM(%E#~vE5iih@@FK*zb>7{y(YTneDL(`02(OtCbF|=g=OHaL0V69BNar)EW~y1K#(T{ng@V`e|6y}%Jl@n=H(xD3<;vo=-qLa?vD)B1Sk4hgh~GiftlfBvx5HnftHEj)V}*mYan^Ef`Z3oUA74l4V)~_g#$Lwaaq1^k1-YK>8q!$=7blnZ;Wj<013BG#BbHjI{kkqk47jCT^(x-C{j}e-RaG~UOhg(4u|6NgLqoZXNU{6U;z%x(I6zPt-n56+>gxnjbIVB^g7K2S8S;gYaZmAQZ8}{sR2u@Io(EtVyE2RzesH*ueqd=U^5!V&B4fJ>gb2kc)hxcaA>oo(;taR{#W7T!xW$SLl_9<x+J8ye!Pp^`^#aoY_I@dh9f(m#zf4B?zc^<;3Chs(+fQ|jnBO@v!O(2(&Vlf?H%Az@zDOx0)8x8-g-C&x#!onc<mG(OnilObI?3B&1Lk6^A#EPbr%a2^yXCSOHqUQhOW=#aCXmp#H6s65R)0+WOBC4Hvu+zNm7r$haMRsfvJ54+ZBS*ag<=dt;o7t<1&MLi<B<Yr(Haa&rE&;MlRGu|Fe0DtD|uIs@mu>?n#9%*f+KPJDb_e=WUVv~ZgRY6JJh90YAimF#1fZtv^Yc`{JP`c1?m}O2T>nqS9JB`3~sU4SEZ5YYqIm|TRO`Pvz=CnS5_={zzJ|Lf;60aH8i;EN{8$+)4EXbYZV(;duBbL-nIO73LO!wa_Ee$Tb*XK%GD7LGWl{8Tjdy8n_sAm%R45$)oN(l-Iz6Q1u=?BL$#mr?H5xTRxwQ&b|Y}NVC12G5&ma>Of{LPYH0)N%}iiaq$d*f*5<B_O1Qh!Lf*((XngOxw(AXKM>(#OMGf~$E#nSWq%-s-i|~5}$rjf_O3*#QzB9n2MDgGytk5Kii;7+r6a)*goO`|ej=%=Y5PWYNx-CfeeLOr@;26tIB~GTVK7*EZf|GVtz%sXkPY3S2X+tag=m+e;jnHa-w%De5ylZhIy<kSJi)rkdo3Py4Ab8&l?Lj-=(bfZS>&)LY+ao@n)1<NXPMn0-?~D(axVf#cuLT8dC29h9<PaYQxQw%?SpaqJrn5PmfcA`9#O6iHl(=i#`NS@>vCa0kSTAyY<TJo_Vbd8`<cm~T5Ns;0N=P*q<(L~=9Ju&~Y9QEn_LLvgl|f>I|1Q#AN>q<=ICAw4e{6sUT4V|Afzv}Q%{}fsGT`FClN4i%&+KRgF>Cp>+KJ-6&$TGr*W<EbONphc0p|Zj;EuDi8Ni~7VY%CwrCj_suNbvrpVya(EoT9OjAMEIgq6a`iBl5wjS<?`#6rbvEqyc@v=LQg$J))(g|B%{_AB>?e0)buur_zp7jx8qmpoDffH%C^7|ixVdUCIn^9Hxjd&zXC-R@X%M$k?=#Yg{T<bf@?GC&Llb%gxQ^sg)56(3b=xSuR=q!ZgiR=vN}3uFiyz3~P~Jp9;Vv)K}XM%g3gJN8dyuiWF$-7Q7{&Ioi!w;PG1degV^^0PWD3KQq&yH+UpmLBMO!b0g;XfA824JbM1{k;1I0;s(&tHLC9`Z`MdH_pm1*yRPH40J31F-r**uYu3{i1s5pM(gA8=)tAUHe*T%b3Bt(O);C>z3f{<W@>rZ!-Al<`0q41#D^HZ75IiLRtE4{5Td5%(Zn_wOm%-6BJv6U>rCd?Eb}(IQBSDP)w@3R<(G!CEB=r~(Oo$6dh0m9s_T>#RjSytTxFA{P@{JCX3Y)Ix?gQNjw*sALTD){62q%G{J>zXMtm)(yNU9}1wvi(GrI>sB%Y`xCsSL*Z9JCa!D*2lklN3~1K;guR(dO_pkWZ!fv$NL;l&x^z*Ftj1~ro6*zU<JdQ`=X;HbwFX8Mu__3&T94oTO`E8QX0!WXwZ)}YzkA1nwQBKUAaw1nfkq^5~l-xb+Xqc)TE&ux09Pj2(P<gBp2<0l>SAu9q=^!21~B*P3lre>uBiTc44L5^<aQ*214D|6e(YN1+G+6pfNL6euMuO<>q0Bh?nldXy!oGjlpGqZF#=j_K~)I^fzpJw^mTkErDky)>4`;EGcB|PD5hmp4U^BkpKJHZrO7O*PrN0ZG`fWD^OfJ@`L*j$BhXrrAdd7UMbY@`iiWZJJVZWJ`Gx7a`UbJ(tCkX)MGVLLC|yx7i_&X^%-(*s7D$n8~Io}CoOthM^dSbhN+d(u$XqHZmwRWf^JV378^3E*h9N8ZH{q6yw(g?Dew)?+pG8FJy$fcg87&92_7_#)L+NcUXsf4P5e=k?)!S?H{`TDKL1Axm>$%4vT>D&*=ATCanSNYClcyxG$_68x+TZI{ViNhla2Q7%EnVPW~^BTI^}1wvnu9Wt09F;EzeZs$r)4To&Gh#Cf5gn4!gpm@SP>Dw3AXrPZQsq?JPbO(miB;!jr^mB`6%xWI0vnG4iEi%PAzeaojLd;{))1ZcE`k8K~Nt}6eKjf5pVln9cx`lP$seq7FYJt3-L7~9JniEBfO~{k<<a;%-*dhsS8)mPEZ1Ry+;@X7f)#TMAUaxL*MZWakH5SPw_i?c%%5WIjF0J#x*~$P5($rL7Z|+N=ZrCCr-~_^a&~D#&yWS#zlt9Hl|NI;Pvp09o8pU1;by3onNmOu67zT+ag*Gc%DmbckwS9q=0d^J{YMfQE9-hCVG1I_P3R@#`$B@xTyI2rCB)%8KE^-_bMWz@H^g91_@@Qug2P*$uBLvdXxG&|9mGd;!6ZDh!|6Oj4Uhh>!I{4ttqAYS`1FVcb1$<0_OsP}YtcG0k@+Yq-$~*=-Q%SFeGQ!HHVyc(3XG7A#O$2+!7QmjN$oU@Xku@PKQosf;Rb*FyFJUH4ePno*Ni1-fM46qEHlzfz5Q55JG3Oav=aLNwk=ZLBXyh1-(Y${HTUI!qu6{(b!`4ET6|zv8f}bQHE8R<PsehT0vxT<E^KuXmX)wi^6p%bBRD$B>h9J?S!tdp4X+@NYZ@=wLc2UTE8(QyG4Ai2o@uhmKULH&w_|&XjO*GNc_*3RK<FUG&Dli6XtH10@iL&T%Z!Z}{&+g)|#mGHp8-9@kb8qB&KD-3yW9+e{+S$aNVIi<m{Wbio^cpr^fDlD-qA!OHEIvmLx9>Kwz2w2g^E?zp_vN3cTl!pCH?~>?__Z=m>Y4B1m;|76Hn2xB>~)!B5AJ(Xny`w$IHcyYJptRlDKY6K>$|jTMi86E7=q6pAMV^ijE!)|B8jG-aMVviIZv&kFV7~(bjMO>E$aL#M|afO;E>t8g+Y*szAasv3}+M75&p3u3xXH)8@cI9TTW~jJH3g%`_G)ScqpR>5Ka`i6ewO%7szKO&nG8eN$|lO+o}O@MRm9nu;1*`ELjKbyW(Gfqx<qn0IbG|D5a!Ig}15EY8e7?6=T7R8WWWYN8g@O_9^b_4@dU>NZ=+Epg6ZoHVm>`5iKo`o6vL}rYNeMT5xoAD0^=7XcKk_@*FJQPO1qcDa=sfa^(F!%l%uAvDUJEZpF3tO&FaO?WhhlR;6+tA;~0ue-SJ1fpC`Mfiw&%dfyf9wC&SYGHvBqQlxf36IB7k2C;iTgo;P6QR*&f_<pImjo)ITe+L$`k?>pR+d7A9XB@LHogTu}ctjClEu4o|g6l4*Yt!^lNLt*4Zu8;~kT`@qki3E!>Ea6ZgA=1lg;eK>Jim`>>7Rw>h3+rRIWZvJgRKSYWgw5jiY74<#CCP%v-1U9ldrDK2dXmVLuT2g<MUdjfGQdrt`<aiLC~M(G;FXc8em?Ts(_TeYdw;5yVc6d54&k~8%%yy?THzJi-EwJF;qdPi}GCSeO<*|uXB>)Z4EVKbSpTD6>-g`&ZKZkR3+``Ba6aIunN^DD~iRM(%ccAx7*myZ2G=3sfPdS;Em8SNB>+sGP&~;PC(|h(ku7Jwsc(-cj*<RDsVcx&SPDMRRRimw_qL1?KeDSM*-by-O6M`v!xV|IHS<2bp>3TAN;zLbHfMX+$tJ;m1?>06hDHkQF@Ng<502^%gT*^%Rz4NJ<W)FxYN>FNEcZ*K5=zuWHwlU62@$oq|IuWKLThQ5e}_t)I5IJv~)r~LA=hi+}^${4A)M0bD5U!kYXS~0QmhI5OP5LP(k!yhQF|TLVW&xXeQbwSF#5hYYxrBK3OkaLC%YF<{Y)mO5r*Q1LV)8(K6sh1!(^vBUUs!K)%qRJyQ6=sJQ>~qt{p0`n6J)vhUa1(Gc%lILoEy>d6HEq*&P2cNYFG$yn1994)VQC`BHc0#YjWD8!53v5{*c$J}QX@@rOZ&Exz3qWe~{v#5puFzu)mFTN;{?0eQBQ<y|r8e_afpVMPo7?tMKFXE-oD*4cb!6!{7SZ&~Rw1N02NiCav2B?~dh|FJZGe-&6HqN&1n{UII&r7Oeg$bou_h|M|LIoWI&kcka&maHtnk?D$zxJ#d<t?&{G&-Z>`A@s|(dlArpQ+Ji=w^rhADI7`5_k~za%>4m<1$Ae$*Qr6jZjaw?YUj-J%;b4Hu~wr7>b!ne~}X5+M#H@U!MsJ8*CgpqxD2x&wEpo2qh&!HsIu@?HK1@^a4fZ{k^2@yg*elsWnM*A8o0Ts%*Nq?)hOik;2y5+2#zV4d4}p5`~?(*cl_jUlA#L%;D#KV_%VDRc-gPVa0;~nw*i|%G9zbT7a1l^99^FM5nsNfqNJ5LklygN9nxu*d(mM@@)aXi%Y|W`)}T{Ee4V6z&&C(6Vybk3%fPy-v_RbhLx<*J_R+)1oGY$l%2Mkg=RL=b|_Wtd6<jqLqd%lOyqT@)qv-03f!wLv9w0rWj8t`6Rbn&HbThck&sZm=as1t$s7|pO#kezd$EK{MZz;viL*NmHUcrX|3y*fYjK=|{ZJ(>9SM*3zSk2{dW_NG<<L=Cl8kGp{h2WpGeSSuuK<DA6t7?GHO%N6UE~fITHG?CG1MS7aE{QEvwqA7jhcnQV>1G(Xw1@9J@+zGzzPMh_Hx9<fQJT@jedqMM$z}ft>oCc1?%wHg`lZp1k#?|UZ^|?S*!$@+8)seyidz>cqY<$qC-o9uOMt97ftMR%TAdoWKKm>FDsD!oVSba&mIV^V#+f9w$?66;@1PcoSX_$r`4*KaMWA!Sv(vcQ#a@st^g#4xtIPuPu#qb96i<T9xvW-G8fHWEy@vPN-F~b`#!*bkUy;TO#ocH+N=nQND#iXBq!CM4H75Hj~vQ^HTPHteBSbOhvIvEAFsW7ZW4_)!7gKVHaSF6!)q>szTTQvm{6V<z7ac^oKIB2qqA6@QEEhuTfYo>CUom+ruCe5)tZd!*waERqCIFjM5k@B1|3L8^#okt$QTcZh#hyR(wN2LdD6dv(u(?Ir)h+(SsYCN<-fD$O}{R6Kt7|fs};ZqZ8bfyOZdR8<)xZ?mMCO;KQj=qgyuW^U6Dm8F|b-2-(YRpPW5-`Dw=benjac%A}!Q@xp^*ngO4Bl`on_3I7I~#alNEg{Ay*jCp|eQ-+VtL;nU|L`}M2JYQ88wY{Lqzn_K;f>qyLt5detwD!GTP$c@?-)0(}JmcWwM#pHZCP5`R2p|)C1pz`*x#|s3WrRneFNB&sZg6h6WD0Eom5-Y>WUTrR%%iwef1FS6bU(=_?UH_Z^$%x^5X63D1NcfZHT{Nfv*3+d)A6gSpmt*Es@co2HeLLnOqE@+SJ2}hqZ_f@duB<rVnMKIG%J26O#J-qRSIOP|tvoZ-4ZP%+yb}_KW2O36sSzWmom0F$<_#WsKBHSSo)72h5DgT*7xuPuKZ7R0kz0@B^%O<Io|ck|IfW2km(r6L#$Rzsj|GyE1j6RVJQg69R%@Z(ZUJ+TF8QYi7r~yjsvcBqqK4>q?-P|(X`^NQU4F!D(Pcn2l4Y}6PXKM`IG=!w3&Q)K6};_2LES&{D2<;l%NYtaj8oKONEHg2I1UP^6GCm^UHt669itxJvcOfh;a$@3RipafyhB#_5TRDqNUAu{V;~;|zuPjc=urW`u{t{)ap=L@x{v?K<YVR2)&qmr&bv&TBQ)~rnxWhF?e6EDWO@>>WY(N_@5rJX#w{?{C=KBru3%BeCsQZSeIWF?2l0~M)l~gxUaF}=R40dL1w0%iv|bJ$HyP%}#aFz|50QnN$D|IxpnZa>OAfZT1H1*XegCQYtsEazJ61|CGe2STN!Ymu;gByR5E<{(Ryh<e)^FCyZ(WrTJu9Ay^eGa=78Be06Ou5jV|`wKs_)&eur654CgniBcl@3g;ZI&^up~6$`B)R8!7X*j9z|luS-6O`Z3mJCF`lK`ba;7=D#$#%m)SDuUH_lbISTmwoXec=GIN<`kC9mxSp$5>s%F_-b;2s(oind?&hO6;yXNlHVCQHLB2#tm;Kvt{QJtpdTg<dqEL@YY$zI!_c+A_Jyz*Zr7ZgbhUvf}efbIlqkImQ`gYlBx?OL60`+HMerd+<?mu*u-_CQC{Mx}77Du}~TUA0<k8oiyXSuuxbb>ORk;^h_p^@`nE{^CSCYBO-i{A{rjv#GBi)9n(XRa05wG5_~BFT)xSU<?#N_`Y9r&5BFE#M?U4xTi21jV%Xtl|%?xl)e0Pwz0_3%*bA(djxi9FkC-W8Pbx2JiP4dL5=#cj{5)+xp$V{cWZXE!AjSqLV|WR@H4@J0pr(}4zGtDL~w(v`qcb%H?l2Nz0t{$B4eIY@}|}#X65oTxM7Sb_P*xN4)d!eD_Q*7felx})8^OyYAk|wE3^rsyYG;FX<uWmzL5eb$n<QI8>kUN9cJ(a3`VNUx{i%`+OJ+r$~O*34@#@^L|9Nv)Thu@EPBy|tWpEqeHbfmE6E7BDXdwL00000d{HTtJ0q+d00GWV{?q~hd-@yfvBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000006834131967784384170759201038355787223463491581713379769676755193781011444552979927035748663', 'computed_previous': '0.3899999995570568049263499056726850661381874029900982636273168908290759774941600483422233702688995486', 'covered_success': {'lower': '0.3902187739582740044956718127775783209519922884254383862094477908770942796290311933875682270522659766', 'upper': '0.3902187739582740044956718127775783209519922884254383862094477908770942796290311933875682270522659768'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000003115613367299374658614397048950195312499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000003115613367299374658614397048950195312500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002022814906511651747145488960298983785695614447356087074672533219041410485481186837171559812534598711', 'upper': '0.0002022814906511651747145488960298983785695614447356087074672533219041410485481186837171559812534598713'}, 'self_coincidence_F3': {'lower': '0.00001240356917998660727283314408827554080414592249687017789035432497743616618627536611640026785454333711', 'upper': '0.00001240356917998660727283314408827554080414592249687017789035432497743616618627536611640026785454333713'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '9.726016623556932256604682939788494490292742933291625541070771737934845560979976710530995831071590445E-7', 'upper': '9.726016623556932256604682939788494490292742933291625541070771737934845560979976710530995831071590447E-7'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 642, 'HF': 111, 'J': 70065, 'LRC': 44408969652495446507933255042334720, 'Tb': 1326263181384309037131395203527081984, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '7dc70bd14eb0bf89deb2c421d7dde875c20154f71f7aaa48aa828176b6908e16', 'previous_grid_upper': '0.3899999995570568049263499056726850661381874029900982636273168908290759774941600483422233702688995488', 'round': 14, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 83760, 'union_lower': '0.3900000006834131967784384170759201038355787223463491581713379769676755193781011444552979927035748661'}
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
