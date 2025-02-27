# main.py

import os
import re
import shutil
import zipfile
import logging
import argparse
from datetime import datetime
from constant import STATES_AND_TERRITORIES, TABBLOCK20_FILE_PATTERN, TABBLOCK20_SRC_FILE_PATTERN

# Configure argument parser
parser = argparse.ArgumentParser(description='Process tabblock20 files.')
parser.add_argument('--base-dir', type=str, default=os.getcwd(), help='Base directory for processing')
parser.add_argument('--log-file', type=str, nargs='?', const='tabblockln_log.log', help='Log file path')
parser.add_argument('-s', '--state', type=str, nargs='*', help='State abbreviation(s) to process, supports ranges like AL..AZ; omit for all states')
args = parser.parse_args()

# Configure logging
if args.log_file is not None:
    log_file_path = os.path.join(args.base_dir, args.log_file)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w')
else:
    logging.basicConfig(level=logging.CRITICAL)

base_dir = args.base_dir
census_dir = os.path.join(base_dir, "USA_Census")
downloads_dir = os.path.expanduser("~/Downloads")

logging.info(f"Base directory: {base_dir}")
logging.info(f"US Census tiger files directory: {census_dir}")
logging.info(f"Downloads directory: {downloads_dir}")

def expand_state_ranges(state_inputs):
    """Expand state ranges (e.g., 'AL..AZ') into a list of state abbreviations."""
    state_abbrs = [state[1] for state in STATES_AND_TERRITORIES]
    expanded_states = []
    
    for state_input in state_inputs:
        if '..' in state_input:
            start, end = state_input.split('..')
            if start in state_abbrs and end in state_abbrs:
                start_idx = state_abbrs.index(start)
                end_idx = state_abbrs.index(end) + 1
                expanded_states.extend(state_abbrs[start_idx:end_idx])
            else:
                logging.warning(f"Invalid state range: {state_input}. Skipping.")
                print(f"Invalid state range: {state_input}. Skipping.")
        else:
            if state_input in state_abbrs:
                expanded_states.append(state_input)
            else:
                logging.warning(f"Invalid state: {state_input}. Skipping.")
                print(f"Invalid state: {state_input}. Skipping.")
    
    return expanded_states

def remove_existing_symlinks(state_dir):
    for item in os.listdir(state_dir):
        item_path = os.path.join(state_dir, item)
        if os.path.islink(item_path):
            logging.debug(f"Removing existing symlink: {item_path}")
            os.remove(item_path)

def move_and_extract_files_from_downloads(state_dir, fips_code):
    if not os.path.exists(state_dir):
        logging.debug(f"Creating directory: {state_dir}")
        os.makedirs(state_dir)

    files_moved = False
    pattern = TABBLOCK20_SRC_FILE_PATTERN.replace(r'\d{2}', fips_code, 1)
    logging.debug(f"Using pattern: {pattern}")
    for file_name in os.listdir(downloads_dir):
        logging.debug(f"Checking file: {file_name}")
        if re.match(pattern, file_name) and not file_name.startswith('._'):
            logging.debug(f"Matched file in Downloads: {file_name}")
            file_path = os.path.join(downloads_dir, file_name)
            target_path = os.path.join(state_dir, file_name)
            if os.path.exists(target_path):
                if os.path.getsize(file_path) == os.path.getsize(target_path):
                    logging.debug(f"File already exists with same name and size: {file_name}")
                    os.remove(file_path)
                    continue
                else:
                    logging.debug(f"Removing older file: {target_path}")
                    os.remove(target_path)
            logging.debug(f"Moving file: {file_path} to {target_path}")
            shutil.move(file_path, target_path)
            files_moved = True
            
            # Extract the zip file
            extract_dir = os.path.join(state_dir, os.path.splitext(file_name)[0])
            if not os.path.exists(extract_dir):
                logging.debug(f"Extracting {target_path} to {extract_dir}")
                with zipfile.ZipFile(target_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            else:
                logging.debug(f"Extraction directory already exists: {extract_dir}")

    if not files_moved:
        logging.debug(f"No tabblock files found for state {fips_code} in Downloads directory.")
        print(f"No tabblock files found for state {fips_code} in Downloads directory.")

def get_latest_tabblock_dir(state_dir, fips_code):
    pattern = re.compile(rf"tl_(\d{{4}})_{fips_code}_tabblock20$")
    latest_year = 0
    latest_dir = None
    
    for dirname in os.listdir(state_dir):
        full_path = os.path.join(state_dir, dirname)
        if os.path.isdir(full_path):
            match = pattern.match(dirname)
            if match:
                year = int(match.group(1))
                if year > latest_year:
                    latest_year = year
                    latest_dir = dirname
                
    return latest_dir

def create_symbolic_links(state_dir, tabblock_dir, fips_code):
    if not os.path.exists(tabblock_dir):
        logging.debug(f"Tabblock directory does not exist: {tabblock_dir}")
        return

    # Debug: List all files in tabblock_dir
    all_files = os.listdir(tabblock_dir)
    logging.debug(f"All files in {tabblock_dir}: {all_files}")

    # Match files with full year pattern (e.g., tl_2024_48_tabblock20.*)
    pattern = rf"tl_\d{{4}}_{fips_code}_tabblock20\..*"
    files = [f for f in all_files if re.match(pattern, f)]
    logging.debug(f"Matched files for symbolic links with pattern {pattern}: {files}")

    if not files:
        logging.warning(f"No files matched in {tabblock_dir} for pattern {pattern}")
        return

    for file_name in files:
        # Create alias by stripping the year (e.g., tl_2024_48_tabblock20.shp -> tl_48_tabblock20.shp)
        alias_name = re.sub(r'tl_\d{4}_', 'tl_', file_name)
        symlink_path = os.path.join(state_dir, alias_name)
        target_path = os.path.join(tabblock_dir, file_name)
        if os.path.exists(symlink_path):
            logging.debug(f"Removing existing symlink: {symlink_path}")
            os.remove(symlink_path)
        logging.debug(f"Creating symlink: {symlink_path} -> {target_path}")
        try:
            os.symlink(target_path, symlink_path)
            logging.debug(f"Symlink created: {symlink_path}")
        except OSError as e:
            logging.error(f"Failed to create symlink {symlink_path}: {e}")

def create_state_directory_and_move_files():
    states_to_process = STATES_AND_TERRITORIES
    if args.state is not None:
        if args.state:
            expanded_states = expand_state_ranges(args.state)
            states_to_process = [state for state in STATES_AND_TERRITORIES if state[1] in expanded_states]
        else:
            states_to_process = STATES_AND_TERRITORIES

    for fips_code, abbr, name in states_to_process:
        print(f"Processing state: {abbr} ({name})")
        state_dir = os.path.join(census_dir, f"{fips_code}_{abbr}_{name.replace(' ', '_')}")
        
        if not os.path.exists(state_dir):
            logging.debug(f"Creating directory: {state_dir}")
            os.makedirs(state_dir)
        
        remove_existing_symlinks(state_dir)
        move_and_extract_files_from_downloads(state_dir, fips_code)
        
        latest_tabblock_dir = get_latest_tabblock_dir(state_dir, fips_code)
        if latest_tabblock_dir:
            tabblock_dir = os.path.join(state_dir, latest_tabblock_dir)
            create_symbolic_links(state_dir, tabblock_dir, fips_code)
        else:
            logging.debug(f"No tabblock directory found for state {abbr} ({name})")

if __name__ == "__main__":
    create_state_directory_and_move_files()