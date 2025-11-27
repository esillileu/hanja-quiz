import re
from typing import List, Tuple

class HanjaExtractor:
    """
    텍스트에서 한자(단일 글자)와 한자 단어(연속된 2자 이상)를 추출합니다.
    """
    # CJK Unified Ideographs 범위 (기본 한자)
    HANJA_PATTERN = re.compile(r'[\u4e00-\u9fff]+')

    def extract(self, text: str) -> Tuple[List[str], List[str]]:
        """
        텍스트를 입력받아 (개별 한자 리스트, 한자 단어 리스트)를 반환합니다.
        
        Args:
            text (str): 분석할 텍스트.
            
        Returns:
            Tuple[List[str], List[str]]: 
                - 첫 번째 리스트: 중복 제거된 개별 한자들
                - 두 번째 리스트: 중복 제거된 2글자 이상의 한자 단어들
        """
        if not text:
            return [], []

        matches = self.HANJA_PATTERN.findall(text)
        
        individual_chars = set()
        words = set()

        for match in matches:
            # 개별 한자 추가
            for char in match:
                individual_chars.add(char)
            
            # 2글자 이상이면 단어로 추가
            if len(match) >= 2:
                words.add(match)

        return list(individual_chars), list(words)
