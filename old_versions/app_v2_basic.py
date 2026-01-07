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
    st.session_state.practice_completed = False
    st.session_state.instructions_exp_shown = False
    st.session_state.trial_num = 0
    st.session_state.practice_trial_num = 0
    st.session_state.responses = []
    st.session_state.practice_responses = []
    st.session_state.practice_trials = None
    st.session_state.exp_trials = None
    st.session_state.start_time = None
    st.session_state.participant_id = None
    st.session_state.age = None
    st.session_state.gender = None
    st.session_state.task_completed = False
    st.session_state.show_fixation = False
    st.session_state.last_response_correct = None


def load_practice_trials():
    """Practice trials 로드 - 24 trials (6 base trials × 4 blocks)"""
    base_trials = pd.read_csv("stimuli/practice_trials_korean.csv")

    # 4 blocks 생성
    all_trials = []
    for _ in range(4):
        block = base_trials.copy()
        block = block.sample(frac=1).reset_index(drop=True)  # Shuffle
        all_trials.append(block)

    trials = pd.concat(all_trials, ignore_index=True)
    return trials


def load_exp_trials():
    """Experimental trials 로드 - 144 trials from CSV"""
    trials = pd.read_csv("stimuli/exp_trials_korean.csv")

    # GitHub 원본은 block shuffling만 함 (within-block order 유지)
    # 여기서는 전체 shuffle (단순화)
    # 나중에 16 blocks로 나누고 block order만 shuffle 가능
    trials = trials.sample(frac=1).reset_index(drop=True)
    return trials


def record_response(trial, response, is_practice=False):
    """반응 기록 함수"""
    rt = time.time() - st.session_state.start_time

    # letterColor와 corrAns는 같은 값
    correct_answer = trial.get('corrAns', trial.get('letterColor'))
    accuracy = 1 if response == correct_answer else 0

    response_data = {
        'trial_num': (st.session_state.practice_trial_num if is_practice else st.session_state.trial_num) + 1,
        'participant_id': st.session_state.participant_id,
        'word': trial['text'],
        'condition': trial.get('condition', 'practice'),
        'color': trial['letterColor'],
        'response': response,
        'accuracy': accuracy,
        'rt': rt,
        'timestamp': datetime.now().isoformat(),
        'phase': 'practice' if is_practice else 'experimental'
    }

    if is_practice:
        st.session_state.practice_responses.append(response_data)
        st.session_state.last_response_correct = accuracy
        st.session_state.practice_trial_num += 1
    else:
        st.session_state.responses.append(response_data)
        st.session_state.trial_num += 1

    st.session_state.start_time = None

    # 완료 체크
    if not is_practice and st.session_state.trial_num >= len(st.session_state.exp_trials):
        st.session_state.task_completed = True

    st.rerun()


def save_data():
    """데이터 저장 함수"""
    if len(st.session_state.responses) > 0:
        # Practice + Experimental 데이터 합치기
        all_responses = st.session_state.practice_responses + st.session_state.responses
        df = pd.DataFrame(all_responses)

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
            # Practice trials 로드
            st.session_state.practice_trials = load_practice_trials()
            st.rerun()
        else:
            st.error("참가자 ID를 입력해주세요.")

    st.stop()


# 2. Practice Instructions
if not st.session_state.practice_completed:
    if st.session_state.practice_trial_num == 0:
        st.title("📋 연습 과제 안내")
        st.markdown("""
        ### 지시사항

        1. 화면에 **색깔로 표시된 단어**가 나타납니다.
        2. **단어의 의미는 무시**하고, **글자의 색깔만** 판단해주세요.
        3. 아래 버튼을 눌러 색깔을 선택하세요:
           - 🔴 **빨강**
           - 🔵 **파랑**
           - 🟢 **초록**
        4. 최대한 **빠르고 정확하게** 반응해주세요.

        먼저 **연습 시행 24번**을 진행합니다. 정답/오답 피드백이 제공됩니다.

        준비가 되면 아래 버튼을 눌러주세요.
        """)

        if st.button("연습 시작", type="primary"):
            st.rerun()

        st.stop()

    # Practice Trial 진행
    if st.session_state.practice_trial_num < len(st.session_state.practice_trials):
        trial = st.session_state.practice_trials.iloc[st.session_state.practice_trial_num]

        # Progress bar
        progress = (st.session_state.practice_trial_num + 1) / len(st.session_state.practice_trials)
        st.progress(progress)
        st.caption(f"연습 {st.session_state.practice_trial_num + 1} / {len(st.session_state.practice_trials)}")

        # Fixation cross (간단히 표시)
        st.markdown("<br>" * 2, unsafe_allow_html=True)

        # 피드백 표시 (이전 trial)
        if st.session_state.last_response_correct is not None:
            if st.session_state.last_response_correct == 1:
                st.success("✅ 정답!")
            else:
                st.error("❌ 오답")
            st.markdown("<br>", unsafe_allow_html=True)

        # 자극 제시
        color_hex_map = {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}
        st.markdown(
            f'<div style="text-align:center;"><h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold;">{trial["text"]}</h1></div>',
            unsafe_allow_html=True
        )

        # 반응시간 측정 시작
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        st.markdown("<br>", unsafe_allow_html=True)

        # 반응 버튼
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔴 빨강", key=f"practice_red_{st.session_state.practice_trial_num}", use_container_width=True):
                record_response(trial, "red", is_practice=True)

        with col2:
            if st.button("🔵 파랑", key=f"practice_blue_{st.session_state.practice_trial_num}", use_container_width=True):
                record_response(trial, "blue", is_practice=True)

        with col3:
            if st.button("🟢 초록", key=f"practice_green_{st.session_state.practice_trial_num}", use_container_width=True):
                record_response(trial, "green", is_practice=True)

    else:
        # Practice 완료
        st.session_state.practice_completed = True
        st.session_state.last_response_correct = None  # 초기화
        st.rerun()

    st.stop()


