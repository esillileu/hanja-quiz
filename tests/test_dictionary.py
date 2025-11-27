import pytest
from src.dictionary import HanjaDictionary

@pytest.fixture
def hanja_dict():
    return HanjaDictionary()

def test_lookup_valid_hanja(hanja_dict):
    char_info = hanja_dict.lookup("漢")
    assert char_info["char"] == "漢"
    assert char_info["sound"] == "한"  # 'hanja' library result for 漢
    assert char_info["meaning"] == "미상"
    assert char_info["radical"] == "?"
    assert char_info["strokes"] == 0

def test_lookup_another_valid_hanja(hanja_dict):
    char_info = hanja_dict.lookup("字")
    assert char_info["char"] == "字"
    assert char_info["sound"] == "자"  # 'hanja' library result for 字
    assert char_info["meaning"] == "미상"
    assert char_info["radical"] == "?"
    assert char_info["strokes"] == 0

def test_lookup_invalid_input(hanja_dict):
    with pytest.raises(ValueError, match="한 글자의 한자만 전달해야 합니다."):
        hanja_dict.lookup("漢字")
    with pytest.raises(ValueError, match="한 글자의 한자만 전달해야 합니다."):
        hanja_dict.lookup("")
    with pytest.raises(ValueError, match="한 글자의 한자만 전달해야 합니다."):
        hanja_dict.lookup("A") # 영어는 한자로 처리하지 않음, 일단 한 글자 검증만

def test_lookup_non_hanja_character(hanja_dict):
    char_info = hanja_dict.lookup("가") # 한글
    assert char_info["char"] == "가"
    assert char_info["sound"] == "" # hanja library won't return sound for non-hanja
    assert char_info["meaning"] == "미상"
    assert char_info["radical"] == "?"
    assert char_info["strokes"] == 0
