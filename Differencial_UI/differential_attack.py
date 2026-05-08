"""
PRESENT Cipher — Differential Cryptanalysis Attack
Attacks reduced-round PRESENT (2, 3, 4, 5 rounds) using chosen plaintext pairs.
"""

import numpy as np
from collections import defaultdict

# ══════════════════════════════════════════════════════════════
# SECTION 1: PRESENT Primitives
# ══════════════════════════════════════════════════════════════

SBOX     = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]
SBOX_INV = [SBOX.index(i) for i in range(16)]

PERM = [0,16,32,48,1,17,33,49,2,18,34,50,3,19,35,51,
        4,20,36,52,5,21,37,53,6,22,38,54,7,23,39,55,
        8,24,40,56,9,25,41,57,10,26,42,58,11,27,43,59,
        12,28,44,60,13,29,45,61,14,30,46,62,15,31,47,63]

def apply_sbox(state):
    out = 0
    for i in range(16):
        out |= SBOX[(state >> (i*4)) & 0xF] << (i*4)
    return out

def apply_perm(state):
    out = 0
    for i in range(64):
        bit = (state >> (63 - i)) & 1
        out |= bit << (63 - PERM[i])
    return out

def bytes_to_int(b):
    r = 0
    for x in b: r = (r << 8) | x
    return r

def nibble_diff(nibble, pos):
    """Place nibble difference at nibble position pos (0 = MSB)."""
    return (nibble & 0xF) << (4 * (15 - pos))

def get_nibble(state, pos):
    return (state >> (4 * (15 - pos))) & 0xF

# ── Key Schedule ──────────────────────────────────────────────
def keyschedule(master_key_bytes):
    subkeys = []
    keyHigh = bytes_to_int(master_key_bytes[:8])
    keyLow  = (master_key_bytes[8] << 8) | master_key_bytes[9]
    subkeys.append(keyHigh)
    for i in range(1, 32):
        t1, t2  = keyHigh, keyLow
        keyHigh = ((t1 << 61) & 0xFFFFFFFFFFFFFFFF) | (t2 << 45) | (t1 >> 19)
        keyLow  = (t1 >> 3) & 0xFFFF
        tmp     = SBOX[keyHigh >> 60]
        keyHigh = (keyHigh & 0x0FFFFFFFFFFFFFFF) | (tmp << 60)
        keyLow ^= ((i & 1) << 15)
        keyHigh ^= (i >> 1)
        subkeys.append(keyHigh)
    return subkeys

# ── Reduced-round Cipher (last round = AddKey+SBox only, no Perm) ─
def present_r_rounds(pt_int, subkeys, rounds):
    """
    Encrypt with 'rounds' rounds.
    Rounds 1..(rounds-1): full (AddKey + SBox + Perm)
    Round 'rounds':       AddKey + SBox only (no Perm) + FinalAddKey
    """
    state = pt_int
    for i in range(rounds - 1):
        state ^= subkeys[i]
        state  = apply_sbox(state)
        state  = apply_perm(state)
    state ^= subkeys[rounds - 1]   # AddKey before last SBox
    state  = apply_sbox(state)
    state ^= subkeys[rounds]        # Final AddKey
    return state

# ══════════════════════════════════════════════════════════════
# SECTION 2: DDT
# ══════════════════════════════════════════════════════════════

DDT = [[0]*16 for _ in range(16)]
for din in range(1, 16):
    for x in range(16):
        DDT[din][SBOX[x] ^ SBOX[x ^ din]] += 1

def best_ddt_output(delta_in):
    """Return the output difference with the highest DDT count."""
    row = DDT[delta_in]
    best_out = max(range(1, 16), key=lambda d: row[d])
    return best_out, row[best_out]

# ══════════════════════════════════════════════════════════════
# SECTION 3: Trail Builder
# ══════════════════════════════════════════════════════════════

