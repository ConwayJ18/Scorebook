import sys
import csv
from tabulate import tabulate

HEADER = "Inn,Score,Out,RoB,Pit(cnt),R/O,@Bat,Batter,Pitcher,wWPA,wWE,Play Description"

# Read multiline input from user (until EOF)
print("Paste your CSV data below. Press Ctrl-D (or Ctrl-Z on Windows) when done:")
input_lines = sys.stdin.read().splitlines()

# Find the header row
try:
    header_idx = input_lines.index(HEADER)
except ValueError:
    print("Header row not found in input.")
    sys.exit(1)

# Only keep lines from header onwards
csv_lines = input_lines[header_idx:]

# Parse CSV
reader = csv.reader(csv_lines)
rows = list(reader)

# Remove columns 1-6 and 9-11 from each row (zero indexed)
filtered_rows = []
for row in rows:
    filtered = [col for i, col in enumerate(row) if i < 1 or (i > 5 and i < 8) or i > 10]
    # Remove letter from Inn column (index 0)
    if filtered and filtered[0] != 'Inn':
        filtered[0] = ''.join(filter(str.isdigit, filtered[0]))
    filtered_rows.append(filtered)

# Remove all rows where @Bat is not 'MIL'
# After filtering, @Bat is at index 1
header = filtered_rows[0]
filtered_rows = [header] + [row for row in filtered_rows[1:] if row and row[1] == 'MIL']

def generate_output(filtered_rows):
    # Find the header indexes
    header = filtered_rows[0]
    inn_idx = header.index('Inn')
    batter_idx = header.index('Batter')
    
    # Get the first 9 unique batters (excluding header)
    batters = []
    for row in filtered_rows[1:]:
        batter = row[batter_idx]
        if batter not in batters:
            batters.append(batter)
        if len(batters) == 9:
            break
    
    # Get all unique Inn values as integers
    inns = sorted(set(int(row[inn_idx]) for row in filtered_rows[1:] if row[inn_idx].isdigit()))
    if not inns:
        print("No valid Inn values found.")
        return
    max_inn = max(max(inns), 9)  # Use 9 if it's larger
    inn_columns = [str(i) for i in range(1, max_inn + 1)]

    # Build a table: rows for batters, columns for innings
    table = []
    for batter in batters:
        row = [batter]
        for inn in inn_columns:
            # Find the first row for this batter and inning
            cell = ''
            for r in filtered_rows[1:]:
                if r[batter_idx] == batter and r[inn_idx] == inn:
                    cell = 'X'  # Or any marker, or r[other_col] if needed
                    break
            row.append(cell)
        table.append(row)

    # Print the table
    headers = ['Batter'] + inn_columns
    print(tabulate(table, headers=headers, tablefmt="grid"))

# Output as table
generate_output(filtered_rows)