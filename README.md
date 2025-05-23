# Baseball Scorebook CSV Parser and Tabulator

This script processes play-by-play CSV data exported from [Baseball-Reference.com](https://www.baseball-reference.com/) and outputs a tabular summary of play descriptions for each Milwaukee Brewers batter by inning.

## Features
- Handles pinch hitters by mapping them to original batters
- Uses scorebook shorthand for play descriptions (e.g., 1B, K, GDP)
- Tracks RBIs, stolen bases, and caught stealing events
- Outputs a table with batters as rows and innings as columns
- Copies the TSV output to your clipboard (macOS and Windows)

## How to Use

1. **Get the CSV Data:**
   - Go to [Baseball Reference](https://www.baseball-reference.com/)
   - Find a Brewers game and click on "Play by Play" at the top of the page
   - Under "Share & Export", select "Get table as CSV (for Excel)"
   - Copy and paste the CSV data into a text file
   - Save the file as `input.txt` in the same directory as `Scorebook.py`

2. **Run the Script:**
   - Open a terminal in the script directory
   - Run:
     ```
     python Scorebook.py
     ```
   - The script will process `input.txt` and print a summary table
   - The TSV output will also be copied to your clipboard (on macOS and Windows) for easy copying into a spreadsheet

## Requirements
- Python 3.7+
- [tabulate](https://pypi.org/project/tabulate/) Python package

Install tabulate with:
```
pip install tabulate
```

## Notes
- The script expects the CSV header to match exactly:
  ```
  Inn,Score,Out,RoB,Pit(cnt),R/O,@Bat,Batter,Pitcher,wWPA,wWE,Play Description
  ```
- Only parses Milwaukee Brewers games
- Only Milwaukee Brewers plate appearances are included in the output.
- The script is designed for use with CSVs from Baseball-Reference.com only.

## Author
Jess Conway

## License
MIT License