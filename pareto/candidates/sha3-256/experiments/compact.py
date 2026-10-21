










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
R=19;S=13728;U=68640;SPW=5;KEY=50;LINK=1924;NREG=1936
SCR=S;LID=S+256;LST=LID+256;DATA=LST+256;P={'DK': 10, 'DPLO': 145, 'DT': 525, 'HF': 111, 'J': 85644, 'LRC': 54283334002973239430891824660611072, 'Tb': 1327200287138767598574930541775159296, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448};LABEL={'start': 0, 'clear': 7, 'initial_walks': 19, 'loop': 28, 'hit': 30, 'hit_ok': 34, 'save_planes': 160, 'dp_loop': 416, 'one_dp': 418, 'ctz_0': 425, 'ctz_1': 430, 'ctz_2': 435, 'ctz_3': 440, 'ctz_4': 445, 'ctz_5': 450, 'ctz_6': 455, 'ctz_7': 460, 'record': 463, 'probe': 476, 'insert': 500, 'insert_done': 507, 'match_0': 510, 'match_1': 513, 'match_2': 516, 'match_3': 519, 'match_4': 522, 'restore_after_hit': 525, 'continue': 526, 'deadline': 529, 'restart': 530, 'restart_ok': 533, 'restart_nowrap': 541, 'setwalk': 543, 'setwalk_loop': 548, 'gather': 560, 'gather_loop': 563, 'restore_planes': 573, 'eval_f': 830, 'output_message': 860, 'match': 887, 'measure': 896, 'measured': 904, 'advance_p': 908, 'advance_q': 915, 'advance_q_loop': 917, 'lock': 924, 'lock_loop': 926, 'found': 939, 'replay_fail': 952, 'end': 953};EXPECTED='d6a40f7a93871cc58fe3c5ab7c79236b5793a4c025428262901087b002391cc5';NI=953;NB=30496
K=(0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0);PD=(8635836852784158193, 16240263356698554435, 9810907220925358596, 578246363499725316);M64=(1<<64)-1;M256=(1<<256)-1
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
 layout,assembly,counts,raw=build(R,SPW,S,LINK,P,5184381065842164725850913460191233)
 if len(raw)!=NB or counts.instructions!=NI or hashlib.sha256(raw).hexdigest()!=EXPECTED:raise AssertionError('emitter output')
 code=decode(raw);checks(code);rows=[]
 for t in q['trials']:
  a,b,n=projection(t['seed']);rows.append({'trial':t['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n,'controller_instructions':NI,'controller_paths':11}})
 json.dump({'schema_version':1,'trials':rows},sys.stdout,sort_keys=True,separators=(',',':'))
STEP_SOURCE='{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;L(sR;#~j*Z3!mRne7ZlpTUJ4tTl~2z!6hQ`oQ{DHg7+4t@_iHHeN8MmGr+MEc{s~F95n)$oi_2w@dYdNooRfQsG$z>8x6ee6*}>&2f7wfQh69oTB}8#IHx2W?~OUvyOJoo{JZ`kQ?$jN*9H}Z>p5ixOA4CkPYlc?s6l0&=4m)5nzm1rOy_DnB2as0JqB2s1D5nlTnb}oK&P5OGRdpBz&SpLey6<@gBVb?8=@<%$@llC#)h8>OJf|Xgz^O1wC~Gh5jgeJ_j>11k=?e;X6F)98zxFEf*eQOAPAkJKr;2b3!6Mbj>7M_M(Mzj;DAEOi;BJT-K@jAE{zQjj0Fhg@ghn0n8N=@NohnG*}g~+cu`XQF8+(`Pf5j878O(+)$tiDe0Sp(O8CTV3`W?bYwGeK)!a2u(g|-R~ud$SBSUo2=N`@PXlASi9+C$L4S`$Qj9+8AB6asP<p4-Y?&GWDNAe@c@lQta4!jvv>73%!#+vc$$#UJp9aEDX%Vx-t&$fhA^q{BeXFrZxOh*l0YBXj>-{3&<sRcS9(`|?bAKMWVqJQG${u3mA1>w`XYFD23GZbfh8kHwD{u-h7FFA5@X_sfVeY@*yISuRl{K2d{h;!2re!V;nM9R+32TViBP|gg`d#U!wQ#qf$(626xmFNh3`oeU+pKzpU4M{>_P6)wNsL!Tc;k9zv!8ZA&?uDc%a?BIi`pGf)GnX+D(GOB<(e%*o~*>r0$7P?+DVu`jrFi$dxzv?N4LAT6-of$m;FoLw4yaL$xzyZ1R=LZQVtIfTX<8sCDchNpU@cxPLTl}@eS1=)T!xfas*as$TY^|qzE*RV+`E~Qll!Gu~DH;{0vPgrh#!Vg!3s98La%B^M@g(G1orB*kA0)dW($QIO7knssQp69SJi;;>I_hN7xLY*ELNWsRZDDj%?s<Q4`(VxRtE)i+pK9G5QVLR5nVavgPz;ykMR!`*NPSflZ5_!F03BiTt&uLn=aYTdKgkxnMnA`rI1K8FxVG2V%=AJ&dOD>%Ut}RO|jI(Z99UtyY95wvuu7I9L}q6B#os=66oZrpX7@zrNDF@4x{vK29!A>Ib!UcEy2IIB0LRbscItgX_9&&ofXUXz7uX&f@qCh~FVx;jsAHS@EX@<)=!*FWU&aI6Iq)3Hkd<zyF@)ikC53wn%${1xZPp*g4>3&1>E}p~a&%>S4Fz78t|sYNqif0SG-9gIiPUzZ#!gvv9j-d#DUBZ#*`kBce58SGOL~(Jh4>NNVqXsQJVYfmaCtg^g@WgM3qRTnQu>2013cD*UxRg-A4xJ8h7J33TUiNSjas!xxf@JUCd<GUYAjF_%)|{NEM?bkj=jpFrMo)F|xr#+sGc3sSwM95;G)rMpqL`X5t!RHfygg`imt$HI6h@SJV^9-RgTSn{p4q&zE@2g$4^zTJGzr)W<v^NfsqtA@XUN;vmJEG3q%<N7wAMOF{Ve(!kpN0&7$io`W{ir7y%(9dy10nS&&dn}dsMl#&`U1ujqLPjyiZxhgYdA^^Z5Rb9RESk2IIJ8>DkI8rKq?eeAilnfbhu#T_X8Gt&(iB4AYS=bHH3jp48k<8P2ZYRhIocz=^eA8Ah=bJOB&K*JV;^Ek6kn2xnL^C)!$gT*>2M;xtJ|tk&NxCCM9a0%4Ukg&0hI@a_;hw)>4ytQh5Qhgl<g>)O=)zAvST<A4510J!s+$x%U<!{J!ZWc01U%Y5QqWBVah<FC4_d)oqf=!W&KFa;6sror9JQ-SIPd9Z`O(sF<%}&&)zo;aq)zU0Wq0OMZRk(((?b?-FFL=#ZZ6W3<bQ-*X)kT?4#!g$O<X_dQCEVyGd7wIq+kb1Z41jQ-COXyVZbGUW4}zW^%sK`n`iG(Wa%$`@uk3DiQ7_^Ku&_W9sBd6VEe^?L9<?iGa&_{{iOu0mq7RFutQmDPFR-@OsF56N%DU{&@miF}4%<cTdXXZ2C8b{LU}U3+?6q_!Fb)_WN;YYB|;QRj!zCzjF~<s7h<gMgxT!P1X^|aq#IwF5zZNS^(zTrL(PnykE(~pH6u<Os`kxtQZ@tz=LyT$h*sy_r3<xr$gXY#2y3_sQ~Cz{}P@F%JTRgCTtocZn<kR@0+MII(ZR|IDIM`ak<IrAH&FFg`?&EcGzMgenCUgl|>fq#_(js{f%|os6r4@q_hZ%3Dfo7UKLxT64$5Oezdh4BOIW^3PI9Ux>@t9%f;4`NPE-74iWZ{D0Eb`R57XWENk@r&x#eA^Ie|cFX5ZW|L6o}3I;Z9V37Lzhrv_lYSQQJD$WOKdu$y+WJT4iB&8Kn=3v-O6ANjg5?m_}tuW;j^dEpIvnAGF1+m@4ZIo8FheRHRz6u$5><+v)#ZGH4h{&z}=|(hWWTv;f72r_(v;%n2?ZEPR-{&zqFiKeSGTG+pWeAwEYjM0Bdv|EIQa(}APQ#M`DvPrn8d~Iq%FoWWEbH{BFVfnwhVcU%x`jQO^ptb=v1d|owC(PCI?VD|BT>CpAqGmrTeBN2xHKbb3tVIZG7~F>#BX*Fs`475uqwMxd#H2VbBQn426qPs8=ywFRd8Ww3+UV><uz;LaOQbfudoaCHs`BB7&j^<_R_!Vd(mU)nSMDr;O_&9qREHIM&nG%b3At`3x7wq^!ecL_|x%6d#Gr*;%ivBR^VO@U<TB^T1T{q{|lTTd{ZLuwg$Nc@PUEZ_MME*^O8y-M}LGPnu?`is3n-i<=dK<VxlUt)X4qQ5{{;P(2=L*=-qz6&mqJv*vg#hZ_29sFL?od9WSa>2T;vx9(K#TwrS4?Y>r)*N;x8(xGo?P)Ux<rqQDH!_Aj~T_uEmOX<JmLL`V#y55MNRQ*<$0?P0V6c;e+YZ=K%93;%=U54yk`0tUio<CAcf{%bPt4uQT;o`urtfZRS=?^<DDH`hdIL`b_QZjvPVK2`d|Jh`*;?-a$uFk{HXv2Kjqusu4fBI4gnvP-VGf(~&QO@I827yT`hY9*4fk(l$AaJh)+iJa;MjkoDNFhySy#NcG<3K&;cV#<NJg)&eIsFhy@AHUl~bmv!OCux6WhLq!pCbObMN42@=AVcho=YD`UWC!x<c#itX#`<Ar^)^FH%M25aVhuh=nR>lxE2Ng<{HeBi0x=@&8z@o-X!FZkAZ}LHme3*2$4BP{;-znZg6aZs;+i`{4RO3-$%S|KuHWQrUOyrqVu`StQayZaDBii>o5*>T*Sf!mj%VPrab(7i!F1tcC<feA{6|W8putt*XXZ=#$<IkE8tGX{W;^AX6hUIqhdW<YNV3^nw(u(@23{*dCM;R}N-{t0!|q!kUom4&6nD`hMIuJoXJ^T{2yKvC*om)1iQH~7ab2})hC5gs{pC)+eU2^q8gopc+bD$P%2D#)GEu>kP)&<6x<xbzW4qWr`xU>#&`k#_*=FGtD7@NRz*V3o0lfJHRd}COzC%Tx9NrcMW6<2Bf#CWds>nOPfL!FNr|TAUA?s(0tiCQ<@tfoNvKxYQLYC(^!mw%oeIZtJ%G_DU8$vdHX`LW^x>yYHk?iM#d!Zq*KOY{f92y3y9)^L_Jr=(;2al20Ld(|G1V8~-hg<@3gw8=4mA2$GmAq)s52_B9HDh@FUZ0YH7+^aNv%O+5X|EE(ISgO5U8R(itXoWpjH@Xbewm_ja{~qc_h(y4ey*R3oOMa%oixA7n5Goj(fH>d!s6IfBiX(@qG~q6QQwKTNZqmsq-}Sj^1M7$Zr|oB>Rk^1o`<V6xzAZ$p<%DGlD;gIxN`oA?-b?=mz82v=>z|=0dZ@21He!OVDR>IIOA~x*~`cFY=}l+`*s(3H6M5wwT^ZIMesd3ysx`Ozp%riZY@>Z?6%<<4K7-8lc4<gQMKHpqb7pl2#Y;ZH`r!JSY*GzX(_~*B%cd}{-nQkAhEhqBo<MB+RJ5S4uWq|pCh^WQxd`&`u^$XgSd+J3rY{yWa>%|q?pSt%-bZt-}r2F(@`A>={asA0UScfh*(K;7mYNJfv9ty{8p_Jb=(lGAC9zg66D=xRPazd>J$qp->mr@C5{l_Rf~rmqvH?Rqw5rixM1BF$={!3;_Z0dXO)qaMrPsS_)MIqqYFNr5mG`T&%Hc>=~R(t2*8-h+!yc2(BxZs?~Nwb5dc>OQ-g^DQ}GvQsY1PZ12nT*IA!PpCTDJbSDl15s?YN`c@SP_aZwg^@=6gH1SSATlU(>$l+qSC*TBVv+-RSg`|L7Q4g}|)C0-HJ(&=$(hBG$Y;bUf$+PSH}w<{ncBvU(@m|e$nz8^j+LsN+borxVMOx~mMf^3rtk8aG!rWXF1XW<}6<qyauzt9d}(FN@RA+(0s@6yN}U=f$u@fZ*^wxPNxSx}K|c0(Ojxvcn(+!X53;Kqve`<DQtnTcQ)N<$dnP%JU@z{BbIen>9tg1+-R`N9FJb<%7$Bf0d5nzxF)QblZc4uiA)JbAPUDt3&`*B{039mvt@tN>{@vj;n4Ca8>Rm;wsi{iuUIdeH+0rVB2-_Fi2GEX;MtRvWqN;aT(hCH0@W;AVqM(FS^e-lDH-`wWiVL^)<49a6ZV6+2+ACYGhg`dn9D@yD6N;n+xO8pE$maw90#JQQ!|l%OE+9N2JIxyjrmvLap~cKu5LOH^BB7@!M%QL8lemqLzuEmJzemNB?S=8ys_aZ-y`ao|@UE~0+_j$b=#sA}#yEM`D=(E~qsV0GT&6D41bLwYgMtoaOoE6h)^RF8a+v&3qUF8u$<w+*b{9lnLV43^B#u>-5?z}#ma6}?NpjjCFEYLkM3ljx6n*Pwe%nE%I?N1fG+23w-e%Ez=HfFE5v+U<ePqqk%j8I&fEG>t8!lDR?ps0OTT9cuKpFrmx@LqsLGktiaJw~+H{j!uFMgl>UBgN;VB>lB=MleQqs!rWc>SfnbAeI^Y?taT!qSei9mQ$G|!`=gMRKT@;IZ)KV;&ZeEpYg7gKr2x<@Q;sI9Dp@YPT%{WyjIhYo>&%4_{FOa8jf&JRfg(%|-^OeZ&pP?Mz16a~6VUA;1PCpT>eu-8fLZAR`|yLaQjW(eu{rX;c(Ydsoz~?_hBPOqO~veB!uR_TlVc^huey}>dk}>xLh*rfb{HvjtBm>WLDz}X_5&x@ztQ`Gd@KJDzw5P4jAjfT%MHk}(d`fKB9pA+Kd?4~B7aX|V~qf5<yrjfFD&bWA~f?@t9k)3bq!z|5@G(8E+-th+g6918F?76&4<FBcl23BHR_Wb`4Bz`c}*KhcS0b1@j1Vf_o{g;1QH|IY#sOetH8Rq>Chm2-#r)1O(ZiB<8-jm&MR5<on`unfcr9IPLN+xytG70v$YFjhm52W9=N)oAQPtm=&>?WF7nw9TjJV4lfFNH=TDPw@&t_ep;{;5qG$q`JU<fMhoHvCSaV_>`M?(h%qo$%G(*e@8OTN{DaR0q3Arq}Z}q4xsuEl~Mgi(e7%Xf4n$rT)TvnHUdqlXiD3-F?;n{?rHcU&X<@a8TF+FE>0=(Vkfalk!iebl|I~1W$#!9hEaY}kbo#ZO%zz7c<@JtXiJ)%YZMn5!Z+(-T<wH%)r8L~|^ssqKVC~sSZs({X`h7}+?l~pApQ6(xj*r?44q6=$Tte2DK^F(Te@~pEI!74z7mhAB$^+Jj+M;iR(#bfJ2K<1+edYa0xc`$mq71g^APq8Z?%=SZ0h8}zCt3ZlI)NF%KBz@A+P0Jc|Do6*i^U?mifflS<-`ac^P|*CwA872ROLz@ZQQ!oDplW8E(hfv>t&wC|!y`)A#3)17y_vhL&*Hr4Oxuszrl6>W5Y-DWfko3)LME<B=f!=Jxay+gP(GDz(r+V7R6wYQHpq6%Hyj7m@ou*Hm(ouN`@0H>V8e7Zm3+kl%e{_clN-GI5)FFjiK@!7S1N%c*N>zX2DMM^YfwV27Ah&J>Uxokp5IEoXUd0+ZS|fW-v>58KrQ;8GEwhmlE@0R{xOO&nq<7C^Q`Wo#({2{?AwMpCHTIzoTL#*A|SD%YAp^tp%A9ykLU#`6G!~GXsZK@Pf{XB!$Vzv<LLc@!|iTyfT67r|F-j5)i1qdJt0<|=0nv`zFJ&s9c`o3Z>DD@3uw$8Af#2NRwd!jG@Mr~zq}bQuLn;0WBd1WQ()$i3v&xJyuM;kyPmELe0?^}dF1fuh7Lbc8naDtX)O`nMie;zPK_5;G6WUUA94i2-`gXc(lHN58q17jN{mv56D{}}+l-OxaYDx2q{p!zrl$Z6#xL}G+!yzTLZ69;!>5%gqWl3@yP6#GVOR?kf0$?_w&kv?x2*FNm*``}LKCTJc`^PG#$^pxkUr54*Yn*pcN?!Ik{e+ZJB_MuiPS_>`#j6*5np-<yI0b)Bw#K+m9K&r>-I1XT4{e;F>svRjp7c3NJt~Bqg`bw4CZrUZX<=IIC_>66z_BuEM;SWP#B%%*k}u%Dsbl+iO&ZY7xoGIw()4|S722Rp;(bLMcMMYFuWN$nBP0WL*WooBMc6SLS6J1g_Y@2wU{Yz)jXP_{^v{%_C>Vx4%Z*JDhStf{vz8KW30bWqI~NL+_8XUTh-`KQQ2A%DIJ&feP@eeAPQ}8<4z3ndmEc_6%|U<2uZJ06yjZHkB?+@3c*(IZaz4EQDZ(XsTx#Fx6wMsZf|f9LjcGbA|eT!^oN5@wuGj!G%GGTS;f|;IZ}<;ZKB~Ae8v4Xb8m-213j<PMx6{ux$vt@aaTiYZGp4NaXo-1j(|4B+bvMJP+IUjwQMaOAV9yAV50VvqIrfx(Wj;&k!&4(S(9I{q%RfRjT&EVRm;6Q3|83g1naZ}qnFxLbmn5$$*E=(eX2;CK2K^gU_QwVOD?w>O=>s#Hkpws_~w$?Va^Pu%n=$EsCdg)TFHKpPV0{Zfp09xfG!5{VbiauaAk@@Dq+)@!rD8XS`L^Zw&8!tw6qEwto=O`ZwMq^Ukfip+lzOV<Uukb`Q)EDOd#s0ieMEhMMqCijEbtwYhyS=Q*t6>5){ES5TIP9sGXBi4I;d>iOm95gKk6R7=v%QxTU6~WJ2gc&zuDb+C=B+l%c!~A(01h@{djvhkyKs1=1=0oOZVN3OQkP`Ah^@eKVH6M9!OAkc=`FXHO8i=XY1`0pj>Y*@Q%<i^sGrz8_p6{WRcA@iIZugKn*n#IL_cu{j?hp#YZJ^Il}>&a9fc7;-n?RUd_u<xp`g=0y#~ghFtSnjCH6y#Q%Jn-kHg*_Fllc9?>vL1&}%4^7f#Azj%cP}aYAT&#Tgei@3uL{lZqn$~pVsL&9oPL^o~q^q{pJOKhTpujV5^lb8)IRIn4Y45J5F2oZHsYgbot=b2!IZEgg^r^~Uj%GZnC93n13tpJ?UHY|rc_A^S0#$`NL(jGf;U47tDED+)T^SOVUO(YzCg|K+RW%Yj*yc>nYV{G}o*Su{7jpmTe%;romy9sq!#cOn2PvjBi*_**%^Hq%-zyEp2<;PQT)hw^59LZK4Dg6mo#}F`%&1rhVeDI=aF2FrXEf?y%}~5}_fkCsiWnNhtmS4gk6~?nB<2<{YC3iyQT(GFJ%7au4X_HnugVGzkkWt5j(s<_n<jiqgZ*%KC@^FQ_Y>pirhgJp$*fZI4GZL}Nr5!-<Rn^Wj)!vYYc))wuu8uYBC<nKn+W75Z0jM0_Y%J;c5`+1-B*cMU&Zvzmw_-T25riV`#n|flDcH$n))4upns%ulc>^3qc+H&idLCh{&-UL+)iBrw9Mw$sY1wruXZFG+@#bPf>OBiI_7mBy~svIKM}1Ts+U^OyF8%ecb)OFsE$SkOiCII03ku?umqxR%iNyX<hT7B0fgg=6~=t=grqXf{}3-=$*y`xz__269JE&?(jQ(Q%_Q>O%;s48<VwLXs*r`b93Sf=FVzVfDX?#o_%xe`_GE?(CE98#SP(5R_O|tB1tV^4gdjY{IRLV}_!>{b^ZCC0uD6En=YL4S6Ku;I%MUO2ViSP_i+s*}_JnHUC=M-ufr&^~Vwjjx!QKwErj2YZaG30z|H5%m5f8_L@r`M3rmSxON4;U!v!R&Nreh{ZZ{)U}C<#LL18}wr?3B0$U7mtFcK{!h4+Z}WAu1pK8ZTw{b>g$k60FXu`Y}BWElrp!yl};bOuH5&&>C}~i8?%Zo$6@C8vB`!)o8-#g4uQ=IBXKg1g4Cv42LdZJAlq`(ec>|Dm=YiP$2XWND9XZF0J-M{_jw47od~Td?GnjeI4-KBQ6f~#%9u0jh-n@<Zsfn@6u*SVq7usl;{YM=1Xbt&BdJ>Vs0G);%&Ft7(x6(d_Vc_Rbme+K|)@mI%5SC0@y3q_BHa)Pzzqs?zARMjMS#QG-jjtB?8YxU=kcuOT328yPN)w`Dr?O);P?I^MM$<-q>_04|{xRG>aS)39~ML%yjA2R_`lP_@)zBEFcV*gk*C<Zb15`mvG~0@(MFep|grWn^Bb#*<;<%Bqok;pUI}!&h++5KX=_MN{X}!sJ!F^bZ_MhMOMZ87N#%%yY8_`&jg}9mbt3h?LXy4oAzo-c{JbAD-#ItZk8B1I9l5%u+HpkZ5G0P6z|<n9#@3JI{<pT>MxXJp$Tjej<9-_ogttei4b)HfsuM~Bnv%6WIWy$>g2NUGUIm9@f__Q8DOX2wwMkwD>&O=lOz(|m-*3JJF$Sl5YjF-1xx#hJ+$_M&bP682z(^v=NUlkyJrBM0XDb;gzVaw`B2ql1}p>Hav}c{)4#w`e({)x@%4m$Gr`>@uD$wx-VvZWUDz)}ZZz9geEd#{#J(jubXq_aHI`7S0Na=8*fJ7STsJ^B_z;d$$qUqzg>$tWX_(QP?t9D3paxVh%v95?rQgtGQOi()kIvMFCD;`yW`3KQP}>9N*g1H=$t5{QJaL`xH4Gm$O~|eC>qRy#XY=>ksryDK6{g5{08*im?H{ZV!uhXcYt!yip)Z1YM0$jdu$@Y|g<#Unq#=4$+GPASWPwNa=k5i6rw*rII}W%0uJ`V2+h|TTBnJ~tF-9tTX}6px`${Nmnx?snDd>aM9yjsO*^o6`a7i;De<69o)uRT_2$hmeZ{#zbt#@`z&G1f^TdD~(lTZqE!t^LUt^DLr8Vq83<?tT$X*6h;Em+a<u3br`2KPbEvip@+FZ<)wFw3Nf_luC6$MyH`l^0pZt6drCBDW&weKyewF4?^D4-{NQx1MC!Ssh#Ik;+7+nYKlP$hApg6x)jm;EvMlG$LIZ5yBO3QS=6HMq@{$@@=DasWp%^%^gu(LjiL@o4zYTR5$2gj;}?}w;p^07G0IR_^EbG<gyg}@|(OfH;*|1@wUf)0YbG9CMMCB#QNOlZ>1kF?Nb_C&ozC|%a*@Y+K*g|vHJ3|YiTOP%`ZsOgSJ$WJT%x}lFbP0J$k5Ycp+4J%(Zp0-fVHeEd8Aj1sK{~3oh?<Z*aN7MiUwITC3)fkTIE=#d0|rrp27Wj2uGw?$&8_CfB_9SCVnCM5^k4^})o8ptGh=8zJ|B1XG;e=(+sl%SG}aSN{>|$n9_bO_biY7+${G$=OD-PD#-g&w={cL~oLMAH_4|SwN~`(zMLKXNfs!Wc?ku29fb*BN}HpEDH^5tF-3(D}l4KL<+M%vv67`qXig_onv5BEyTB`S@_Om(S-INu;?iBeIkGzWee{JMD`_+P^X$?o{Zc5s7erV+vs2pfP>%BV@_s04DDxy4bE<L=9B^am^J4zk{2BZ4l)n0+{bSY+Qu~Ss1FoL;gJ_0FDTXOJosVWIVvkq_00Bl1zO=KyJLUht!*l4rGqVIG60d+rFrH-F?u1BF0t+vjh8gn%3=G}OKQIKV)&utEfgD73syL%-15r`@*mhZ8Bfky^FZu0AtWh400W&mCq_8c_^ZRR_<AP<HRH%A#HIFb+H`TBbKg$~ZW8vd6oFx$$5jTL1X3j-t%uSRMov)lFn1rXM~5(WE&kskepS%FkYpaxi@>Dd$5=TllC=)IMIvpytycH$V!IPPKaB`q6eNHyQs{>x7a$t1OPj3>O@cxc=|0p^UOpx6awSbPET&F*!s;xEjvF>zYZyr7BK9n}Dn*RiwRw-UH~bxr6W|k&ZF~0Z1Y-8t{q*<7UX1XhBA~Rs-#3%+u}JV})~dAG$K`onKM?FWWkWFZ`7Uqki?t|+^4{c7NWpkc&s-$9<^ktM%qip$Om$FzIqGbMt<m|N!&X}d9lmi*V5q>WOH#iF&`dqkLZ1)*S$265Szg6E#OC#PuuF=ev9XHprDry9YC*Vo{8Wxdvw4^rxTQZexCEZa+%W_w-2od4YxWgQGo|uYZ$9l31#)7Bwk$b(bZR5a=wzH+?!WpFKbKo%BJpW9$u1tg>V*$tR>u2#0h25UL!65F=G_jTz6Fx>0<l+Uz2Wn6E%IN=6Ha-`qmbGyy|5AE9D_X3svs2uAC=i*X~9ysmgY?c&{}W{S2!mMn58{-e!}bMPP5wAfCeEnT6{dfe{c<zd5y;-aSYaq9$aAq7HD*(E00z<NZS~&vf2AlEIa*yIcBqWIE(=!ThS9cM749t;-NACyLDkSzI=KqqI@Q}JK@*Uk><^xW?MFxw`0tvGc~ndKaUS=LYxx@^J0WDEOq6n0qq==X^J*r0#(3PAG?=pw_Gx#>qNL7uK-8OyPCnm6mDG<sPmZzZW5Dauo6)z*O)A}u9k0t{{vp-l}AgEx+oKqG8UnJNOz35*BwYtib?DUk$IL{hLG<D`xcQh;?AX!Uf6$fGuwc0sFF<foXuGl!O$i;Y~(T7WG4XBQH${6XW{v%US57@61l4S77Rpir<+qmznYuhG^TM5cf^@0D`BgFy$Jt;n4{YrtebZyv-zM6caBcddr`XL3@j>X@NUMva1cqISFdI26FNpXl8Lh=kp8X7N+S5OP2$H1xM;XmT5K3Kl$4{cjNV}u_rk6|5UL9+UqPycgc0bX0k%1wX|G{tR)TB5z10#l_!Qd!;#Se1B8^ar&g}KCC;1{<w3yImv7K$~`9E5rl~dn|9qBWD)ZH7RYcmo9rgCTja?$t0e-)@n-?O#S4ZG+uB9RG~YtScCEXo|4G}~LuT_Tt?G{}PS_G{~3`QAFPaa~K9u7dOKHgX#XIq&fyX`?EVeMB`(j;uc@=s1vO&-y3#2MP{Y@E%@Wp@h{N7#2m8|8f6r(CxyJB*Rg-Rtr)Ay`kjDtwC<<`E&*n--ri+z{72MeYe#-lIrM<{#o6uQh)>I0vUP!_TE`46^-G9&v=jEKk$;=Y`dmMD6ENS`%q|NMqW~xL9L0D?4cK&xtUrB!Fo*kQK+x@8sh-YL1AQ*53Fa#i;POzry;A;1+w?SyJAr;xo^q9C91}O%?U`1NK@U-Z)%|-)GIN7C8*HfCWK$NVWY>-Dy7-=CzKD*_m~@-K!vc!-n%&<hkt`2So%ZJ8p<|UXOx`ChyH(sb5X+&PrD!fQ}=PgKEa#!P%C*ex;YIti-ezBSn^*JIv3Vewgj8STbh$FSCv587eDOrq=_xCIx%P^&8FEMra6PI8B4~&c81D-;aelWff&5%RM4HROmEg=Pq8>dvPL*F2iUbCF`99RwFMs{Dxr_oe+It)l-#+i{pjgcpmP6>&V}rSAT%NH;kAy|bXjncFWU|zLVfo2+PXBg=uW+&X6-R~y`}eTqw+pf7Rtl75v2;K99UzqhGRLunDI$K5-fWprAt1X5+&qNOtTLZOWTP#&x?YqXez7^u>I3TzEKBqsVe2a7`z(_*9|w;vYXi9mIP9;pSV6#x>&DShk?#W#|d5BV>}x9j{5<yE8*dFcU=W450R-!WUM$Mp`nzkRkzIs@zycf(mgLpg=VE9%QlX=P80*Gg2+_T2kW3Nne6LK$_B}$Lr=P&rO;TQk!!n5Y$u}Nw`T;b-ikWjFp#~F#<tY|J=H}5EvIpA!uGJ=^7Y^Up7T6DQlivRBNdm?_-|hCyy!V_;4E*qlG)kF{^vsp6qHxSq*l4+oH>Jc!iE1`Z2GVyjwsk?JCp&w!r=kVpW&_d`s=#9x_>suGYwtimb&9amAtR&>zKSD=`dUNoZs&5;>9iCh;9^fRzN|QF(Eaa4#?Rn^yvNDarz%lqgaW}eO3cPf+wGS<Qfkgh^<?rU<#BaGgl92BH=*SA_J^Z+K90XAbGVxrtFJE$kCJh?2R!l!Z7n_$iHMO&<$10xVrtlOfLffsbybhr3&<w45v(h2(XfNqRD7O!?^rGZVD)tO0=m!Vk)lO20Yb&)baFuJe<rWbX4yeG<!w@+TSK#xmP899}y6MWqr{)c!l_rZAF~*LYT}ooszFtWSY1OEHqr23(tJ`iPl^3{jF%nq02Q8<#-<>-fatn4dr4Zz%hBVbXIgQM}>)Kul@1VgQ{^$T>l-hA~h~uH6EPV6jl}4f!POMN!8agZ(Vg(=zCYwIxT1Tc*QYgk{Ws}jju|ydZg$UF22c5!)aBR8d{ZLRBz<ObQ(i{rT<7p(pD#gRqo71oP4n;3WAOhViN>;#MVk*rg9OT&=p8W1Uoph5vOhc?f)_qm{7t$@RXf1Zq`wV&(a~Ne+jjr1AS9S45iqi@{*+CkBfhzVPtSdg3BHcvGjpw<(!<`2XM*La)j;I^8=y8?x#Hhf_Flw$NURhfU99%S}3CCii3=layINmcpMYjkmbD<W5o6e)gE_3dtX<$v--h);*p1b??<!n^Cs*7{7Y!X4P(cCTQhR>F|G?h@upnv$2pz8XE~Z6o$*Sojd|N#8(=Gs{$GYTN6Qh>u;g>I2~59fQE^njZO&#w?0$(sl06ww6qIxz;UrO^H+eQTs+rp(GQKG$AhrfS&472Li{*N*&%sZkG@HYJ>FO7umi7);ct$2Cz#)HybW0HpDOHFMwdEhBgIL@X15DB+i{DeZ<Sa*qb$<^50-h&4_iWub@i37m?3OIZ=qH-Kt#4udU=tGnZaYu{0z!~ncsUfFu29`XI+xg<+!}5SCwrvURgv!l^hHc({C@;`x_5|As1W!o{xRz^iW(za0z4mV;ill~_WM@z#$X>}y_MBHhFnyuBtkqLZRtecWxh)BY=vYr3x!-xeBG&-$%3;r!LZf?ez!MVB2uqe+{~U)NNIIAS>5lTCABGh;p^}cMq*yLsBwI5!dv1f-e{W?+Bq|amkkhzh`mn3lMI62ZRY(m+u9Tz;p<vL&hBl*IzGIcaN;Kqy3T=-ecMMHd7m8|Hhvs7t7dP-AiWP!oLYP?oV<ec0~WjGBH1a)DWT<^`>^3pFl2d>o+ttEF3ywYC0Ob-kx#m@37tSW&)w>|`XT9NL&2+5#u{-4-7cK!wnd{br+ygE2rR6DA9~kFpz5sjz)b3bpMa*oUN_%uk^qUpStEaDN6)^YkO5tm+ouDiRhUk3=Pn_&FYD^H4%2E_M%F`cz*#uB3}dVBufgO?ue>@2b951jQpJp@6I$_zNv~3cE`!-lZeWK-nM%*`M$ujjCgVWM=xW;v_l+ZW%O-ZTKkwL)6YO71PrGFXPv+1r+yE3$M46-s-V$7P5eWkj+$A6H;M7DK)0u`4+(8Uto4iPDCNO~0<c~N={-4?1mp36RB^8=f;Ck%YtU@S;T+++)Fqud!a-8TQ?o~wnk_7Fv{&dut5##35oS4UC6vp)XCGc4MISD?rMh3OiNGq_=455aF#NzndU9S?6mDS?<)U*0=e`K8hIl6&co|TSUD)8KxmDBZZg^;-5iQ<65ZF>zXBbATy@qQthn(FPITP*C))0pi|@Xw33iOvRWcr@0{Hj5z`0NR8@yy8`JY(Uo@xk_y^OByApDl6D6P@E5r(PK&lw-U_yzilMYTTw-`lcf6KzZLcUzjp~P+pcIP4IJnMxF3x&oG!9VAdNBVb~I%TpG030>q)LlCFO7bUO+~2*AALr5%sY(#k74Bmp}|GA)9*6d>yrMG}(o$_vUR7tljudoJz`U-)u+rZIVe1RvarGUY<^KA$_p59!x;Gq|qaUZa5SmhDs~!p)>B8pK(q8y4R<u4^zaM%qr;I#aZ7Qj|*g1J6uNV{Pqs*Nr7@O=fgVlnn%TZm6beC#4fChNP#zqoO^dry*7xGC1?0+6i8nU_n0!k6hKUi_^HwR<1o?%7Wk9vP1t9ehGbI={yGbrAzdC^D_@!zbFK|5a#|OTHkXq1;qp{GNmbAflE3HhJuiPXVt1TQiug=S+(meNB3GIKu95Q#retzfL_+>mWjlBq`q`mXIGTk)zQIi0Ftqf<#VumFc0IP_rk<t!sdSKgUi)lmFU7r$v*$OGxp%rNNhDFK>p`jWL3o2vmlgJy7N|LsOR&*v;Gk98K?rh{WG@Vh{k{DeN{ykeQF^tO{Yr=jhh7I(6SYF<e`&oaA&cUzzV@Yk*<WfktP?Gx`XW-8wMf))!{C#u>_jN8<_yNBtI3KxT+QxNoH_ksCj2Occ9_HpPec_?&5&Qc$pX9LHieAd6rE@#`=*icwg**F9}oABaT%`E;I$8b4SIua$x_AE^r|V6L!>&sB=37a;ne>9JW^v?(stJ%Y?wqQJ-sRlnTO}p(o$oVG4hn%FP*OF%DBjf{exgtvoH+FEVWy>F(};N0Ic}VdFk>#I8Mt11KOe~rKEOL37$~RHM68+ia~?BTwjv+leyqkY8-uUu+hozzjO6gEJoini~@G9R_)ttW@Iz*+Lh?o?iljML&-2=c481AF#hDJ?17eIq&|&u2|k0#JpG;Z$!)GN9rZS50c;>B7^pzG%~xq|;h!+yssj+6KHFZ=H@Fj@fv4fo95HJaaM0AI$V8stR@BE-HnR|FHoR_hJ~=laq-u!<mPMPEiZ3`t$4;l9-+>5?vh&oM^EGWcgCD$_*kf7jGU73?vVewxD3Vax%kH7W_~)sJja`|xZ|%z7U}DQ1jmBot1OG|Usp=2#e1F-!%ew&@dm@~;Z<g%*5gOG?=^1Q%suv;bA9LH%_p2cm*R1|zz-cbUShG#4At@HsP0xHsn8#(5&3vWPd;-CqlK=nlrE{KN#fqvOX}|YhO`Xh-%g6N5aL4)G#99m*HA&$*Q1V7>cjhAdSynOJ5xL>_)D50NZ<hv|b5|T1-Vs1l10%}FbE0|=eGZ_$R^b{5q&moM_gzO&INs5MI!MVxyI1UE6|3D_GU9rbEC2uixtD!R0C#T<00I76k)s0uRb=5-vBYQl0ssI200dcD'

from decimal import Decimal as D,getcontext
CERT={'computed_bound': '0.3900000001224188806811788112418850762328459932194893109491377915168972108628920411675964945062953690', 'computed_previous': '0.3899999990047467173318387497361653783810273652190846658526563176193633835179228347271020143239870934', 'covered_success': {'lower': '0.3902253772910058068334513127703389832063897404675547416309833522150881977341835915215140927384427597', 'upper': '0.3902253772910058068334513127703389832063897404675547416309833522150881977341835915215140927384427599'}, 'failure_intervals': {'endpoint_alias': {'lower': '0.000002092303930112393572926521301269531249999999999999999999999999999999999999999999999999999999999999999', 'upper': '0.000002092303930112393572926521301269531250000000000000000000000000000000000000000000000000000000000000001'}, 'hit_cap_F5': {'lower': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811023E-302', 'upper': '9.332636185032188789900895447238171696170914463717080246217143397959669109757756344544403270978811025E-302'}, 'numeric_rounding': {'lower': '8.673617379884035472059622406959533691406249999999999999999999999999999999999999999999999999999999999E-19', 'upper': '8.673617379884035472059622406959533691406250000000000000000000000000000000000000000000000000000000001E-19'}, 'replay_cap_F6': {'lower': '0.0002033264821186383876481244037850903678420834675381763687084188632861353958045591167114202481864841504', 'upper': '0.0002033264821186383876481244037850903678420834675381763687084188632861353958045591167114202481864841506'}, 'self_coincidence_F3': {'lower': '0.00001519982993197278911564625850340136054421768707482993197278911564625850340136054421768707482993197278', 'upper': '0.00001519982993197278911564625850340136054421768707482993197278911564625850340136054421768707482993197280'}, 'start_replay_collision': {'lower': '8.077935669463160887416100508495730991853633895516395568847656249999999999999999999999999999999999999E-28', 'upper': '8.077935669463160887416100508495730991853633895516395568847656250000000000000000000000000000000000001E-28'}, 'table_exhaustion_F2': {'lower': '0.000004758552606201714574065548667031561629116655889004390966253533895203420446073808222865909130974703113', 'upper': '0.000004758552606201714574065548667031561629116655889004390966253533895203420446073808222865909130974703115'}}, 'key_bits': 50, 'parameters': {'DK': 10, 'DPLO': 145, 'DT': 525, 'HF': 111, 'J': 85644, 'LRC': 54283334002973239430891824660611072, 'Tb': 1327200287138767598574930541775159296, 'W': 633825300114114700748351602688, 'granularity': 2475880078570760549798248448}, 'plan_sha256': '0af996790d8613061073072a2be66b753150b69a4478a7dda11a8221b567b2d0', 'previous_grid_upper': '0.3899999990047467173318387497361653783810273652190846658526563176193633835179228347271020143239870936', 'round': 19, 'rounding': '100-digit Decimal; every published endpoint moved one representable value outward', 'schema': 'hashsmash-random-function-success-v1', 'target': '0.39', 'trails': 68640, 'union_lower': '0.3900000001224188806811788112418850762328459932194893109491377915168972108628920411675964945062953688'}
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
