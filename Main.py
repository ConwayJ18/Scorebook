# Main.py - Baseball Scorebook CSV Parser and Tabulator
#
# This script reads play-by-play CSV data (NOTE: Must be from Baseball-Reference.com), processes it to extract and summarize play descriptions for each batter and inning, and outputs a tabular summary.
# - To create a CSV file:
#   - Go to Baseball Reference
#   - Find a Milwaukee Brewers game (script only parses Brewers games)
#   - Click on "Play by Play" at the top of the page.
#   - Under "Share & Export", select "Get table as CSV (for Excel)
#   - Copy & paste into a text file
#   - Save it as "input.txt" in the same directory as this script.
#
# Features:
# - Handles pinch hitters by mapping them to original batters.
# - Uses scorebook shorthand for play descriptions (e.g., 1B, K, GDP).
# - Tracks RBIs, stolen bases, and caught stealing events.
# - Outputs a table with batters as rows and innings as columns.
#
# Usage:
#   Run the script and paste the CSV data from Baseball Reference when prompted. End input with Ctrl-D (or Ctrl-Z on Windows).
#
# Author: Jess Conway
# Date: 22 May 2025

import sys
import csv
import platform
import subprocess
from tabulate import tabulate

# --- Scorebook Conversion Functions ---
def score_unassisted(desc):
    """Map position abbreviations to scorebook numbers."""
    pos_map = {"1B": "3", "2B": "4", "3B": "5", "SS": "6", "LF": "7", "CF": "8", "RF": "9", "P": "1", "C": "2"}
    for key, val in pos_map.items():
        if key in desc:
            return val
    return ""

def score_groundout(desc):
    """Convert groundout play descriptions to scorebook format."""
    if not desc:
        return ""
    result = []
    for word in desc.split():
        if "-" in word:
            result.extend(score_unassisted(pos) for pos in word.split("-") if score_unassisted(pos))
    return "-".join(result)

def to_scorebook(desc):
    """Convert full play descriptions to scorebook shorthand."""
    if not desc:
        return ""
    foul = "FOUL" in desc
    if "WALK" in desc:
        return "BB"
    if "HIT BY PITCH" in desc:
        return "HBP"
    if "SACRIFICE" in desc:
        return "SAC"
    if "SINGLE" in desc:
        return "1B"
    if "DOUBLE" in desc:
        return "GDP " + score_groundout(desc) if "DOUBLE PLAY" in desc else "2B"
    if "TRIPLE" in desc:
        return "GTP " + score_groundout(desc) if "TRIPLE PLAY" in desc else "3B"
    if "HOMERS" in desc or "HOME RUN" in desc:
        return "HR"
    if "STRIKEOUT" in desc:
        return "K*" if "LOOKING" in desc else "K"
    if "GROUNDOUT" in desc:
        return score_unassisted(desc) if "UNASSISTED" in desc else score_groundout(desc)
    if "LINEOUT" in desc:
        val = "L" + score_unassisted(desc)
        return val + "f" if foul else val
    if "POPFLY" in desc:
        val = "P" + score_unassisted(desc)
        return val + "f" if foul else val
    if "FLYBALL" in desc:
        val = "F" + score_unassisted(desc)
        return val + "f" if foul else val
    return ""

HEADER = "Inn,Score,Out,RoB,Pit(cnt),R/O,@Bat,Batter,Pitcher,wWPA,wWE,Play Description"

# --- Input and Pinch Hitter Mapping ---
def get_input_lines():
    with open('input.txt', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

input_lines = get_input_lines()

# Map pinch hitters to original batters
pinch_map = {}
for line in input_lines:
    line = line.upper()
    if "PINCH HITS FOR" in line:
        words = line.split("PINCH HITS FOR")
        try:
            name1 = words[0].split()[-1]
            if len(words[1].split()) > 2:
                name2 = words[1].split()[1]
                pinch_map[name1] = name2
        except ValueError:
            continue

# --- CSV Parsing and Filtering ---
try:
    header_idx = input_lines.index(HEADER)
except ValueError:
    print("Header row not found in input.")
    sys.exit(1)

csv_lines = input_lines[header_idx:]
reader = csv.reader(csv_lines)
rows = list(reader)

# Keep only columns: Inn, @Bat, Batter, Play Description
filtered_rows = []
for row in rows:
    filtered = []
    for idx in [0, 6, 7, 11]:
        if idx < len(row):
            val = row[idx]
            if idx == 7:
                words = val.split()
                if len(words) > 1:
                    filtered_words = [w for i, w in enumerate(words) if i != 0 or not w[0].isupper()]
                    val = ' '.join(filtered_words)
            filtered.append(val)
    filtered_rows.append(filtered)

# Only keep rows where @Bat is 'MIL'
header = filtered_rows[0]
filtered_rows = [header] + [row for row in filtered_rows[1:] if len(row) > 1 and row[1] == 'MIL']

# --- Build Play Description Dictionary ---
arr = {}
inn_idx = header.index('Inn')
batter_idx = header.index('Batter')
desc_idx = header.index('Play Description')
for row in filtered_rows[1:]:
    if len(row) <= max(inn_idx, batter_idx, desc_idx):
        continue
    inn = ''.join(filter(str.isdigit, row[inn_idx]))
    batter = row[batter_idx].upper()
    desc = row[desc_idx].upper()
    play = desc.split("(")[0]
    rbi = desc.count("SCORES")
    sb = desc.count("STEALS")
    cs = desc.count("CAUGHT STEALING")
    desc = "FC" if batter + " TO " in desc else to_scorebook(play)
    if inn not in arr:
        arr[inn] = {}
    if batter in pinch_map:
        batter = pinch_map[batter]
    if batter in arr[inn] and arr[inn][batter]:
        arr[inn][batter] += "; " + desc
    else:
        arr[inn][batter] = desc
    if arr[inn][batter] != "": arr[inn][batter] += ", RBI" * rbi
    for i in range(sb):
        sb_player = row[desc_idx].upper().split("STEALS")[i].split()[-1]
        if sb_player in pinch_map:
            sb_player = pinch_map[sb_player]
        arr[inn][sb_player] = arr[inn].get(sb_player, "") + ", SB"
    for j in range(cs):
        cs_player = row[desc_idx].upper().split("CAUGHT STEALING")[0].split()[-1]
        if cs_player in pinch_map:
            cs_player = pinch_map[sb_player]
        arr[inn][cs_player] = arr[inn].get(cs_player, "") + ", CS"

# --- Output Table ---
batters_order = []
for inn in sorted(arr.keys(), key=lambda x: int(x)):
    for batter in arr[inn]:
        if batter not in batters_order:
            batters_order.append(batter)
max_inn = max(max([int(i) for i in arr.keys()]), 9) if arr else 9
inn_columns = [str(i) for i in range(1, max_inn + 1)]
output_rows = []
for batter in batters_order:
    row = [batter]
    for inn in inn_columns:
        row.append(arr.get(inn, {}).get(batter, ""))
    output_rows.append(row)
headers = ["Batter"] + inn_columns
output = tabulate(output_rows, headers=headers, tablefmt="tsv")
print(tabulate(output_rows, headers=headers, tablefmt="simple"))

if platform.system() == "Darwin":  # macOS
    subprocess.run("pbcopy", text=True, input=output)
    print("Output copied to clipboard (macOS).")
elif platform.system() == "Windows":
    subprocess.run("clip", text=True, input=output)
    print("Output copied to clipboard (Windows).")
else:
    print("Could not copy to clipboard. Please copy manually.")