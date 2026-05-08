"""
TOY PRESENT Cipher
==================
A miniature version of PRESENT for educational purposes.

  - Block size : 16 bits  (instead of 64)
  - Key size   : 20 bits  (instead of 80)
  - S-boxes    : 4        (instead of 16)
  - Rounds     : 8        (instead of 31)
  - Same S-box and structure as real PRESENT

Since everything is tiny, every step can be traced by hand or printed.
"""

from collections import defaultdict

# ══════════════════════════════════════════════════════════════
# SECTION 1: TOY PRESENT Primitives
# ══════════════════════════════════════════════════════════════

SBOX     = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]
SBOX_INV = [SBOX.index(i) for i in range(16)]

# 16-bit P-layer: bit i goes to position 4*(i%4) + i//4
# This preserves the PRESENT "spread across nibbles" property
PERM_16 = [4*(i % 4) + i // 4 for i in range(16)]

def apply_sbox_toy(state):
    """Apply S-box to all 4 nibbles of a 16-bit state."""
    out = 0
    for i in range(4):
        out |= SBOX[(state >> (i*4)) & 0xF] << (i*4)
    return out & 0xFFFF

def apply_sbox_inv_toy(state):
    """Apply inverse S-box to all 4 nibbles."""
    out = 0
    for i in range(4):
        out |= SBOX_INV[(state >> (i*4)) & 0xF] << (i*4)
    return out & 0xFFFF

def apply_perm_toy(state):
    """Apply 16-bit permutation."""
    out = 0
    for i in range(16):
        bit = (state >> i) & 1
        out |= bit << PERM_16[i]
    return out & 0xFFFF

def apply_perm_inv_toy(state):
    """Apply inverse 16-bit permutation."""
    inv = [0]*16
    for i, p in enumerate(PERM_16):
        inv[p] = i
    out = 0
    for i in range(16):
        bit = (state >> i) & 1
        out |= bit << inv[i]
    return out & 0xFFFF

def get_nibble(state, pos, total=4):
    """Get nibble at position pos (0=MSB) from a state with 'total' nibbles."""
    return (state >> (4 * (total - 1 - pos))) & 0xF

def set_nibble(state, pos, val, total=4):
    """Set nibble at position pos (0=MSB)."""
    shift = 4 * (total - 1 - pos)
    state &= ~(0xF << shift)
    state |= (val & 0xF) << shift
    return state

def nibble_diff_toy(nibble, pos):
    """Place nibble difference at nibble position pos (0=MSB) in 16-bit state."""
    return (nibble & 0xF) << (4 * (3 - pos))

# ── Key Schedule (20-bit key → 9 subkeys of 16 bits each) ────
def keyschedule_toy(key_20bit):
    """
    Generate subkeys from a 20-bit master key.
    Rotates left by 1, applies S-box to top nibble.
    """
    subkeys = []
    k = key_20bit & 0xFFFFF
    for i in range(9):
        subkeys.append(k >> 4)         # top 16 bits → subkey
        k = ((k << 1) | (k >> 19)) & 0xFFFFF  # rotate left 1
        top = (k >> 16) & 0xF          # apply S-box to top nibble
        k   = (k & 0x0FFFF) | (SBOX[top] << 16)
    return subkeys

# ── Reduced-round Toy Encrypt ─────────────────────────────────
def toy_encrypt(pt, subkeys, rounds):
    """
    Encrypt 16-bit plaintext with 'rounds' rounds.
    Rounds 1..(rounds-1): full (AddKey + SBox + Perm)
    Round  rounds:        AddKey + SBox only + Final AddKey
    """
    state = pt & 0xFFFF
    for i in range(rounds - 1):
        state ^= subkeys[i]
        state  = apply_sbox_toy(state)
        state  = apply_perm_toy(state)
    state ^= subkeys[rounds - 1]
    state  = apply_sbox_toy(state)
    state ^= subkeys[rounds]
    return state & 0xFFFF

# ── Full Toy Encrypt (8 rounds, standard) ────────────────────
def toy_present_encrypt(pt, key_20bit):
    sks = keyschedule_toy(key_20bit)
    return toy_encrypt(pt, sks, rounds=8)

# ══════════════════════════════════════════════════════════════
# SECTION 2: Difference Distribution Table (DDT)
# ══════════════════════════════════════════════════════════════

DDT = [[0]*16 for _ in range(16)]
for din in range(1, 16):
    for x in range(16):
        DDT[din][SBOX[x] ^ SBOX[x ^ din]] += 1

def best_ddt_output(delta_in):
    row      = DDT[delta_in]
    best_out = max(range(1, 16), key=lambda d: row[d])
    return best_out, row[best_out]

# ══════════════════════════════════════════════════════════════
# SECTION 3: Trail Builder for Toy PRESENT (16-bit)
# ══════════════════════════════════════════════════════════════

def build_trail_toy(num_rounds):
    """
    Build differential trail for (num_rounds - 1) full rounds.
    Returns (DELTA_IN, DELTA_MID, active_nibbles, probability)
    """
    DELTA_IN  = nibble_diff_toy(0x1, 0)   # 0x1 in nibble 0
    after_sb  = nibble_diff_toy(0x3, 0)   # 0x1 → 0x3 (prob 4/16 from DDT)
    delta     = apply_perm_toy(after_sb)  # after P-layer
    prob      = 4 / 16

    for _ in range(num_rounds - 2):       # chain more rounds
        next_delta = 0
        for pos in range(4):
            d_in = get_nibble(delta, pos)
            if d_in:
                d_out, count = best_ddt_output(d_in)
                next_delta   = set_nibble(next_delta, pos, d_out)
                prob        *= count / 16
        delta = apply_perm_toy(next_delta)

    active = [i for i in range(4) if get_nibble(delta, i) != 0]
    return DELTA_IN, delta, active, prob

# ══════════════════════════════════════════════════════════════
# SECTION 4: Differential Attack on Toy PRESENT
# ══════════════════════════════════════════════════════════════

def toy_differential_attack(secret_key_20bit, target_rounds, num_pairs=None):
    """
    Differential cryptanalysis on reduced-round Toy PRESENT.
    Recovers nibbles of the last-round subkey.
    """
    subkeys = keyschedule_toy(secret_key_20bit)
    LAST_SK = subkeys[target_rounds]

    DELTA_IN, DELTA_MID, active_nibs, prob = build_trail_toy(target_rounds)

    if num_pairs is None:
        num_pairs = min(10000, max(500, int(3 / prob)))

    print(f"\n{'='*50}")
    print(f"  {target_rounds}-ROUND TOY PRESENT DIFFERENTIAL ATTACK")
    print(f"{'='*50}")
    print(f"  Input diff        : 0x{DELTA_IN:04X}")
    print(f"  Expected mid diff : 0x{DELTA_MID:04X}")
    print(f"  Active nibbles    : {active_nibs}")
    print(f"  Trail probability : {prob:.4f}")
    print(f"  Pairs used        : {num_pairs}")
    print()

    # Generate chosen plaintext pairs
    import random
    pairs = []
    for _ in range(num_pairs):
        p1 = random.randint(0, 0xFFFF)
        p2 = p1 ^ DELTA_IN
        c1 = toy_encrypt(p1, subkeys, target_rounds)
        c2 = toy_encrypt(p2, subkeys, target_rounds)
        pairs.append((c1, c2))

    # Attack each active nibble of the last subkey
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
            print(f"  Nibble {nib_idx}: ⚠  No scores — increase num_pairs!")
            continue

        best   = max(scores, key=scores.get)
        actual = get_nibble(LAST_SK, nib_idx)
        ok     = best == actual
        if ok: correct += 1
        tag    = "✅" if ok else "❌"

        # Print all 16 scores so you can see the correct one standing out!
        score_bar = "  ".join(
            f"\033[91m0x{g:X}:{scores[g]:4d}\033[0m" if g == best
            else f"0x{g:X}:{scores[g]:4d}"
            for g in range(16)
        )
        print(f"  Nibble {nib_idx}: best=0x{best:X} actual=0x{actual:X} {tag}")
        print(f"    Scores: {score_bar}\n")

    print(f"  Result: {correct}/{len(active_nibs)} nibbles correct.")
    if correct == len(active_nibs):
        print(f"  🏆 Subkey nibbles recovered! Subkey[{target_rounds}] = 0x{LAST_SK:04X}")
    print()

# ══════════════════════════════════════════════════════════════
# SECTION 5: Demo — Trace Through ONE Encryption by Hand
# ══════════════════════════════════════════════════════════════

def demo_trace(pt, key_20bit, rounds=2):
    """Print a step-by-step trace of the toy PRESENT encryption."""
    sks   = keyschedule_toy(key_20bit)
    state = pt & 0xFFFF

    print(f"\n{'─'*50}")
    print(f"  TOY PRESENT TRACE  (pt=0x{pt:04X}, key=0x{key_20bit:05X})")
    print(f"{'─'*50}")
    print(f"  Subkeys: {[f'0x{s:04X}' for s in sks[:rounds+1]]}")
    print(f"\n  Initial state : 0x{state:04X}  ({state:016b})")

    for r in range(rounds - 1):
        state ^= sks[r]
        print(f"\n  ── Round {r+1} ──────────────────────")
        print(f"  After AddKey  : 0x{state:04X}  ({state:016b})")
        state = apply_sbox_toy(state)
        print(f"  After SBox    : 0x{state:04X}  ({state:016b})")
        state = apply_perm_toy(state)
        print(f"  After Perm    : 0x{state:04X}  ({state:016b})")

    print(f"\n  ── Round {rounds} (Last) ──────────────")
    state ^= sks[rounds - 1]
    print(f"  After AddKey  : 0x{state:04X}  ({state:016b})")
    state = apply_sbox_toy(state)
    print(f"  After SBox    : 0x{state:04X}  ({state:016b})")
    state ^= sks[rounds]
    print(f"  Final AddKey  : 0x{state:04X}  ({state:016b})")
    print(f"\n  Ciphertext    : 0x{state:04X}")
    print(f"{'─'*50}")
    return state

# ══════════════════════════════════════════════════════════════
# SECTION 6: Run Everything
# ══════════════════════════════════════════════════════════════

SECRET_KEY = 0xABCDE   # 20-bit key

print("=" * 50)
print("  TOY PRESENT CIPHER — EDUCATIONAL DEMO")
print("=" * 50)
print(f"  Block size : 16 bits (4 nibbles)")
print(f"  Key size   : 20 bits")
print(f"  S-boxes    : 4 per round")
print(f"  Same S-box as real PRESENT")

# Step-by-step trace of one encryption
demo_trace(pt=0x1234, key_20bit=SECRET_KEY, rounds=3)

# Run differential attacks for 2, 3, 4 rounds
for rounds in [2, 3, 4]:
    toy_differential_attack(SECRET_KEY, target_rounds=rounds)
