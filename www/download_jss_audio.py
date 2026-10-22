import os
import glob
import pandas as pd
from gtts import gTTS

script_dir = os.path.dirname(os.path.abspath(__file__))
audio_dir = os.path.join(script_dir, "audio_files")
os.makedirs(audio_dir, exist_ok=True)

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(script_dir, "*.csv"))

if not csv_files:
    print("❌ No CSV files found in this directory!")
    exit(1)

total_downloaded = 0

for csv_path in csv_files:
    filename = os.path.basename(csv_path)
    print(f"\n📂 Processing file: {filename}")
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"⚠️ Could not read {filename}: {e}")
        continue

    # Find the column containing words
    word_col = None
    for col in df.columns:
        if "word" in col.lower():
            word_col = col
            break
            
    if not word_col:
        word_col = df.columns[0] # Fallback to first column

    print(f"   Using column: '{word_col}'")
    words = df[word_col].dropna().unique()

    for word in words:
        clean_word = str(word).strip().lower()
        # Skip empty strings or non-alphabet headers
        if not clean_word or clean_word == "word":
            continue

        file_path = os.path.join(audio_dir, f"{clean_word}.mp3")

        # Only download if the file doesn't already exist
        if not os.path.exists(file_path):
            print(f"   Downloading: {clean_word}")
            try:
                tts = gTTS(text=clean_word, lang='en', tld='com.ng')
                tts.save(file_path)
                total_downloaded += 1
            except Exception as e:
                print(f"   ❌ Failed to download {clean_word}: {e}")

print(f"\n✅ Batch complete! Downloaded {total_downloaded} new audio file(s).")