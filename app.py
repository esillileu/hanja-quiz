import streamlit as st
import pandas as pd
from sqlalchemy import func, desc
from src.models import init_db, HanjaInfo, UserProgress
from src.quiz import QuizGenerator
from src.repository import HanjaRepository
from src.api import get_top_hanja, get_top_radicals, get_top_hanja_in_words

# Initialize DB, Quiz Generator & Repository
SessionLocal = init_db()
quiz_gen = QuizGenerator(SessionLocal)
repository = HanjaRepository()

st.set_page_config(
    page_title="Hanja Master", layout="wide", initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
st.sidebar.title("📚 Hanja Master")
mode = st.sidebar.radio("메뉴 선택", ["📊 데이터 조회", "📝 실전 퀴즈", "📈 학습 현황", "💾 데이터 관리"]) # Add 데이터 관리

# ... (Existing Modes) ...

# --- Mode 4: Data Management ---
if mode == "💾 데이터 관리":
    st.title("데이터 관리 (백업/복원)")
    
    db = SessionLocal()
    try:
        st.subheader("1. 학습 현황 내보내기 (Export)")
        st.write("현재 저장된 한자/단어의 중요도 레벨 데이터를 CSV 파일로 다운로드합니다.")
        
        if st.button("데이터 로드"):
            progress_data = repository.get_flat_progress(db)
            if progress_data:
                df_export = pd.DataFrame(progress_data)
                csv = df_export.to_csv(index=False).encode('utf-8-sig') # BOM for Excel compatibility
                
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv,
                    file_name="hanja_progress_backup.csv",
                    mime="text/csv",
                )
                st.success(f"총 {len(progress_data)}개의 학습 기록을 찾았습니다.")
            else:
                st.warning("저장된 학습 기록이 없습니다.")

        st.divider()

        st.subheader("2. 학습 현황 불러오기 (Import)")
        st.write("백업된 CSV 파일을 업로드하여 중요도 레벨을 복원합니다.")
        
        uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                # Validate columns
                required_cols = {'type', 'target', 'importance_level'}
                if not required_cols.issubset(df_import.columns):
                    st.error(f"CSV 파일 형식이 올바르지 않습니다. 필요 컬럼: {required_cols}")
                else:
                    st.dataframe(df_import.head())
                    if st.button("🔄 데이터 적용하기"):
                        data_list = df_import.to_dict('records')
                        count = repository.import_progress_data(db, data_list)
                        st.success(f"성공적으로 {count}개의 항목을 업데이트했습니다!")
            except Exception as e:
                st.error(f"파일 처리 중 오류 발생: {e}")

    finally:
        db.close()
if mode == "📊 데이터 조회":
    st.title("기출 데이터 분석 및 조회")

    tab1, tab2, tab3 = st.tabs(["최빈출 한자", "최빈출 부수", "단어 형성 빈출자"])

    db = SessionLocal()
    try:
        with tab1:
            st.subheader("가장 많이 출제된 한자 TOP 100")
            data = get_top_hanja(page=1, size=100, db=db)
            df_data = []
            for item in data["items"]:
                h = item.hanja
                reading = h.readings[0] if h.readings else None
                meaning = f"{reading.meaning} {reading.sound}" if reading else ""
                df_data.append(
                    {
                        "순위": len(df_data) + 1,
                        "한자": h.char,
                        "훈음": meaning,
                        "빈도": item.frequency,
                        "부수": h.radical,
                        "획수": h.strokes,
                    }
                )
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

        with tab2:
            st.subheader("가장 많이 출제된 부수 TOP 50")
            data = get_top_radicals(page=1, size=50, db=db)
            df_data = []
            for item in data["items"]:
                df_data.append(
                    {
                        "순위": len(df_data) + 1,
                        "부수": item.radical,
                        "총 빈도": item.frequency,
                    }
                )
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

        with tab3:
            st.subheader("단어를 가장 많이 만드는 한자 TOP 100")
            data = get_top_hanja_in_words(page=1, size=100, db=db)
            df_data = []
            for item in data["items"]:
                hinfo = item.hanja_info
                reading = "?"
                if hinfo and hinfo.readings:
                    reading = f"{hinfo.readings[0].meaning} {hinfo.readings[0].sound}"

                df_data.append(
                    {
                        "순위": len(df_data) + 1,
                        "한자": item.char,
                        "훈음": reading,
                        "단어 내 빈도": item.frequency,
                    }
                )
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

    finally:
        db.close()

