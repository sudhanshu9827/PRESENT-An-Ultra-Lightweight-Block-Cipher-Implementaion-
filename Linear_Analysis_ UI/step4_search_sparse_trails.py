# ============================================================
# STEP 4
# SEARCH SPARSE LINEAR TRAILS
#
# File Name:
# step4_search_sparse_trails.py
#
# Goal:
# -----
# Search for:
#
# - sparse mask propagation
# - minimum active S-boxes
# - strongest practical trails
#
# using:
#
# - REAL PRESENT permutation
# - REAL diffusion
#
# This follows actual LC methodology.
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import json
import matplotlib.pyplot as plt


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
# APPLY PRESENT PERMUTATION TO MASK
# ============================================================

def permute_mask(mask):


    result = 0


    for i in range(64):


        bit = (

            mask >> i

        ) & 1


        result |= (

            bit << PBOX[i]
        )


    return result


# ============================================================
# COUNT ACTIVE S-boxes
#
# One active nibble = nonzero nibble
# ============================================================

def count_active_sboxes(mask):


    count = 0


    for i in range(16):


        nibble = (

            mask >> (4 * i)

        ) & 0xF


        if nibble != 0:

            count += 1


    return count


# ============================================================
# LOAD BEST APPROXIMATIONS
# ============================================================

with open(

    "best_approximations.json",

    "r"

) as f:

    approximations = json.load(f)


# ============================================================
# STORE TRAIL RESULTS
# ============================================================

trail_results = []


print("\n================================================")
print("STEP 4")
print("SEARCH SPARSE LINEAR TRAILS")
print("================================================")


# ============================================================
# TEST TOP APPROXIMATIONS
# ============================================================

TOP_N = 20


for approx in approximations[:TOP_N]:


    alpha = approx["input_mask"]

    beta = approx["output_mask"]

    lat_bias = approx["bias"]


    # ========================================================
    # ROUND 1 MASK
    #
    # Activate ONLY first S-box
    # ========================================================

    round1_input = alpha

    round1_output = beta


    # ========================================================
    # PROPAGATE THROUGH PRESENT P-LAYER
    # ========================================================

    propagated = permute_mask(

        round1_output
    )


    # ========================================================
    # COUNT ACTIVE S-boxes AFTER PERMUTATION
    # ========================================================

    active_sboxes = count_active_sboxes(

        propagated
    )


    trail_results.append({

        "alpha":

            alpha,

        "beta":

            beta,

        "lat_bias":

            lat_bias,

        "propagated_mask":

            propagated,

        "active_sboxes":

            active_sboxes
    })


# ============================================================
# SORT:
#
# 1. MINIMUM ACTIVE S-boxes
# 2. MAXIMUM LAT BIAS
# ============================================================

trail_results.sort(

    key=lambda x:

    (

        x["active_sboxes"],

        -abs(x["lat_bias"])
    )
)

# ============================================================
# SAVE TRAIL VISUALIZATION
# ============================================================

# ============================================================
# SAVE TRAIL VISUALIZATION
# ============================================================

def save_trail_plot(trails):

    labels = []

    active = []


    for trail in trails[:10]:

        labels.append(

            f"{trail['alpha']:04b}->{trail['beta']:04b}"
        )

        active.append(

            trail['active_sboxes']
        )


    plt.figure(figsize=(12, 5))

    plt.bar(labels, active)

    plt.xlabel("Linear Trail")

    plt.ylabel("Active S-boxes")

    plt.title("Sparse Linear Trails")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(

        "sparse_trails.png",

        dpi=300,

        facecolor="white"
    )

    plt.close()


save_trail_plot(trail_results)

# ============================================================
# PRINT BEST TRAILS
# ============================================================

print("\n================================================")
print("BEST SPARSE TRAILS")
print("================================================")


TOP_SHOW = 10


for i, trail in enumerate(trail_results[:TOP_SHOW]):


    print(

        f"\nTrail {i+1}"
    )


    print(

        f"α = {trail['alpha']:04b}"
    )


    print(

        f"β = {trail['beta']:04b}"
    )


    print(

        f"LAT Bias = {trail['lat_bias']}"
    )


    print(

        f"Propagated Mask = "

        f"{trail['propagated_mask']:064b}"
    )


    print(

        f"Active S-boxes = "

        f"{trail['active_sboxes']}"
    )


# ============================================================
# BEST TRAIL
# ============================================================

best = trail_results[0]


print("\n================================================")
print("SELECTED TRAIL")
print("================================================")


print(f"\nα = {best['alpha']:04b}")

print(f"β = {best['beta']:04b}")

print(f"LAT Bias = {best['lat_bias']}")

print(

    f"Active S-boxes = "

    f"{best['active_sboxes']}"
)


# ============================================================
# SAVE BEST TRAIL
# ============================================================

with open(

    "best_sparse_trail.json",

    "w"

) as f:

    json.dump(best, f, indent=4)


print("\n================================================")
print("Files Saved")
print("================================================")


print("\nGenerated Files:")

print("1. best_sparse_trail.json")
print("2. sparse_trails.png")