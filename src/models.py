from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

class HanjaInfo(Base):
    __tablename__ = "hanja_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    char = Column(String(1), unique=True, nullable=False)
    sound = Column(String, nullable=False)
    meaning = Column(String, nullable=True)
    radical = Column(String, nullable=True)
    strokes = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<HanjaInfo(char='{self.char}', sound='{self.sound}')>"

class UsageExample(Base):
    __tablename__ = "usage_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True, nullable=False)
    sound = Column(String, nullable=True)
    frequency = Column(Integer, default=1)

    def __repr__(self):
        return f"<UsageExample(word='{self.word}', frequency={self.frequency})>"

def init_db(db_url="sqlite:///hanja.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
