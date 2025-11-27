import random
from sqlalchemy.sql import func, desc
from src.models import HanjaInfo, UsageExample, DocumentHanja, DocumentWord, UserProgress

class QuizGenerator:
    def __init__(self, session_factory):
        self.Session = session_factory

    def get_weighted_hanja(self, session, limit=100, radical=None):
        """
        Fetch top frequent Hanjas.
        If radical is provided, filter by it.
        """
        query = session.query(
            HanjaInfo, 
            func.sum(DocumentHanja.frequency).label('total_freq')
        ).join(DocumentHanja)
        
        if radical:
            query = query.filter(HanjaInfo.radical == radical)
            
        results = query.group_by(HanjaInfo.id).order_by(desc('total_freq')).limit(limit).all()
        
        # Return list of (hanja, weight)
        return [(r[0], r[1]) for r in results]

    def generate_quiz(self, mode='random', q_type='hanja_to_meaning', radical=None, min_importance_level=0):
        """
        Generates a single quiz question based on mode and type.
        Modes: 'random', 'radical', 'word', 'importance_review'
        Types: 'hanja_to_meaning', 'meaning_to_hanja', 'word_to_sound', 'sound_to_word'
        min_importance_level: Only for 'importance_review' mode, filter by importance level.
        """
        session = self.Session()
        try:
            question_data = None
            
            # --- Importance Review Mode ---
            if mode == 'importance_review':
                question_data = self._generate_importance_review_quiz(session, q_type, min_importance_level)
                if question_data:
                    random.shuffle(question_data['options'])
                    return question_data
                
            # --- Hanja Quiz (Random / Radical) ---
            if mode in ['random', 'radical']:
                # 1. Select Target Hanja (Weighted)
                candidates = self.get_weighted_hanja(session, limit=200, radical=radical)
                if not candidates:
                    return None
                
                # Weighted random choice
                total_weight = sum(w for h, w in candidates)
                if total_weight == 0: return None
                pick_val = random.uniform(0, total_weight)
                current = 0
                target = None
                for h, w in candidates:
                    current += w
                    if current > pick_val:
                        target = h
                        break
                
                if not target or not target.readings:
                    return None # Skip if no reading info

                reading = target.readings[0]
                meaning_sound = f"{reading.meaning} {reading.sound}"
                
                # 2. Select Distractors
                distractors = []
                others_query = session.query(HanjaInfo).filter(HanjaInfo.id != target.id)
                if radical: 
                    others_query = others_query.filter(HanjaInfo.radical != radical) # Get distractors from other radicals
                
                # Try to get enough unique distractors
                possible_distractors = others_query.order_by(func.random()).limit(min(50, others_query.count())).all()
                for o in possible_distractors:
                    if o.readings:
                        r = o.readings[0]
                        ms = f"{r.meaning} {r.sound}"
                        
                        # Ensure val is always assigned before use
                        if q_type == 'hanja_to_meaning':
                            val = ms
                        else: # meaning_to_hanja
                            val = o.char
                            
                        if val not in distractors and val != meaning_sound and val != target.char: # Avoid correct answer and duplicates
                            distractors.append(val)
                        if len(distractors) == 3:
                            break
                
                if len(distractors) < 3: return None

                # 3. Formulate Question
                if q_type == 'hanja_to_meaning':
                    question_data = {
                        "q_text": target.char,
                        "correct": meaning_sound,
                        "options": distractors + [meaning_sound],
                        "info": f"부수: {target.radical}, 획수: {target.strokes}",
                        "hanja_id": target.id, # For mistake tracking
                        "word_id": None
                    }
                else: # meaning_to_hanja
                    question_data = {
                        "q_text": meaning_sound,
                        "correct": target.char,
                        "options": distractors + [target.char],
                        "info": f"부수: {target.radical}, 획수: {target.strokes}",
                        "hanja_id": target.id, # For mistake tracking
                        "word_id": None
                    }

            # --- Word Quiz ---
            elif mode == 'word':
                # Get random word from UsageExample
                target = session.query(UsageExample).filter(UsageExample.sound != None).order_by(func.random()).first()
                if not target: return None
                
                distractors = []
                others = session.query(UsageExample).filter(UsageExample.id != target.id, UsageExample.sound != None).order_by(func.random()).limit(min(50, session.query(UsageExample).count())).all()
                
                for o in others:
                    if q_type == 'word_to_sound':
                        val = o.sound
                    else: # sound_to_word
                        val = o.word
                    
                    if val not in distractors and val != target.sound and val != target.word: # Avoid correct answer and duplicates
                        distractors.append(val)
                    if len(distractors) == 3:
                        break
                
                if len(distractors) < 3: return None

                if q_type == 'word_to_sound':
                    question_data = {
                        "q_text": target.word,
                        "correct": target.sound,
                        "options": distractors + [target.sound],
                        "info": "",
                        "hanja_id": None,
                        "word_id": target.id # For mistake tracking
                    }
                else: # sound_to_word
                    question_data = {
                        "q_text": target.sound,
                        "correct": target.word,
                        "options": distractors + [target.word],
                        "info": "",
                        "hanja_id": None,
                        "word_id": target.id # For mistake tracking
                    }

            if question_data:
                random.shuffle(question_data['options'])
            return question_data
        finally:
            session.close()

    def _generate_importance_review_quiz(self, session, q_type: str, min_importance_level: int):
        """
        Generates a quiz question from UserProgress, weighted by importance_level.
        """
        # Collect candidates based on q_type and importance level
        candidates = []
        if q_type in ['hanja_to_meaning', 'meaning_to_hanja']:
            progress_entries = session.query(UserProgress).filter(
                UserProgress.hanja_id != None,
                UserProgress.importance_level >= min_importance_level
            ).all()
            for up in progress_entries:
                if up.hanja and up.hanja.readings: # Ensure hanja object is loaded and has readings
                    candidates.append((up.hanja, up.importance_level + 1)) # +1 to ensure non-zero weight
        elif q_type in ['word_to_sound', 'sound_to_word']:
            progress_entries = session.query(UserProgress).filter(
                UserProgress.word_id != None,
                UserProgress.importance_level >= min_importance_level
            ).all()
            for up in progress_entries:
                if up.word and up.word.sound: # Ensure word object is loaded and has sound
                    candidates.append((up.word, up.importance_level + 1)) # +1 to ensure non-zero weight
        
        if not candidates:
            return None # No items to review at this importance level
            
        # Weighted random choice based on importance_level
        total_weight = sum(w for _, w in candidates)
        if total_weight == 0: return None
        pick_val = random.uniform(0, total_weight)
        current = 0
        target = None
        for item, weight in candidates:
            current += weight
            if current > pick_val:
                target = item
                break
        
        if not target: return None

        # Generate question based on target (HanjaInfo or UsageExample)
        if isinstance(target, HanjaInfo):
            reading = target.readings[0]
            meaning_sound = f"{reading.meaning} {reading.sound}"
            
            distractors = []
            others_query = session.query(HanjaInfo).filter(HanjaInfo.id != target.id)
            possible_distractors = others_query.order_by(func.random()).limit(min(50, others_query.count())).all()

            for o in possible_distractors:
                if o.readings:
                    r = o.readings[0]
                    ms = f"{r.meaning} {r.sound}"
                    val = ms if q_type == 'hanja_to_meaning' else o.char
                    if val not in distractors and val != meaning_sound and val != target.char:
                        distractors.append(val)
                    if len(distractors) == 3: break
            
            if len(distractors) < 3: return None

            if q_type == 'hanja_to_meaning':
                return {
                    "q_text": target.char,
                    "correct": meaning_sound,
                    "options": distractors + [meaning_sound],
                    "info": f"부수: {target.radical}, 획수: {target.strokes}",
                    "hanja_id": target.id,
                    "word_id": None
                }
            else: # meaning_to_hanja
                return {
                    "q_text": meaning_sound,
                    "correct": target.char,
                    "options": distractors + [target.char],
                    "info": f"부수: {target.radical}, 획수: {target.strokes}",
                    "hanja_id": target.id,
                    "word_id": None
                }
        
        elif isinstance(target, UsageExample):
            distractors = []
            others = session.query(UsageExample).filter(UsageExample.id != target.id, UsageExample.sound != None).order_by(func.random()).limit(min(50, session.query(UsageExample).count())).all()
            for o in others:
                val = o.sound if q_type == 'word_to_sound' else o.word
                if val not in distractors and val != target.sound and val != target.word:
                    distractors.append(val)
                if len(distractors) == 3: break
            
            if len(distractors) < 3: return None

            if q_type == 'word_to_sound':
                return {
                    "q_text": target.word,
                    "correct": target.sound,
                    "options": distractors + [target.sound],
                    "info": "",
                    "hanja_id": None,
                    "word_id": target.id
                }
            else: # sound_to_word
                return {
                    "q_text": target.sound,
                    "correct": target.word,
                    "options": distractors + [target.word],
                    "info": "",
                    "hanja_id": None,
                    "word_id": target.id
                }
        return None


    def get_all_radicals(self):
        session = self.Session()
        try:
            radicals = session.query(HanjaInfo.radical).distinct().filter(HanjaInfo.radical != None).all()
            return sorted([r[0] for r in radicals])
        finally:
            session.close()