from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from src.models import HanjaInfo, UsageExample, Document, DocumentHanja, DocumentWord, HanjaReading, RefHanja, RefHanjaReading, UserProgress

class HanjaRepository:
    def __init__(self):
        pass

    def get_document_by_hash(self, session, file_hash: str) -> Document:
        return session.query(Document).filter_by(file_hash=file_hash).first()

    def create_document(self, session, filename: str, file_hash: str) -> Document:
        doc = Document(filename=filename, file_hash=file_hash)
        session.add(doc)
        session.flush()
        return doc

    def add_hanja_info(self, session, char: str, sound: str, meaning: str = None, radical: str = None, strokes: int = None, readings: list = None) -> HanjaInfo:
        hanja = session.query(HanjaInfo).filter_by(char=char).first()
        if not hanja:
            hanja = HanjaInfo(char=char, radical=radical, strokes=strokes)
            session.add(hanja)
            session.flush()
        else:
            # Update info if missing
            if radical and not hanja.radical: hanja.radical = radical
            if strokes and not hanja.strokes: hanja.strokes = strokes
        
        # Process readings list
        if readings:
            for reading_data in readings:
                r_sound = reading_data.get('sound')
                r_meaning = reading_data.get('meaning')
                if r_sound:
                    reading = session.query(HanjaReading).filter_by(hanja_id=hanja.id, sound=r_sound, meaning=r_meaning).first()
                    if not reading:
                        reading = HanjaReading(hanja_id=hanja.id, sound=r_sound, meaning=r_meaning)
                        session.add(reading)
        else:
            # Fallback for single sound/meaning provided as args (legacy support)
            reading = session.query(HanjaReading).filter_by(hanja_id=hanja.id, sound=sound).first()
            if not reading:
                reading = HanjaReading(hanja_id=hanja.id, sound=sound, meaning=meaning)
                session.add(reading)
        
        return hanja

    def update_document_hanja_frequency(self, session, document_id: int, hanja_char: str) -> DocumentHanja:
        hanja = session.query(HanjaInfo).filter_by(char=hanja_char).first()
        if not hanja:
            return None # Should act after add_hanja_info
            
        doc_hanja = session.query(DocumentHanja).filter_by(document_id=document_id, hanja_id=hanja.id).first()
        if doc_hanja:
            doc_hanja.frequency += 1
        else:
            doc_hanja = DocumentHanja(document_id=document_id, hanja_id=hanja.id, frequency=1)
            session.add(doc_hanja)
        return doc_hanja

    def add_usage_example(self, session, word: str, sound: str = None) -> UsageExample:
        example = session.query(UsageExample).filter_by(word=word).first()
        if not example:
            example = UsageExample(word=word, sound=sound)
            session.add(example)
            session.flush()
        elif sound and not example.sound:
            example.sound = sound
        return example

    def update_document_word_frequency(self, session, document_id: int, word_str: str) -> DocumentWord:
        word = session.query(UsageExample).filter_by(word=word_str).first()
        if not word:
            return None
            
        doc_word = session.query(DocumentWord).filter_by(document_id=document_id, word_id=word.id).first()
        if doc_word:
            doc_word.frequency += 1
        else:
            doc_word = DocumentWord(document_id=document_id, word_id=word.id, frequency=1)
            session.add(doc_word)
        return doc_word

    def get_user_progress(self, session, hanja_id: int = None, word_id: int = None) -> UserProgress:
        if hanja_id:
            return session.query(UserProgress).filter_by(hanja_id=hanja_id).first()
        elif word_id:
            return session.query(UserProgress).filter_by(word_id=word_id).first()
        return None

    def update_importance_level(self, session, hanja_id: int = None, word_id: int = None, change: int = 0) -> UserProgress:
        if not (hanja_id or word_id):
            raise ValueError("Either hanja_id or word_id must be provided.")

        progress = None
        if hanja_id:
            progress = session.query(UserProgress).filter_by(hanja_id=hanja_id).first()
            if not progress:
                # Default start level is 5. If correct (-1) -> 4, if wrong (+1) -> 6
                initial_level = 5
                progress = UserProgress(hanja_id=hanja_id, importance_level=max(0, initial_level + change))
                session.add(progress)
            else:
                progress.importance_level = max(0, progress.importance_level + change)
        elif word_id:
            progress = session.query(UserProgress).filter_by(word_id=word_id).first()
            if not progress:
                initial_level = 5
                progress = UserProgress(word_id=word_id, importance_level=max(0, initial_level + change))
                session.add(progress)
            else:
                progress.importance_level = max(0, progress.importance_level + change)
        
        session.flush()
        return progress

    def get_all_user_progress(self, session, min_importance: int = 0):
        query = session.query(UserProgress).filter(UserProgress.importance_level >= min_importance)
        return query.order_by(UserProgress.importance_level.desc(), UserProgress.last_tested_at.asc()).all()
    
    def get_user_progress_hanja(self, session, hanja_id: int) -> UserProgress:
        return session.query(UserProgress).filter_by(hanja_id=hanja_id).first()

    def get_user_progress_word(self, session, word_id: int) -> UserProgress:
        return session.query(UserProgress).filter_by(word_id=word_id).first()

    def get_all_hanja_info(self, session):
        return session.query(HanjaInfo).all()

    def get_all_usage_examples(self, session):
        return session.query(UsageExample).all()
