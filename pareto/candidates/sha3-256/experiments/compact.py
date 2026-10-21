










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
R=12;S=18768;U=93840;SPW=5;KEY=50;LINK=2180;NREG=2192
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 720, 'HF': 111, 'J': 62492, 'LRC': 39609010654731255879165988355178496, 'Tb': 1325810588030066223532131533912539136, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 152, 'dp_loop': 408, 'one_dp': 410, 'ctz_0': 417, 'ctz_1': 422, 'ctz_2': 427, 'ctz_3': 432, 'ctz_4': 437, 'ctz_5': 442, 'ctz_6': 447, 'ctz_7': 452, 'record': 455, 'probe': 468, 'insert': 492, 'insert_done': 499, 'match_0': 502, 'match_1': 505, 'match_2': 508, 'match_3': 511, 'match_4': 514, 'restore_after_hit': 517, 'continue': 518, 'deadline': 521, 'restart': 522, 'restart_ok': 525, 'restart_nowrap': 533, 'setwalk': 535, 'setwalk_loop': 540, 'gather': 552, 'gather_loop': 555, 'restore_planes': 565, 'eval_f': 822, 'output_message': 852, 'match': 879, 'measure': 888, 'measured': 896, 'advance_p': 900, 'advance_q': 907, 'advance_q_loop': 909, 'lock': 916, 'lock_loop': 918, 'found': 931, 'replay_fail': 944, 'end': 945};EXPECTED='a013f220d483e4ac7c9adac7a76a6054854323a27962294408848714e143e99b';NI=945;NB=30240
K=(0, 0, 13265668776992266707, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 7928103212675454578, 0, 8575737624765115194, 2590537648358642454, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(17280816612797506951, 291745068822427891, 1165927463059528306, 1162491935228166656);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5178952548521767372163578448576513)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;G69wKwSU@Z3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+1+t=8IlRBlpzT5|P_D)kV>w%cbY3e@Uqi&}^t?PXi<3~ZvPtwG0FNTIDnbZ6rZysS$+wyYP7$~ndiXjl#j{LB)L+%P)3`6C6&2`rbgxLJTDZ#HSfZ~y2MGs(jS!dnr-VFjDqo(JYb(SEImc~0-))lu!SXzyBk^i#%x3)2*t*ejkJ0tj%OOoqk5^%``B~@_z9H`KMnJAaYxsmp2-80BqTOO#oC^Q%8Sfk))VUVRxzWc<<>w!$1`@}+9J}brKFzHb}9cP-8(nf{mI-fZb_pmu`4)JUj>z#xs3rPm#XY{c4y=_&6$+eR<Y&-OvY31^i{o43=!{^c`y14ah#Ry05X<EQYF?>O`7%fYig+blLbsE+Q%Do!yI8VQn<EqOS4@30NQH+vNU~|Ws&9-k2V2HM|ktnL9aMd0ii&1~zH)Jz&UUEwHI`6$Zbr+EJmE%R*P)oQkM{YK&P3r@eHKeFa+=TDP;S2jW{_}$q7qicIcJhj{@Qu!~(@~E2mT=9B{-#Mrcqm@P!rI>4RT$_2!kP9cL_(u%C(b!nmMv=&mH5NT<t6{O@U(ji9OezCL=+E5ZSmp=N;zNbJLgzyK|n__059}$EkL}%&PmcA;09c)uUN&2$*#ZT=Y;5!kD8DonHd%wZVj9chSLJ#9Vx(BX#8twsNN{L<IaUgoI!df84>(Bl<-z`?QN<PM)ZQ*7AY;Ws<hKJuF0bedEy#DIC`3WQEQ1{92`ZfX60L;MC-!*7w-Mf))1<+gTi)#SC6cD-?X##0?l+`v%lFRmzT%@@bd$_%ix4qAn(4k$I^pBZ5hmvE<O_#Ij-V2(?T7$l`3Ll`~#D}gxqVU+M-{ov440jhmS|@aG|XLI4V4#6(61PMe#SlVsOdcc0_RCm>du~S2w<J!r%C>A!G3Vwa=Nhblud!{D8wF)sJIF=<VT7j$c=Gsp{-5lX&amo?F)Rx%-{C!R_AH4(<vNPjwOZL_h2xDAWUarHp!O^5!Ntkyh&>QdZ)9d9BWfTE)(ofSGun+cI&M2I`W+HZ1#8>VUpOe%GvOx%;<sQ6(hCSY_G+(fn=KrNMp-7vXD}x-(65lSB(=+K+_k<IjSL(r!Uy>q7s<$uBI8yiy5-nl@}F>4Z2h#2f<mJ~&3|Z-=KTyY)Y=x(vn!`b)&noQKMH(;2tht)XA;$7kAf`TjVeFH2e)>`1~g7a+JEsRQ%krYQ;=0_+8>>?WYtb+q@@$B3;LY~B8@nT3X)Byk`Vuy$wMc@g0aWsc|yKE<c<)Z^#C167kg@12>+;VRQ}@{^p^jfCk!m&Pwyc)l4)ckrqZ5J9vlbE@#NdjaM`X?v_JU3zL)`lh<@#BOVXhJf(zjx${K{%N!E=_T0^@kNMp8AlMmtl=GlI`vseV&ctkiNY#@)n9TDFKqpP?bY^G_&)5J8xQsM-wFxIQ%bn^0#%A*kFN#cmbvP@t8nObwM))~Fk9ZBOHFH1yc}u$0}+j_!hvXG<^;6sDDh5aZ_4AMys5?Q^D(c+4l(^()a-u%T5b+_L3M?Fo-=j~-=fT0C89fr0BaWs908q3t|GV+ZF|fXnaO&{=r*#s3WWi&Gc6s}vIN|okU(zJ2j>@8V?+bs(D^oE=>@dW=@bqP_lOdfjt+*bwv(fXo>zqBCtmD{rdMUQ(#t<{b>PoVP8L!l5%@qY9L{`hMTrL$ocL!zgI3q#ybI;+2j7*UMrrhWX?=ql<Cfjr%9$b+?%a9D5W>N1Z}VqGz=DLw0AW5p(gN}+&wtM`OtCal3cq}87JtJx!J^&B^Io=b`t0pp>>JxjIgUe=cEr>%OkVJUVJl=WjaY3~A?f5?S9?<1-(OuyVFQ{R6f5O?p#9Ig^tqLONnNH5G!>JG0Y>d*^7tvutt6ig@gHV8#S3%sjf3F_Y^8T<`Vnd5oA4LYdcFexsgO-WHWjf_(xApNG4-+L#fPE8wLJG<4EJok8(`=SbIT1sAczc{>9LDhq*3oX;5C0E;n^r9)$Xrc?VOx@46pJY6e01;ZS`rXW&db!nYboof%U=_JW>qgZeVcn!;mS&WK?Ar@;L&KNK=kY_5*k6`^`w)=&zd+&=_C&XKN!~2)G(FYDx|w<K3)n4;?^gZAHyb0g!4l6>w>v``|{5f;0B>4%vse=2g2$G+#_1h+hrDf=RIOr3zhn#WZ4aA=UZ(U(V0U^Z@zAm@}wSa(Rss^CaHN;K^n`wh&ij3~?kEv(!x=1R(OQ0teS^oxOHcbm@o&jdz`+!4pwft@9+OJiaJSxR#aj&0aJOZSa3Sl>%MXa&%m<s&(jTqBBCr2T=wJVyL;%o7$on0_1|>;pd@t-urWW7mgxx=tqSw)@nDK`NV9^?ynJ#sjuzHnZDM;A7K}w<PelpTulgV7%^vVTVnNNBPpJ5Y#bFht+HLXNM>45Cq|#=>}PKcG&Ch07!cB-u6j`irnONG7Srxf3b{sexOn1ogweWVA)(V|xlcv;e|ZG0jIt%`A}%~iKBfwIt7q*;f53unr~rQ<yjswuRK{^@HcH8^Lw>r5G$u&IE1)mE2AS`NE{awyw$1Q0dWPD)X5P`L%wlxAN2b1I+GCL%yxfQ!w<n3iPqAP?DE08L{^kjBK%BN{DO57)%Xg$fha>fFkx;dv5M}UOE~HCGn|jh(e*MPCJ3KYYQ3Jf6XwrQV=V;0@=TJsaAfW9kw>XFP9W-zIy8r4+V{IYY<z4;?2Zr_ud+TYk9k^F`QJ;hc#LB-3oQ9r2o&8L_7ckX=(kz0#wd!T_<7q^ni1rd5v}uY<V0W<LEC28;zY#toN(D5?qiyK$=bT*Abq7vtLGnu4Rn)JUETb<fpM-e3egfNocOpw0$Le3K&%~dH8s>9zWhKjx!rtjDBuLs94p}gDtTzP(AAaQd<ll*q+J;Z<Z1T52^*ok=$wezbJPHBb(~GedAf+DFh;tvHL$j@~N^mP^rvwax00%rYfI$X-A=lI_^)<r=*w&EVJwom}G-{5I);8Z$`i2N~p=6&?kck)7Kw=RMeG2X?H{1=o-b$em?P(W}uYq{NG3Prayjd_<s|>xF0~t;&a$PzCmrTc_pi(;wzq8ZSZy(j2Y_^HjaX3&UaG>CrLbk*E8B?0I@l{fs@5hbyRWv(VQD)NKCG3PAtMewLUNg~o6lX(9@BqA$A`7-7`=7)E9{;;63~uJ6nVs)>Iz~ruh6ZtmbBoq+u-i5=(Wqn#nas1YUr$zj$aowkKDbP9NG&M^jt-_V9B<mW^k$2Uo6cb0e+!;}H-&KyT2sOu@&o2Au8#FOc)s9mZ@ZV%jgR6^y+rk}f4wjH52%&ap3AGWXjE2>_<c!Ru=?R@L{Gx|^!*YYhucRxbc)p%d*_WXoOVUjv<B(eB-QqF79fCm=+~G7tW5;mlx|!3t6<9VI`-XxTKozDq1c&+fPK-WeJUFuLxo}@8Z?u$Om0K#DK~z9mL)9EqO9ekN?Bt+Qo1@eC#foXTCr2i3LV}g=^T71@#wt){;`BX;0Ab@q_`upf?x1Fj&R~!?1DZUcPw61*zgm}646EkN|3Um^>|&}Cl&D{JVdxnKCmPf)!#WS=F%4OrV4;DP>VNzl8fEoy0?>c%wPfQc$`QZ%@pHg4PAy>T6{tQDjT-PrP90fpimOOih@8OgDAab#GO<<YGN&K$Fh$v4Rf5oTmKFiV$`BuitWsiLp#tM!%}9e5RDx-g;<}s$VSBt6G29n{q)DnV^4|`BSs+!q??&yKRGpd$v)z|4r(l%l&>PskVA4)z5iK=4n0-KL`!7jA9Iv~gBG*9tz~Yw12aJssDlL%v(TIP1a1fJ5%{afoHpxiEl)|wl6giEdRS|$_5w#yJ~#cDgAfU(aL}}cMWqr06;7mvIN7ByUy3C?t8sw^W8t7o4*SmeC-Sw3v}BFT8qMtR(;&gj@*>EnUel`S;ROb^A@Bw79CLS>bS49nyp{z=vS^?$_L~%86{I-=F)2-m=^$BF*3(8$kF{>@GOxYf`-*(q|6ro>K%Ow5vLnbg?A7P5IYD%ZkVJy}hbZ1riT)w)`)v7Shoo}3Gl{l*=>=X5J&{UQ^?cezH$zn@kYQ&i10vii0E2F@l0BmQo5P0?w7>W5*wX(7$r9D;5dRzbc`DSP+?J+5o=)YX9yp`2WB_Yjh<@R0_k6%cQfX~F>=-?9kSMY<cca-rW_f99;FK7gEw&rhm)%?;IVSAyf#|&1g_j!U)|^D$0&n7E(*4npOdJI-uO%2eQO)ed^i2?S*V0r|`NyOac|fH@sQc^S>_}vR#nqN9H{E|;cj+&Wk_%IlLteUcbW}a$@NNxoEpv>)3@1(hI-2#SOjOy|dQ0CUvV1n2|H6Xzou3YVEiiV#n}qYb@^r{9a$YJbc5a3cA5rmjq~7Q7I#ViYK^>)*1D{uHjgWe?9n+oePJzI|dUK)O(7GBBej?whLvA%ooml@a>SlKItl~)L!`$<?C8A*ah$`PF{%Y`6sXqE|aa*$!PG4qpK>D}Dl((Z&!$o>ekJ2YxKvb{xM0h0~rNhHjGL(IEerDRq7TT9ET%_{%v`E1Wl~C099H;79bw=l=<K|Xe7b)SKMuq{i%X8YX&=R*w{3M0o6XFN<wpF}!)770tWh0@Z?b-ZWwf2EFNRo36CC3^&p_hqmGuv;EnS7)f)We$~8K|Xu;h~QJD&m+D(4DDyo!nOlo9^jKGiStT&Bs<wxhe|j<kiRkD^lfC)xy)z3j%+q0yg3ZP7RTFK_MHSB{JFOKIOghf-l^ReKs^+GRi0ildAXGW%Rm&au$XEnYA;SD73vvMHpcKDYJ$?m*zZZ{D`zzoPm1#S{0(zp~L8v22E>cd!C<+`r*FNdmb=^A-jK`j*AgSsVWw$(u&RdvtVTqKwG(pa2fOEc?hOWfQ}Takm^vh>aKmEw?v44^-=b8wXd8$h~4HZe5XKAA&?V}x0a8V9rvb6iE2^!lrMIzsaDO4P@-mf2!$&}l$b$zd%HQ0KGsnBUbh$T`PuH*bKOMv8tuPYO9rhkYuFtcBiseCt?7+?j*6ISKOo=vaX3q8HUao0{h9ch#5)&M0zzEaj{qnk8!)OVZb>$lq@}U^XJisOwGi1h1;is!S45TY-l>BWl5~AwCE0xjA!h!@5-))y@fWaV+~rCYBsN)meH<S+GZz7$R2&|cI|lRmv^XG<U=5&UJY=|VE4^czx$5HUAWisOY^pn%ZzTls$Obf3mv#(pHf=UWkUaxQj+ug(%-AEQ>W6Wdvi0)31Q2#2B#r<W0Nq%~fujX>QuP0b&I7<|p#-wWJ=tIgIWArs^jH6lBs00WZR{CZgG=4c<~G*{@UJ3gyefbbj2F=00t(Ge(cDGv%LJ?6Rd~o}xS^GCG3u87jj(S8Jopq4<YAb*YnYFRek0?AZcHFM<T3Vl6A*_C*?J!MeRZu%!&T8Q=LPa8CV&PPo7{xd;own&h9n9lyBbFd6Ec47iM?pk+HFbnqR&G<JH06@#8&Xs(aQ~HCuz?(8Ss*3L2n{A9GL<lYG0rOv7xlk3)&HZA#%L@35t>qf8p-Usm*A%n-=a5&Gg9g+D?UhCqb*iIfUfthB1UKrNS6vIPkD56infP<UI-3MY+u>$`6Xd#lqGLhuIm4GJqFG^!?B`jDf4U%LcUZ{k{-pVfIQ#XZ*h8^Eu^E63xS!M#GK{;9_{NePa#Ck>4>AMjb#<0MmCep##*K=}cJN11YoB!gzoFozS<?{5MABqyGz7S=`;TYo1XAqwT7tRgvw85|!RG&pfg8t|5jl;!$OUzG8wpp8AM?7G8~b-_xmGk220cr2jIn0H55gQRb|0MiG+)VM~!-C6A6qm%jD_#Ox2?rnP~B2P9hby|(&(qzIhl?8Bpcf7<3YH*xLJXwE@^9pE~rhkp$rCm19)A&8mV<~6T*CKzXgC$n!=S}WS92Up)}!ovV59=5X`JROICs-EYOtHJ47=k*mc1Mkp3H(?9WX|^vY2n-gJBro)i)-oHusYITEc2&Xn2noC+9o$<=jP|6l*=?2h$$V;!8#=z@aO8hPrM<{k;Z;JagQvF^LK5>o{*Hq=4yCEy(F9^Ovpzb&*8i-@uZ}1ZGNS`chEFWQS<jO*@`jztHWqkCo-)4}+>ulZ&xM{1{vE-lE5j>OMJC*R^)1OXvjbXVvGTwD^H2A49)lVKkS)6eXXwGJEIg-7((-Y`QYkCR_Eaw)qr0#<{^rf@0BsrEQ?W!`EHYnexbb&VN`-ke?-KkD(Um&F5AKjhTzbtC`S%4h5E60->1pmjM&w-Aiew}ai>S5*Fb6HkRD%96=s<I4&Qo~O`nU)V%^c0}RX~Z27gkbt{(O`Cwp6lYAXKt0LLfcf7|-!Ugc3Uq7s#}z1Mp?83a0*%_TGQCcg={Tz^FYL!<w+ij1DhTwduv&Ud0VeQSnWrLAde?3cIh1^G8WZ1jF_YQbHV#C{OD~^95fpr;2>pKleM>C!T93I`^wHw5kqhhrK5A+3^P1HA-!$sOPNTPt_GFm;>tX5o9~{c)-uW>MY>+b4F(Cl}&9BELX$bl&YC_!I6}=7P@IOVdU;e5>CbM5k~V<rM=H~Ai8R2*#$s=Vju%gkx>wG@r~?k(7;E|c%t#j+V|V+FA0w)$Pgjl?5!cSdUAixS=?RuD9BJlxv}4LhBlB8U`SEE&v1nQw6lp^{LHzAx$g--EoLtl#mYZR2WkBqFEd3WCx?WYVO5mV64TGwev^V8V3z$2u1U}7yO|mP)iOp1730j1r9NT$8f&Q>40cC0=H4f3xtYe?o&yC1AZU<|h|2$J^5l>m(BFD`)>3cR<n?d_0ldBQ3{R(SzqS&p;!m=VNscD-*F2xm_FtyFVzzkJ+K59))N_A?^bU}JAGSX`gf2(Qg`QB~x6}fWqp?+F1=i;xJ<NO$r%0bhSh#-t&&DZQVz*RV94|LnNBOnlUQp(Zx)JRJw_On_Yqd%bhrTHV4v~qGTmZOfmLAb%AFvF-;e?MV@P|d+Fz?`B(EGT<DX<m%5qLM$wV6QWZoe(lwbCU+ea5o^>BAsk6ZO66NjF4cy+Z_oJihqZ)iSFgm?8Bn0?9twAPvZ%x&5Kr(?KX7_rGaYWIm|Xy)5aj(uDPr;LXCW@45@N?XCB)3imtHC>X|rP-H(17k9h}qjt&5fX|Y{yFcgJa|#Yk!DZBoK?XrL_=BL%nB&@7K)i>#nTBI$2~7E3@Bk>xwkWzJ2=&RJBZdW%_$OFA_mK1A99kpPN96?XCKeqoL;LEmxHoF>b`H1{6Y7gRsiZu}{jGnd!1o);ZhQV5o<zs_F(;6ApZ12NXdw==b8@&<f>v+Nh;vgw7A%@&dxTZ6aoLc23Z3j-_s-QFrVpi<mZRe)0wv~c&9O893B8R6OQAiWwl%mG%Fyp>ng4%uQZP2W<QJHCMl1hGR1pm!u&Tp6zH_>rTg9XgGi9s#Og#XKKvAT7o8}#U^(8+G>H8_u!sw~tE;yts-H9>IZH3hkB4>|ssv6JJ|B1*#)qenBrT?1Z`w?^rHB9yYRNVDQM7;8<GB!K>2(Lv0TgEL10j0z1t30Nb@qOG3&(vNWQG+xh{~S5`6ypqJ*m@+?kY}*qcdUX)Hn~L0)`Q4zCfrog;1F4fFEFb<%!Q0hpELaZ8X4>?Dt;kPir`O9;k3_l{<TW!!=Q_xt)Rp?CwHm4N2Zl9N|Rl64Im7?>Pg8h?$v1QDT6JVUI4|00#S#;dpmt};1Ov~ECa}_eD@%X|C-VKFyRJB=vBZD=Y&~AjNnAFWwg;l&&>pG{+aILdT&pv+kJ`f+Z2sz)8&MraNm_IHE}ViEoiq`7o&$h^fiB_RRImLziuJBZ{y9oQAoo<rpOJV2&mPKb$95$SQG6_#3oxuAEt_Oy>tJTf6RtjzdKkljm1S(6K9}3XUa+69anz*<E|*o`pZ!Mq!ihq!kj^xe2H_ToLrbr0k!>G#WAzT-T7C+C%Htx4T0HfHTxa~4qID!2UlZ135sZeIwVu}qnS6EVkT-H_MVlJWq8Ri#|=$L>}Xea`!J{9AkEVgvNgjyv1Br#%2OVZ6F0p@GehGPBVP+NAA<#y0v@@W=tTwwqyER5H7AhvLnGjoyggApRwF>D*)*zHhaZoax;-FN9kuH--%m9mxyKS*yRll&Lcp<qx3$Bi=3i-U(9oijw&#aR@JtSN^hSf_=K>QhVcq-Alp}dVDZlWLLp$aVYcsH6jRcGZABX>?&&E4ZAqlwr1wq!|6Re_<M(=4eZdC1HH)?vv>c++-?M`UOT!*6vjbkFJ!^aLTRoGV$)c^>Q_{q!0SrHtuWLo0IHHM+_ewJ%WNB%hyJi-*_s02*lGX{ZJX?*5yAlk(cc`eUc1F`qeZZ@4R<y_U_P2_&+6uIVv!?)Ssj&e|je31U<ga_l}vG6~A$Hvcl>LllE^exzZgZ5{ulRuN|(z&JjvF-X4yAAX|;lE^w63|Lt2$VnM%Z!|LaF*D!f;~b`rGtz`#k<fb9@^LQVon`KldJp6VH*0WY=a9P>7~a__mmTjh$^ncGNMko*L5|SZZJ-WgXb7P8IiGUF4sfDPlj7yCJ11|;BpD13mek}3Iw~iRGjZ1RLLHy7KkJ8POpmnX+v;VOn&s@vtVgp68#bw8{pXh-_mfgGZ2Pj%JJg_8te-j`|K!XN)2}5>wwHZ4?#&zrI}^Go5Lpe7Vjo)&_>$&(RNUQa%cW5lROlLa@hz3UVE!g_P_XrN=T->Lx9;B=2T!oY!RpSNpqHF5V_ELlkc!1-VWh2*IE4=cdu3f0}h%86Fg)Btsx=8w@Hj5%Arjyz9WP_9dAZ6!OifWTUSqBEfA|Hp_5=Oa%q(e#`D-&ne0qd&MwVXOk5X=?Q4@2HjHmJi8Y%`>3H>s=@OwS&C1A1Adiqv-yo=BL2Cp;JjN&S6Q~Kt;k=03F6r3^nAI-LAu+D|x*Io<46b<<R74a!oJPAE{|ts#s93Sygs$fxxo3QhVY(e43VO!`%f=rd2(X~M3>~@RDm!jm7~J1f52K(a`9GPN3?92n9fkT+K+7RKWFyt<u11#+JplD36t<5EczZAQdiYlMNm3PD;`x97cPGmwPYNbWC$bd@y3Yp_!%g!^tbzo-8>LgORDVPm3^by~;Pi#T%U376#F9kJb5HCqgTsVgbp+CgkyK+YeOPQNNZt}`s(vKiXGQAWiXmRwd>)wiPi<<oN>tTG9v87ADG3$?^TQ8UvAnlfo;7Y?{NLiKQd;PFlIvKMbS26X>=~tBks?t6TdX9_Colf*{X8EE*4NRGT|TpY0>bYy%8!|%&PG;=M0=UMj~zyiD_t2Z7<sH}siLi?)TUIf@!7_B1hf42yx%OHS$-JK@$tg+RqNa0LTr;(;r}DkVHKeE5KMRJ?j30VotW*perN!*PvQKmnWnA<8R#M>-^IYq3%+x`_?B!Nd-gvrP66mtn9(|i&Y!smV1<YhAv8BLXkQ@n+xHhD!7GpxI`HKnck+cAUH54qJ|N!TQ`lC8y}JiMaNp@=`Ehjp^10Vcn?nikyF!VJ`Z^^#1lFo%ez%m1Xn<H9Q-ydn8AMHbJzt(p-?%ad8tDXlT{IP7&XsA2`j1=Lp>T|Qv%^)YG@^roA7QrD87-j;DnsaKV#wPiWnC3|;f3)PLuMGlrIMNJyzNTdK3FxxpKVqYi<^8f=~r$wloIoriFg<mgmxz>#GIYGovtrmm-=W%ezADj9Gr?`%alFSyc<&7t2?G<11{wH#q_j_4_<=|3t6YU8U`2xJI5>WAjAyc`u^QXzL#EDwohS5C37=pUv@&W_2s)%?KDT!uJtdZ;Ls~oq;%!WDfc6IY{`%3r5D{SXTPKM$G##7F!5^Bfe6<JIMa1<msf@rI#c~HMkITva7}73aG>kOFmyNX_s&q8_RLsBT24N6F#y`OAwsz0P67fN6;w^Q>G1hUh5OgUlSQIxMVvd=Snk^-#|!rN8&t$4L<ri>w}s?Rv(y(2DZ>rwAW$-U7zO|!<^04gRAp_>I&MqxEOcCkkYCuH5l9KtiJwT&{E}x!WhzT>8x)O_2$4rCfw1PnE+x;7SVIbQ;EG7RUUIke_i;9r90V{Nj1Yq$+B^;EM2-yuI9e}X)TU74zEr2hj<DM2eeqMM>DGw%rj9d3Uok#xSj1TTQ;@iJ-0c2gYf@EM4)s_9%-&;_JKlCNNg@>J<Ssk?Ow%&UoA4z1?XT`sB%BRlQz1|p`0C6}&bs%1Xt%zlcP&XF5u#rJIJU$F|HecQs7L$~gaHIIZi619rcq-|@U$rqR^{$DV^iPO0b8=Jg7QRcva`hjqq^7BiVy?6OM6iOxG1RIaMqh(T0h|M`>4+w<oRbRUCbPilG9ml=+Qg%1a(^7JVDbW{d6P)b>a)pWybyytHZ68-VL0Qv99{z24X!I>d@uFiEe!`!G612BftgUHsgE>gsa8TQNgcyHa2Q~Y|jYn=!{~<v(|lCAL@QBY*z~_5W-92=4L>Ft%>BDYhhR_;s~GFxg4eAbFpJ=cbZI!cJdPT7!@Ll)Rs4dQ8jLTfw7e-AFYb5aB%PR$oiq_OI<l5&QBJB%{B0fgIGEj&XyhxZi%R2gx@lvWot2BFQCG%ENnbQq*>%Sj(DN_fDI&t0=1+j&{-`SxQ)NsHUv}}HIHoPoa|^>wk`TgrqHwkKLY6>5IDS@?*h2|36Sl&f{r)F<(CN2)u+OrNLTZmU%p&~?OM0`4sqi8pkIMNmxHa2^1Xw9?A8y#sM-yl@3vi_@QT_E=cVF;wTlE~NE4k1ex)?EZk0pbji#yxsA2dUu!T)&@Z-LCe31!XN%M~581P*?yW(DabT)~Vd`3L5V{34OQKv3n`Nd~``a6*fKdSyL;f7p(Yhx?+PuD%1voGwsPUq6jIM!U+wW+}Gm7mp~IVI-Oh;>&D7exK-N8VFJ=uEA5Fl$h^JwjQum2e+0BBtBfp?N6PH`wo<ID+i!=qKkJVB^Md&d&=e8O_+0vxa>?kiWIZ&ky5$YNFJRP@grDQWea}pnmTnGlyOf=kAs(ooSj-k-Mw}4U$cdwxAq#y4IY*eC|rV_px|PvC1v1JN4C8dU9pnl(+sc5&-wTsP{+DX<jj%y4efNYxJV4)z$keXpeB~6qH?F)0GmVxDHK`6L&m|r;MRQ-+qL34RmVLHRijWmC>_9aJfb49$sf4;yH}bHw;VzJuM>Q_>GK@So>Ta5;bQB#GrwgENPebsW&tv6^*c(Adr&D<6NZ3BG+r1`Jqr$^}03s>-9A&S$!mNZ2di5dxjO@6hk1Npv(m<UWFxC^9xqm(%wFJxH_SQ8U{{uSaMvYoH+nj>1E}l$uB^7Xa|T<#5Y8|;JsWGfj>9cS0HFj%toF^uX}i@6eqSd=AqiV_+VTO<zWsfYUVwAW0)0aYy|ZB6?ET(J8M`#5h*RI=VTOq$RrHH*X=trkr^Bd41H`s#P!YcM0=zu7x!FjbcRPTWr<NLd;$4Kr65bUdM7fQjo_u)H2k{Cir>7GIR&eoR6vvQbtyMuj;F@I{aJh1wfqSK#YOj%NIT?QI$czeB)oJZXz|=>q+|9=IJd$!X3rq>@{~QC8`O#^A$60M2h??8>$FxKFzw#(H)>)Mi5at4a6oR5ucrW)db1ZkpQ60yJ|qFMS)&^M$ioKS1a`HUI<*Je+M_OpebNy}wChIImBleinf(N5eF%5aAZi`qFMD-CeHw(KlY>xFG%h*r&A<jpmmc7$cI~uWW67i=MMM7AzbU~RSKBpyc^AA+voj3Zklkl~mF{7TyI}YJBYJ0xu)a*wS8^~NTl-H4{tcm&jwnblLTqUNqP)q4s>i9x=aMzM`_CL8yoMq+#0fe`j`ASd8IwzJE;B<s9h8|Q5mSlqmG;M|>HTL;G&?~xWQGnF`6lebIpa293)NVy{is8dsr7zo01Tz9+I<)tsk9q`Rn~2nbMV`11Q=C#(H>leVs}m$=P|8M&;@2p3QV{Rfq81sM@&}GIRseyLC*=49zZu<-Z-PA<9~UVQ9)Rmq5pARAzD@>Ft@iiA#Q5D8Oh3ED3YB5E4^|=EkrSwnTp(8&iaJ;XK?c#g|`00e?N>#Fggurlcb0j=hs_aqdF)bFt(MWiaG`YYh)Pcu8GuNK5IPGe@s9?x`V6gou4?{x&j<*A(9Q$Xp6~Iog<QE<x!ZaSA+2{NtVstG5+|3hXcyM<aH5jwba8N>|X!?po3tolKjV_00G=e?zaK}ee`W`vBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000008813821248185388046615239750983165114139620489667708734464310138853143949270360923505826680', 'computed_previous': '0.3899999997533097757568093470506355603707166845302812860460667010820057646024217510358553316318238587', 'covered_success': {'lower': '0.3902169168137394618834651884836331146201428759972405743068539605113000114860138703581064617740552437', 'upper': '0.3902169168137394618834651884836331146201428759972405743068539605113000114860138703581064617740552439'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000003910625423486635554581880569458007812499999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000003910625423486635554581880569458007812500000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002016241203729775175316570459395083420922708671494483419914105914624928744808035970991322050913438409', 'upper': '0.0002016241203729775175316570459395083420922708671494483419914105914624928744808035970991322050913438411'}, 'self_coincidence_F3': {'lower': '0.00001104849356192129629629629629629629629629629629629629629629629629629629629629629629629629629629629628', 'upper': '0.00001104849356192129629629629629629629629629629629629629629629629629629629629629629629629629629629629630'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '3.326929989507481821098031067627233469679822693607115972809917468188782828186529093159220849357022274E-7', 'upper': '3.326929989507481821098031067627233469679822693607115972809917468188782828186529093159220849357022276E-7'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 720, 'HF': 111, 'J': 62492, 'LRC': 39609010654731255879165988355178496, 'Tb': 1325810588030066223532131533912539136, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': 'fe64c0325a3e3484d1c3974aa55d11f3685dc05acc7ca6fdcdff789869d2ace6', 'previous_grid_upper': '0.3899999997533097757568093470506355603707166845302812860460667010820057646024217510358553316318238589', 'round': 12, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 93840, 'union_lower': '0.3900000008813821248185388046615239750983165114139620489667708734464310138853143949270360923505826678'}
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
