# ============================================================
# STEP 1 : LINEAR MASKS AND S-BOX UTILITIES
# File Name : step1_linear_masks.py
#
# Goal:
# -----
# This step implements the basic mathematical operations
# required for Linear Cryptanalysis.
#
# Following:
# - Lecture 10
# - Lecture 11
#
# Concepts Implemented:
# ---------------------
# 1. PRESENT 4-bit S-box
# 2. Bit parity
# 3. Linear mask / scalar product
# 4. Testing linear equations
#
# Mathematical Equation:
# ----------------------
# Linear cryptanalysis studies equations of the form:
#
#      α · x = β · S(x)
#
# where:
#   α = input mask
#   β = output mask
#   x = plaintext/input
#   S(x) = S-box output
#
# The dot product means XOR of selected bits.
#
# Example:
#
# α = 1010
# x = 1101
#
# α · x = (1·1) ⊕ (0·1) ⊕ (1·0) ⊕ (0·1)
#        = 1 ⊕ 0
#        = 1
#
# ============================================================


# ============================================================
# PRESENT S-box
# ============================================================
#
# This is the 4-bit substitution box used in PRESENT cipher.
#
# Input  -> Output
# 0000   -> 1100
# 0001   -> 0101
# ...
#
# We use decimal representation internally.
#
# Example:
# SBOX[0] = 12 (1100)
#
# ============================================================

SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]


# ============================================================
# FUNCTION : parity(x)
# ============================================================
#
# Computes XOR of all bits of x.
#
# Mathematical Meaning:
#
# parity(1011)
# = 1 ⊕ 0 ⊕ 1 ⊕ 1
# = 1
#
# parity(1100)
# = 1 ⊕ 1 ⊕ 0 ⊕ 0
# = 0
#
# Used heavily in linear cryptanalysis.
#
# ============================================================

def parity(x):

    # Count number of 1-bits
    ones = bin(x).count("1")

    # If odd number of 1s -> parity = 1
    # If even number of 1s -> parity = 0
    return ones % 2


# ============================================================
# FUNCTION : linear_mask(mask, value)
# ============================================================
#
# Computes:
#
#      mask · value
#
# using parity.
#
# Mathematical Formula:
#
#      α · x = parity(α AND x)
#
# Example:
#
# α = 1010
# x = 1101
#
# α AND x = 1000
#
# parity(1000) = 1
#
# So:
#
# α · x = 1
#
# ============================================================

def linear_mask(mask, value):

    # Select only bits indicated by mask
    masked_value = mask & value

    # Compute XOR/parity of selected bits
    return parity(masked_value)


# ============================================================
# FUNCTION : test_linear_relation(alpha, beta, x)
# ============================================================
#
# Tests the linear approximation:
#
#      α · x = β · S(x)
#
# Returns:
# --------
# True  -> equation satisfied
# False -> equation not satisfied
#
# ============================================================

def test_linear_relation(alpha, beta, x):

    # Left side:
    # α · x
    left = linear_mask(alpha, x)

    # Compute S-box output
    sbox_output = SBOX[x]

    # Right side:
    # β · S(x)
    right = linear_mask(beta, sbox_output)

    # Check if equation holds
    return left == right


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n================================================")
    print("STEP 1 : LINEAR MASKS AND S-BOX UTILITIES")
    print("================================================")


    # ========================================================
    # TEST 1 : Parity Function
    # ========================================================

    print("\n[TEST 1] PARITY FUNCTION")

    test_value = 0b1011

    print("Input binary =", format(test_value, "04b"))

    result = parity(test_value)

    print("Parity =", result)

    print("\nExplanation:")
    print("1 XOR 0 XOR 1 XOR 1 = 1")


    # ========================================================
    # TEST 2 : Linear Mask Operation
    # ========================================================

    print("\n================================================")
    print("[TEST 2] LINEAR MASK / SCALAR PRODUCT")
    print("================================================")

    alpha = 0b1010
    x = 0b1101

    print("\nInput mask α =", format(alpha, "04b"))
    print("Input value x =", format(x, "04b"))

    result = linear_mask(alpha, x)

    print("\nα · x =", result)

    print("\nExplanation:")
    print("α AND x =", format(alpha & x, "04b"))
    print("Parity of selected bits =", result)


    # ========================================================
    # TEST 3 : Linear Approximation Equation
    # ========================================================

    print("\n================================================")
    print("[TEST 3] LINEAR APPROXIMATION")
    print("================================================")

    alpha = 0b0001
    beta = 0b0101
    x = 0b0110

    print("\nTesting equation:")
    print("α · x = β · S(x)")

    print("\nα =", format(alpha, "04b"))
    print("β =", format(beta, "04b"))
    print("x =", format(x, "04b"))

    # Compute S-box output
    s_output = SBOX[x]

    print("S(x) =", format(s_output, "04b"))

    left = linear_mask(alpha, x)
    right = linear_mask(beta, s_output)

    print("\nLeft Side  (α · x)     =", left)
    print("Right Side (β · S(x)) =", right)

    relation = test_linear_relation(alpha, beta, x)

    print("\nEquation Satisfied ?", relation)


    # ========================================================
    # SAVE SMALL OUTPUT FILE
    # ========================================================

    # Save outputs so later steps / report can use them

    with open("step1_output.txt", "w") as f:

        f.write("STEP 1 OUTPUT\n")
        f.write("=========================\n\n")

        f.write("Parity Test:\n")
        f.write(f"Input = {format(test_value,'04b')}\n")
        f.write(f"Parity = {result}\n\n")

        f.write("Linear Approximation Test:\n")
        f.write(f"alpha = {format(alpha,'04b')}\n")
        f.write(f"beta  = {format(beta,'04b')}\n")
        f.write(f"x     = {format(x,'04b')}\n")
        f.write(f"S(x)  = {format(s_output,'04b')}\n")
        f.write(f"Left  = {left}\n")
        f.write(f"Right = {right}\n")
        f.write(f"Relation Holds = {relation}\n")


    print("\n================================================")
    print("Output saved to step1_output.txt")
    print("================================================")