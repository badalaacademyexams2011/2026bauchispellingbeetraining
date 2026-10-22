import csv
import os
import asyncio
import edge_tts

# Configuration settings
ORAL_CSV = 'words.csv'
WRITTEN_CSV = 'written_words.csv'
OUTPUT_FOLDER = 'audio_files'
VOICE = 'en-NG-AbeoNeural'  # Clear Nigerian English Voice

async def download_word_audio(word):
    if not word:
        return
        
    # Clean the word format to make a safe filename
    word_clean = word.strip().lower()
    safe_filename = "".join(c for c in word_clean if c.isalnum() or c in (' ', '_')).rstrip()
    output_path = os.path.join(OUTPUT_FOLDER, f"{safe_filename}.mp3")
    
    # Avoid duplicate downloads
    if os.path.exists(output_path):
        return

    try:
        communicate = edge_tts.Communicate(word_clean, VOICE)
        await communicate.save(output_path)
        print(f"✅ Downloaded: {word_clean}")
    except Exception as e:
        print(f"❌ Error downloading '{word_clean}': {e}")

async def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    unique_words = set()

    # 1. Parse the Oral Word Bank (Single column under 'Word')
    if os.path.exists(ORAL_CSV):
        print(f"Reading {ORAL_CSV}...")
        with open(ORAL_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Word'):
                    unique_words.add(row['Word'].strip())

    # 2. Parse the Written Word Bank (Three columns under 'Word,Meaning,Example_Sentence')
    if os.path.exists(WRITTEN_CSV):
        print(f"Reading {WRITTEN_CSV}...")
        with open(WRITTEN_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Word'):
                    unique_words.add(row['Word'].strip())

    word_list = list(unique_words)
    print(f"Found {len(word_list)} total unique words across both files. Starting downloads...")
    
    # Download in managed concurrency batches to avoid network drops
    batch_size = 15
    for i in range(0, len(word_list), batch_size):
        batch = word_list[i:i+batch_size]
        tasks = [download_word_audio(word) for word in batch]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.3)

    print("🎉 All audio downloads completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
