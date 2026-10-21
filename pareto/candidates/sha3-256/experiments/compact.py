










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
R=13;S=17744;U=88720;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 681, 'HF': 111, 'J': 66062, 'LRC': 41871766976138645360837603576774656, 'Tb': 1326027569208392007845194752810024960, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 162, 'dp_loop': 418, 'one_dp': 420, 'ctz_0': 427, 'ctz_1': 432, 'ctz_2': 437, 'ctz_3': 442, 'ctz_4': 447, 'ctz_5': 452, 'ctz_6': 457, 'ctz_7': 462, 'record': 465, 'probe': 478, 'insert': 502, 'insert_done': 509, 'match_0': 512, 'match_1': 515, 'match_2': 518, 'match_3': 521, 'match_4': 524, 'restore_after_hit': 527, 'continue': 528, 'deadline': 531, 'restart': 532, 'restart_ok': 535, 'restart_nowrap': 543, 'setwalk': 545, 'setwalk_loop': 550, 'gather': 562, 'gather_loop': 565, 'restore_planes': 575, 'eval_f': 832, 'output_message': 862, 'match': 889, 'measure': 898, 'measured': 906, 'advance_p': 910, 'advance_q': 917, 'advance_q_loop': 919, 'lock': 926, 'lock_loop': 928, 'found': 941, 'replay_fail': 954, 'end': 955};EXPECTED='a881d57e5373472a5599e676424611d16979de0a2694b44ba89f508f524a1f61';NI=955;NB=30560
K=(0, 0, 13265668776992266707, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 7928103212675454578, 0, 8575737624765115194, 2590537648358642454, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(18178323383345041548, 14091932390633223133, 268420692512026360, 11547217295379744);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5179800132057920345702360489656321)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;G;DriCq8%Z3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<<{ulyGb*D`#sI?oX8x(<aa<3=+Mdh%;2>RRRJ1l+G8%6;oJ~JCsz`j)Me&_TBe>XPCT=xQ>&k^7z!k1^VPgHtX5dlL-moScDxp0v-I*$r=HLpvI)Z0g?)l!ju8eP`%2_e7$b44j^jz~BLUG!2iz1g|9$G6jf(QH`9*CV9<w7VemYL5Nc=iMNWa>a-z%Hyk3TQlYReYNWFRT;B)saM?(Nd1$&ft~mM-mi+>Nwl9w+^XwFVq+bp27p|#E~XIYF`pl$O8EcpVct^9s|A;G`!Qhs{u^XKIO+NDpzZ8KH0ioaRjjq;aB-p668jYCiCUK$tlYzth&?}|)U)KNiM0tl-}|za(I|@v!m;DUTay*(aU#<!2(#gBQL*I#O5@(dYxOHbK@Vmuw1P(HpPwA}%&V+d2GC%W@fjWd$P#>Lz8>Jyzi7qYTe$o~DtGsv9odJn`@N5c9-hTop;7i2tp5I>lPVQ^Jm4d*s8zgXcn;1}kEIZ+9djkQ!b$@*R1!eee(tUOTGt^BTF`Lq%+zC)NRSU+CywOzi+K)^KZmA2vjNI6@-^aXd>~FxRJdy5i}{8UUn1Rd4lfVt=ZwP`&xcC__y;XLoTrviDNmgI@#Oms<TMWs==UR4q?G>CPP-G$V2utZe+1;)!+ttg@)miRTHrvG;11ca2QaeM$8B=*AJ=wlTNO7@=kg?vGEf|#vhPC{d~>QRWKcPn6BHHqlUZwTv0|ONa+$tbbxG(6Vm$}Qhn6w&gt8y~mwHI=;z>kIv6#7CnND^v6&M9*bJOk2?Z9!`2Q`rrD=s#+7DM_A^@Z2T{9U#MRuIU$5)3ls?-Zy!lDs3aqmKkY+8`C>pcj5<qv&*d^&U$7%Y<kq1KTl((=8FkOwXnyX%$a^qFAF+%8fKc2fusHFQ;I?k*6wE@^X{frw8;*cft$5owTOam?nUtRrhuv5w2jpJ|L}IkRp>2Wna-z55D=^2|Kx>)%-*_><4$=sm(UKL(|?Wg?S@aL~SQH>9Ek0_+($(s3hwwszHf<XG%Im_NuRM)ncqUHTfLL|E(>QJWw%X<Dk?IndsgrY;-uAN(fn1Y=NNQcOD1s#8^5N6zsc(vLQanQy5dawYr=NNa55vU29i89&Z6sN+ZvDkAW9us*MCBKFn^4Y2VnVvez`Q4V?p_N;q3G(u#uQ<M8L9aBj)|CbHO;)sA7$3FUtRM!9tWHwGQDNTvL30=&EoD0UbFeH+O=IxAp{W!+tmTWsHs3q&~6EfM)!_-}rPru>gm!KQ9%>pU^Jlp|^&sU9UrhT7x0c(g`r=$YEJug!0kdo@3A7Cb)j{)FBVN0tGj_%B^q{y@H}{h!NrTf<}FVxBsK=67P>Sbu_+)ULB0lWcrCX}fX!G5XW1wSBZg_LH->(@Q2Z@ku}y+E2M5$?Vl_g+^f2<>zk3V$u0;&Y1$4p^y7k5;frUH?vJOH!{Bn#X3@1`4k1st+-FnKJ(B^^}EdpxvLLV66(J?Z%^cmv$w<E`6QJx?*B0?G7Z0@#|`plhSVoL@$7?`OI(%~r_wk0qIN9RnSX5aw2IauLxV0zILp<`maB=pMoQl&%R|3KaO#|=`xT-YlWiE1VY+TU8a+v>u>>JfzI@g5wA+dGSGce-u{M0#oC54{?j<>oFr0mg&v9&*aW@U7){iJ|ge&)?zCw%}vNxF0y*beZ^t+=79@@QbW4R-j>4dg%zd~@A62%F$(_*dCLBCCHqUv9rOR)EuYBbaF^9GmVdn1!p{z61pJ6XLnzZLAw7aC7cPp_lCTrz?q*iP-Cg_lAE;#v+6$%oNL8t95nx3mC%#84*dgiE^0Y!Ku{^MMl3Au%0l!h3w^k?IRH4jYo@r7^j`90`1aY_z><y7P>KR}4&jauz1lisIfh?C@HH1_?dRs&1n+u&7rS_QH34Aot0ldvHkeIwp)TCnv+ntAB14H^!&n>Kxt9^@a#}0uL1U+u-Jd{Bl`54OP#OO9=dgNk?od)#3XRZxcK!haIgFg9$93)2$|B<#~h~k`^Vir-P*c8AHxo72$|p-HV{GjUzpi{^>!!PU*DuRO#)dm%#p-3+9f+U5+i284Gy0JtYdqmTPKXp{w^gi%gU4i)#FTIb-uBT_HeTl8azyZ13wk1M+?M0&g3VjZzS+H(CdJupLx08Y-HBR73S!zoQ-Baw?XB&IFID-fyn6^CXX+n@P+k_)fr4Y4t}YKp221!+Q8RK7BhU?i|&A77`8h8PLKP@{h~5yua}opeNWaVpi|QGx_)J*>Uf`7O&=hai_s4qeBD;qCFIr5DxsSG0{T6sHC^{8mtI-VbDqKWo&6xYUT2#L_>md&eI6k`YIr#Prhl;0*<q$<E`P~0f4E#vfdkgc%bM1rJ+{@54FS$UqIbEhCjc>gOugpyH)WxF3Q<T1#_m5%m=-TYRQK}>S>A9gpI3xa_xHMHonn?<V=DA0n7UvJFC>99~Ym7CMdT&YsAiyYc=$jEwrvRyNuNLAhw8g$vwrn;qgXV4?<H2X<La<#ZSA;KzwTa{_VQ?2nwb)mR_w>D)`#j(f}I{KucPFnpPGhXnDaD0x-2#$mo+ENv~5L&3A#6{%<sia-pnPuUxvnL8>__PFs@UDP5{M0eM5qz_XnkaS$P~gSo-WbVew|f!ne>AFYJo0!SsfNPlpayN!aElgq=E@+w>4&7fet-3N~e#vXirBJSjjR#5EX<H8$bP(}n<F`sUTm(4BO?W5kDCwFAMcM0KRwUJ`2j@TN}nw7-9xX-6oKOWcOnoRQq@yEBOy407wqC60|dzXP*%KS)ixb1XmlbH$*;H9(x49W@n!4`h;SaRZ;E#4<aK=)RJ|0jC3Fua3a1#XNtEgDp7gj>A_uN`%?y3G=#rqgI^>r5mRjDCukRX0IZD08x%xD&(}3*dG-O(wZ+_gwdR8!AN-X}TO%PP8F`a)l)K#(CTrD%a=smW!r9kO4@~rE!SvxYB3X6xVB4S<Z1NHXTC7{cUYfozG?Y@OjOk9`$qfEPQh~L03Hxbh6C*1hSnf)Xh@D83?4GSCU-F)0@nzHtBGCg?i-L;gqbM#QD7L3UsYXr}|?lQ<HVh7`qzU>MSxfAWAES4>^<-a(-x3BFm<0^Gg3<J6fap8P#N-^FjEDO{9ajBH6)MA<rWCCfmzip^P9>Y23ddMc|-JpM##czrMa%o>&z_QTI1j0L98i(F={Px2vk)tVfKEJZHN`gRb-IB}VK|&R4?-H`2`hy5|_)*6yFg+Q_Her`ttPDa-XD`?rV>+u+{xBY+Rhh)St^C7#w32fJ9bD;Oa*vW6vCK*8unw46AEG#U_wL+ADJu6Squ#{D9iV7OXwU*$DxW_~TE%3~A^lCa2q$jtPp-DdTvhy274)JyQTo;9{#8mKlA9ZG4li#Qt)A!{IZu$B00HqjXgjz6jvEo%w(=k@dXHj}q{vhi=xi%EA$8}9JEO44l;OIN%-sI3bSG&%jp1CMl=^Ri1Wv%{AoBvt*Lf<GrewyuZbs~!o~V4yEcd-6mpd0)MfA^*RFwyW>sz*PJjASxh()f|?$$z7w4Ih2cP7wIGY?~KsRQt;}wW-*nz*~%>zg9UWG$;STf02HyrgHG7M4Ng`c9+rP5V<C=CnUw!Q0Yaa@L7Jo=`dK=0WGnq7M<PmKkxUqx223NrT#ty=`!QQ{-~m73dNQaf-9qQ1-u6o6Zfbq?QRQv7FLO>-PyN>U)1aAr*{o7^n1?pV)`YoB+^6#Qn)Pg?BEDJbPU`9lm8l_knBL)}c=}C(@4+Z3d&tLK^?`m=81ld+uFfYhmwYIWgCNWUB1PbD(2chRuWL=y;KdT^v-XB}&9N_W35Kz9&qSY*C~)CUIsLyy9`<5*n1IYnr8pS1*(MO~IK>45>Xziw474}dndr@!hNnplpy@E+S};)vu{Rs~QGrxG4+1k^2%>&6^Q!i&=OQ^U6J_FwNJCcqa&en`UO18x8>j5Efl);q`P5LFpfF`%J+Are$)y1{`-p?EnSheH%AdqktW&WXQ!OBOHOlCA^GsaU<R^_>AWZp#(Qj*pXWKUKrpg8|0nh;*%YWPKDVBG9V150Q6h)`!ELY7Y&e`ciqi2zqd8;Rga?z<rNq?xcGhRY=x~W95&{1YKHAt?S1??tlbVnM{Kn>_dS3%Au5QI!qa$TP|zA5}F_j<rQ&rQd_1!mY*2K_bA8lZgkZffI^6$I=U)j=lGr3DFszxKxA9OMY^tDWim9syAtIl6`yPbNYY1KzUzGR1`I&d$4MXe|wa$c8taBZu)oa)oei5?Ia$R|CkKWZqMhzCuOp8-lF>v!7rY3RPJj$9fK8xtg^AotMVa&Cm>|W4fAapLcQX+&*>+2t@@Om8=G0c+QmvSwYaL%$W2bht`zpVzxUTG|EFG8|J*BhWyT2i=TVq`C|<5mBOIrH^p9p7a~x&`Zdij;$3DlfhG8f0yHC(m}_5#LWq?)&QyuP(2k<Qxjlp!3FSExF=^UAo##i-bC;t~n1jBIIK-yS36~dTCD%ugP;9cT5;^rZEy0PZNbfoz;zaw0{V@5sZ+mo#w25e+Z{HX`$iiMS82?rFmcL;UzD~-Rn>NprS|(2XpR$l*xQPo$Fz?5#Ywf^d4pf(1GW%Wi#vs=&Gg88n|ARHbK>vviA!~a1-9yb9oXjp#SvNUD+1hhgM9!vVfsxbr8NQ`La%xSsO`0!eVFHt`?_`AD#xEd${Qh1!-dQL^Db;yAANP->DETt8VuiLzJbXFhJQG8RArS=r$!cgCZ-bl^k!411%tWf!q_=R}2>=SutVU$I#Qe`?D57ySm38EtCklq6qd;hte)eN&C#fcBJ&|At5y~+fKk>>WtoZh9J8vj%1znXNWW(z5Nct^W-1mzgtV$DW?kWk94sqt}Mw9KFze=6#NUz7br%%g?gss%HZ^}E*v2yeBqb;FJzFxG}JL_(N0Ws^bZeln~mhxCdC{0k&rg>3-4sCbCbUiDSQWX~dS;AIZz=K^G)u#mbJ($#OMZ1kiX}~*30zn0N-nAy>(zOtl=fEzaW2F06Vllt3`U<POwR!r#4}@O21AT&*9KZ!}YDNh;`2ltGZF5+9ndLo|qhn_Bb<&PvR?agfQsWr{pFfiJCl7~Qtx;X{Z$9R^IZ?kpsL+em>U7r2scJ-RZPF)+o)udmPXGW&*C8jrMy%a=sm&>Ag3{$*4S)feD(?1F6_D!fb|Jor#1ZoIU)Q!>C`cU(Y(WGb-+$|&_=tEKH~Lqzt58XyrO-emtRH-YF8}l(2Zkh}3d0>x@9&U5Jn9oYSgNj1#H85WJ`|=mi_M#@XrE}>P=>Q=+s3G3L$qn$bI6!Q@no5$$Y?CNhzQafaG|>xr1t^xteh{-5oNDU`YKZv*69d<7&T0loR0+be5;U;?G!w+UcCvF+7L?`Q;vsN^?0SNbyL8aC6wq{V%E`9>My7vZGF?<IQ-WY{-m@$6KOh4Az~}t#l1i73`pP|LSIv)9;8}LLaiwfC-FF6b>rf3ycTo8aI9l{JpJn(*CHZ=h8P#Nr@c;F`A|ffeAh1NTd6~~?qcMdZx`8)h26i6Oln--$1C0y0x~1MX$AT<F#hWn5w-l~M2-L@s=G4z4%{O17Pa+uz)-n1om_8m;{TC#;wbnd5<FDwVpJ}V{4p%sfB&anf$sY1l<y?5NpQ-v{Cw@F_0~m8T}5E5BU?5dhhkqzXRI|0L4H7&eiOLG1t9Xg?qZolooSoFA+gUmj*eM;&&Sr;*_uzwghr>NmYsp_cbv0cjc<)1y(++{uFFu|cMHQOTWSUbz_9dZMcfjw;RlswdEM#c;J0;k^ppywPAa{5Y6G*HMd1e--t-B!Fh<|K2^@spZR0b$xgt{p?`Gmos_^ZLXf9k-<~K%0vI`(HvT1trRqV$u$)y0yRK-YblU0VL6hXwDm=yM`itJGqUbEmoU<LNegEF?(Jm<d0Q`rJwIe@pQuCNM{w{;tnU82a(_iv9GwDU@~{&dI{6hW8Z0FVD6Z%Z5(joF#8vV0NvS%#6^OHD$k0aqvqSM&OBbx&mX6l=<wq3AK*v@{UR@<CI9r~|Hg4nNS5ZG6D=<pqqQO%6gJ(8awQvt^Dqa05x{rU?|i<F@9;UJr=`)8Y^P9mTd^AH7w+SN{X!%EYpB;hev{#Nc0u#%(z;`sJ!J{Xt%JD#I!t%&kl?@$Qj>M;=l1%Lt-aunAr1_`_yAg{2PIrOeQpy}<ciPLz5sa)toW0C0Tn-}~9Al2FN8<g$sMz8fx-vW^@iP05321Y}PvUJBH1@*sm(K~ea@0#=rV(YND1ypyp8Ip?$g;gA!VW~-0{^Q(IZ-UHPq(Nn(!zH@J-vkHGrTcg-xtU96bf(kgu641m<)f$^FFj*e3(9V9z!_`FN%^!RTlZ-OF9+4LdpSHEkdZ)RvgXqGVkpssfS1S-U5<pR#sI3t;N)EQA>{Q6{`^CQX5_}`CU@z4mfI^g_JR+_^{_V=AC%C3~^k`YK)X?7=CUbpBC2RR^zSfNdRhQN`*{_BBHx5?~2?*4TgEB3~F4)m0O>*Q=>F>PmfAH=2ZmU|QB!TCw!>^_Jm2$Agm7N5sQ#EWh2R1N=G4#*8GCjpal&d?CzzNr`rwn7`X#aNn67)g5*ECu=YAlUx{#~CD=I8_0cq%9`FF!$hZq5_d=<*C|R}V-2G1*BG&LLsHHcRC?2jGTVzTW>y!O$LR>~QqUzaD>GHmtGnohJUB65PQN(BtQ~(Vl)d(93p-Xvob8+w!nhN8toEcrA4PjtAkjml%flpM&@lYgs{4uG7-HNJ0_OJFJQZgI3cR<4k6)AjK<MU)E#bIIjlN1CF*m_L?#W=P)f@OIc;LvTNODuq7!-;Zx0xrpWF*`bLP?O)xR_+pPwXiz0+N(bZeEc!9m0ZnU+dScWm^G85Gal(W#G!?fOuuyF;KINR6iQuDeeMe^}G1Os?k7uHF~4tTO!75}$P>A+YFgYBY0^;2M*d8k(@w;lD;*lrSfcP4lN_B5+*`CimU@zOTPU}S5){SYt!TNVP4Mg@q5wc`}a+bM1OVd*y*-bh3o50&Z<-ec!{*68K_&Csdt-Wzn6`&BJn)au!2?W{eh?Y<#)L6&cWzUR^-lj;k)90clm_JT<e)-SL58g?W22}p5v18YF=s=c)5r|(q-6w2{SlmbQVjOa|x68P#&7+|!ASApuI<3;E|rRX}nKIHx^pcE3`$cG|VSgy#dic2ezxd;+j?WS7X8S93!7}Op2Z!A6sW<Hb0)F=9^eiPLvIYN+4`B_4346x$d6z>tVR_Ak~URsh=3D~F2&BPUuY3nvnkFj*KiJQrhKIxlgBZS3=*|`j`&TfTa=qg+^A7jbzUFL?mBj>x@EQg2dIqTV%2s?(iL!6-ydMU*Z*p}ulRN#`LQ@|7cq@2j7B!VA(lVgxs@f5)y*U00z4;wBLak~gutBQgAzQio&9~_Dg^h|*7zC((rSe}98!S}##vPsPSFlY7|^ITe`F~;-+!Z?36WIdR$raJ3V6v)CfZ7L!gTWZH4MwW6yaK5Of?*70Rk+#3mwt+o0leK;8*V|T>53Z0?F=0P(vO!M^sHzS#a_Q%?YgbVx)DACNitO}LL!dX}Mq(I6b6|F;N_?E)NTBr1aTN#Dxx2)WM;p_qHKq9|y2cp3ih4VPlW&V1Zvlw<?b^}U44B`(q*`Rwie+{U_9)nPg0%R+NmQrRvMsK0>3us94~>i%ljmyhEp7L)L}K6i9<nAB$vkDc<}DmJ+1JkStnVi+<<R~D1E+LbzSv%F^W%6}TW+RY0#WRw=Lt{Yf=_)Mt#LaB*y8Hk&1~VP%83)yeRB@YX3|3_d%K(VJ=>0O7+<e=s>sE8qh|ZN11cnY=Cnb$B)aX=U44Ik5!3apy}}VoT?e@ule>o&@M{M>Ck`WD4~H-uGj*ADnCMD-SOp&ZS-@2cy=+jhf`Sl4tV@xmh($#->j!$@THNC{w(E}3L#w~wI5os{c-uwJajM!mYoezAI8%?DEn9@!WP|V+2ep|0#I9H#A%zGT1LbOTlni&QCQ4bf#TD{cBC{VZHW#qeS2wk^of)jzj9yj=hw7b@0*1%OV^sZ$ahBN++=-8YG(!qE6`?{MB|KZWo_OD;;PIh<a;kaGIvT0T(l{KhjaZ!(g~9KyA%&i0^Jgc!r#z4V9SMcmUL|F9Z7D`1z=rnw)b;6b2A@AJ&n=rzIhyv1fG8`|FuOoVnbUwu%%PC&!Rfw9wUgEfU1fpV9Z5({rq%-4?*%Pl0QZ>NU8_Ums3E1MS^0b<)P*moxuG=?W+YRop8sjVX7DO{6#Fm120*rKVwea9fW-O&d;sro$ef7Z^R)sbXdBL<9z_bZkqFg*ML_vsWU%B<_rhstA2?lUTwj9-SyY#wx3TMxJRS1u^46wi<_m5ZB-S`h+{LvKC;3zD0cx6Q1DTp=e{O*ii}{16^?>cj-9K~Y!>2K;zRR2sbWceK2YIyK)$aFGB=`HT(X4<Opu3AbSQ%KGj+U&E=A=)UCf3rf-5Z0j`!9Fu)R%@qdWJaS{M{>c!LCz0=Y&{`+PN^ND#5N9Dj1-gOyGc&I5FrDOyWya`?lk40ogxl-D1R?(Oi-$S>fz&agruxsbuBeCGv~w$=NWU+$d|_5_TS<=}*34kxDbc0+NXBO6z=1Gz(6%VOmWQ4C<MLv|MXJb0>+12kugp`&G>Pn#K*nrFUsES?pbtF<Ij2RWex}2JuNre5W~YS@vy9$Snx{!Tcp@Li<KyVuU+JSF85{XNJww`jL;IFWVyvL!dE79mI+c(92Nd3X26dEzz<g4#9@4%nI`8ElO9m=(48ZM@z7$Zng8mrMx8is%tmNHR=3Lq<;F0clb#`oX58>Y1q}YG+F2RS}n!kg3VoGPbl`lt*KfRV=?ZJKC6LuiyHg$O7c4ZY8e&B;I59JtEUW_wr?sc(2tVMc*}RTvSzjfP{&>85b%b=RpD<GcW4?bo)@SOb8@l4XT@{PjTc|^6&s<RR(=DfP-9N&&?L#p{!{SP>I3nZSPjbfpb-tYY&4lH*olKin6K2@%eeoF3mpb#Ky0yuzm>9RQP8l{hoi@Ia@P8#%r@~`zn1C*!go4a4BbV^V!m-S=I=E+`?rA?I+$~0_c)nR5*t1McN>`z3N?jFM&fjG%c$-#XV)3xcc^4q!7bmyTkq-1A*S#L_khcjEEw$^SJPC;rOT7^Q4d^-riW+G{(DR`@~{9ee~m<k6S$QqS2ykSPcH(B|M}haCqmU|x<WgY>Gqwq?BatB3S5oP8|nX7GW=IYQ|Jod+BBzVE-a%!q47ZQzyW1V%|E$I^%*cC0NIms?U50>orks~T6dt`aBsgL0ZlBJM9>?AAW{&DegxGVai;z$iK1M6nx&5k(O>-r@WT+{PZ+A^En)?|MM$xFh?v!inV`2A*fkE$W9Oyl;Cl~AQ6MnYoLAltP^3{5Rsg!S>vj+CWt=tRE+m7cOj39V)VhtQ+Bx0?E=y2A9{<9Ahb%`l?q{;ka7J*|X4Qz{ihHlEQCYXzGzH`u`PGl%X%YpP%Xcs^nP%l2(1>-RMUd`(N7`Rh08LRO$NhpHAW9|Q{fIWiYME&+hzRNC!1yxSA%aES&PMqTu?1N=GpPfk#|vyBdW$GndJp_XaE7a%y#cvene81P*jH3WB;h`d$}Yr)3yuD~fHZVF)hoc?%~*%8%v#gG6QLLxRZ6{#v=IppG5=UwDmgv1pMy&<a8q!Id0)@!fzhD=e376Ban2RG<LW~AtJoyjm<37<aZNOqi?g0hE)k)>GHE4Sx+u7(Pl3k%N=L^gGdCVxVN9Og`TneGl}b{&6QFt6gKOi{|Jj!2c~L-tXUyrx==d=ABX#7>xOIvTO^O=3c)6_mHsXRsKDR-XdDC+D_kpm#7sGaEA1oO^+CvES{=i@*qzF~O!+9VM{IMu@eetTeG9O5Da~UlbjjjX1KN~Xv!qs8N{niq31k4d{H#qeBlCW{%x6T_(Zaoa(V6l!P7^f1IXJgh*qM`ca&t+S<E=6ONBc1n{HVxaiMJDT(rGF@BkzQu;ahsR{*pjQG?aZqHQawv*q7*cS{)M7*o4g+5?OHeoB2XvKP4QO-KEt+HciSS0_uM!kb)_isSe7&6e2jzEIqZxjf$nxs5!CR}7VU~pNv<CD*;K)2Mc^q)^m+7TF!vnaiw(a(7^K;5Zck?qiO5p;YjZ^~vK-#<D|Y8veoG*crudyY;u-RHtz%ksk)$Rv<!KLwJq9OijR#|fXe&b(m8;ucgETaq@1YHb!o9iVWoOJMIbv@gGwBudp*Dbz083xS<bf7R9wYP9-^!jaIzL>6pL>ox--FT;eJmzvik$zI&FVMps>7xEqw!6c0JyL=J^L7GChEDRwxG)v=_()|OzQj|>%Ri9DMo!4(1x3u-`EC?$N9^<$ksF5S?X}$(ew>a=>_~XRmWo@u?*O_Vr$mJ>{TJwU_ZE>htt~zi6qZ4pT6!`h|+68&I87Plr9Zbk-)k%RJS=$tG1f;_^E^iA<%^Mx>OQy9ir#V(VS$JLrU}dxW|0b7Fn^=+<|s3W~6>5H>;&hTn34_9VrZd%(}wtp#{ow%^%%<B%W6hygb{c<?|%}Au#g|eZBj8=skB@R$^m~tjZDhcOYA^OF$l25+&3IdcIQQ$*U|5H{}f#cV2C66*<tE{cx(?DAk<`N%N6$!KV_xzAKaZC^=a&1veZhR5M>mKHIS|TD7=tv%El8B`kx>A%2nNXk2rvPrV%9yfCWOx}8I{GQFMek6Pr}1BaS)ngCq$G|Dsh1Gu0wF5A9^qRbtBOnqj?>$1A7^M1KM9%c>i;NVLu^xq{m;Phs2n@0ibB^39S1miJu!zTODf;-kHxI0T>%w-k!C!HNIlqrbhrsz{0h;nI5&kTlAZ@p!igu!B-v8N=UIFkhT37ld|drJdq7l0j}3}vCH9_uZlRXK%%z7O0%n3s99dSt@>Nk{H<31CjPz};Ala4%_II%mFs|EZwo>9n_((ag(O8uxH;JNF5D_NQErrMF%3`}Kk}wXRQ3QbjCbUE5hW=MnXwhSm!W=^bz+jMjCsJj&gYgc?U|T@zPq9n&pIQ6Gr=)ITp^p%BDs_|=#gmW6=mzW|QM@HwydS;}^1KqbVJZsDD$;53?d1ILf?<li&@^s$oIum$xgZd$C_Ca@WjS||r8{YJJ-bLe`IIJkDzMTwAlf36~5BN4}KdvW_{As_>oLul8X$UR(g^VXDkuZ#Wo`!Qb@d%`LE==Gk*<@5Q0Fs4=cp^iDoj}#$;qPMQIzd1uo6>)<5)*X%nQF9lF!wHI~ZVGQKQF8<1Xo`8*y=~kKE&_x(AV>MdnoC9<BFwpHc;oJYE<XH2eec77o`yXm`*z7f-5TSuF`su5oc>EFq|lCeX0g<>JM@y4yTV2#2J-k#qgX0IQbJTNV`v+8rtX-U9Ll)0B>$iKuuwHwCN)G-#NH$FEif!?dU6V?{-1d2m=4_pWLolvj1y+jshh9?zk7U2Ms4?V@+5~0UNprss+GQM77IT*<t#YvG7Rf?;wbq&8N+2fX$j#n5<uNF0<o2{!FO4l%p!1@I|=n5hyrBzybF_^<|t`Q*wKWlxdTYK>NC<z%A)S4deg6q;KMKm%F^$1xbuV$0NR&DHgrw6rDa{B_yL9wE{T&cjW8D;G&eLN&Oq(ySqT3>zSp}_#zsWAKk4L4Q3q%k5}tfkRB|oG!kp<FR*KEMKGzaMhY{X%Bw<@)<$H;<Y!Zz0;T@i4_@lV1>YVl4NoyirT1|UGp_XyWHI4$xcVl%ya5TdZdFU=(+VGkA)E4l66MYifuct%y?@4cNwg^#32xd{vTCoDhi;@G7&%tIA-2IfaGrCSeeoyQ;Clh|tnAksMt!po%D1`}PJNc|Yn`d=w@y#p0C7aZ9TEzPUV6(@D@nT8fc4&&4ExhUCypXH{8NMA@RmXrV+870g4a2cH=rwf-+m;a-k%wj_oi`$5)I)O=fkmDRU?VeH|Dd&(YA31N*G>qeAl^a-ILeE1qmgiZT7K9wE#4SQ-NjF^r)7Xn;r6wWz1^4zB`V^X%dNC(uUgmeK(~mx{(?jYp&(cLtVOt9XNB!j0y%cfX!j*QFt8o|Fw^>sPaZ<fH3{D8=*vtGy*r5NGjDH=mEhcp09HrD&LP0neqQ4+N2xOwhsy?;ozRUbyEJ(3Umh}0E&#qW{QHkf8x2h{AN-BiW9*J$DF)9xW;Pyd5E8If=h=cnl#*dVQBI&{Rc(x*DAd6UzsXOmK)kW;&qL*#azThc_{AJ~05&QG{vOhVBW=Wl<z)ur-x-G|uNh*kUkyC~p#`Ai)^Nm_6KsESH{$VCM&_lu;^!u9&9D!~000006RX4$Wp84I00E^<w#EVgPEqQ$vBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000000532403905683647430959109452965243620782837234375708760039601537905125077057799423129974936', 'computed_previous': '0.3899999989307247318489782176179490676417933906012970359557677939772168163439143791127440386098166863', 'covered_success': {'lower': '0.3902194545266874834459493198164848109952437012952770881439272509953635208205254011198752067935755811', 'upper': '0.3902194545266874834459493198164848109952437012952770881439272509953635208205254011198752067935755813'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000003495532041597471106797456741333007812499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000003495532041597471106797456741333007812500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002019399190324609319807351394521964552071807439097782180180467824147907989078201970912195610715013560', 'upper': '0.0002019399190324609319807351394521964552071807439097782180180467824147907989078201970912195610715013562'}, 'self_coincidence_F3': {'lower': '0.00001167635713762045536386198925739766819547137426389886169815918112993546244725192502172455208609607103', 'upper': '0.00001167635713762045536386198925739766819547137426389886169815918112993546244725192502172455208609607105'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000002342665235413151771443338925824415225857661256267636442069842495251217018264407216695367420490133633', 'upper': '0.000002342665235413151771443338925824415225857661256267636442069842495251217018264407216695367420490133635'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 681, 'HF': 111, 'J': 66062, 'LRC': 41871766976138645360837603576774656, 'Tb': 1326027569208392007845194752810024960, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '588fe4d49ba0bf31cc3fdf316331c59a3099c02c5d8485e64e57a76d31844bf8', 'previous_grid_upper': '0.3899999989307247318489782176179490676417933906012970359557677939772168163439143791127440386098166865', 'round': 13, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 88720, 'union_lower': '0.3900000000532403905683647430959109452965243620782837234375708760039601537905125077057799423129974934'}
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
