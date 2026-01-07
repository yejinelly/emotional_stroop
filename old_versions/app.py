import streamlit as st
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import random

# 페이지 설정
st.set_page_config(
    page_title="Emotional Word Stroop Task",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Session state 초기화
if 'task_started' not in st.session_state:
    st.session_state.task_started = False
    st.session_state.instructions_shown = False
    st.session_state.trial_num = 0
    st.session_state.responses = []
    st.session_state.trials = None
    st.session_state.start_time = None
    st.session_state.participant_id = None
    st.session_state.age = None
    st.session_state.gender = None
    st.session_state.task_completed = False


def generate_trials():
    """Trial 생성 함수 - 단어와 색상 조합"""
    words_df = pd.read_csv("stimuli/word_list.csv")
    colors_df = pd.read_csv("stimuli/colors.csv")

    trials = []
    for _, word_row in words_df.iterrows():
        for _, color_row in colors_df.iterrows():
            trials.append({
                'word': word_row['word_ko'],
                'valence': word_row['valence'],
                'color_name': color_row['color_name'],
                'color_hex': color_row['hex_code'],
                'correct_answer': color_row['color_name']
            })

    # 랜덤 셔플
    random.shuffle(trials)
    return pd.DataFrame(trials)


def record_response(trial, response):
    """반응 기록 함수"""
    rt = time.time() - st.session_state.start_time
    accuracy = 1 if response == trial['correct_answer'] else 0

    st.session_state.responses.append({
        'trial_num': st.session_state.trial_num + 1,
        'participant_id': st.session_state.participant_id,
        'word': trial['word'],
        'valence': trial['valence'],
        'color': trial['color_name'],
        'response': response,
        'accuracy': accuracy,
        'rt': rt,
        'timestamp': datetime.now().isoformat()
    })

    # 다음 trial로 이동
    st.session_state.trial_num += 1
    st.session_state.start_time = None

    # 모든 trial 완료 확인
    if st.session_state.trial_num >= len(st.session_state.trials):
        st.session_state.task_completed = True

    st.rerun()


def save_data():
    """데이터 저장 함수"""
    if len(st.session_state.responses) > 0:
        df = pd.DataFrame(st.session_state.responses)

        # data/responses 폴더 생성
        output_dir = Path("data/responses")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 파일명: participant_id_timestamp.csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"{st.session_state.participant_id}_{timestamp}.csv"

        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    return None


# ========== 메인 앱 로직 ==========

# 1. 참가자 정보 입력 화면
if not st.session_state.task_started:
    st.title("🧠 Emotional Word Stroop Task")
    st.markdown("### 참가자 정보")

    participant_id = st.text_input("참가자 ID:", placeholder="예: P001")
    age = st.number_input("연령:", min_value=18, max_value=100, value=25)
    gender = st.selectbox("성별:", ["선택 안 함", "남성", "여성", "기타"])

    if st.button("과제 시작", type="primary"):
        if participant_id:
            st.session_state.participant_id = participant_id
            st.session_state.age = age
            st.session_state.gender = gender if gender != "선택 안 함" else None
            st.session_state.task_started = True
            # Trial 생성
            st.session_state.trials = generate_trials()
            st.rerun()
        else:
            st.error("참가자 ID를 입력해주세요.")

    st.stop()


# 2. Instructions 화면
if not st.session_state.instructions_shown:
    st.title("📋 과제 안내")

    st.markdown("""
    ### 지시사항

    1. 화면에 **색깔로 표시된 단어**가 나타납니다.
    2. **단어의 의미는 무시**하고, **글자의 색깔만** 판단해주세요.
    3. 아래 버튼을 눌러 색깔을 선택하세요:
       - 🔴 **빨강**
       - 🔵 **파랑**
       - 🟢 **초록**
    4. 최대한 **빠르고 정확하게** 반응해주세요.
    5. 총 **{0}번**의 시행이 진행됩니다.

    준비가 되면 아래 버튼을 눌러주세요.
    """.format(len(st.session_state.trials)))

    if st.button("시작하기", type="primary"):
        st.session_state.instructions_shown = True
        st.rerun()

    st.stop()


# 3. Task 완료 화면
if st.session_state.task_completed:
    st.title("✅ 과제 완료!")
    st.success("모든 시행을 완료했습니다. 감사합니다!")

    # 데이터 저장
    saved_file = save_data()
    if saved_file:
        st.info(f"데이터가 저장되었습니다: {saved_file}")

    # 기술통계 표시
    if len(st.session_state.responses) > 0:
        df_responses = pd.DataFrame(st.session_state.responses)

        st.markdown("### 📊 수행 결과")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("전체 정확도", f"{df_responses['accuracy'].mean():.1%}")
        with col2:
            st.metric("평균 반응시간", f"{df_responses['rt'].mean():.2f}초")

        # 정서가별 성적
        st.markdown("### 정서가별 정확도")
        valence_acc = df_responses.groupby('valence')['accuracy'].mean()
        st.bar_chart(valence_acc)

        # 다운로드 버튼
        csv = df_responses.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 데이터 다운로드 (CSV)",
            data=csv,
            file_name=f"stroop_{st.session_state.participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    st.stop()


# 4. Task 화면 (Trial 진행)
if st.session_state.trial_num < len(st.session_state.trials):
    trial = st.session_state.trials.iloc[st.session_state.trial_num]

    # Progress bar
    progress = (st.session_state.trial_num + 1) / len(st.session_state.trials)
    st.progress(progress)
    st.caption(f"Trial {st.session_state.trial_num + 1} / {len(st.session_state.trials)}")

    # 여백 추가
    st.markdown("<br>" * 3, unsafe_allow_html=True)

    # 자극 제시 (단어를 색상으로 표시)
    st.markdown(
        f'<div style="text-align:center;"><h1 style="color:{trial["color_hex"]}; font-size:80px; font-weight:bold;">{trial["word"]}</h1></div>',
        unsafe_allow_html=True
    )

    # 반응시간 측정 시작 (첫 렌더링 시)
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    # 여백 추가
    st.markdown("<br>" * 2, unsafe_allow_html=True)

    # 반응 버튼 (3개 색상)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 빨강", key=f"red_{st.session_state.trial_num}", use_container_width=True):
            record_response(trial, "red")

    with col2:
        if st.button("🔵 파랑", key=f"blue_{st.session_state.trial_num}", use_container_width=True):
            record_response(trial, "blue")

    with col3:
        if st.button("🟢 초록", key=f"green_{st.session_state.trial_num}", use_container_width=True):
            record_response(trial, "green")

else:
    # 만약 여기 도달하면 task_completed를 True로 설정
    st.session_state.task_completed = True
    st.rerun()
