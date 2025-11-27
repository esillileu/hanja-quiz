import hanja
from src.models import RefHanja, RefHanjaReading

class HanjaDictionary:
    """
    한자 캐릭터에 대한 음, 뜻, 부수, 획수 정보를 조회하는 클래스.
    DB의 Reference Dictionary(RefHanja)를 조회하며, 없을 경우 hanja 라이브러리를 fallback으로 사용합니다.
    """
    def __init__(self):
        pass

    def lookup(self, session, char: str) -> dict:
        """
        단일 한자의 음, 뜻, 부수, 획수 정보를 DB에서 조회합니다.
        
        Args:
            session: SQLAlchemy session.
            char (str): 조회할 한자 한 글자.
            
        Returns:
            dict: 한자 정보 {'char', 'sound', 'meaning', 'radical', 'strokes', 'readings'}.
        """
        if not char or len(char) != 1:
            raise ValueError("lookup 메소드에는 한 글자의 한자만 전달해야 합니다.")

        if not ('\u4e00' <= char <= '\u9fff'):
             raise ValueError("입력된 문자는 한자가 아닙니다.")

        # 1. Try to find in RefHanja DB
        ref_hanja = session.query(RefHanja).filter_by(char=char).first()
        
        if ref_hanja:
            readings = []
            for r in ref_hanja.readings:
                readings.append({'meaning': r.meaning, 'sound': r.sound})
            
            first_reading = readings[0] if readings else {'meaning': '미상', 'sound': ''}
            
            return {
                "char": char,
                "sound": first_reading['sound'],
                "meaning": first_reading['meaning'],
                "radical": ref_hanja.radical,
                "strokes": ref_hanja.strokes,
                "readings": readings
            }

        # 2. Fallback to hanja library
        sound = self._get_sound(char)
        return {
            "char": char,
            "sound": sound,
            "meaning": "미상",
            "radical": "?",
            "strokes": 0,
            "readings": [{"sound": sound, "meaning": "미상"}]
        }

    def _get_sound(self, char: str) -> str:
        return hanja.translate(char, mode='substitution')

    def get_word_sound(self, word: str) -> str:
        return hanja.translate(word, mode='substitution')

    