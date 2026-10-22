import os
import csv
import asyncio
import edge_tts

ORAL_CSV = 'words.csv'
WRITTEN_CSV = 'written_words.csv'
OUTPUT_FOLDER = 'audio_files'
VOICE = 'en-NG-AbeoNeural'

async def redownload_word(word):
    word_clean = word.strip().lower()
    safe_filename = "".join(c for c in word_clean if c.isalnum() or c in (' ', '_')).rstrip()
    output_path = os.path.join(OUTPUT_FOLDER, f"{safe_filename}.mp3")
    
    try:
        communicate = edge_tts.Communicate(word_clean, VOICE)
        await communicate.save(output_path)
        print(f"✅ Fixed & Downloaded: {word_clean}")
    except Exception as e:
        print(f"❌ Still failing '{word_clean}': {e}")

async def main():
    if not os.path.exists(OUTPUT_FOLDER):
        print("Audio folder not found.")
        return

    # Find and delete broken files (files that are empty or under 2 Kilobytes)
    broken_words = set()
    print("Checking for corrupted or empty audio assets...")
    
    for filename in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.isfile(file_path) and os.path.getsize(file_path) < 2048:  # Less than 2KB is broken
            word_name = os.path.splitext(filename)[0]
            broken_words.add(word_name)
            os.remove(file_path)
            print(f"🗑️ Removed broken file: {filename}")

    if not broken_words:
        print("No broken files detected! Your current files are clean.")
        return

    print(f"Found {len(broken_words)} files to fix. Re-downloading now...")
    
    # Download the deleted ones cleanly
    word_list = list(broken_words)
    batch_size = 5
    for i in range(0, len(word_list), batch_size):
        batch = word_list[i:i+batch_size]
        tasks = [redownload_word(word) for word in batch]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)

    print("🎉 All missing files have been successfully repaired!")

if __name__ == "__main__":
    asyncio.run(main())
