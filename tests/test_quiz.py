import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, HanjaInfo, HanjaReading, UsageExample, DocumentHanja, Document, UserProgress
from src.quiz import QuizGenerator

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Seed Data for HanjaInfo, UsageExample
    h1 = HanjaInfo(char="學", radical="子", strokes=16)
    h2 = HanjaInfo(char="校", radical="木", strokes=10)
    h3 = HanjaInfo(char="生", radical="生", strokes=5)
    h4 = HanjaInfo(char="人", radical="人", strokes=2) # Added for distractors
    session.add_all([h1, h2, h3, h4])
    session.flush() # Assign IDs
    
    session.add_all([
        HanjaReading(hanja_id=h1.id, sound="학", meaning="배울"),
        HanjaReading(hanja_id=h2.id, sound="교", meaning="학교"),
        HanjaReading(hanja_id=h3.id, sound="생", meaning="날"),
        HanjaReading(hanja_id=h4.id, sound="인", meaning="사람")
    ])
    
    w1 = UsageExample(word="學校", sound="학교")
    w2 = UsageExample(word="學生", sound="학생")
    w3 = UsageExample(word="先生", sound="선생")
    w4 = UsageExample(word="人生", sound="인생")
    w5 = UsageExample(word="國語", sound="국어")
    w6 = UsageExample(word="數學", sound="수학")
    w7 = UsageExample(word="科學", sound="과학")
    w8 = UsageExample(word="英語", sound="영어")
    w9 = UsageExample(word="歷史", sound="역사")
    w10 = UsageExample(word="美術", sound="미술")
    w11 = UsageExample(word="音樂", sound="음악")
    w12 = UsageExample(word="體育", sound="체육")
    w13 = UsageExample(word="世界", sound="세계")
    w14 = UsageExample(word="文化", sound="문화")
    w15 = UsageExample(word="學習", sound="학습")
    w16 = UsageExample(word="知識", sound="지식")
    w17 = UsageExample(word="智慧", sound="지혜")
    w18 = UsageExample(word="幸福", sound="행복")
    w19 = UsageExample(word="希望", sound="희망")
    w20 = UsageExample(word="成功", sound="성공")
    session.add_all([w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14, w15, w16, w17, w18, w19, w20])
    session.flush() # Assign IDs
    
    # Add Document Frequencies (for weighted random hanja quiz)
    doc = Document(filename="test", file_hash="hash")
    session.add(doc)
    session.flush()
    
    session.add(DocumentHanja(document_id=doc.id, hanja_id=h1.id, frequency=10)) # High freq
    session.add(DocumentHanja(document_id=doc.id, hanja_id=h3.id, frequency=1))  # Low freq
    
    # Seed UserProgress for importance review quiz
    up_h1 = UserProgress(hanja_id=h1.id, importance_level=5) # 學 - level 5
    up_h2 = UserProgress(hanja_id=h2.id, importance_level=1) # 校 - level 1
    up_w1 = UserProgress(word_id=w1.id, importance_level=3)  # 學校 - level 3
    session.add_all([up_h1, up_h2, up_w1])

    session.commit()
    
    # Mock close to prevent the method from closing our test session
    session.close = lambda: None
    
    yield session

@pytest.fixture
def quiz_gen(session):
    class MockSessionFactory:
        def __call__(self):
            return session
    return QuizGenerator(MockSessionFactory())

def test_get_weighted_hanja(quiz_gen):
    session = quiz_gen.Session()
    candidates = quiz_gen.get_weighted_hanja(session, limit=5)
    assert len(candidates) > 0
    top_hanja = candidates[0][0]
    assert top_hanja.char == "學"

def test_get_all_radicals(quiz_gen):
    radicals = quiz_gen.get_all_radicals()
    assert "子" in radicals
    assert "木" in radicals
    assert "生" in radicals
    assert "人" in radicals

def test_generate_quiz_hanja_random(quiz_gen):
    # Test Hanja -> Meaning
    q = quiz_gen.generate_quiz(mode='random', q_type='hanja_to_meaning')
    assert q is not None
    assert "q_text" in q
    assert len(q['options']) == 4
    assert q['correct'] in q['options']
    assert q['hanja_id'] is not None # Check ID for mistake tracking
    
    # Test Meaning -> Hanja
    q = quiz_gen.generate_quiz(mode='random', q_type='meaning_to_hanja')
    assert q is not None
    assert "q_text" in q
    assert q['correct'] in ["學", "校", "生", "人"]
    assert q['hanja_id'] is not None

def test_generate_quiz_word(quiz_gen):
    # Test Word -> Sound
    q = quiz_gen.generate_quiz(mode='word', q_type='word_to_sound')
    assert q is not None
    assert q['word_id'] is not None # Check ID for mistake tracking
    
    # Test Sound -> Word
    q = quiz_gen.generate_quiz(mode='word', q_type='sound_to_word')
    assert q is not None
    assert q['word_id'] is not None

def test_generate_quiz_radical_filter(quiz_gen):
    q = quiz_gen.generate_quiz(mode='radical', q_type='hanja_to_meaning', radical="子")
    if q:
        assert q['q_text'] == "學"
        assert q['hanja_id'] is not None

def test_generate_quiz_importance_review_hanja(quiz_gen):
    # 學 (importance=5), 校 (importance=1)
    
    # Test Hanja -> Meaning
    q = quiz_gen.generate_quiz(mode='importance_review', q_type='hanja_to_meaning')
    assert q is not None
    assert q['hanja_id'] is not None
    
    session = quiz_gen.Session()
    h1_id = session.query(HanjaInfo.id).filter_by(char="學").scalar()
    h2_id = session.query(HanjaInfo.id).filter_by(char="校").scalar()
    
    # Should pick from UserProgress hanjas
    assert q['hanja_id'] in [h1_id, h2_id] 
    assert len(q['options']) == 4

def test_generate_quiz_importance_review_word(quiz_gen):
    # 學校 (importance=3)
    
    # Test Word -> Sound
    q = quiz_gen.generate_quiz(mode='importance_review', q_type='word_to_sound')
    assert q is not None
    assert q['word_id'] is not None
    
    session = quiz_gen.Session()
    w1_id = session.query(UsageExample.id).filter_by(word="學校").scalar()
    
    assert q['word_id'] == w1_id
    assert len(q['options']) == 4

def test_generate_quiz_importance_review_min_importance_filter(quiz_gen):
    # 學 (importance=5), 校 (importance=1)
    # Filter for min_importance_level = 2
    q = quiz_gen.generate_quiz(mode='importance_review', q_type='hanja_to_meaning', min_importance_level=2)
    assert q is not None
    assert q['hanja_id'] is not None
    
    session = quiz_gen.Session()
    h1_id = session.query(HanjaInfo.id).filter_by(char="學").scalar()
    
    assert q['hanja_id'] == h1_id # Should only pick 學 (level 5)