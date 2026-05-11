# ============================================================
# STEP 2 : CONSTRUCT LINEAR APPROXIMATION TABLE (LAT)
# File Name : step2_compute_LAT.py
#
# Goal:
# -----
# Construct the Linear Approximation Table (LAT)
# of the PRESENT S-box.
#
# Following:
# - Lecture 10
# - Lecture 11
#
# Mathematical Idea:
# ------------------
#
# For every:
#
#   α = input mask
#   β = output mask
#
# we test:
#
#      α · x = β · S(x)
#
# for ALL possible 4-bit inputs x.
#
# If the equation holds more often than 8 times,
# there exists positive bias.
#
# If it holds less often than 8 times,
# there exists negative bias.
#
# Bias Formula:
#
#      LAT[α][β] = count - 8
#
# because:
#
# Random behavior for 4-bit inputs:
# equation should hold exactly:
#
#      16 / 2 = 8 times
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import json
import matplotlib.pyplot as plt
import numpy as np


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
# FUNCTION : parity(x)
# ============================================================
#
# Computes XOR of all bits.
#
# ============================================================

def parity(x):

    return bin(x).count("1") % 2


# ============================================================
# FUNCTION : linear_mask(mask, value)
# ============================================================
#
# Computes:
#
#      mask · value
#
# using:
#
#      parity(mask AND value)
#
# ============================================================

def linear_mask(mask, value):

    return parity(mask & value)


# ============================================================
# FUNCTION : compute_LAT()
# ============================================================
#
# Builds the complete LAT table.
#
# LAT size:
#
#      16 x 16
#
# because:
#
# - 16 input masks
# - 16 output masks
#
# ============================================================

def compute_LAT():

    # Create empty 16x16 table
    LAT = [[0 for _ in range(16)] for _ in range(16)]


    # ========================================================
    # Loop over ALL input masks α
    # ========================================================

    for alpha in range(16):


        # ====================================================
        # Loop over ALL output masks β
        # ====================================================

        for beta in range(16):


            # Counter:
            # how many times equation holds
            count = 0


            # =================================================
            # Test ALL possible 4-bit inputs x
            # =================================================

            for x in range(16):


                # =============================================
                # LEFT SIDE:
                #
                # α · x
                # =============================================

                left = linear_mask(alpha, x)


                # =============================================
                # Compute S-box output
                # =============================================

                s_output = SBOX[x]


                # =============================================
                # RIGHT SIDE:
                #
                # β · S(x)
                # =============================================

                right = linear_mask(beta, s_output)


                # =============================================
                # Check linear approximation
                #
                # α · x = β · S(x)
                # =============================================

                if left == right:

                    count += 1


            # =================================================
            # Compute bias
            #
            # Expected random count = 8
            #
            # bias = count - 8
            # =================================================

            LAT[alpha][beta] = count - 8


    return LAT


# ============================================================
# FUNCTION : print_LAT(LAT)
# ============================================================
#
# Prints LAT nicely.
#
# ============================================================

def print_LAT(LAT):

    print("\n================================================")
    print("LINEAR APPROXIMATION TABLE (LAT)")
    print("================================================\n")


    # ========================================================
    # Column headers
    # ========================================================

    print("      ", end="")

    for beta in range(16):

        print(f"{beta:>4X}", end="")

    print()


    print("     " + "-" * 65)


    # ========================================================
    # Print each row
    # ========================================================

    for alpha in range(16):

        print(f"{alpha:>3X} |", end="")

        for beta in range(16):

            print(f"{LAT[alpha][beta]:>4}", end="")

        print()


# ============================================================
# FUNCTION : find_best_approximations(LAT)
# ============================================================
#
# Finds strongest non-trivial approximations.
#
# Ignore:
#
# α = 0000
# β = 0000
#
# because they are trivial.
#
# ============================================================

def find_best_approximations(LAT):

    best = []

    max_bias = 0


    # ========================================================
    # Search entire LAT
    # ========================================================

    for alpha in range(1, 16):

        for beta in range(1, 16):


            bias = LAT[alpha][beta]


            # ================================================
            # Keep track of strongest absolute bias
            # ================================================

            if abs(bias) > abs(max_bias):

                max_bias = bias


    # ========================================================
    # Store all approximations with strongest bias
    # ========================================================

    for alpha in range(1, 16):

        for beta in range(1, 16):

            bias = LAT[alpha][beta]

            if abs(bias) == abs(max_bias):

                best.append({

                    "input_mask": alpha,
                    "output_mask": beta,
                    "bias": bias,

                    # Correlation:
                    #
                    # bias / 8
                    #
                    "correlation": bias / 8,

                    # Probability:
                    #
                    # (8 + bias) / 16
                    #
                    "probability":

                        (8 + bias) / 16
                })

    return best


# ============================================================
# FUNCTION : save_results()
# ============================================================
#
# Saves LAT and best approximations.
#
# ============================================================

