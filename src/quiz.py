import random
from sqlalchemy.sql import func, desc
from src.models import HanjaInfo, UsageExample, DocumentHanja, DocumentWord

class QuizGenerator:
    def __init__(self, session_factory):
        self.Session = session_factory

    def get_weighted_hanja(self, session, limit=100, radical=None):
        """
        Fetch top frequent Hanjas using the provided session.
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

    def generate_quiz(self, mode='random', q_type='hanja_to_meaning', radical=None):
        """
        Generates a single quiz question based on mode and type.
        Modes: 'random', 'radical', 'word'
        Types: 'hanja_to_meaning', 'meaning_to_hanja', 'word_to_sound', 'sound_to_word'
        """
        session = self.Session()
        try:
            question_data = {}
            
            # --- Hanja Quiz ---
            if mode in ['random', 'radical']:
                # 1. Select Target Hanja (Weighted)
                candidates = self.get_weighted_hanja(session, limit=200, radical=radical)
                if not candidates:
                    return None
                
                # Weighted random choice
                total_weight = sum(w for h, w in candidates)
                pick_val = random.uniform(0, total_weight)
                current = 0
                target = candidates[0][0]
                for h, w in candidates:
                    current += w
                    if current > pick_val:
                        target = h
                        break
                
                if not target.readings:
                    return None # Skip if no reading info

                reading = target.readings[0]
                meaning_sound = f"{reading.meaning} {reading.sound}"
                
                # 2. Select Distractors
                # Get random other hanjas
                distractors = []
                others = session.query(HanjaInfo).filter(HanjaInfo.id != target.id).order_by(func.random()).limit(10).all()
                
                for o in others:
                    if o.readings:
                        r = o.readings[0]
                        ms = f"{r.meaning} {r.sound}"
                        
                        if q_type == 'hanja_to_meaning':
                            val = ms
                        else: # meaning_to_hanja
                            val = o.char
                            
                        if val not in distractors:
                            distractors.append(val)
                        if len(distractors) == 3:
                            break
                
                if len(distractors) < 3: return None

                # 3. Formulate Question
                if q_type == 'hanja_to_meaning':
                    question_text = target.char
                    correct_answer = meaning_sound
                    options = distractors + [correct_answer]
                else: # meaning_to_hanja
                    question_text = meaning_sound
                    correct_answer = target.char
                    options = distractors + [correct_answer]

                random.shuffle(options)
                question_data = {
                    "q_text": question_text,
                    "correct": correct_answer,
                    "options": options,
                    "info": f"부수: {target.radical}, 획수: {target.strokes}"
                }

            # --- Word Quiz ---
            elif mode == 'word':
                # Get random word from UsageExample (weighted by frequency would be better, but simple random for now)
                target = session.query(UsageExample).filter(UsageExample.sound != None).order_by(func.random()).first()
                if not target: return None
                
                distractors = []
                others = session.query(UsageExample).filter(UsageExample.id != target.id, UsageExample.sound != None).order_by(func.random()).limit(10).all()
                
                for o in others:
                    if q_type == 'word_to_sound':
                        val = o.sound
                    else: # sound_to_word
                        val = o.word
                    
                    if val not in distractors:
                        distractors.append(val)
                    if len(distractors) == 3:
                        break
                
                if len(distractors) < 3: return None

                if q_type == 'word_to_sound':
                    question_text = target.word
                    correct_answer = target.sound
                    options = distractors + [correct_answer]
                else: # sound_to_word
                    question_text = target.sound
                    correct_answer = target.word
                    options = distractors + [correct_answer]

                random.shuffle(options)
                question_data = {
                    "q_text": question_text,
                    "correct": correct_answer,
                    "options": options,
                    "info": ""
                }

            return question_data

        finally:
            session.close()

    def get_all_radicals(self):
        session = self.Session()
        try:
            radicals = session.query(HanjaInfo.radical).distinct().filter(HanjaInfo.radical != None).all()
            return sorted([r[0] for r in radicals])
        finally:
            session.close()