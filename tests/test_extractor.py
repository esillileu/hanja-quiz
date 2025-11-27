import pytest
from src.extractor import HanjaExtractor

def test_extract_hanja_and_words():
    extractor = HanjaExtractor()
    text = "이것은 學校에서 배우는 漢字입니다. 人生은 아름답다."
    
    chars, words = extractor.extract(text)
    
    # Check individual chars
    expected_chars = {'學', '校', '漢', '字', '人', '生'}
    assert set(chars) == expected_chars
    
    # Check words
    expected_words = {'學校', '漢字', '人生'}
    assert set(words) == expected_words

def test_extract_no_hanja():
    extractor = HanjaExtractor()
    text = "한글만 있는 문장입니다. English too."
    
    chars, words = extractor.extract(text)
    
    assert chars == []
    assert words == []

def test_extract_single_char_words():
    extractor = HanjaExtractor()
    text = "一 더하기 二는 三이다."
    
    chars, words = extractor.extract(text)
    
    assert set(chars) == {'一', '二', '三'}
    assert words == [] # Single chars are not words in this logic

def test_extract_mixed_content():
    extractor = HanjaExtractor()
    text = "abc 123 混合된 content."
    
    chars, words = extractor.extract(text)
    
    assert set(chars) == {'混', '合'}
    assert words == ['混合']