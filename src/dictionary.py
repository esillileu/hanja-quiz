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
        # hanja.split_hanja는 한자의 음을 리스트로 반환합니다.
        # 첫 번째 음을 사용하고, 없을 경우 빈 문자열 반환
        result = hanja.split_hanja(char)
        if result and isinstance(result, list) and len(result) > 0:
            return result[0][0] # 예: ('漢', '한', '한나라 한') -> '한'
        return ""