# 3. Experimental Instructions
if not st.session_state.instructions_exp_shown:
    st.title("📋 본 과제 안내")
    st.markdown("""
    ### 연습이 끝났습니다!

    이제 **본 과제 144번**을 진행합니다.

    - 과제 중간에 **3번의 휴식** 기회가 있습니다.
    - **정답/오답 피드백은 제공되지 않습니다.**
    - 앞의 연습과 동일하게, **글자의 색깔만** 판단해주세요.

    준비가 되면 아래 버튼을 눌러주세요.
    """)

    if st.button("본 과제 시작", type="primary"):
        st.session_state.instructions_exp_shown = True
        # Experimental trials 로드
        st.session_state.exp_trials = load_exp_trials()
        st.rerun()

    st.stop()


# 4. Task 완료 화면
if st.session_state.task_completed:
    st.title("✅ 과제 완료!")
    st.success("모든 시행을 완료했습니다. 감사합니다!")

    # 데이터 저장
    saved_file = save_data()
    if saved_file:
        st.info(f"데이터가 저장되었습니다: {saved_file}")

    # 기술통계 표시 (Experimental만)
    if len(st.session_state.responses) > 0:
        df_responses = pd.DataFrame(st.session_state.responses)

        st.markdown("### 📊 수행 결과 (본 과제)")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("전체 정확도", f"{df_responses['accuracy'].mean():.1%}")
        with col2:
            st.metric("평균 반응시간", f"{df_responses['rt'].mean():.2f}초")

        # 정서가별 정확도
        st.markdown("### 정서가별 정확도")
        valence_acc = df_responses.groupby('condition')['accuracy'].mean()
        st.bar_chart(valence_acc)

        # 다운로드 버튼
        all_responses = st.session_state.practice_responses + st.session_state.responses
        csv = pd.DataFrame(all_responses).to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 데이터 다운로드 (CSV)",
            data=csv,
            file_name=f"stroop_{st.session_state.participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    st.stop()


# 5. Experimental Trials 진행
if st.session_state.trial_num < len(st.session_state.exp_trials):
    trial = st.session_state.exp_trials.iloc[st.session_state.trial_num]

    # Rest break 체크 (36 trials마다 = trial_num 36, 72, 108)
    if st.session_state.trial_num > 0 and st.session_state.trial_num % 36 == 0:
        st.title("☕ 휴식 시간")
        st.markdown(f"""
        ### {st.session_state.trial_num}번 완료!

        잠시 휴식하세요.

        준비가 되면 계속 진행합니다.
        """)

        if st.button("계속하기", type="primary"):
            st.rerun()

        st.stop()

    # Progress bar
    progress = (st.session_state.trial_num + 1) / len(st.session_state.exp_trials)
    st.progress(progress)
    st.caption(f"Trial {st.session_state.trial_num + 1} / {len(st.session_state.exp_trials)}")

    st.markdown("<br>" * 2, unsafe_allow_html=True)

    # 자극 제시
    color_hex_map = {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}
    st.markdown(
        f'<div style="text-align:center;"><h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold;">{trial["text"]}</h1></div>',
        unsafe_allow_html=True
    )

    # 반응시간 측정 시작
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.markdown("<br>", unsafe_allow_html=True)

    # 반응 버튼
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
    st.session_state.task_completed = True
    st.rerun()
