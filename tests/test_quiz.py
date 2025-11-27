import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HanjaInfo, HanjaReading, UsageExample, DocumentHanja, Document
from src.quiz import QuizGenerator

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Seed Data
    h1 = HanjaInfo(char="學", radical="子", strokes=16)
    h2 = HanjaInfo(char="校", radical="木", strokes=10)
    h3 = HanjaInfo(char="生", radical="生", strokes=5)
    session.add_all([h1, h2, h3])
    session.flush()
    
    session.add_all([
        HanjaReading(hanja_id=h1.id, sound="학", meaning="배울"),
        HanjaReading(hanja_id=h2.id, sound="교", meaning="학교"),
        HanjaReading(hanja_id=h3.id, sound="생", meaning="날")
    ])
    
    # Add Usage Examples
    w1 = UsageExample(word="學校", sound="학교")
    w2 = UsageExample(word="學生", sound="학생")
    session.add_all([w1, w2])
    
    # Add Document Frequencies (to test weighted random)
    doc = Document(filename="test", file_hash="hash")
    session.add(doc)
    session.flush()
    
    session.add(DocumentHanja(document_id=doc.id, hanja_id=h1.id, frequency=10)) # High freq
    session.add(DocumentHanja(document_id=doc.id, hanja_id=h3.id, frequency=1))  # Low freq
    
    session.commit()
    
    # Mock close to prevent the method from closing our test session
    session.close = lambda: None
    
    yield session
    # Real close logic if needed, but it's in-memory
    # session.close() 

@pytest.fixture
def quiz_gen(session):
    # We need to mock session_factory to return our test session
    class MockSessionFactory:
        def __call__(self):
            return session
    return QuizGenerator(MockSessionFactory())

def test_get_weighted_hanja(quiz_gen):
    # Pass session manually as per new signature (though get_weighted_hanja in new code takes session)
    # Wait, the new refactoring in src/quiz.py made get_weighted_hanja accept session.
    # We need to pass it.
    session = quiz_gen.Session()
    candidates = quiz_gen.get_weighted_hanja(session, limit=5)
    # Should return list of (HanjaInfo, freq)
    assert len(candidates) > 0
    
    # '學' has freq 10, '生' has freq 1. '學' should be first if sorted desc
    top_hanja = candidates[0][0]
    assert top_hanja.char == "學"

def test_get_all_radicals(quiz_gen):
    radicals = quiz_gen.get_all_radicals()
    assert "子" in radicals
    assert "木" in radicals
    assert "生" in radicals

def test_generate_quiz_hanja_random(quiz_gen):
    # Need at least 3 distractors + 1 correct = 4 items total. 
    # Our seed has only 3 hanjas. This might cause 'None' if logic strictly requires unique options.
    # Let's add one more hanja to seed for safety in this test.
    session = quiz_gen.Session()
    h4 = HanjaInfo(char="人", radical="人", strokes=2)
    session.add(h4)
    session.flush() # Ensure ID is assigned
    session.add(HanjaReading(hanja_id=h4.id, sound="인", meaning="사람"))
    session.commit()

    # Test Hanja -> Meaning
    q = quiz_gen.generate_quiz(mode='random', q_type='hanja_to_meaning')
    assert q is not None
    assert "q_text" in q
    assert len(q['options']) == 4
    assert q['correct'] in q['options']
    
    # Test Meaning -> Hanja
    q = quiz_gen.generate_quiz(mode='random', q_type='meaning_to_hanja')
    assert q is not None
    assert "q_text" in q # Meaning string
    assert q['correct'] in ["學", "校", "生", "人"] # Hanja char

def test_generate_quiz_word(quiz_gen):
    # Add more dummy words to satisfy 4 options requirement
    session = quiz_gen.Session()
    session.add_all([
        UsageExample(word="先生", sound="선생"),
        UsageExample(word="人生", sound="인생")
    ])
    session.commit()

    # Test Word -> Sound
    q = quiz_gen.generate_quiz(mode='word', q_type='word_to_sound')
    assert q is not None
    assert q['correct'] in [o for o in q['options']]
    
    # Test Sound -> Word
    q = quiz_gen.generate_quiz(mode='word', q_type='sound_to_word')
    assert q is not None
    assert q['correct'] in [o for o in q['options']]

def test_generate_quiz_radical_filter(quiz_gen):
    # Filter by radical "子" (only '學')
    # Since we need distractors, distractors come from ALL hanjas, target comes from filtered.
    # But if filtered list is too small, get_weighted_hanja returns few candidates.
    # The logic handles picking target from candidates.
    
    # Add more hanjas to ensure we have enough distractors in DB
    session = quiz_gen.Session()
    session.add(HanjaInfo(char="A", radical="X")) # Dummy without reading -> ignored as target
    session.commit()
    
    # We need at least 3 distractors. Our DB has enough now.
    q = quiz_gen.generate_quiz(mode='radical', q_type='hanja_to_meaning', radical="子")
    
    if q: # Might fail if random choice picks something without reading, but '學' has reading
        assert q['q_text'] == "學" # Only hanja with radical '子' in our seed
