import streamlit as st
import pandas as pd
from src.models import init_db
from src.quiz import QuizGenerator
from src.api import get_top_hanja, get_top_radicals, get_top_hanja_in_words

# Initialize DB & Quiz Generator
SessionLocal = init_db()
quiz_gen = QuizGenerator(SessionLocal)

st.set_page_config(page_title="Hanja Master", layout="wide", initial_sidebar_state="expanded")

# --- Sidebar Navigation ---
st.sidebar.title("📚 Hanja Master")
mode = st.sidebar.radio("메뉴 선택", ["📊 데이터 조회", "📝 실전 퀴즈"])

# --- Mode 1: Analysis ---
if mode == "📊 데이터 조회":
    st.title("기출 데이터 분석 및 조회")
    
    tab1, tab2, tab3 = st.tabs(["최빈출 한자", "최빈출 부수", "단어 형성 빈출자"])
    
    db = SessionLocal()
    try:
        with tab1:
            st.subheader("가장 많이 출제된 한자 TOP 100")
            data = get_top_hanja(page=1, size=100, db=db)
            df_data = []
            for item in data['items']:
                h = item.hanja
                reading = h.readings[0] if h.readings else None
                meaning = f"{reading.meaning} {reading.sound}" if reading else ""
                df_data.append({
                    "순위": len(df_data) + 1,
                    "한자": h.char,
                    "훈음": meaning,
                    "빈도": item.frequency,
                    "부수": h.radical,
                    "획수": h.strokes
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

        with tab2:
            st.subheader("가장 많이 출제된 부수 TOP 50")
            data = get_top_radicals(page=1, size=50, db=db)
            df_data = []
            for item in data['items']:
                df_data.append({
                    "순위": len(df_data) + 1,
                    "부수": item.radical,
                    "총 빈도": item.frequency
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)

        with tab3:
            st.subheader("단어를 가장 많이 만드는 한자 TOP 100")
            data = get_top_hanja_in_words(page=1, size=100, db=db)
            df_data = []
            for item in data['items']:
                h = item.hanja_info
                reading = "?"
                if h and h.readings:
                    reading = f"{h.readings[0].meaning} {h.readings[0].sound}"
                
                df_data.append({
                    "순위": len(df_data) + 1,
                    "한자": item.char,
                    "훈음": reading,
                    "단어 내 빈도": item.frequency
                })
            st.dataframe(pd.DataFrame(df_data), use_container_width=True)
            
    finally:
        db.close()

# --- Mode 2: Quiz ---
elif mode == "📝 실전 퀴즈":
    st.title("실전 객관식 퀴즈")

    # Quiz Settings (Sidebar)
    st.sidebar.divider()
    st.sidebar.subheader("퀴즈 설정")
    
    quiz_mode = st.sidebar.selectbox("학습 모드", ["랜덤 출제 (빈도순)", "부수별 학습", "단어 학습"])
    
    selected_radical = None
    if quiz_mode == "부수별 학습":
        radicals = quiz_gen.get_all_radicals()
        selected_radical = st.sidebar.selectbox("부수 선택", radicals)

    # Determine Question Type based on Mode
    if quiz_mode == "단어 학습":
        q_type_options = {"한자어 보고 음 고르기": "word_to_sound", "음 보고 한자어 고르기": "sound_to_word"}
    else:
        q_type_options = {"한자 보고 훈음 고르기": "hanja_to_meaning", "훈음 보고 한자 고르기": "meaning_to_hanja"}
    
    q_type_label = st.sidebar.radio("문제 유형", list(q_type_options.keys()))
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
        mode_key = 'word' if quiz_mode == "단어 학습" else ('radical' if quiz_mode == "부수별 학습" else 'random')
        q = quiz_gen.generate_quiz(mode=mode_key, q_type=q_type, radical=selected_radical)
        
        if q:
            st.session_state.quiz_state['q_data'] = q
            st.session_state.quiz_state['result'] = None
        else:
            st.error("문제를 생성할 수 없습니다. (데이터 부족)")

    def check(ans):
        correct = st.session_state.quiz_state['q_data']['correct']
        st.session_state.quiz_state['total'] += 1
        if ans == correct:
            st.session_state.quiz_state['score'] += 1
            st.session_state.quiz_state['result'] = 'correct'
        else:
            st.session_state.quiz_state['result'] = 'wrong'

    # Main Quiz Area
    if st.session_state.quiz_state['q_data'] is None:
        if st.button("퀴즈 시작하기", type="primary", use_container_width=True):
            next_question()
            st.rerun()
    else:
        q = st.session_state.quiz_state['q_data']
        
        # Score Board
        col1, col2, col3 = st.columns(3)
        col1.metric("맞춘 문제", st.session_state.quiz_state['score'])
        col2.metric("푼 문제", st.session_state.quiz_state['total'])
        if st.session_state.quiz_state['total'] > 0:
            acc = (st.session_state.quiz_state['score'] / st.session_state.quiz_state['total']) * 100
            col3.metric("정답률", f"{acc:.1f}%")

        st.divider()

        # Question Display
        st.markdown(f"<div style='text-align: center; font-size: 20px;'>다음은 무엇입니까?</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 80px; font-weight: bold; color: #333; margin: 20px 0;'>{q['q_text']}</div>", unsafe_allow_html=True)
        
        if q.get('info'):
            st.info(f"💡 힌트: {q['info']}")

        # Options
        if st.session_state.quiz_state['result'] is None:
            cols = st.columns(2)
            for i, opt in enumerate(q['options']):
                if cols[i % 2].button(opt, key=f"opt_{i}", use_container_width=True):
                    check(opt)
                    st.rerun()
        else:
            # Result Display
            if st.session_state.quiz_state['result'] == 'correct':
                st.success(f"⭕ 정답입니다! ({q['correct']})")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 **{q['correct']}** 입니다.")
            
            if st.button("다음 문제 👉", type="primary", use_container_width=True):
                next_question()
                st.rerun()