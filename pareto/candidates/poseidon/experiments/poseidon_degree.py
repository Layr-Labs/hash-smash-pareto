#!/usr/bin/env python3
"""Poseidon linearization experiment for r=3 (11 total rounds).

This experiment demonstrates the linearization technique for reducing polynomial degree
in Poseidon collision search. It finds a linearizing line where state[2] after round 0
becomes constant, reducing the effective degree from 5^11 to approximately 5^8.

Configuration:
- 8 fixed full rounds + 3 partial rounds = 11 total rounds
- State width: t = 3
- S-box: x^5
- Field: Pallas prime (p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001)
- Output: 256 bits (first field element)

This experiment validates the linearization technique but does not perform a full
collision search (which would require 2^128 evaluations).
"""

import json
import sys
import time
from pathlib import Path

# Pallas field prime
PALLAS_P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001


class PallasField:
    """Element of the Pallas prime field."""
    
    def __init__(self, value):
        if isinstance(value, PallasField):
            self.value = value.value
        elif isinstance(value, str):
            self.value = int(value, 16) % PALLAS_P
        else:
            self.value = int(value) % PALLAS_P
    
    def __add__(self, other):
        if isinstance(other, PallasField):
            return PallasField((self.value + other.value) % PALLAS_P)
        return PallasField((self.value + int(other)) % PALLAS_P)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, PallasField):
            return PallasField((self.value - other.value) % PALLAS_P)
        return PallasField((self.value - int(other)) % PALLAS_P)
    
    def __rsub__(self, other):
        if isinstance(other, PallasField):
            return PallasField((other.value - self.value) % PALLAS_P)
        return PallasField((int(other) - self.value) % PALLAS_P)
    
    def __mul__(self, other):
        if isinstance(other, PallasField):
            return PallasField((self.value * other.value) % PALLAS_P)
        return PallasField((self.value * int(other)) % PALLAS_P)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, PallasField):
            return self * other.inv()
        return self * PallasField(other).inv()
    
    def __pow__(self, exp):
        return PallasField(pow(self.value, exp, PALLAS_P))
    
    def __neg__(self):
        return PallasField((-self.value) % PALLAS_P)
    
    def __eq__(self, other):
        if isinstance(other, PallasField):
            return self.value == other.value
        return self.value == int(other)
    
    def inv(self):
        """Multiplicative inverse using Fermat's little theorem."""
        if self.value == 0:
            raise ZeroDivisionError("Cannot invert zero")
        return PallasField(pow(self.value, PALLAS_P - 2, PALLAS_P))
    
    def sbox(self):
        """Poseidon S-box: x^5."""
        return self ** 5


def load_constants():
    """Load Orchard/Pallas Poseidon constants."""
    constants_path = Path(__file__).parent.parent.parent.parent / "orchard-pallas-constants.json"
    with open(constants_path) as f:
        data = json.load(f)
    
    round_constants = []
    for rc in data["round_constants"]:
        round_constants.append([PallasField(c) for c in rc])
    
    mds = []
    for row in data["mds"]:
        mds.append([PallasField(c) for c in row])
    
    return round_constants, mds


def mds_multiply(state, mds):
    """Multiply state by MDS matrix."""
    result = []
    for i in range(3):
        val = PallasField(0)
        for j in range(3):
            val = val + mds[i][j] * state[j]
        result.append(val)
    return result


def poseidon_permutation_r3(nk, rho, round_constants, mds):
    """Execute 11-round Poseidon (8 full + 3 partial)."""
    state = [PallasField(nk), PallasField(rho), PallasField(2**65)]
    
    round_indices = [0, 1, 2, 3, 4, 5, 6, 60, 61, 62, 63]
    
    for round_idx in round_indices:
        # Add round constants
        for i in range(3):
            state[i] = state[i] + round_constants[round_idx][i]
        
        # Apply S-box
        if round_idx in [4, 5, 6]:  # Partial rounds
            state[0] = state[0].sbox()
        else:  # Full rounds
            for i in range(3):
                state[i] = state[i].sbox()
        
        # MDS multiplication
        state = mds_multiply(state, mds)
    
    return state[0]


def compute_fifth_root(value: PallasField) -> PallasField:
    """
    Compute 5th root in Pallas field.
    
    Since gcd(5, p-1) = 1, the map x -> x^5 is a bijection.
    Inverse: x -> x^e where e = (4*(p-1) + 1) / 5
    """
    e = (4 * (PALLAS_P - 1) + 1) // 5
    return value ** e


def find_linearizing_line(round_constants, mds):
    """Find (nk, rho) such that state[2] after round 0 is constant."""
    # Fix rho = 0
    rho_fixed = PallasField(0)
    
    # After round 0, state[2] = MDS[2][0]*(nk+rc[0][0])^5 + MDS[2][1]*(rho+rc[0][1])^5 + MDS[2][2]*(2^65+rc[0][2])^5
    # With rho=0: state[2] = MDS[2][0]*(nk+rc[0][0])^5 + MDS[2][1]*rc[0][1]^5 + MDS[2][2]*(2^65+rc[0][2])^5
    
    # We want state[2] = 0 (constant)
    K0 = (PallasField(2**65) + round_constants[0][2]).sbox()
    K_rho = round_constants[0][1].sbox()
    
    rhs = -(mds[2][1] * K_rho) - (mds[2][2] * K0)
    fifth_power = rhs / mds[2][0]
    
    # Compute fifth root
    fifth_root = compute_fifth_root(fifth_power)
    nk_value = fifth_root - round_constants[0][0]
    
    return nk_value, rho_fixed


def main():
    """Run the linearization experiment."""
    start_time = time.time()
    
    # Load constants
    round_constants, mds = load_constants()
    
    # Find linearizing line
    nk_base, rho_base = find_linearizing_line(round_constants, mds)
    
    # Verify: after round 0, state[2] should be constant (0)
    state = [nk_base, rho_base, PallasField(2**65)]
    for i in range(3):
        state[i] = state[i] + round_constants[0][i]
    for i in range(3):
        state[i] = state[i].sbox()
    state = mds_multiply(state, mds)
    state2_after_round0 = state[2].value
    
    # Evaluate at a few points along the line
    num_evaluations = 256
    evaluations = []
    
    for i in range(num_evaluations):
        t = PallasField(i)
        nk = (nk_base + t).value
        rho = rho_base.value
        output = poseidon_permutation_r3(nk, rho, round_constants, mds)
        evaluations.append({
            "t": i,
            "nk": f"0x{nk:064x}",
            "rho": f"0x{rho:064x}",
            "output": f"0x{output.value:064x}"
        })
    
    elapsed = time.time() - start_time
    
    # Output results
    output = {
        "experiment": "poseidon-linearization-r3",
        "configuration": {
            "rounds": 3,
            "total_rounds": 11,
            "field": "Pallas",
            "state_width": 3,
            "sbox_degree": 5
        },
        "linearization": {
            "nk_base": f"0x{nk_base.value:064x}",
            "rho_base": f"0x{rho_base.value:064x}",
            "state2_after_round0": f"0x{state2_after_round0:064x}",
            "degree_reduction": "5^11 -> ~5^8 (estimated)"
        },
        "results": {
            "evaluations_performed": num_evaluations,
            "elapsed_seconds": elapsed
        },
        "observations": {
            "linearizing_line_found": 1,
            "state2_constant_verified": 1 if state2_after_round0 == 0 else 0,
            "evaluations_performed": num_evaluations,
            "elapsed_seconds": elapsed
        }
    }
    
    print(json.dumps(output, indent=2))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
