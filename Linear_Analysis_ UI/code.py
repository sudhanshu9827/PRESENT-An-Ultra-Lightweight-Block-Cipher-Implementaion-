import random
from collections import defaultdict
import matplotlib.pyplot as plt

# ============================================================
# PRESENT SBOX
# ============================================================

SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]

INV_SBOX = [0] * 16

for i, v in enumerate(SBOX):
    INV_SBOX[v] = i

# ============================================================
# PRESENT PERMUTATION
# ============================================================

PBOX = [
    0,16,32,48,1,17,33,49,2,18,34,50,3,19,35,51,
    4,20,36,52,5,21,37,53,6,22,38,54,7,23,39,55,
    8,24,40,56,9,25,41,57,10,26,42,58,11,27,43,59,
    12,28,44,60,13,29,45,61,14,30,46,62,15,31,47,63
]

# ============================================================
# UTILITIES
# ============================================================

def add_round_key(state, key):
    return state ^ key


# ------------------------------------------------------------

def get_nibble(x, idx):
    return (x >> (4 * idx)) & 0xF


# ------------------------------------------------------------

def set_nibble(x, idx, val):

    x &= ~(0xF << (4 * idx))
    x |= (val & 0xF) << (4 * idx)

    return x


# ------------------------------------------------------------

def sbox_layer(state):

    out = 0

    for i in range(16):

        nibble = get_nibble(state, i)

        out |= SBOX[nibble] << (4 * i)

    return out


# ------------------------------------------------------------

def p_layer(state):

    out = 0

    for i in range(64):

        bit = (state >> i) & 1

        out |= bit << PBOX[i]

    return out


# ============================================================
# RANDOM ROUND KEYS
# Educational simplified setup
# ============================================================

ROUND_KEYS = [
    random.getrandbits(64),
    random.getrandbits(64),
    random.getrandbits(64),
    random.getrandbits(64)
]

print("ROUND KEY 3:", hex(ROUND_KEYS[3]))


# ============================================================
# REAL TARGET SUBKEYS
# We attack:
# nibble 1
# nibble 5
# ============================================================

REAL_K1 = get_nibble(ROUND_KEYS[3], 1)
REAL_K5 = get_nibble(ROUND_KEYS[3], 5)

REAL_TARGET = REAL_K1 | (REAL_K5 << 4)

print("REAL TARGET 8-bit SUBKEY =", hex(REAL_TARGET))


# ============================================================
# 3 ROUND PRESENT
# ============================================================

def encrypt_3round_present(pt):

    state = pt

    # ROUND 1
    state = add_round_key(state, ROUND_KEYS[0])
    state = sbox_layer(state)
    state = p_layer(state)

    # ROUND 2
    state = add_round_key(state, ROUND_KEYS[1])
    state = sbox_layer(state)
    state = p_layer(state)

    # ROUND 3
    state = add_round_key(state, ROUND_KEYS[2])
    state = sbox_layer(state)

    # FINAL WHITENING
    state = add_round_key(state, ROUND_KEYS[3])

    return state


# ============================================================
# DIFFERENTIAL PARAMETERS
#
# Trail:
# F -> 2 -> 3
#
# Active Sboxes:
# Round1 : 15
# Round2 : 7
# Round3 : 1 and 5
# ============================================================

INPUT_DIFF = 0xF

NUM_PAIRS = 2**18

pairs = []


# ============================================================
# GENERATE PAIRS
# ============================================================

for _ in range(NUM_PAIRS):

    p1 = random.getrandbits(64)

    p2 = p1 ^ INPUT_DIFF

    c1 = encrypt_3round_present(p1)
    c2 = encrypt_3round_present(p2)

    diff = c1 ^ c2

    pairs.append((c1, c2, diff))

print("Generated pairs:", len(pairs))


# ============================================================
# FILTERING
#
# We only require:
# nibble1 active
# nibble5 active
#
# Other active nibbles are allowed.
# ============================================================

filtered_pairs = []

for c1, c2, diff in pairs:

    n1 = get_nibble(diff, 1)
    n5 = get_nibble(diff, 5)

    if n1 != 0 and n5 != 0:

        filtered_pairs.append((c1, c2))

print("Filtered pairs:", len(filtered_pairs))


# ============================================================
# DIFFERENTIAL ATTACK
# ============================================================

scores = defaultdict(int)

for key_guess in range(256):

    k1 = key_guess & 0xF
    k5 = (key_guess >> 4) & 0xF

    count = 0

    for c1, c2 in filtered_pairs:

        # ====================================================
        # ONLY UNDO GUESSED NIBBLES
        #
        # Attacker does NOT know full whitening key.
        # ====================================================

        c1_n1 = get_nibble(c1, 1)
        c2_n1 = get_nibble(c2, 1)

        c1_n5 = get_nibble(c1, 5)
        c2_n5 = get_nibble(c2, 5)

        # ----------------------------------------------------
        # Partial inverse whitening
        # ----------------------------------------------------

        u1_n1 = c1_n1 ^ k1
        u2_n1 = c2_n1 ^ k1

        u1_n5 = c1_n5 ^ k5
        u2_n5 = c2_n5 ^ k5

        # ----------------------------------------------------
        # Inverse sbox
        # ----------------------------------------------------

        v1_n1 = INV_SBOX[u1_n1]
        v2_n1 = INV_SBOX[u2_n1]

        v1_n5 = INV_SBOX[u1_n5]
        v2_n5 = INV_SBOX[u2_n5]

        # ----------------------------------------------------
        # Backward difference
        # ----------------------------------------------------

        d1 = v1_n1 ^ v2_n1
        d5 = v1_n5 ^ v2_n5

        # ====================================================
        # EXPECTED INPUT DIFFERENCE TO ROUND3 SBOXES
        #
        # From our trail:
        # 2 -> 3
        #
        # so input difference should be 1
        # ====================================================

        if d1 == 0x1 and d5 == 0x1:

            count += 1

    scores[key_guess] = count


# ============================================================
# SORT RESULTS
# ============================================================

best = sorted(
    scores.items(),
    key=lambda x: x[1],
    reverse=True
)


# ============================================================
# HISTOGRAM
# ============================================================

xvals = list(scores.keys())
yvals = list(scores.values())

plt.figure(figsize=(16, 6))

bars = plt.bar(xvals, yvals)

# Highlight real key
bars[REAL_TARGET].set_color('red')

plt.xlabel("8-bit Key Guess")
plt.ylabel("Score")
plt.title("3-Round PRESENT Differential Cryptanalysis")

plt.show()


# ============================================================
# RESULTS
# ============================================================

print("\n================================================")
print("TOP KEY CANDIDATES")
print("================================================\n")

for k, v in best[:15]:

    marker = ""

    if k == REAL_TARGET:
        marker = "<-- REAL KEY"

    print(
        f"Key Guess = {hex(k):>6} "
        f"Score = {v:>4} "
        f"{marker}"
    )

print("\nREAL TARGET KEY =", hex(REAL_TARGET))