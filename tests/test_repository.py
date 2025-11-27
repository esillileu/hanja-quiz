import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HanjaInfo, UsageExample, Document, DocumentHanja, DocumentWord, HanjaReading, RefHanja, RefHanjaReading
from src.repository import HanjaRepository

@pytest.fixture
def session():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repository():
    return HanjaRepository()

def test_create_document(session, repository):
    doc = repository.create_document(session, "test.pdf", "hash123")
    assert doc.id is not None
    assert doc.filename == "test.pdf"
    assert doc.file_hash == "hash123"

    # Check retrieval
    retrieved = repository.get_document_by_hash(session, "hash123")
    assert retrieved.id == doc.id

def test_add_hanja_info(session, repository):
    # Add new
    hanja = repository.add_hanja_info(session, char="學", sound="학", meaning="배울", radical="子", strokes=16)
    assert hanja.id is not None
    assert hanja.char == "學"
    
    # Check reading added
    reading = session.query(HanjaReading).filter_by(hanja_id=hanja.id).first()
    assert reading.sound == "학"
    assert reading.meaning == "배울"

    # Add duplicate (should not fail, just return existing)
    hanja2 = repository.add_hanja_info(session, char="學", sound="학", meaning="배울")
    assert hanja2.id == hanja.id

def test_add_usage_example(session, repository):
    word = repository.add_usage_example(session, word="學校", sound="학교")
    assert word.id is not None
    assert word.word == "學校"
    assert word.sound == "학교"

def test_update_document_hanja_frequency(session, repository):
    doc = repository.create_document(session, "doc1", "h1")
    repository.add_hanja_info(session, char="學", sound="학")
    
    # First occurrence
    doc_hanja = repository.update_document_hanja_frequency(session, doc.id, "學")
    assert doc_hanja.frequency == 1
    assert doc_hanja.document_id == doc.id
    
    # Second occurrence
    doc_hanja = repository.update_document_hanja_frequency(session, doc.id, "學")
    assert doc_hanja.frequency == 2

def test_update_document_word_frequency(session, repository):
    doc = repository.create_document(session, "doc1", "h1")
    repository.add_usage_example(session, word="學校", sound="학교")
    
    # First occurrence
    doc_word = repository.update_document_word_frequency(session, doc.id, "學校")
    assert doc_word.frequency == 1
    
    # Second occurrence
    doc_word = repository.update_document_word_frequency(session, doc.id, "學校")
    assert doc_word.frequency == 2
