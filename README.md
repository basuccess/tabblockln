# Broadband Geopackage Project

tabblockln
A Python script to process and organize U.S. Census TIGER/Line Tabblock20 files by moving, extracting, and creating symbolic links for state-specific shapefiles.


## Project Structure

```
tabblockln
├── src
│   ├── constant.py        # Contains constants for the project
│   └── main.py            # Main entry point for the project
├── data
│   ├── USA_Census         # Directory for tabblock20 shapefiles
├── requirements.txt       # Lists project dependencies
├── setup.py               # Packaging and metadata for the project
└── README.md              # Project documentation
```

Purpose
tabblockln automates the handling of Tabblock20 .zip files from the U.S. Census Bureau:

Moves files from ~/Downloads to a structured directory under a specified base path.
Extracts .zip files into state-specific subdirectories.

Creates symbolic links (e.g., tl_48_tabblock20.shp) to the latest extracted files (e.g., tl_2024_48_tabblock20.shp).

In preparation for catfccbdc to process and merge FCC BDC broadband Provider service reports.

Prerequisites
Python 3.6+
Modules: os, re, shutil, zipfile, logging, argparse (standard library)
Write access to the target base directory
Installation
Clone or download the repository:

Copy
git clone https://github.com/basuccess/tabblockln.git
cd tabblockln

Ensure constant.py is in the same directory as main.py—it defines state lists and file patterns.

Usage
Run the script from the command line with optional arguments:

Basic Command

python src/main.py --base-dir "/path/to/base" --log-file
Processes all 59 U.S. states and territories from STATES_AND_TERRITORIES in constant.py.
With Specific States

python src/main.py --state TX --base-dir "/Volumes/T7 Shield/SharedData" --log-file
Processes only Texas (TX).

With State Range

python src/main.py --state "AL..AZ" --base-dir "/Volumes/T7 Shield/SharedData" --log-file
Processes Alabama (AL) to Arizona (AZ)—expands to AL, AK, AZ.
Options
--base-dir: Target directory (default: current working directory).
--log-file: Enable logging to tabblockln_log.log (optional; omit for no logging).
-s/--state: List of state abbreviations or ranges (e.g., TX, AL..AZ); omit for all states.
Workflow

Move: Transfers .zip files (e.g., tl_2024_48_tabblock20.zip) from ~/Downloads to {base_dir}/USA_Census/{fips}_{abbr}_{name}/.

Extract: Unzips each .zip into a folder (e.g., tl_2024_48_tabblock20/).

Symlink: Creates links in the state directory (e.g., tl_48_tabblock20.shp → tl_2024_48_tabblock20/tl_2024_48_tabblock20.shp).
Example Output
For --state TX --base-dir "/Volumes/T7 Shield/SharedData":

Directory: /Volumes/T7 Shield/SharedData/USA_Census/48_TX_Texas/

Extracted: tl_2024_48_tabblock20/ (contains tl_2024_48_tabblock20.shp, .shx, etc.)

Symlinks:
tl_48_tabblock20.shp → tl_2024_48_tabblock20/tl_2024_48_tabblock20.shp
tl_48_tabblock20.shx → tl_2024_48_tabblock20/tl_2024_48_tabblock20.shx
Troubleshooting

No Symlinks: Check tabblockln_log.log for “Matched files” or “Symlink created”—ensure .zip files match TABBLOCK20_SRC_FILE_PATTERN (e.g., tl_2024_48_tabblock20.zip).

Permission Errors: Verify write access to {base_dir}/USA_Census/ (chmod -R u+w /Volumes/T7\ Shield/SharedData).
File Not Found: Place Tabblock20 .zip files in ~/Downloads—e.g., download from Census TIGER/Line.

Notes
Uses constant.py for state codes and file patterns—edit for custom states or formats.
Tested with 2024 TIGER/Line files—adjust patterns if file naming changes.