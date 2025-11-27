from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.models import HanjaInfo, UsageExample

class HanjaRepository:
    def __init__(self):
        pass

    def add_hanja_info(self, session, char: str, sound: str, meaning: str = None, radical: str = None, strokes: int = None) -> HanjaInfo:
        try:
            hanja = session.query(HanjaInfo).filter_by(char=char).first()
            if hanja:
                hanja.sound = sound
                hanja.meaning = meaning
                hanja.radical = radical
                hanja.strokes = strokes
            else:
                hanja = HanjaInfo(char=char, sound=sound, meaning=meaning, radical=radical, strokes=strokes)
                session.add(hanja)
            session.flush() # Flush to assign ID if new, but don't commit yet
            return hanja
        except IntegrityError:
            session.rollback()
            existing_hanja = session.query(HanjaInfo).filter_by(char=char).first()
            return existing_hanja
        except Exception as e:
            session.rollback()
            raise e

    def get_hanja_info(self, session, char: str) -> HanjaInfo:
        return session.query(HanjaInfo).filter_by(char=char).first()

    def add_usage_example(self, session, word: str, sound: str = None) -> UsageExample:
        try:
            example = session.query(UsageExample).filter_by(word=word).first()
            if example:
                example.frequency += 1
                if sound and not example.sound:
                    example.sound = sound
            else:
                example = UsageExample(word=word, sound=sound, frequency=1)
                session.add(example)
            session.flush() # Flush to assign ID if new, but don't commit yet
            return example
        except IntegrityError:
            session.rollback()
            existing_example = session.query(UsageExample).filter_by(word=word).first()
            return existing_example
        except Exception as e:
            session.rollback()
            raise e

    def get_usage_example(self, session, word: str) -> UsageExample:
        return session.query(UsageExample).filter_by(word=word).first()

    def get_all_hanja_info(self, session):
        return session.query(HanjaInfo).all()

    def get_all_usage_examples(self, session):
        return session.query(UsageExample).all()
