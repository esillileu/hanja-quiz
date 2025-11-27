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
    h4 = HanjaInfo(char="人", radical="人", strokes=2)
    h5 = HanjaInfo(char="山", radical="山", strokes=3)
    h6 = HanjaInfo(char="水", radical="水", strokes=4)
    h7 = HanjaInfo(char="天", radical="大", strokes=4)
    session.add_all([h1, h2, h3, h4, h5, h6, h7])
    session.flush() # Assign IDs
    
    session.add_all([
        HanjaReading(hanja_id=h1.id, sound="학", meaning="배울"),
        HanjaReading(hanja_id=h2.id, sound="교", meaning="학교"),
        HanjaReading(hanja_id=h3.id, sound="생", meaning="날"),
        HanjaReading(hanja_id=h4.id, sound="인", meaning="사람"),
        HanjaReading(hanja_id=h5.id, sound="산", meaning="메"),
        HanjaReading(hanja_id=h6.id, sound="수", meaning="물"),
        HanjaReading(hanja_id=h7.id, sound="천", meaning="하늘")
    ])
    
    # Massively expanded UsageExample seed data for robust distractor generation
    words_data = [
        ("學校", "학교"), ("學生", "학생"), ("先生", "선생"), ("人生", "인생"),
        ("國語", "국어"), ("數學", "수학"), ("科學", "과학"), ("英語", "영어"),
        ("歷史", "역사"), ("美術", "미술"), ("音樂", "음악"), ("體育", "체육"),
        ("世界", "세계"), ("文化", "문화"), ("學習", "학습"), ("知識", "지식"),
        ("智慧", "지혜"), ("幸福", "행복"), ("希望", "희망"), ("成功", "성공"),
        ("友情", "우정"), ("愛情", "애정"), ("平和", "평화"), ("自由", "자유"),
        ("正義", "정의"), ("民主", "민주"), ("共和", "공화"), ("統一", "통일"),
        ("獨立", "독립"), ("發展", "발전"), ("創造", "창조"), ("革新", "혁신"),
        ("未來", "미래"), ("過去", "과거"), ("現在", "현재"), ("變化", "변화"),
        ("思想", "사상"), ("哲學", "철학"), ("文學", "문학"), ("藝術", "예술"),
        ("國家", "국가"), ("社會", "사회"), ("經濟", "경제"), ("政治", "정치"),
        ("法律", "법률"), ("道德", "도덕"), ("教育", "교육"), ("健康", "건강"),
        ("自然", "자연"), ("環境", "환경"), ("科學技術", "과학기술"), ("情報", "정보")
    ]
    w_objs = [UsageExample(word=w, sound=s) for w, s in words_data]
    session.add_all(w_objs)
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
    up_w1 = UserProgress(word_id=w_objs[0].id, importance_level=3)  # 學校 - level 3
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
    # Allow any of the seeded hanjas (h1~h7)
    possible_answers = ["學", "校", "生", "人", "山", "水", "天"]
    assert q['correct'] in possible_answers 
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