# --- Mode 2: Quiz ---
elif mode == "📝 실전 퀴즈":
    st.title("실전 객관식 퀴즈")

    # Quiz Settings (Sidebar)
    st.sidebar.divider()
    st.sidebar.subheader("퀴즈 설정")
    
    # Callback to reset quiz state when settings change
    def reset_quiz():
        st.session_state.quiz_state['q_data'] = None
        st.session_state.quiz_state['result'] = None

    quiz_mode = st.sidebar.selectbox(
        "학습 모드", 
        ["랜덤 출제 (중요도 가중치)", "부수별 학습", "단어 학습", "중요도별 복습"],
        on_change=reset_quiz
    )
    
    selected_radical = None
    min_importance_level = 0
    
    if quiz_mode == "부수별 학습":
        radicals = quiz_gen.get_all_radicals()
        selected_radical = st.sidebar.selectbox("부수 선택", radicals, on_change=reset_quiz)
    elif quiz_mode == "중요도별 복습":
        min_importance_level = st.sidebar.slider("최소 중요도 레벨", 0, 10, 1, on_change=reset_quiz)

    # Determine Question Type based on Mode
    if quiz_mode == "단어 학습" or (quiz_mode == "중요도별 복습" and 'q_type_options_word_context' in locals() and 'q_type_options_word_context' == "단어"):
        q_type_options = {"한자어 보고 음 고르기": "word_to_sound", "음 보고 한자어 고르기": "sound_to_word"}
        if quiz_mode == "중요도별 복습":
            q_type_options_word_context = st.sidebar.radio("복습 대상", ["한자", "단어"], on_change=reset_quiz)
            if q_type_options_word_context == "한자":
                 q_type_options = {"한자 보고 훈음 고르기": "hanja_to_meaning", "훈음 보고 한자 고르기": "meaning_to_hanja"}
            else:
                 q_type_options = {"한자어 보고 음 고르기": "word_to_sound", "음 보고 한자어 고르기": "sound_to_word"}

    else: # 랜덤 출제, 부수별 학습
        q_type_options = {"한자 보고 훈음 고르기": "hanja_to_meaning", "훈음 보고 한자 고르기": "meaning_to_hanja"}
    
    q_type_label = st.sidebar.radio("문제 유형", list(q_type_options.keys()), on_change=reset_quiz)
    q_type = q_type_options[q_type_label]

    # Initialize Session State
    if 'quiz_state' not in st.session_state:
        st.session_state.quiz_state = {
            'q_data': None,
            'score': 0,
            'total': 0,
            'result': None
        }

    def next_question():
        mode_key_map = {
            "랜덤 출제 (중요도 가중치)": 'random', 
            "부수별 학습": 'radical', 
            "단어 학습": 'word', 
            "중요도별 복습": 'importance_review'
        }
        actual_mode = mode_key_map.get(quiz_mode, 'random')

        q = quiz_gen.generate_quiz(mode=actual_mode, q_type=q_type, radical=selected_radical, min_importance_level=min_importance_level)
        
        if q:
            st.session_state.quiz_state['q_data'] = q
            st.session_state.quiz_state['result'] = None
        else:
            st.session_state.quiz_state['q_data'] = None # Clear data if gen fails
            st.error("문제를 생성할 수 없습니다. (데이터 부족 또는 조건에 맞는 항목 없음)")

    # Auto-load question if none exists (e.g., after settings change reset)
    if st.session_state.quiz_state['q_data'] is None:
         next_question() # Try to load immediately

    def check(ans):
        question = st.session_state.quiz_state["q_data"]
        correct = question["correct"]
        st.session_state.quiz_state["total"] += 1

        db = SessionLocal()
        try:
            if ans == correct:
                st.session_state.quiz_state["score"] += 1
                st.session_state.quiz_state["result"] = "correct"
                
                # Decrease importance level
                progress = repository.update_importance_level(
                    db,
                    hanja_id=question.get("hanja_id"),
                    word_id=question.get("word_id"),
                    change=-1,
                )
                db.commit()
                st.session_state.quiz_state["new_level"] = progress.importance_level

            else:
                st.session_state.quiz_state["result"] = "wrong"
                # Increase importance level
                progress = repository.update_importance_level(
                    db,
                    hanja_id=question.get("hanja_id"),
                    word_id=question.get("word_id"),
                    change=+1,
                )
                db.commit()
                st.session_state.quiz_state["new_level"] = progress.importance_level
        finally:
            db.close()

    # Main Quiz Area
    if st.session_state.quiz_state["q_data"] is None:
        st.info("💡 퀴즈 전략: 모든 단어는 기본 중요도 **Lv.5**로 시작합니다. 맞추면 **-1**, 틀리면 **+1** 됩니다. 중요도가 높을수록 더 자주 출제됩니다.")
        if st.button("퀴즈 시작하기", type="primary", use_container_width=True):
            next_question()
            st.rerun()
    else:
        q = st.session_state.quiz_state["q_data"]

        col1, col2, col3 = st.columns(3)
        col1.metric("맞춘 문제", st.session_state.quiz_state["score"])
        col2.metric("푼 문제", st.session_state.quiz_state["total"])
        if st.session_state.quiz_state["total"] > 0:
            acc = (st.session_state.quiz_state["score"] / st.session_state.quiz_state["total"]) * 100
            col3.metric("정답률", f"{acc:.1f}%")

        st.divider()

        st.markdown(f"<div style='text-align: center; font-size: 20px;'>다음은 무엇입니까?</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 80px; font-weight: bold; color: #333; margin: 20px 0;'>{q['q_text']}</div>", unsafe_allow_html=True)

        if q.get("info"):
            st.info(f"💡 힌트: {q['info']}")

        if st.session_state.quiz_state["result"] is None:
            cols = st.columns(2)
            for i, opt in enumerate(q["options"]):
                if cols[i % 2].button(opt, key=f"opt_{i}", use_container_width=True):
                    check(opt)
                    st.rerun()
        else:
            new_lv = st.session_state.quiz_state.get("new_level", "?")
            if st.session_state.quiz_state["result"] == "correct":
                st.success(f"⭕ 정답입니다! 🎉 ({q['correct']})")
                st.caption(f"📉 중요도 감소! 현재 레벨: **Lv.{new_lv}**")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{q['correct']}** 입니다.")
                st.caption(f"📈 중요도 증가! 현재 레벨: **Lv.{new_lv}**")
            
            if st.button("다음 문제 👉", type="primary", use_container_width=True):
                next_question()
                st.rerun()

