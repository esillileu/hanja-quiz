import hanja

class HanjaDictionary:
    """
    한자 캐릭터에 대한 음, 뜻, 부수, 획수 정보를 조회하는 클래스.
    현재는 hanja 라이브러리를 통해 음만 제공하며, 나머지는 플레이스홀더입니다.
    """
    def lookup(self, char: str) -> dict:
        """
        단일 한자의 음, 뜻, 부수, 획수 정보를 조회합니다.
        
        Args:
            char (str): 조회할 한자 한 글자.
            
        Returns:
            dict: 한자 정보 {'char', 'sound', 'meaning', 'radical', 'strokes'}.
        """
        if not char or len(char) != 1:
            raise ValueError("lookup 메소드에는 한 글자의 한자만 전달해야 합니다.")

        # CJK Unified Ideographs 범위: U+4E00 ~ U+9FFF
        if not ('\u4e00' <= char <= '\u9fff'):
             raise ValueError("입력된 문자는 한자가 아닙니다.")

        sound = self._get_sound(char)
        
        # 부수, 뜻, 획수 정보는 현재 데이터 소스가 없으므로 플레이스홀더 사용
        meaning = "미상" # 미상: 未詳 (불분명)
        radical = "?"
        strokes = 0 # 획수 정보도 현재는 알 수 없음

        return {
            "char": char,
            "sound": sound,
            "meaning": meaning,
            "radical": radical,
            "strokes": strokes
        }

    def _get_sound(self, char: str) -> str:
        """
        hanja 라이브러리를 사용하여 한자의 음을 가져옵니다.
        """
        return hanja.translate(char, mode='substitution')

    def get_word_sound(self, word: str) -> str:
        """
        한자 단어(2글자 이상)의 음(한글)을 반환합니다.
        
        Args:
            word (str): 한자 단어.
            
        Returns:
            str: 한글 발음.
        """
        return hanja.translate(word, mode='substitution')

    