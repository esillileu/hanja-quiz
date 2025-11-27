import csv
import ast
import os
from src.models import RefHanja, RefHanjaReading

class DictionaryLoader:
    def __init__(self, session_factory):
        self.Session = session_factory

    def load_csv_data(self):
        session = self.Session()
        try:
            # Check if data already exists
            if session.query(RefHanja).count() > 0:
                print("Reference dictionary already loaded. Skipping.")
                return

            data_path = os.path.join(os.path.dirname(__file__), 'data', 'hanja.csv')
            print(f"Loading dictionary from {data_path}...")
            
            if not os.path.exists(data_path):
                print(f"Error: Data file not found at {data_path}")
                return

            with open(data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    char = row['hanja']
                    strokes = int(row['total_strokes']) if row['total_strokes'].isdigit() else 0
                    
                    hanja = RefHanja(
                        char=char,
                        radical=row['radical'],
                        strokes=strokes,
                        level=row['level']
                    )
                    session.add(hanja)
                    session.flush() # Get ID

                    try:
                        # Parse meaning: "[[['집'], ['가']]]"
                        meaning_data = ast.literal_eval(row['meaning'])
                        if isinstance(meaning_data, list):
                            for item in meaning_data:
                                if isinstance(item, list) and len(item) == 2:
                                    hun = item[0][0] if item[0] else ""
                                    eum = item[1][0] if item[1] else ""
                                    reading = RefHanjaReading(
                                        hanja_id=hanja.id,
                                        meaning=hun,
                                        sound=eum
                                    )
                                    session.add(reading)
                    except (ValueError, SyntaxError):
                        pass
                    
                    count += 1
                    if count % 1000 == 0:
                        print(f"Loaded {count} entries...")
                
                session.commit()
                print(f"Successfully loaded {count} Hanja entries into Reference Dictionary.")
        
        except Exception as e:
            session.rollback()
            print(f"Error loading dictionary: {e}")
        finally:
            session.close()
