import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, RefHanja, RefHanjaReading
from src.dictionary import HanjaDictionary

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Seed Reference Dictionary
    hanja = RefHanja(char="學", radical="子", strokes=16, level="8급")
    session.add(hanja)
    session.flush()
    
    reading = RefHanjaReading(hanja_id=hanja.id, sound="학", meaning="배울")
    session.add(reading)
    session.commit()
    
    yield session
    session.close()

def test_lookup_from_db(session):
    dictionary = HanjaDictionary()
    
    # Should find in DB
    result = dictionary.lookup(session, "學")
    
    assert result['char'] == "學"
    assert result['sound'] == "학"
    assert result['meaning'] == "배울"
    assert result['radical'] == "子"
    assert result['strokes'] == 16
    assert len(result['readings']) == 1

def test_lookup_fallback(session):
    dictionary = HanjaDictionary()
    
    # '生' is NOT in DB, so it should use fallback (hanja library)
    # Note: hanja library returns '생' for '生'. Meaning will be '미상'.
    result = dictionary.lookup(session, "生")
    
    assert result['char'] == "生"
    assert result['sound'] == "생"
    assert result['meaning'] == "미상" # Fallback default
    assert result['radical'] == "?"

def test_lookup_invalid_input(session):
    dictionary = HanjaDictionary()
    
    with pytest.raises(ValueError):
        dictionary.lookup(session, "AB") # Too long
        
    with pytest.raises(ValueError):
        dictionary.lookup(session, "A") # Not Hanja

def test_get_word_sound():
    dictionary = HanjaDictionary()
    sound = dictionary.get_word_sound("學校")
    assert sound == "학교"