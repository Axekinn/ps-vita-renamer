#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def setup_logging() -> logging.Logger:
    """Configure the logging system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('psvita_renamer.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_csv_data(csv_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load data from CSV file and return it as a dictionary.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Dictionary with filename as key and game data
    """
    games_data = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Use filename as key to avoid conflicts
                filename = row.get('Update_Filename', '').strip()
                media_id = row.get('Media_ID', '').strip()
                if filename and media_id:
                    games_data[filename] = {
                        'title_name': row.get('Title', '').strip(),
                        'version': row.get('Update_Version', '').strip(),
                        'media_id': media_id
                    }
        
        logging.info(f"Loaded {len(games_data)} games from CSV")
        return games_data
        
    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")
        return {}
    except Exception as e:
        logging.error(f"Error loading CSV: {e}")
        return {}

def clean_title_name(title: str) -> str:
    """
    Clean title name to make it valid as a filename.
    
    Args:
        title: Title name to clean
        
    Returns:
        Cleaned title name
    """
    # Replace invalid characters for filenames
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '', title)
    
    # Replace special characters with spaces
    cleaned = re.sub(r'[^\w\s\-\.\(\)\[\]]', ' ', cleaned)
    
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def extract_title_id_from_filename(filename: str) -> Optional[str]:
    """
    Extract Title_ID from PKG filename.
    
    Args:
        filename: PKG filename
        
    Returns:
        Extracted Title_ID or None if not found
    """
    # Pattern to extract Title_ID (format PCxx00000)
    pattern = r'-(PC[SABE]\w{5})[_-]'
    match = re.search(pattern, filename)
    
    if match:
        return match.group(1)
    
    # Alternative pattern if the first one doesn't work
    pattern2 = r'UP\d+-([A-Z]{4}\d{5})_'
    match2 = re.search(pattern2, filename)
    
    if match2:
        return match2.group(1)
    
    # Pattern for HP files (Asian region)
    pattern3 = r'HP\d+-([A-Z]{4}\d{5})_'
    match3 = re.search(pattern3, filename)
    
    if match3:
        return match3.group(1)
    
    # Pattern for EP files (European region)
    pattern4 = r'EP\d+-([A-Z]{4}\d{5})_'
    match4 = re.search(pattern4, filename)
    
    if match4:
        return match4.group(1)
    
    # Pattern for JP files (Japanese region)
    pattern5 = r'JP\d+-([A-Z]{4}\d{5})_'
    match5 = re.search(pattern5, filename)
    
    if match5:
        return match5.group(1)
    
    return None

def is_correctly_formatted(filename: str) -> bool:
    """
    Check if the file is already correctly formatted.
    
    Args:
        filename: Filename to check
        
    Returns:
        True if the file is already correctly formatted
    """
    pattern = r'.+\s\[UPDATE\s[\d\.]+\]\[[A-Z]{4}\d{5}\]\(axekin\.com\)\.pkg$'
    return bool(re.match(pattern, filename))

def generate_new_filename(title_name: str, version: str, title_id: str) -> str:
    """
    Generate new filename according to specified format.
    
    Args:
        title_name: Game name
        version: Update version
        title_id: Title ID
        
    Returns:
        New formatted filename
    """
    clean_title = clean_title_name(title_name)
    return f"{clean_title} [UPDATE {version}][{title_id}](axekin.com).pkg"

def rename_files(directory_path: str, csv_path: str, dry_run: bool = True) -> Tuple[List[str], List[str]]:
    """
    Rename files in directory according to CSV data.
    
    Args:
        directory_path: Path to directory containing files
        csv_path: Path to CSV file
        dry_run: If True, simulate renaming without doing it
        
    Returns:
        Tuple containing lists of successfully renamed files and errors
    """
    logger = logging.getLogger(__name__)
    
    # Load CSV data
    games_data = load_csv_data(csv_path)
    if not games_data:
        logger.error("No data loaded from CSV")
        return [], ["No data loaded from CSV"]
    
    # Check if directory exists
    if not os.path.isdir(directory_path):
        error_msg = f"Directory not found: {directory_path}"
        logger.error(error_msg)
        return [], [error_msg]
    
    renamed_files = []
    errors = []
    
    # Browse all .pkg files in directory
    for filename in os.listdir(directory_path):
        if not filename.lower().endswith('.pkg'):
            continue
        
        # Check if file is already correctly formatted
        if is_correctly_formatted(filename):
            logger.info(f"File already correctly formatted: {filename}")
            continue
        
        # Search for corresponding data in CSV using filename
        game_data = None
        title_id = None
        
        # Search for exact match with filename
        if filename in games_data:
            game_data = games_data[filename]
            title_id = game_data['media_id']
        else:
            # If no exact match, extract Title_ID and search by pattern
            title_id = extract_title_id_from_filename(filename)
            if not title_id:
                error_msg = f"Cannot extract Title_ID from: {filename}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
            
            # Search for corresponding file in CSV
            for csv_filename, data in games_data.items():
                if data['media_id'] == title_id and csv_filename in filename:
                    game_data = data
                    break
        
        if not game_data:
            error_msg = f"No data found for file: {filename}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Get game data
        title_name = game_data['title_name']
        version = game_data['version']
        
        if not title_name or not version:
            error_msg = f"Missing data for {filename}: title='{title_name}', version='{version}'"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        # Generate new filename
        new_filename = generate_new_filename(title_name, version, title_id)
        
        # Full paths
        old_path = os.path.join(directory_path, filename)
        new_path = os.path.join(directory_path, new_filename)
        
        # Check if destination file already exists
        if os.path.exists(new_path):
            error_msg = f"Destination file already exists: {new_filename}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue
        
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would rename: {filename} -> {new_filename}")
                renamed_files.append(f"{filename} -> {new_filename}")
            else:
                os.rename(old_path, new_path)
                logger.info(f"Renamed: {filename} -> {new_filename}")
                renamed_files.append(f"{filename} -> {new_filename}")
                
        except OSError as e:
            error_msg = f"Error renaming {filename}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    return renamed_files, errors

def main():
    """Main function of the script."""
    logger = setup_logging()
    
    print("=== PS Vita File Renamer ===")
    print()
    
    # Ask user for paths
    directory_path = input("Enter the path to directory containing .pkg files: ").strip()
    csv_path = input("Enter the path to CSV file: ").strip()
    
    # Simulation option
    dry_run_choice = input("Do you want to run a simulation (y/n)? [y]: ").strip().lower()
    dry_run = dry_run_choice != 'n'
    
    if dry_run:
        print("\n=== SIMULATION MODE - No files will be renamed ===")
    else:
        print("\n=== REAL MODE - Files will be renamed ===")
    
    print()
    
    # Perform renaming
    renamed_files, errors = rename_files(directory_path, csv_path, dry_run)
    
    # Display results
    print(f"\n=== RESULTS ===")
    print(f"Files processed successfully: {len(renamed_files)}")
    print(f"Errors encountered: {len(errors)}")
    
    if renamed_files:
        print(f"\nFiles {'that would be ' if dry_run else ''}renamed:")
        for rename_info in renamed_files:
            print(f"  - {rename_info}")
    
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\nDetailed logs are available in: psvita_renamer.log")

if __name__ == "__main__":
    main()
