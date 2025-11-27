import argparse
from src.models import init_db
from src.extractor import HanjaExtractor
from src.dictionary import HanjaDictionary
from src.repository import HanjaRepository
from src.reader import read_file
from sqlalchemy.orm import sessionmaker

def main():
    # 0. Parse CLI arguments
    parser = argparse.ArgumentParser(description="Extract Hanja from text or PDF files.")
    parser.add_argument("file", nargs="?", help="Path to the input file (.txt or .pdf)")
    args = parser.parse_args()

    # 1. Initialize the database and get a Session factory
    Session_factory = init_db()
    session = Session_factory() # Create a single session for this run
    
    # 2. Create instances of the components
    extractor = HanjaExtractor()
    dictionary = HanjaDictionary()
    repository = HanjaRepository() # No longer pass Session_factory to repo

    print("--- Hanja Extraction and Storage Process ---")

    try:
        # 3. Determine text source
        text_to_process = ""
        if args.file:
            print(f"Reading file: {args.file}")
            try:
                text_to_process = read_file(args.file)
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        else:
            print("No file provided. Using default sample text.")
            text_to_process = "이것은 學을 배우는 학생들을 위한 교과서입니다. 人生은 배움의 연속입니다."
        
        print(f"\nProcessing Text (Length: {len(text_to_process)} chars)...")
        if len(text_to_process) < 200:
             print(f"Preview: '{text_to_process}'")

        # 4. Extract Hanja characters and words
        individual_hanja, hanja_words = extractor.extract(text_to_process)
        print(f"Extracted individual Hanja: {individual_hanja}")
        print(f"Extracted Hanja words: {hanja_words}")

        # 5. Look up and save individual Hanja information
        print("\n--- Processing Individual Hanja ---")
        for char in individual_hanja:
            try:
                hanja_info = dictionary.lookup(char)
                saved_hanja = repository.add_hanja_info(
                    session, # Pass the session
                    char=hanja_info["char"],
                    sound=hanja_info["sound"],
                    meaning=hanja_info["meaning"],
                    radical=hanja_info["radical"],
                    strokes=hanja_info["strokes"]
                )
                print(f"Saved/Updated Hanja Info: {saved_hanja}")
            except ValueError as e:
                print(f"Error processing '{char}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred for '{char}': {e}")

        # 6. Save usage examples (Hanja words)
        print("\n--- Processing Hanja Words ---")
        for word in hanja_words:
            word_sound = dictionary.get_word_sound(word)
            saved_example = repository.add_usage_example(session, word=word, sound=word_sound) # Pass the session and sound
            print(f"Saved/Updated Usage Example: {saved_example}")

        # 7. Verify by retrieving all saved data
        print("\n--- Stored Data Verification ---")
        all_hanja = repository.get_all_hanja_info(session) # Pass the session
        print("\nAll Stored Hanja Info:")
        for hanja in all_hanja:
            print(f"- {hanja.char} ({hanja.sound}, {hanja.meaning}, {hanja.radical}, {hanja.strokes} strokes)")

        all_examples = repository.get_all_usage_examples(session) # Pass the session
        print("\nAll Stored Usage Examples:")
        for example in all_examples:
            print(f"- {example.word} (Sound: {example.sound if example.sound else 'N/A'}, Frequency: {example.frequency})")
        
        session.commit() # Commit all changes at the end
        print("\n--- Process Completed ---")

    except Exception as e:
        session.rollback() # Rollback on error
        print(f"\n--- An Error Occurred: {e} ---")
    finally:
        session.close() # Always close the session


if __name__ == "__main__":
    main()