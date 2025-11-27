import argparse
import hashlib
from src.models import init_db
from src.extractor import HanjaExtractor
from src.dictionary import HanjaDictionary
from src.repository import HanjaRepository
from src.reader import read_file
from src.loader import DictionaryLoader
from sqlalchemy.orm import sessionmaker

def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def main():
    # 0. Parse CLI arguments
    parser = argparse.ArgumentParser(description="Extract Hanja from text or PDF files.")
    parser.add_argument("file", nargs="?", help="Path to the input file (.txt or .pdf)")
    args = parser.parse_args()

    # 1. Initialize the database and get a Session factory
    Session_factory = init_db()
    
    # 1.1 Pre-load Reference Dictionary
    print("--- Checking Reference Dictionary ---")
    loader = DictionaryLoader(Session_factory)
    loader.load_csv_data()

    session = Session_factory() # Create a single session for this run
    
    # 2. Create instances of the components
    extractor = HanjaExtractor()
    dictionary = HanjaDictionary()
    repository = HanjaRepository()

    print("\n--- Hanja Extraction and Storage Process ---")

    try:
        # 3. Determine text source
        text_to_process = ""
        filename = "sample_text"
        if args.file:
            print(f"Reading file: {args.file}")
            try:
                text_to_process = read_file(args.file)
                filename = args.file
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        else:
            print("No file provided. Using default sample text.")
            text_to_process = "이것은 學을 배우는 학생들을 위한 교과서입니다. 人生은 배움의 연속입니다."
        
        # 3.1 Idempotency Check
        file_hash = calculate_hash(text_to_process)
        existing_doc = repository.get_document_by_hash(session, file_hash)
        
        if existing_doc:
            print(f"Skipping: Document '{filename}' (Hash: {file_hash[:8]}...) already processed.")
            return # Stop processing if duplicate

        print(f"Processing new document: '{filename}'")
        current_doc = repository.create_document(session, filename, file_hash)

        print(f"\nProcessing Text (Length: {len(text_to_process)} chars)...")
        
        # 4. Extract Hanja characters and words
        individual_hanja, hanja_words = extractor.extract(text_to_process)
        print(f"Extracted individual Hanja: {len(individual_hanja)} items")
        print(f"Extracted Hanja words: {len(hanja_words)} items")

        # 5. Look up and save individual Hanja information
        print("\n--- Processing Individual Hanja ---")
        for char in individual_hanja:
            try:
                # Pass session to lookup
                hanja_info = dictionary.lookup(session, char)
                repository.add_hanja_info(
                    session, 
                    char=hanja_info["char"],
                    sound=hanja_info["sound"],
                    meaning=hanja_info["meaning"],
                    radical=hanja_info["radical"],
                    strokes=hanja_info["strokes"],
                    readings=hanja_info.get("readings")
                )
                # Update frequency for this specific document
                repository.update_document_hanja_frequency(session, current_doc.id, char)
                print(f"Processed: {char} ({hanja_info['meaning']} {hanja_info['sound']})")
                
            except ValueError as e:
                print(f"Error processing '{char}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred for '{char}': {e}")

        # 6. Save usage examples (Hanja words)
        print("\n--- Processing Hanja Words ---")
        for word in hanja_words:
            word_sound = dictionary.get_word_sound(word)
            repository.add_usage_example(session, word=word, sound=word_sound)
            # Update frequency for this specific document
            repository.update_document_word_frequency(session, current_doc.id, word)
            print(f"Processed Word: {word} ({word_sound})")

        # 7. Verify by retrieving all saved data
        print("\n--- Stored Data Verification ---")
        all_hanja = repository.get_all_hanja_info(session) # Pass the session
        print(f"\nTotal Unique Hanja stored: {len(all_hanja)}")
        for h in all_hanja[:5]: # Show first 5
             readings_str = ", ".join([f"{r.meaning} {r.sound}" for r in h.readings])
             print(f"- {h.char} (Radical: {h.radical}, Strokes: {h.strokes}): {readings_str}")

        all_examples = repository.get_all_usage_examples(session) # Pass the session
        print(f"Total Unique Words stored: {len(all_examples)}")
        
        session.commit() # Commit all changes at the end
        print("\n--- Process Completed ---")

    except Exception as e:
        session.rollback() # Rollback on error
        print(f"\n--- An Error Occurred: {e} ---")
        import traceback
        traceback.print_exc()
    finally:
        session.close() # Always close the session


if __name__ == "__main__":
    main()