# --- Mode 3: User Progress ---
elif mode == "📈 학습 현황":
    st.title("학습 현황")

    db = SessionLocal()
    try:
        st.markdown("### 중요도 분포")
        # ... (Chart logic could be added here)

        st.subheader("학습 중인 한자 (Lv.1 이상)")
        hanja_progress = (
            db.query(UserProgress)
            .filter(UserProgress.hanja_id != None)
            .order_by(
                UserProgress.importance_level.desc(), UserProgress.last_tested_at.asc()
            )
            .all()
        )

        if hanja_progress:
            df_hanja_progress = []
            for up in hanja_progress:
                hanja = up.hanja
                reading = hanja.readings[0] if hanja and hanja.readings else None
                meaning_sound = (f"{reading.meaning} {reading.sound}" if reading else "정보 없음")
                df_hanja_progress.append({
                    "한자": hanja.char if hanja else "없음",
                    "훈음": meaning_sound,
                    "부수": hanja.radical if hanja else "없음",
                    "중요도 레벨": up.importance_level,
                    "상태": "🔥 집중 학습" if up.importance_level > 5 else ("✅ 안정" if up.importance_level < 3 else "⚠️ 보통"),
                    "마지막 학습일": up.last_tested_at.strftime("%Y-%m-%d %H:%M"),
                })
            st.dataframe(pd.DataFrame(df_hanja_progress), use_container_width=True)
        else:
            st.info("아직 학습 기록이 없습니다. 퀴즈를 풀어보세요!")

        st.divider()

        st.subheader("학습 중인 단어 (Lv.1 이상)")
        word_progress = (
            db.query(UserProgress)
            .filter(UserProgress.word_id != None)
            .order_by(
                UserProgress.importance_level.desc(), UserProgress.last_tested_at.asc()
            )
            .all()
        )

        if word_progress:
            df_word_progress = []
            for up in word_progress:
                word = up.word
                df_word_progress.append({
                    "단어": word.word if word else "없음",
                    "음": word.sound if word else "없음",
                    "중요도 레벨": up.importance_level,
                    "상태": "🔥 집중 학습" if up.importance_level > 5 else ("✅ 안정" if up.importance_level < 3 else "⚠️ 보통"),
                    "마지막 학습일": up.last_tested_at.strftime("%Y-%m-%d %H:%M"),
                })
            st.dataframe(pd.DataFrame(df_word_progress), use_container_width=True)
        else:
            st.info("아직 학습 기록이 없습니다. 퀴즈를 풀어보세요!")

    finally:
        db.close()