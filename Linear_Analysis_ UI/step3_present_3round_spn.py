# ============================================================
# STEP 3
# 3-ROUND PRESENT SPN
#
# File Name:
# step3_present_3round_spn.py
#
# Goal:
# -----
# Build a REAL PRESENT-style SPN:
#
# - REAL PRESENT permutation
# - REAL diffusion
# - 3 rounds
#
# This version is more realistic
# for Linear Cryptanalysis.
#
# Later:
# - Step 4 will search for trails
# - Step 5 will recover partial key bits
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import json
import matplotlib.pyplot as plt


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
# REAL PRESENT P-LAYER
#
# Bit permutation:
#
# P(i) = 16*i mod 63
#
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
# APPLY S-box LAYER
# ============================================================

def apply_sbox(state):


    result = 0


    # ========================================================
    # 16 nibbles
    # ========================================================

    for i in range(16):


        nibble = (

            state >> (4 * i)

        ) & 0xF


        result |= (

            SBOX[nibble] << (4 * i)
        )


    return result


# ============================================================
# APPLY PRESENT PERMUTATION
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


    # ========================================================
    # ROUND 1
    # ========================================================

    state ^= round_keys[0]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # ========================================================
    # ROUND 2
    # ========================================================

    state ^= round_keys[1]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # ========================================================
    # ROUND 3
    # ========================================================

    state ^= round_keys[2]

    state = apply_sbox(state)

    state = apply_permutation(state)


    # ========================================================
    # FINAL WHITENING
    # ========================================================

    ciphertext = state ^ round_keys[3]


    return ciphertext


# ============================================================
# SAVE SIMPLE ROUND DIAGRAM
# ============================================================

def save_round_diagram():

    plt.figure(figsize=(6, 4))

    plt.axis("off")

    plt.text(0.5, 0.8, "Plaintext", ha='center', fontsize=14)

    plt.text(0.5, 0.65, "↓ AddRoundKey", ha='center')

    plt.text(0.5, 0.5, "↓ S-box Layer", ha='center')

    plt.text(0.5, 0.35, "↓ Permutation Layer", ha='center')

    plt.text(0.5, 0.2, "Ciphertext", ha='center', fontsize=14)

    plt.title("PRESENT SPN Structure")

    plt.savefig(

        "spn_structure.png",

        dpi=300,

        bbox_inches='tight'
    )

    plt.close()


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":


    print("\n================================================")
    print("STEP 3")
    print("3-ROUND PRESENT SPN")
    print("================================================")


    # ========================================================
    # FIXED PLAINTEXT
    # ========================================================

    plaintext = 0x1234567890ABCDEF


    # ========================================================
    # FIXED ROUND KEYS
    # ========================================================

    round_keys = [

        0x3A94D63F2B1C7890,
        0x56789ABCDEF01234,
        0x13579BDF2468ACE0,
        0x0F1E2D3C4B5A6978
    ]


    # ========================================================
    # ENCRYPT
    # ========================================================

    ciphertext = encrypt(

        plaintext,

        round_keys
    )

    save_round_diagram()

    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print("\nPlaintext:")

    print(f"{plaintext:064b}")


    print("\nRound Keys:")


    for i, key in enumerate(round_keys):

        print(

            f"K{i+1} = {key:064b}"
        )


    print("\nCiphertext:")

    print(f"{ciphertext:064b}")


    # ========================================================
    # SAVE FILE
    # ========================================================

    output_data = {

        "plaintext":

            plaintext,

        "round_keys":

            round_keys,

        "ciphertext":

            ciphertext
    }


    with open(

        "present_3round_cipher.json",

        "w"

    ) as f:

        json.dump(output_data, f, indent=4)


    print("\n================================================")
    print("Files Saved")
    print("================================================")


    print("\nGenerated Files:")

    print("1. present_3round_cipher.json")
    print("2. spn_structure.png")