import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HanjaInfo, UsageExample

@pytest.fixture
def session():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_hanja_info(session):
    hanja = HanjaInfo(char="漢", sound="한", meaning="한나라", radical="水", strokes=14)
    session.add(hanja)
    session.commit()

    retrieved = session.query(HanjaInfo).filter_by(char="漢").first()
    assert retrieved is not None
    assert retrieved.sound == "한"
    assert retrieved.radical == "水"

def test_create_usage_example(session):
    example = UsageExample(word="漢字", sound="한자")
    session.add(example)
    session.commit()

    retrieved = session.query(UsageExample).filter_by(word="漢字").first()
    assert retrieved is not None
    assert retrieved.sound == "한자"
    assert retrieved.frequency == 1  # Default value check

def test_unique_constraints(session):
    # Test Hanja uniqueness
    h1 = HanjaInfo(char="字", sound="자")
    session.add(h1)
    session.commit()
    
    h2 = HanjaInfo(char="字", sound="자")
    session.add(h2)
    
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

    # Test Word uniqueness
    w1 = UsageExample(word="단어")
    session.add(w1)
    session.commit()

    w2 = UsageExample(word="단어")
    session.add(w2)

    with pytest.raises(IntegrityError):
        session.commit()
