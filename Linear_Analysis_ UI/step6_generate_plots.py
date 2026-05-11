# ============================================================
# STEP 6
# GENERATE PLOTS
#
# File Name:
# step6_generate_plots.py
#
# Goal:
# -----
# Generate plots for:
#
# 1. LAT Heatmap
# 2. Approximation Comparison
# 3. Key Ranking
#
# All plots saved inside:
#
# plots/
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import json
import os

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

PLOT_FOLDER = "plots"

os.makedirs(PLOT_FOLDER, exist_ok=True)


# ============================================================
# LOAD LAT
# ============================================================

with open(

    "lat.json",

    "r"

) as f:

    LAT = json.load(f)


LAT = np.array(LAT)


# ============================================================
# PLOT 1
# LAT HEATMAP
# ============================================================

plt.figure(figsize=(10, 8))

plt.imshow(

    LAT,

    cmap="coolwarm",

    interpolation="nearest"
)

plt.colorbar(label="Bias")


plt.title(

    "Linear Approximation Table (LAT)"
)

plt.xlabel("Output Mask β")

plt.ylabel("Input Mask α")


plt.xticks(range(16))

plt.yticks(range(16))


plt.tight_layout()


plt.savefig(

    os.path.join(

        PLOT_FOLDER,

        "lat_heatmap.png"
    ),

    dpi=300,

    facecolor="white"
)

plt.close()


# ============================================================
# LOAD TOP APPROXIMATIONS
# ============================================================

with open(

    "best_approximations.json",

    "r"

) as f:

    approximations = json.load(f)


# ============================================================
# PLOT 2
# TOP APPROXIMATION BIASES
# ============================================================

labels = []

biases = []


for item in approximations[:10]:


    alpha = item["input_mask"]

    beta = item["output_mask"]

    bias = abs(item["bias"])


    labels.append(

        f"{alpha:X}->{beta:X}"
    )

    biases.append(bias)


plt.figure(figsize=(12, 5))

plt.bar(

    labels,

    biases
)

plt.xlabel("Approximation (α → β)")

plt.ylabel("LAT Bias")

plt.title(

    "Top Linear Approximations"
)

plt.grid(True, axis='y')

plt.xticks(rotation=45)

plt.tight_layout()


plt.savefig(

    os.path.join(

        PLOT_FOLDER,

        "approximation_biases.png"
    ),

    dpi=300,

    facecolor="white"
)

plt.close()


# ============================================================
# LOAD KEY RECOVERY RESULTS
# ============================================================

with open(

    "present_partial_key_results.json",

    "r"

) as f:

    key_data = json.load(f)


results = key_data["results"]

real_key = key_data["real_key"]


# ============================================================
# SORT RESULTS
# ============================================================

results.sort(

    key=lambda x:

    x["bias"],

    reverse=True
)


# ============================================================
# PREPARE KEY RANKING DATA
# ============================================================

labels = []

biases = []

colors = []


for item in results:


    key = item["key_guess"]

    bias = item["bias"]


    labels.append(

        f"{key:04b}"
    )

    biases.append(bias)


    # ========================================================
    # HIGHLIGHT REAL KEY
    # ========================================================

    if key == real_key:

        colors.append("red")

    else:

        colors.append("steelblue")


# ============================================================
# PLOT 3
# KEY RANKING
# ============================================================

plt.figure(figsize=(12, 6))

plt.bar(

    labels,

    biases,

    color=colors
)

plt.xlabel("Key Guess")

plt.ylabel("Bias")

plt.title(

    "Partial Key Recovery Ranking"
)

plt.grid(True, axis='y')

plt.tight_layout()


plt.savefig(

    os.path.join(

        PLOT_FOLDER,

        "key_ranking.png"
    ),

    dpi=300,

    facecolor="white"
)

plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n================================================")
print("PLOTS GENERATED")
print("================================================")


print(f"\nSaved inside folder: {PLOT_FOLDER}")


print("\nGenerated Files:")

print("1. lat_heatmap.png")

print("2. approximation_biases.png")

print("3. key_ranking.png")