"""
GreenLight/scripts/katzin_2021/katzin_2021_generate_output.py
Copyright (c) 2025 David Katzin, Wageningen Research Foundation
SPDX-License-Identifier: BSD-3-Clause-Clear
https://github.com/davkat1/GreenLight

Script for generating Figure 6 from Katzin (2021a), which also appeared as Katzin (2021) Chapter 4.
The script also generates figures comparing the result from the current simulation and the data in Katzin 2021.

This script assumes that katzin_2021_run_sims.py has been run successfully, and that the output files are in
models/katzin_2021/output

References:
    Katzin, Marcelis, Van Mourik (2021a). “Energy Savings in Greenhouses by Transition from High-Pressure Sodium
        to LED Lighting.” Applied Energy 281: 116019. https://doi.org/10.1016/j.apenergy.2020.116019.
    Katzin, D. (2021). Energy Saving by LED Lighting in Greenhouses : A Process-Based Modelling Approach.
        PhD thesis, Wageningen University. https://doi.org/10.18174/544434
"""

import os
import re
import sys

import matplotlib
import numpy as np

import scripts.analyze_output as ao

matplotlib.use("TkAgg")  # Ensure that the TkAgg backend is used

# "noqa: E402" is used to have the linter/pre-commit ignore the rule "E402 module level import not at top of file"
# This allows to set the TkAgg backend for matplotlib
import matplotlib.pyplot as plt  # noqa: E402

"""Set up directories"""
if "__file__" in locals():  # Running this from script
    project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
else:
    project_dir = os.getcwd()  # Most likely the active directory is the project directory
sys.path.append(project_dir)

# Location of simulation outputs
output_dir = os.path.join(project_dir, "models", "katzin_2021", "output")

"""Get list of location names"""
# Regex pattern for file names of the form "katzin_2021_<xxx>_led.csv"
pattern = r"^katzin_2021_([A-Za-z]{3})_led.csv$"
locations = []
for file_name in os.listdir(output_dir):
    match = re.match(pattern, file_name)
    if match:
        locations.append(match.group(1))

# Lists that contain the data generated by the simulation
greenlight2_data = []
labels2 = []

# Load the data and location names
for i, loc in enumerate(locations, start=1):
    print(f"Loading location {i}/15... ")
    for lamp in ["HPS", "LED"]:
        file_path = os.path.join(output_dir, "katzin_2021_" + loc + "_" + lamp.lower() + ".csv")
        out_df = ao.make_output_df(file_path)

        time_step = out_df.loc[1, "Time"] - out_df.loc[0, "Time"]
        heat = time_step * (sum(out_df["hBoilPipe"]) + sum(out_df["hBoilGroPipe"])) * 1e-6
        light = time_step * (sum(out_df["qLampIn"]) + sum(out_df["qIntLampIn"])) * 1e-6

        greenlight2_data.append([heat, light])
        labels2.append(loc + lamp)


"""Make bar charts"""
# Convert list to a numpy array (2-column matrix)
bardata = np.array(greenlight2_data)
labels = labels2

# Plot the matrix as a bar plot
fig, ax = plt.subplots()

b1 = ax.bar(labels, bardata[:, 0])
b2 = ax.bar(labels, bardata[:, 1], bottom=bardata[:, 0])

# Add data values of bars
for bar in b1:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        2000,
        f"{height:.0f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

for bar in b2:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        3000,
        f"{height:.0f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

ax.set_ylabel("Values (MJ/m2)")
ax.set_xlabel("Files")
ax.set_title("Bar Plot of Extracted Values")
ax.legend(["Heating", "Lighting"])
plt.xticks(rotation=45)  # Rotate labels for readability
plt.ylim([0, 3500])
plt.show()

"""Compare results to data from Katzin 2021"""

# The data from Katzin 2021 - simply typed in from the published paper
katzin_2021_data = np.array(
    [
        [831, 1459],
        [1040, 875],
        [923, 1592],
        [1147, 955],
        [1381, 1511],
        [1567, 907],
        [660, 787],
        [739, 472],
        [1397, 1110],
        [1525, 666],
        [270, 1563],
        [402, 938],
        [1739, 1656],
        [1929, 994],
        [919, 1434],
        [1109, 860],
        [1132, 1227],
        [1292, 737],
        [438, 920],
        [521, 552],
        [1007, 1524],
        [1214, 915],
        [554, 856],
        [638, 514],
        [1065, 1012],
        [1193, 607],
        [443, 1309],
        [607, 785],
        [895, 941],
        [1014, 565],
    ]
)

"""Relative difference"""
fig, ax = plt.subplots()

b1 = ax.bar(labels, bardata[:, 0] / katzin_2021_data[:, 0])
b2 = ax.bar(labels, bardata[:, 1] / katzin_2021_data[:, 1], bottom=bardata[:, 0] / katzin_2021_data[:, 0])

for bar in b1:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        0.2,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

for bar in b2:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        1.2,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

ax.set_ylabel("Relative difference (%)")
ax.set_xlabel("Files")
ax.set_title("Relative difference between current simulation and data in Katzin 2021")
ax.legend(["Heating", "Lighting"])
plt.xticks(rotation=45)  # Rotate labels for readability
plt.show()


"""Absolute difference"""
fig, ax = plt.subplots()

b1 = ax.bar(labels, bardata[:, 0] - katzin_2021_data[:, 0])
b2 = ax.bar(labels, bardata[:, 1] - katzin_2021_data[:, 1], bottom=bardata[:, 0] - katzin_2021_data[:, 0])

for bar in b1:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        40,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

for bar in b2:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        60,
        f"{height:.2f}",
        ha="center",
        va="bottom",
        fontsize=10,
        color="black",
        rotation=90,
    )

ax.set_ylabel("Absolute difference (MJ/m2)")
ax.set_xlabel("Files")
ax.set_title("Absolute difference between current simulation and data in Katzin 2021")
ax.legend(["Heating", "Lighting"])
plt.xticks(rotation=45)  # Rotate labels for readability
plt.show()
