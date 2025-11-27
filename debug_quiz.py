from src.models import init_db, HanjaInfo, HanjaReading, UsageExample, UserProgress
from src.quiz import QuizGenerator
import random

def debug_quiz_generation():
    Session = init_db()
    session = Session()
    generator = QuizGenerator(Session)
    
    print("--- Database Status Check ---")
    h_count = session.query(HanjaInfo).count()
    hr_count = session.query(HanjaReading).count()
    w_count = session.query(UsageExample).count()
    up_count = session.query(UserProgress).count()
    
    print(f"HanjaInfo count: {h_count}")
    print(f"HanjaReading count: {hr_count}")
    print(f"UsageExample count: {w_count}")
    print(f"UserProgress count: {up_count}")
    
    if h_count == 0 or hr_count == 0:
        print("CRITICAL: HanjaInfo or HanjaReading table is empty! Quizzes cannot be generated.")
        return

    print("\n--- Quiz Generation Test (Random Mode) ---")
    # Test get_weighted_hanja
    candidates = generator.get_weighted_hanja(session, limit=10)
    print(f"Weighted candidates (top 10): {len(candidates)}")
    if candidates:
        print(f"Sample candidate: {candidates[0][0].char} (Weight: {candidates[0][1]})")
    else:
        print("No candidates found via get_weighted_hanja.")

    # Test generate_quiz
    q = generator.generate_quiz(mode='random', q_type='hanja_to_meaning')
    if q:
        print("\n[SUCCESS] Random Quiz Generated:")
        print(q)
    else:
        print("\n[FAIL] Random Quiz Generation returned None.")
        # Dig deeper: Check why
        # 1. Pick a target
        target = candidates[0][0] if candidates else None
        if target:
            print(f"Target selected: {target.char}")
            if not target.readings:
                print("Target has NO readings.")
            else:
                print(f"Target readings: {target.readings[0].meaning} {target.readings[0].sound}")
                
                # Check distractors
                others_query = session.query(HanjaInfo).filter(HanjaInfo.id != target.id)
                count = others_query.count()
                print(f"Potential distractors count: {count}")
                possible = others_query.limit(50).all()
                valid_distractors = []
                for o in possible:
                    if o.readings:
                        valid_distractors.append(o)
                print(f"Valid distractors (with readings) in sample: {len(valid_distractors)}")
        else:
            print("Could not select a target.")

    print("\n--- Quiz Generation Test (Word Mode) ---")
    q_word = generator.generate_quiz(mode='word', q_type='word_to_sound')
    if q_word:
        print("\n[SUCCESS] Word Quiz Generated:")
        print(q_word)
    else:
        print("\n[FAIL] Word Quiz Generation returned None.")

    session.close()

if __name__ == "__main__":
    debug_quiz_generation()
