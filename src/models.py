from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class RefHanja(Base):
    """
    Reference Dictionary Table.
    Pre-loaded from hanja.csv.
    """
    __tablename__ = "ref_hanja"

    id = Column(Integer, primary_key=True, autoincrement=True)
    char = Column(String(1), unique=True, nullable=False, index=True)
    radical = Column(String, nullable=True)
    strokes = Column(Integer, nullable=True)
    level = Column(String, nullable=True) # Grade level
    
    readings = relationship("RefHanjaReading", back_populates="hanja", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RefHanja(char='{self.char}')>"

class RefHanjaReading(Base):
    """Readings for Reference Dictionary"""
    __tablename__ = "ref_hanja_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hanja_id = Column(Integer, ForeignKey("ref_hanja.id"), nullable=False)
    sound = Column(String, nullable=False)
    meaning = Column(String, nullable=True)
    
    hanja = relationship("RefHanja", back_populates="readings")

# --- User Data Tables (Target Data) ---

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    hanja_occurrences = relationship("DocumentHanja", back_populates="document")
    word_occurrences = relationship("DocumentWord", back_populates="document")

    def __repr__(self):
        return f"<Document(filename='{self.filename}')>"

class HanjaInfo(Base):
    """Collected Hanja from documents"""
    __tablename__ = "hanja_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    char = Column(String(1), unique=True, nullable=False)
    # We can copy data from RefHanja for faster access or join. 
    # Copying is often better for independent adjustment.
    radical = Column(String, nullable=True)
    strokes = Column(Integer, nullable=True)
    
    readings = relationship("HanjaReading", back_populates="hanja", cascade="all, delete-orphan")
    occurrences = relationship("DocumentHanja", back_populates="hanja")

    def __repr__(self):
        return f"<HanjaInfo(char='{self.char}')>"

class HanjaReading(Base):
    """Readings for Collected Hanja"""
    __tablename__ = "hanja_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hanja_id = Column(Integer, ForeignKey("hanja_info.id"), nullable=False)
    sound = Column(String, nullable=False)
    meaning = Column(String, nullable=True)
    
    hanja = relationship("HanjaInfo", back_populates="readings")

class UsageExample(Base):
    __tablename__ = "usage_examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True, nullable=False)
    sound = Column(String, nullable=True)
    
    occurrences = relationship("DocumentWord", back_populates="word")

    def __repr__(self):
        return f"<UsageExample(word='{self.word}')>"

class DocumentHanja(Base):
    __tablename__ = "document_hanja"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    hanja_id = Column(Integer, ForeignKey("hanja_info.id"), nullable=False)
    frequency = Column(Integer, default=1)
    
    document = relationship("Document", back_populates="hanja_occurrences")
    hanja = relationship("HanjaInfo", back_populates="occurrences")

class DocumentWord(Base):
    __tablename__ = "document_words"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("usage_examples.id"), nullable=False)
    frequency = Column(Integer, default=1)
    
    document = relationship("Document", back_populates="word_occurrences")
    word = relationship("UsageExample", back_populates="occurrences")

def init_db(db_url="sqlite:///hanja.db"):
    from sqlalchemy import create_engine
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
