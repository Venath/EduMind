import pandas as pd
import glob
import os
import csv

# CONFIGURATION
# Path to your raw EdNet KT1 folder
SOURCE_FOLDER = '/Users/ravinbandara/Downloads/archive/EdNet-KT1/KT1' 

# The final file where all data will be saved
OUTPUT_FILE = 'data/full_processed_data.csv'

# Ensure the output directory exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def process_full_dataset():
    # 1. Get all CSV files
    print(f"Scanning {SOURCE_FOLDER}...")
    all_files = glob.glob(os.path.join(SOURCE_FOLDER, "u*.csv"))
    
    if not all_files:
        print("No files found. Check your path.")
        return

    print(f"Found {len(all_files)} files. Starting batch processing...")

    # 2. Initialize the Output File
    headers = ['user_id', 'total_interactions', 'avg_response_time', 'consistency_score', 'last_active_timestamp']
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    # 3. Process Files One by One
    batch_data = []
    BATCH_SIZE = 1000  # Write to disk every 1000 students to save RAM

    for i, file_path in enumerate(all_files):
        try:
            # --- EXTRACT (Read raw file) ---
            df = pd.read_csv(file_path)
            
            # --- TRANSFORM (Feature Engineering) ---
            user_id = os.path.basename(file_path).replace('u', '').replace('.csv', '')
            
            # Calculate stats (Handling potential empty files/errors)
            if len(df) > 0:
                total_interactions = int(len(df))
                avg_response_time = float(df['elapsed_time'].mean())
                consistency_score = float(df['elapsed_time'].std() if not pd.isna(df['elapsed_time'].std()) else 0)
                last_active_timestamp = int(df['timestamp'].max())

                stats = [
                    user_id,
                    total_interactions,
                    avg_response_time,
                    consistency_score,
                    last_active_timestamp
                ]
                
                batch_data.append(stats)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        # --- LOAD (Write batch to disk) ---
        if len(batch_data) >= BATCH_SIZE:
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(batch_data)
            
            # Clear memory
            batch_data = []
            print(f"Saved progress: {i + 1}/{len(all_files)} students processed...")

    # Write any remaining data in the buffer
    if batch_data:
        with open(OUTPUT_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(batch_data)

    print(f"COMPLETED! All data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_full_dataset()