def save_results(LAT, best_approximations):


    # ========================================================
    # Save LAT
    # ========================================================

    with open("lat.json", "w") as f:

        json.dump(LAT, f, indent=4)


    # ========================================================
    # Save strongest approximations
    # ========================================================

    with open("best_approximations.json", "w") as f:

        json.dump(best_approximations, f, indent=4)


    # ========================================================
    # Save readable text file
    # ========================================================

    with open("step2_output.txt", "w") as f:

        f.write("STEP 2 OUTPUT\n")
        f.write("==============================\n\n")

        f.write("Strongest Linear Approximations\n\n")


        for entry in best_approximations:

            f.write(

                f"alpha = "
                f"{entry['input_mask']:04b}"

                f" | beta = "
                f"{entry['output_mask']:04b}"

                f" | bias = "
                f"{entry['bias']}"

                f" | probability = "
                f"{entry['probability']:.4f}\n"
            )

# ============================================================
# FUNCTION : save_LAT_table_image(LAT)
#
# Saves actual LAT matrix as image
# with all values visible.
# ============================================================

# ============================================================
# FUNCTION : save_LAT_table_image(LAT)
#
# Creates a professional-looking LAT table image
# ============================================================

# ============================================================
# FUNCTION : save_LAT_table_image(LAT)
#
# Creates a professional square LAT table image
# ============================================================

def save_LAT_table_image(LAT):

    # ========================================================
    # CREATE SQUARE FIGURE
    # ========================================================

    fig, ax = plt.subplots(figsize=(12, 12))

    ax.axis('off')


    # ========================================================
    # BUILD TABLE DATA
    # ========================================================

    table_data = []


    # ========================================================
    # HEADER ROW
    # ========================================================

    header = ["α \\ β"] + [f"{i:X}" for i in range(16)]

    table_data.append(header)


    # ========================================================
    # LAT VALUES
    # ========================================================

    for alpha in range(16):

        row = [f"{alpha:X}"]

        for beta in range(16):

            row.append(str(LAT[alpha][beta]))

        table_data.append(row)


    # ========================================================
    # CREATE TABLE
    # ========================================================

    table = ax.table(

        cellText=table_data,

        loc='center',

        cellLoc='center'
    )


    # ========================================================
    # FONT SETTINGS
    # ========================================================

    table.auto_set_font_size(False)

    table.set_fontsize(10)


    # ========================================================
    # MAKE TABLE LOOK SQUARE
    # ========================================================

    table.scale(1.25, 1.25)


    # ========================================================
    # STYLE TABLE
    # ========================================================

    for (row, col), cell in table.get_celld().items():


        # ====================================================
        # HEADER CELLS
        # ====================================================

        if row == 0 or col == 0:

            cell.set_facecolor("#2F5597")

            cell.set_text_props(

                color='white',

                weight='bold'
            )


        else:

            value = int(table_data[row][col])


            # =================================================
            # STRONG POSITIVE BIAS
            # =================================================

            if value >= 4:

                cell.set_facecolor("#C6EFCE")

                cell.set_text_props(

                    color='darkgreen',

                    weight='bold'
                )


            # =================================================
            # STRONG NEGATIVE BIAS
            # =================================================

            elif value <= -4:

                cell.set_facecolor("#FFC7CE")

                cell.set_text_props(

                    color='darkred',

                    weight='bold'
                )


            # =================================================
            # ZERO VALUES
            # =================================================

            elif value == 0:

                cell.set_facecolor("#F2F2F2")


            # =================================================
            # MEDIUM VALUES
            # =================================================

            else:

                cell.set_facecolor("#FFF2CC")


        # ====================================================
        # CELL BORDER
        # ====================================================

        cell.set_edgecolor("black")


    # ========================================================
    # TITLE
    # ========================================================

    plt.title(

        "Linear Approximation Table (LAT) of PRESENT S-box",

        fontsize=18,

        fontweight='bold',

        pad=25
    )


    # ========================================================
    # CLEAN SPACING
    # ========================================================

    plt.tight_layout()


    # ========================================================
    # SAVE IMAGE
    # ========================================================

    plt.savefig(

        "LAT_table.png",

        dpi=300,

        bbox_inches='tight',

        facecolor='white'
    )

    plt.close()


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n================================================")
    print("STEP 2 : COMPUTE LAT")
    print("================================================")


    # ========================================================
    # Compute LAT
    # ========================================================

    LAT = compute_LAT()

    # Save LAT image image
    save_LAT_table_image(LAT)

    # ========================================================
    # Print LAT
    # ========================================================

    print_LAT(LAT)


    # ========================================================
    # Find strongest approximations
    # ========================================================

    best_approximations = find_best_approximations(LAT)


    # ========================================================
    # Print strongest approximations
    # ========================================================

    print("\n================================================")
    print("STRONGEST LINEAR APPROXIMATIONS")
    print("================================================")


    for entry in best_approximations:

        print(

            f"\nα = {entry['input_mask']:04b}"

            f" | β = {entry['output_mask']:04b}"

            f" | bias = {entry['bias']}"

            f" | correlation = {entry['correlation']:.3f}"

            f" | probability = {entry['probability']:.3f}"
        )


    # ========================================================
    # Save outputs
    # ========================================================

    save_results(LAT, best_approximations)