# ============================================================
# STEP 5
# PARTIAL KEY RECOVERY ON 3-ROUND PRESENT
#
# File Name:
# step5_present_partial_key_recovery.py
#
# Goal:
# -----
# Perform Linear Cryptanalysis using:
#
# - REAL PRESENT permutation
# - sparse optimized trail
# - partial last-round decryption
#
# Attack:
# -------
#
# Recover one last-round nibble subkey.
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import json
import random
import matplotlib.pyplot as plt

random.seed(42)
# ============================================================
# PRESENT S-box
# ============================================================

SBOX = [

    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]


# ============================================================
# INVERSE S-box
# ============================================================

INV_SBOX = [0] * 16

for i in range(16):

    INV_SBOX[SBOX[i]] = i


# ============================================================
# REAL PRESENT P-LAYER
# ============================================================

PBOX = [

     0, 16, 32, 48,
     1, 17, 33, 49,
     2, 18, 34, 50,
     3, 19, 35, 51,

     4, 20, 36, 52,
     5, 21, 37, 53,
     6, 22, 38, 54,
     7, 23, 39, 55,

     8, 24, 40, 56,
     9, 25, 41, 57,
    10, 26, 42, 58,
    11, 27, 43, 59,

    12, 28, 44, 60,
    13, 29, 45, 61,
    14, 30, 46, 62,
    15, 31, 47, 63
]


# ============================================================
# PARITY
# ============================================================

def parity(x):

    return bin(x).count("1") % 2


# ============================================================
# LINEAR MASK
# ============================================================

def linear_mask(mask, value):

    return parity(mask & value)


# ============================================================
# APPLY SBOX
# ============================================================

def apply_sbox(state):


    result = 0


    for i in range(16):


        nibble = (

            state >> (4 * i)

        ) & 0xF


        result |= (

            SBOX[nibble] << (4 * i)
        )


    return result


# ============================================================
# APPLY PERMUTATION
# ============================================================

def apply_permutation(state):


    result = 0


    for i in range(64):


        bit = (

            state >> i

        ) & 1


        result |= (

            bit << PBOX[i]
        )


    return result


# ============================================================
# ENCRYPTION
# ============================================================

def encrypt(plaintext, round_keys):


    state = plaintext


    # ROUND 1

    state ^= round_keys[0]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # ROUND 2

    state ^= round_keys[1]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # ROUND 3

    state ^= round_keys[2]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # FINAL WHITENING

    ciphertext = state ^ round_keys[3]


    return ciphertext

# ============================================================
# SAVE KEY RANKING PLOT
# ============================================================

def save_key_ranking_plot(results, real_key):

    labels = []

    biases = []

    colors = []


    for item in results:


        labels.append(

            f"{item['key_guess']:04b}"
        )

        biases.append(

            item['bias']
        )


        # Highlight REAL KEY
        if item['key_guess'] == real_key:

            colors.append("red")

        else:

            colors.append("steelblue")


    plt.figure(figsize=(12, 5))

    plt.bar(

        labels,

        biases,

        color=colors
    )

    plt.xlabel("Key Guess")

    plt.ylabel("Bias")

    plt.title("Partial Key Recovery Ranking")

    plt.grid(True, axis='y')

    plt.tight_layout()

    plt.savefig(

        "key_ranking.png",

        dpi=300,

        facecolor="white"
    )

    plt.close()

# ============================================================
# LOAD BEST TRAIL
# ============================================================

with open(

    "best_sparse_trail.json",

    "r"

) as f:

    trail = json.load(f)


alpha = 0b0111
beta  = 0b0100


# ============================================================
# FIXED ROUND KEYS
# ============================================================

round_keys = [

    0x3A94D63F2B1C7890,
    0x56789ABCDEF01234,
    0x13579BDF2468ACE0,
    0x0F1E2D3C4B5A6978
]


# ============================================================
# TARGET LAST ROUND NIBBLE
#
# Since trail activates one nibble,
# attack lowest nibble only.
# ============================================================

real_subkey = 0b1000


print("\n================================================")
print("STEP 5")
print("PRESENT PARTIAL KEY RECOVERY")
print("================================================")


print("\nSelected Trail:")

print(f"α = {alpha:04b}")

print(f"β = {beta:04b}")


print("\nReal Subkey:")

print(f"{real_subkey:04b}")


# ============================================================
# GENERATE PLAINTEXT/CIPHERTEXT PAIRS
# ============================================================

NUM_SAMPLES = 200000


print("\nGenerating plaintext-ciphertext pairs...")


pairs = []


for _ in range(NUM_SAMPLES):


    plaintext = random.getrandbits(64)

    ciphertext = encrypt(

        plaintext,

        round_keys
    )

    pairs.append((plaintext, ciphertext))


print("Done.")


# ============================================================
# STORE RESULTS
# ============================================================

key_results = []


# ============================================================
# TRY ALL 16 SUBKEY GUESSES
# ============================================================

for guessed_key in range(16):


    count = 0


    for plaintext, ciphertext in pairs:


        # ====================================================
        # TARGET CIPHERTEXT NIBBLE
        # ====================================================

        c = ciphertext & 0xF


        # ====================================================
        # PARTIAL DECRYPTION
        # ====================================================

        u = c ^ guessed_key

        u = INV_SBOX[u]


        # ====================================================
        # LEFT SIDE
        # ====================================================

        left = linear_mask(

            alpha,

            plaintext & 0xF
        )


        # ====================================================
        # RIGHT SIDE
        # ====================================================

        right = linear_mask(

            beta,

            u
        )


        # ====================================================
        # CHECK APPROXIMATION
        # ====================================================

        if left == right:

            count += 1


    probability = count / NUM_SAMPLES

    bias = abs(

        probability - 0.5
    )


    key_results.append({

        "key_guess":

            guessed_key,

        "bias":

            bias,

        "probability":

            probability
    })


# ============================================================
# SORT RESULTS
# ============================================================

key_results.sort(

    key=lambda x:

    x["bias"],

    reverse=True
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n================================================")
print("KEY RANKING")
print("================================================")


real_rank = None


for rank, result in enumerate(key_results):


    key_guess = result["key_guess"]

    bias = result["bias"]

    probability = result["probability"]


    marker = ""


    if key_guess == real_subkey:

        marker = " <-- REAL KEY"

        real_rank = rank + 1


    print(

        f"\nRank {rank+1:2d}"

        f" | Key = {key_guess:04b}"

        f" | Bias = {bias:.8f}"

        f" | Probability = {probability:.8f}"

        f"{marker}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

best_guess = key_results[0]["key_guess"]


print("\n================================================")
print("FINAL RESULT")
print("================================================")


print(f"\nBest Key Guess = {best_guess:04b}")

print(f"Real Key       = {real_subkey:04b}")

print(f"Real Key Rank  = {real_rank}")


# ============================================================
# SAVE RESULTS
# ============================================================

output_data = {

    "real_key":

        real_subkey,

    "real_rank":

        real_rank,

    "results":

        key_results
}


with open(

    "present_partial_key_results.json",

    "w"

) as f:

    json.dump(output_data, f, indent=4)


print("\n================================================")
print("Files Saved")
print("================================================")


print("\nGenerated Files:")

print("1. present_partial_key_results.json")