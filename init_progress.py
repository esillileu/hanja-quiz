from src.models import init_db, HanjaInfo, UsageExample, UserProgress

def init_importance():
    Session = init_db()
    session = Session()
    
    try:
        print("Initializing UserProgress importance levels to 5...")
        
        # 1. HanjaInfo
        hanjas = session.query(HanjaInfo).all()
        hanja_count = 0
        for h in hanjas:
            progress = session.query(UserProgress).filter_by(hanja_id=h.id).first()
            if not progress:
                progress = UserProgress(hanja_id=h.id, importance_level=5)
                session.add(progress)
                hanja_count += 1
            else:
                if progress.importance_level != 5:
                    progress.importance_level = 5
                    hanja_count += 1
        
        # 2. UsageExample
        words = session.query(UsageExample).all()
        word_count = 0
        for w in words:
            progress = session.query(UserProgress).filter_by(word_id=w.id).first()
            if not progress:
                progress = UserProgress(word_id=w.id, importance_level=5)
                session.add(progress)
                word_count += 1
            else:
                if progress.importance_level != 5:
                    progress.importance_level = 5
                    word_count += 1
        
        session.commit()
        print(f"Updated {hanja_count} Hanja entries and {word_count} Word entries to importance level 5.")
        
    except Exception as e:
        session.rollback()
        print(f"Error initializing progress: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    init_importance()