def build_trail(num_rounds):
    """
    Build differential trail for (num_rounds - 1) rounds.
    Returns (DELTA_IN, DELTA_MID, active_nibbles, trail_probability)
    """
    # Start with single active nibble: 0x1 in nibble 0
    DELTA_IN   = nibble_diff(0x1, 0)
    delta      = nibble_diff(0x3, 0)  # 0x1 → 0x3 via SBox (DDT prob 4/16)
    delta      = apply_perm(delta)    # after P-layer = round 1 output
    prob       = 4 / 16              # first transition

    for r in range(num_rounds - 2):  # chain extra rounds
        next_delta = 0
        for pos in range(16):
            d_in = get_nibble(delta, pos)
            if d_in != 0:
                d_out, count = best_ddt_output(d_in)
                next_delta  |= nibble_diff(d_out, pos)
                prob        *= count / 16
        delta = apply_perm(next_delta)

    active = [i for i in range(16) if get_nibble(delta, i) != 0]
    return DELTA_IN, delta, active, prob

# ══════════════════════════════════════════════════════════════
# SECTION 4: The Attack
# ══════════════════════════════════════════════════════════════

def differential_attack(secret_key_bytes, target_rounds, num_pairs=None):
    """
    Run differential cryptanalysis on reduced-round PRESENT.

    target_rounds : 2, 3, 4, or 5
    num_pairs     : number of chosen plaintext pairs (auto if None)
    """
    subkeys   = keyschedule(bytearray(secret_key_bytes))
    LAST_SK   = subkeys[target_rounds]  # the key we're attacking

    # Build the (target_rounds - 1) round trail
    DELTA_IN, DELTA_MID, active_nibs, prob = build_trail(target_rounds)

    # Auto-select number of pairs (capped at 50000 for speed)
    if num_pairs is None:
        num_pairs = min(50000, max(2000, int(5 / prob)))

    print(f"\n{'='*55}")
    print(f"  {target_rounds}-ROUND DIFFERENTIAL ATTACK ON PRESENT")
    print(f"{'='*55}")
    print(f"  Input diff        : 0x{DELTA_IN:016X}")
    print(f"  Expected mid diff : 0x{DELTA_MID:016X}")
    print(f"  Active nibbles    : {active_nibs}")
    print(f"  Trail probability : {prob:.6f}  (1/{int(1/prob)})")
    print(f"  Pairs used        : {num_pairs}")
    print()

    # Generate chosen plaintext pairs
    pairs = []
    for _ in range(num_pairs):
        p1 = bytes_to_int(bytearray(np.random.randint(0, 256, 8, dtype=np.uint8)))
        p2 = p1 ^ DELTA_IN
        c1 = present_r_rounds(p1, subkeys, target_rounds)
        c2 = present_r_rounds(p2, subkeys, target_rounds)
        pairs.append((c1, c2))

    # Attack each active nibble of the last-round subkey
    correct = 0
    for nib_idx in active_nibs:
        exp_diff = get_nibble(DELTA_MID, nib_idx)
        scores   = defaultdict(int)

        for c1, c2 in pairs:
            n1 = get_nibble(c1, nib_idx)
            n2 = get_nibble(c2, nib_idx)
            for guess in range(16):
                if SBOX_INV[n1 ^ guess] ^ SBOX_INV[n2 ^ guess] == exp_diff:
                    scores[guess] += 1

        if not scores:
            print(f"  Nibble {nib_idx:2d}: ⚠  No scores — increase num_pairs!")
            continue

        best   = max(scores, key=scores.get)
        actual = get_nibble(LAST_SK, nib_idx)
        ok     = best == actual
        if ok:
            correct += 1
        tag = "✅" if ok else "❌"
        print(f"  Nibble {nib_idx:2d}: "
              f"recovered=0x{best:X}  actual=0x{actual:X}  "
              f"score={scores[best]:5d}/{num_pairs}  {tag}")

    print(f"\n  Result: {correct}/{len(active_nibs)} nibbles correct.")
    if correct == len(active_nibs):
        print("  🏆 Last-round subkey nibbles fully recovered!\n")
    else:
        print("  ⚠  Try increasing num_pairs for better accuracy.\n")

# ══════════════════════════════════════════════════════════════
# SECTION 5: Run Attacks for 2, 3, 4, 5 Rounds
# ══════════════════════════════════════════════════════════════

SECRET_KEY = [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x11, 0x22, 0x33, 0x44]

for rounds in [2, 3, 4, 5]:
    differential_attack(SECRET_KEY, target_rounds=rounds)
