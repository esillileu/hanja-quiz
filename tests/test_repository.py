import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HanjaInfo, UsageExample, Document, DocumentHanja, DocumentWord, HanjaReading, RefHanja, RefHanjaReading, UserProgress
from src.repository import HanjaRepository
from datetime import datetime, timedelta

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

@pytest.fixture
def seed_data(session):
    # Seed common data for multiple tests
    h1 = HanjaInfo(char="學", radical="子", strokes=16)
    h2 = HanjaInfo(char="校", radical="木", strokes=10)
    w1 = UsageExample(word="學校", sound="학교")
    w2 = UsageExample(word="人生", sound="인생")
    
    session.add_all([h1, h2, w1, w2])
    session.flush() # Assign IDs
    
    session.add_all([
        HanjaReading(hanja_id=h1.id, sound="학", meaning="배울"),
        HanjaReading(hanja_id=h2.id, sound="교", meaning="학교"),
    ])
    session.commit()
    return {"h1": h1, "h2": h2, "w1": w1, "w2": w2}

def test_create_document(session, repository):
    doc = repository.create_document(session, "test.pdf", "hash123")
    assert doc.id is not None
    assert doc.filename == "test.pdf"
    assert doc.file_hash == "hash123"

    # Check retrieval
    retrieved = repository.get_document_by_hash(session, "hash123")
    assert retrieved.id == doc.id

def test_add_hanja_info(session, repository, seed_data):
    # Test adding new hanja
    h_new = repository.add_hanja_info(session, char="愛", sound="애", meaning="사랑", radical="心", strokes=13)
    assert h_new.id is not None
    assert h_new.char == "愛"
    
    reading = session.query(HanjaReading).filter_by(hanja_id=h_new.id).first()
    assert reading.sound == "애"
    assert reading.meaning == "사랑"

    # Test updating existing hanja (should just return existing and add reading if new)
    h_existing = repository.add_hanja_info(session, char="學", sound="학", meaning="배울")
    assert h_existing.id == seed_data["h1"].id

def test_add_usage_example(session, repository, seed_data):
    # Test adding new word
    w_new = repository.add_usage_example(session, word="希望", sound="희망")
    assert w_new.id is not None
    assert w_new.word == "希望"
    assert w_new.sound == "희망"

    # Test updating existing word
    w_existing = repository.add_usage_example(session, word="學校", sound="학교")
    assert w_existing.id == seed_data["w1"].id

def test_update_document_hanja_frequency(session, repository, seed_data):
    doc = repository.create_document(session, "doc1", "h1")
    
    # First occurrence
    doc_hanja = repository.update_document_hanja_frequency(session, doc.id, "學")
    assert doc_hanja.frequency == 1
    assert doc_hanja.document_id == doc.id
    
    # Second occurrence
    doc_hanja = repository.update_document_hanja_frequency(session, doc.id, "學")
    assert doc_hanja.frequency == 2

def test_update_document_word_frequency(session, repository, seed_data):
    doc = repository.create_document(session, "doc1", "h1")
    
    # First occurrence
    doc_word = repository.update_document_word_frequency(session, doc.id, "學校")
    assert doc_word.frequency == 1
    
    # Second occurrence
    doc_word = repository.update_document_word_frequency(session, doc.id, "學校")
    assert doc_word.frequency == 2

def test_update_importance_level_hanja(session, repository, seed_data):
    hanja = seed_data["h1"] # 學
    
    # Initial creation with +1 (default 5 + 1 = 6)
    up = repository.update_importance_level(session, hanja_id=hanja.id, change=+1)
    session.commit()
    assert up.importance_level == 6
    assert up.hanja_id == hanja.id
    
    # Decrease (-1) (6 - 1 = 5)
    up2 = repository.update_importance_level(session, hanja_id=hanja.id, change=-1)
    session.commit()
    assert up2.importance_level == 5
    
    # Decrease to below zero (should be 0)
    up3 = repository.update_importance_level(session, hanja_id=hanja.id, change=-10)
    session.commit()
    assert up3.importance_level == 0

def test_update_importance_level_word(session, repository, seed_data):
    word = seed_data["w1"] # 學校
    
    # Initial creation with -1 (default 5 - 1 = 4)
    up = repository.update_importance_level(session, word_id=word.id, change=-1)
    session.commit()
    assert up.importance_level == 4
    assert up.word_id == word.id
    
    # Increase again (+1) (4 + 1 = 5)
    up2 = repository.update_importance_level(session, word_id=word.id, change=+1)
    session.commit()
    assert up2.importance_level == 5

def test_update_importance_level_no_id_raises_error(session, repository):
    with pytest.raises(ValueError, match="Either hanja_id or word_id must be provided."):
        repository.update_importance_level(session)

def test_get_user_progress(session, repository, seed_data):
    hanja = seed_data["h1"]
    word = seed_data["w1"]
    
    repository.update_importance_level(session, hanja_id=hanja.id, change=1) # Sets to 5+1=6
    repository.update_importance_level(session, word_id=word.id, change=2) # Sets to 5+2=7
    session.commit()
    
    retrieved_hanja_up = repository.get_user_progress(session, hanja_id=hanja.id)
    assert retrieved_hanja_up is not None
    assert retrieved_hanja_up.hanja.char == "學"
    assert retrieved_hanja_up.importance_level == 6 
    
    retrieved_word_up = repository.get_user_progress(session, word_id=word.id)
    assert retrieved_word_up is not None
    assert retrieved_word_up.word.word == "學校"
    assert retrieved_word_up.importance_level == 7

def test_get_all_user_progress(session, repository, seed_data):
    h1 = seed_data["h1"]
    h2 = seed_data["h2"]
    w1 = seed_data["w1"]
    
    repository.update_importance_level(session, hanja_id=h1.id, change=5) # 5+5=10
    repository.update_importance_level(session, hanja_id=h2.id, change=1) # 5+1=6
    repository.update_importance_level(session, word_id=w1.id, change=3) # 5+3=8
    session.commit()
    
    all_progress = repository.get_all_user_progress(session)
    assert len(all_progress) == 3
    # Ordered by importance_level desc, then last_tested_at asc
    assert all_progress[0].hanja.char == "學" # Level 10
    assert all_progress[1].word.word == "學校" # Level 8
    assert all_progress[2].hanja.char == "校" # Level 6

    # Test min_importance filter
    # All are > 7 except '校' (Level 6). So if min=7, we expect 2.
    high_importance_progress = repository.get_all_user_progress(session, min_importance=7)
    assert len(high_importance_progress) == 2
    assert high_importance_progress[0].hanja.char == "學" # Level 10
    assert high_importance_progress[1].word.word == "學校" # Level 8
