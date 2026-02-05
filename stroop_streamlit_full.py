import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import random

# ========== Timing 상수 ==========
MAX_RESPONSE_TIME = 3.0  # 최대 응답 시간 (초)
ITI_MIN = 0.8  # ITI 최소 (초)
ITI_MAX = 1.2  # ITI 최대 (초)
FIXATION_DURATION = 0.5  # Fixation 지속 시간 (초)
BREAK_MIN = 30  # 휴식 최소 시간 (초)
BREAK_MAX = 120  # 휴식 최대 시간 (초)

# ========== Block 구조 ==========
TRIALS_PER_BLOCK_FULL = 36   # full: 블록당 36 시행 (4블록)
TRIALS_PER_BLOCK_PILOT = 15  # pilot: 블록당 15 시행 (2블록)

# ========== 실험 모드 설정 ==========
# URL 파라미터로 모드 전환: ?mode=pilot (30 trials) 또는 ?mode=full (144 trials)
# 예: https://emo-stroop-101.streamlit.app/?mode=pilot
N_PER_CONDITION_PILOT = 10  # pilot: 조건당 10개 = 30 trials
N_PER_CONDITION_FULL = 48   # full: 조건당 48개 = 144 trials

# Google Sheets 백업용
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# 클라이언트 사이드 RT 측정용
try:
    from streamlit_javascript import st_javascript
    ST_JAVASCRIPT_AVAILABLE = True
except ImportError:
    ST_JAVASCRIPT_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="Emotional Word Stroop Task",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 추가 (GitHub 원본 스타일 재현: 검정 배경, 버튼 없음)
st.markdown("""
<style>
    /* 전체 배경 검정색 */
    .stApp, .main, body {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    /* Streamlit UI 숨기기 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Deploy 버튼과 메뉴 숨기기 */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .stDeployButton {display: none !important;}
    button[kind="header"] {display: none !important;}

    /* Progress bar 숨기기 */
    .stProgress {display: none !important;}

    /* Caption (trial 번호) 숨기기 */
    .stCaptionContainer {display: none !important;}

    /* 반응 버튼 숨기기 (columns 안의 버튼) - 키보드로만 반응 */
    .stColumn button {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        opacity: 0.01 !important;
        width: 1px !important;
        height: 1px !important;
        overflow: hidden !important;
        pointer-events: auto !important;
        z-index: -1 !important;
    }

    /* 일반 버튼들 스타일 (시작, 다운로드 등) - 모든 일반 버튼 */
    button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FFFFFF !important;
        visibility: visible !important;
    }

    button *,
    button p,
    button div,
    button span,
    button::before,
    button::after {
        color: #000000 !important;
    }

    /* 버튼 내부 모든 요소 검은색 */
    .stButton button,
    .stButton button *,
    .stButton button p,
    .stButton button div {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    /* Download 버튼 */
    .stDownloadButton button {
        background-color: #4CAF50 !important;
        color: #FFFFFF !important;
    }

    /* Input 필드 */
    input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Text input label */
    label {
        color: #FFFFFF !important;
    }

    /* Fixation cross - 흰색, 화면 중앙 고정 */
    .fixation-cross {
        color: #FFFFFF;
        font-size: 80px;
        text-align: center;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        animation: fadeOut 0.5s ease-in-out forwards;
        z-index: 1000;
    }

    /* Stimulus word - 화면 중앙 고정 (fixation 후 나타남) */
    .stimulus-container {
        text-align: center;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        animation: fadeIn 0.5s ease-in-out 0.5s forwards;
        opacity: 0;
        z-index: 1000;
    }

    /* Stimulus word - fixation 없이 바로 나타남 */
    .stimulus-container-immediate {
        text-align: center;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        animation: fadeInImmediate 0.3s ease-in-out forwards;
        opacity: 0;
        z-index: 1000;
    }

    @keyframes fadeOut {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }

    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    @keyframes fadeInImmediate {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    /* 연습 시행 피드백: 0.8초 보이고 나서 fadeOut */
    @keyframes feedbackShow {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; }
    }

    /* 연습 시행 자극: 피드백 후 (1초 뒤) fadeIn */
    @keyframes stimulusAfterFeedback {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    .practice-feedback {
        position: fixed;
        top: 50px;
        left: 50%;
        transform: translateX(-50%);
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 24px;
        font-weight: bold;
        z-index: 999;
        animation: feedbackShow 1s ease-in-out forwards;
    }

    .practice-feedback-correct {
        background-color: rgba(76, 175, 80, 0.2);
        border: 2px solid #4CAF50;
        color: #4CAF50;
    }

    .practice-feedback-incorrect {
        background-color: rgba(244, 67, 54, 0.2);
        border: 2px solid #f44336;
        color: #f44336;
    }

    .practice-feedback-timeout {
        background-color: rgba(255, 165, 0, 0.2);
        border: 2px solid #FFA500;
        color: #FFA500;
    }

    /* 피드백 후 자극 표시 (1초 delay) */
    .stimulus-after-feedback {
        text-align: center;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        animation: stimulusAfterFeedback 0.3s ease-in-out 1s forwards;
        opacity: 0;
        z-index: 1000;
    }

    /* 지시사항 텍스트 흰색 */
    .element-container p, li {
        color: #FFFFFF !important;
    }

    /* 제목들은 흰색 (일반 텍스트만) */
    .stApp h2,
    .stApp h3 {
        color: #FFFFFF !important;
    }

    /* Title 텍스트 흰색 */
    .stTitle {
        color: #FFFFFF !important;
    }

    /* Success/Error 메시지 - 화면 상단에 고정 */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        position: fixed !important;
        top: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 999 !important;
        width: auto !important;
        max-width: 400px !important;
    }

    .stAlert p, .stAlert div {
        color: #FFFFFF !important;
    }

    /* Success 메시지 (정답) - 초록 테두리 */
    .stSuccess {
        border-color: #4CAF50 !important;
    }

    /* Error 메시지 (오답) - 빨강 테두리 */
    .stError {
        border-color: #f44336 !important;
    }

    /* Info 메시지 */
    .stInfo {
        background-color: rgba(33, 150, 243, 0.1) !important;
        color: #FFFFFF !important;
        border: 2px solid #2196F3 !important;
    }

    .stInfo p, .stInfo div {
        color: #FFFFFF !important;
    }

    /* 지시사항 버튼 중앙 정렬 (columns 밖에 있는 버튼) */
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* stButton 내부 버튼도 중앙 */
    div[data-testid="stButton"] > button {
        margin: 0 auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state 초기화 (개별 체크 - 기존 세션에서도 작동)
if 'task_started' not in st.session_state:
    st.session_state.task_started = False
if 'practice_completed' not in st.session_state:
    st.session_state.practice_completed = False
if 'instructions_exp_shown' not in st.session_state:
    st.session_state.instructions_exp_shown = False
if 'practice_instructions_shown' not in st.session_state:
    st.session_state.practice_instructions_shown = False
if 'instruction_page' not in st.session_state:
    st.session_state.instruction_page = 0
if 'exp_instruction_page' not in st.session_state:
    st.session_state.exp_instruction_page = 0
if 'trial_num' not in st.session_state:
    st.session_state.trial_num = 0
if 'practice_trial_num' not in st.session_state:
    st.session_state.practice_trial_num = 0
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'practice_responses' not in st.session_state:
    st.session_state.practice_responses = []
if 'practice_trials' not in st.session_state:
    st.session_state.practice_trials = None
if 'exp_trials' not in st.session_state:
    st.session_state.exp_trials = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'participant_id' not in st.session_state:
    st.session_state.participant_id = None
if 'task_completed' not in st.session_state:
    st.session_state.task_completed = False
if 'last_response_correct' not in st.session_state:
    st.session_state.last_response_correct = None
if 'pending_client_rt' not in st.session_state:
    st.session_state.pending_client_rt = None
if 'showing_iti' not in st.session_state:
    st.session_state.showing_iti = False
if 'iti_start_time' not in st.session_state:
    st.session_state.iti_start_time = None
if 'current_iti_duration' not in st.session_state:
    st.session_state.current_iti_duration = None
if 'last_was_timeout' not in st.session_state:
    st.session_state.last_was_timeout = False
if 'showing_break' not in st.session_state:
    st.session_state.showing_break = False
if 'breaks_shown' not in st.session_state:
    st.session_state.breaks_shown = set()  # 이미 휴식 화면을 보여준 블록 번호
if 'break_start_time' not in st.session_state:
    st.session_state.break_start_time = None  # 휴식 시작 시간
if 'show_block_key_reminder' not in st.session_state:
    st.session_state.show_block_key_reminder = False  # 블록 시작 전 키 안내 표시
if 'experiment_start_time' not in st.session_state:
    st.session_state.experiment_start_time = None  # 본 시행 시작 시간
if 'showing_practice_redo' not in st.session_state:
    st.session_state.showing_practice_redo = False
if 'practice_attempt' not in st.session_state:
    st.session_state.practice_attempt = 1  # 연습 시도 횟수

# 실험 모드 감지 (URL 파라미터)
if 'experiment_mode' not in st.session_state:
    mode_param = st.query_params.get("mode", "full")
    st.session_state.experiment_mode = mode_param if mode_param in ["pilot", "full"] else "full"

# 모드에 따른 trial 수 설정
if st.session_state.experiment_mode == "pilot":
    N_PER_CONDITION = N_PER_CONDITION_PILOT  # 10 → 30 trials
    TOTAL_TRIALS = N_PER_CONDITION * 3  # 30
else:
    N_PER_CONDITION = N_PER_CONDITION_FULL  # 48 → 144 trials
    TOTAL_TRIALS = N_PER_CONDITION * 3  # 144


def read_client_rt():
    """localStorage에서 클라이언트 사이드 RT를 읽고 클리어"""
    if not ST_JAVASCRIPT_AVAILABLE:
        return None

    try:
        # localStorage에서 RT 읽고 바로 삭제 (atomic operation)
        rt_str = st_javascript("""
            (function() {
                const rt = localStorage.getItem('stroopClientRT');
                if (rt !== null) {
                    localStorage.removeItem('stroopClientRT');
                    return rt;
                }
                return null;
            })()
        """)

        if rt_str is not None and rt_str != "null" and rt_str != 0:
            return float(rt_str)
    except Exception:
        pass
    return None


def create_practice_trials():
    """Practice trials 생성 - final_practice_words.csv에서 neutral 단어 사용

    각 단어를 빨강/초록으로 무작위 배정하여 연습 시행 생성
    """
    # final_practice_words.csv에서 연습 단어 로드
    practice_path = Path("stimuli/final_practice_words.csv")
    df = pd.read_csv(practice_path)

    colors = ['red', 'green']
    trials = []

    for _, row in df.iterrows():
        color = random.choice(colors)
        trials.append({
            'text': row['word'],
            'letterColor': color,
            'corrAns': color,
            'condition': 'practice'
        })

    # 전체 무선화
    random.shuffle(trials)
    return pd.DataFrame(trials)


def create_exp_trials(n_per_condition=10):
    """Experimental trials 생성 - final_144_words.csv에서 조건별 n개씩 선택

    Args:
        n_per_condition: 조건별 단어 수 (기본 10 = pilot, 최대 48 = full)
    """

    # final_144_words.csv에서 단어 로드
    stimuli_path = Path("stimuli/final_144_words.csv")
    df = pd.read_csv(stimuli_path)

    colors = ['red', 'green']

    trials = []
    # 조건별로 n개씩 랜덤 샘플링
    for condition in ['positive', 'negative', 'neutral']:
        cond_words = df[df['category'] == condition].sample(n=n_per_condition)
        for _, row in cond_words.iterrows():
            color = random.choice(colors)
            trials.append({
                'text': row['word'],
                'letterColor': color,
                'corrAns': color,
                'condition': row['category']
            })

    # 전체 무선화
    random.shuffle(trials)
    return pd.DataFrame(trials)


def record_response(trial, response, is_practice=False, client_rt=None, is_timeout=False):
    """반응 기록 함수

    Args:
        trial: 현재 trial 정보
        response: 참가자 반응 ('red', 'green', 'timeout')
        is_practice: 연습 시행 여부
        client_rt: 클라이언트 사이드에서 측정된 RT (ms) - 우선 사용
        is_timeout: timeout 여부
    """
    # Timeout 처리
    if is_timeout:
        rt = MAX_RESPONSE_TIME
        rt_source = 'timeout'
        response = 'timeout'
        accuracy = 0
        st.session_state.last_was_timeout = True
    else:
        # RT 결정: 클라이언트 RT 우선, 없으면 서버 RT 사용
        if client_rt is not None and client_rt > 0:
            rt = client_rt / 1000  # ms -> seconds
            rt_source = 'client'
        else:
            rt = time.time() - st.session_state.start_time
            rt_source = 'server'

        correct_answer = trial.get('corrAns', trial.get('letterColor'))
        accuracy = 1 if response == correct_answer else 0
        st.session_state.last_was_timeout = False

    response_data = {
        'participant_id': st.session_state.participant_id,
        'word': trial['text'],
        'condition': trial.get('condition', 'practice'),
        'color': trial['letterColor'],
        'response': response,
        'accuracy': accuracy,
        'rt': rt,
        'rt_source': rt_source,  # 'client' or 'server'
        'timestamp': datetime.now().isoformat(),
        'phase': 'practice' if is_practice else 'experimental'
    }

    if is_practice:
        st.session_state.practice_responses.append(response_data)
        st.session_state.last_response_correct = accuracy
        st.session_state.practice_trial_num += 1
        # 피드백은 다음 trial 렌더링 시 함께 표시됨 (phase 없음)
    else:
        st.session_state.responses.append(response_data)
        st.session_state.trial_num += 1
        # 실험 시행: ITI 시작
        st.session_state.showing_iti = True
        st.session_state.iti_start_time = time.time()
        st.session_state.current_iti_duration = random.uniform(ITI_MIN, ITI_MAX)

    st.session_state.start_time = None

    # 완료 체크
    if not is_practice and st.session_state.trial_num >= len(st.session_state.exp_trials):
        st.session_state.task_completed = True
        st.session_state.showing_iti = False  # ITI 종료

    st.rerun()


def create_summary_row():
    """참가자별 요약 데이터 생성 (한 행)"""
    if len(st.session_state.responses) == 0:
        return None

    # Experimental 데이터만 사용
    exp_df = pd.DataFrame(st.session_state.responses)

    # 기본 정보
    end_time = datetime.now()
    start_time = st.session_state.experiment_start_time

    # 총 소요시간 계산 (초 단위)
    if start_time:
        total_duration = (end_time - start_time).total_seconds()
    else:
        total_duration = None

    summary = {
        'participant_id': st.session_state.participant_id,
        'date': end_time.strftime("%Y-%m-%d"),
        'timestamp_start': start_time.isoformat() if start_time else None,
        'timestamp_end': end_time.isoformat(),
        'total_duration_sec': round(total_duration, 2) if total_duration else None,
    }

    # 조건별 요약 통계 (정답 trial만 사용하여 RT 계산)
    for condition in ['positive', 'negative', 'neutral']:
        cond_data = exp_df[exp_df['condition'] == condition]
        correct_data = cond_data[cond_data['accuracy'] == 1]

        summary[f'rt_{condition}_mean'] = round(correct_data['rt'].mean(), 4) if len(correct_data) > 0 else None
        summary[f'rt_{condition}_sd'] = round(correct_data['rt'].std(), 4) if len(correct_data) > 1 else None
        summary[f'acc_{condition}'] = round(cond_data['accuracy'].mean(), 4) if len(cond_data) > 0 else None
        summary[f'n_{condition}'] = len(cond_data)

    # 간섭 점수 (negative/positive RT - neutral RT)
    if summary.get('rt_neutral_mean') and summary.get('rt_negative_mean'):
        summary['interference_negative'] = round(summary['rt_negative_mean'] - summary['rt_neutral_mean'], 4)
    if summary.get('rt_neutral_mean') and summary.get('rt_positive_mean'):
        summary['interference_positive'] = round(summary['rt_positive_mean'] - summary['rt_neutral_mean'], 4)

    # 전체 통계
    correct_all = exp_df[exp_df['accuracy'] == 1]
    summary['rt_overall_mean'] = round(correct_all['rt'].mean(), 4) if len(correct_all) > 0 else None
    summary['acc_overall'] = round(exp_df['accuracy'].mean(), 4)
    summary['n_total'] = len(exp_df)

    # Practice 원시 데이터
    practice_df = pd.DataFrame(st.session_state.practice_responses)
    for i, (_, row) in enumerate(practice_df.iterrows(), 1):
        summary[f'p{i}_word'] = row['word']
        summary[f'p{i}_color'] = row['color']
        summary[f'p{i}_resp'] = row['response']
        summary[f'p{i}_acc'] = row['accuracy']
        summary[f'p{i}_rt'] = round(row['rt'], 4)

    # Practice 요약
    if len(practice_df) > 0:
        practice_correct = practice_df[practice_df['accuracy'] == 1]
        summary['practice_acc'] = round(practice_df['accuracy'].mean(), 4)
        summary['practice_rt_mean'] = round(practice_correct['rt'].mean(), 4) if len(practice_correct) > 0 else None

    # Experimental 원시 데이터 (trial별로 컬럼에 추가)
    # 항상 144개 trial 컬럼 생성 (pilot 모드에서도 동일한 헤더 유지)
    FULL_TRIAL_COUNT = 144
    for i in range(1, FULL_TRIAL_COUNT + 1):
        if i <= len(exp_df):
            row = exp_df.iloc[i - 1]
            summary[f't{i}_word'] = row['word']
            summary[f't{i}_cond'] = row['condition'][:3]  # pos/neg/neu
            summary[f't{i}_color'] = row['color']
            summary[f't{i}_resp'] = row['response']
            summary[f't{i}_acc'] = row['accuracy']
            summary[f't{i}_rt'] = round(row['rt'], 4)
        else:
            # Pilot 모드: 나머지 컬럼은 빈 값
            summary[f't{i}_word'] = None
            summary[f't{i}_cond'] = None
            summary[f't{i}_color'] = None
            summary[f't{i}_resp'] = None
            summary[f't{i}_acc'] = None
            summary[f't{i}_rt'] = None

    return pd.DataFrame([summary])


def save_data():
    """데이터 저장 함수"""
    if len(st.session_state.responses) > 0:
        df = create_summary_row()

        if df is not None:
            # data/responses 폴더 생성
            output_dir = Path("data/responses")
            output_dir.mkdir(parents=True, exist_ok=True)

            # 파일명: participant_id_timestamp.csv
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"{st.session_state.participant_id}_{timestamp}.csv"

            df.to_csv(filename, index=False, encoding='utf-8-sig')
            return filename, df
    return None, None


def backup_to_google_sheets(df):
    """Google Sheets에 데이터 백업"""
    if not GSPREAD_AVAILABLE:
        return False, "gspread 라이브러리가 설치되지 않았습니다."

    try:
        # Streamlit secrets에서 credentials 가져오기
        credentials_dict = st.secrets["gcp_service_account"]

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_info(
            dict(credentials_dict),
            scopes=scopes
        )

        gc = gspread.authorize(credentials)

        # Spreadsheet ID (emotional stroop responses)
        SPREADSHEET_ID = "1qz17jEAWlJcP-erMPM99qRE9SPa2m7GqrYzzBnj25NE"
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)

        # 첫 번째 시트 사용
        worksheet = spreadsheet.sheet1

        # 기존 데이터가 있는지 확인
        existing_data = worksheet.get_all_values()

        # 헤더 확인 및 추가
        expected_headers = df.columns.tolist()
        if len(existing_data) == 0 or existing_data[0] != expected_headers:
            if len(existing_data) == 0:
                worksheet.append_row(expected_headers)
            else:
                # 첫 행이 헤더가 아니면 맨 위에 헤더 삽입
                worksheet.insert_row(expected_headers, 1)

        # 데이터 추가
        for _, row in df.iterrows():
            worksheet.append_row(row.tolist())

        return True, "Google Sheets 백업 완료"

    except Exception as e:
        return False, f"백업 실패: {str(e)}"


# ========== 메인 앱 로직 ==========

# 1. 참가자 정보 입력 화면
if not st.session_state.task_started:
    st.title("Emotional Word Stroop Task")
    st.markdown("### 참가자 정보")
    if st.session_state.experiment_mode == "pilot":
        st.caption(f"🧪 Pilot 모드: {TOTAL_TRIALS} trials ({N_PER_CONDITION} × 3 conditions)")
    else:
        st.caption("📊 Full 모드")

    st.info("⚠️ **시작 전**: 전체화면 모드로 전환해주세요  \n(Mac: Cmd+Ctrl+F, Windows: F11)")

    participant_id = st.text_input("참가자 ID:", placeholder="예: P001")

    if st.button("과제 시작"):
        if participant_id:
            st.session_state.participant_id = participant_id
            st.session_state.task_started = True
            # Practice trials 생성
            st.session_state.practice_trials = create_practice_trials()
            st.rerun()
        else:
            st.error("참가자 ID를 입력해주세요.")

    st.stop()


# 2. Practice Instructions (여러 화면으로 분리)
if not st.session_state.practice_completed and not st.session_state.showing_practice_redo:
    if not st.session_state.practice_instructions_shown:
        # 지시사항 페이지 정의 (2줄씩)
        instruction_pages = [
            {
                "lines": [
                    "화면에 <strong>색깔로 표시된 단어</strong>가 나타납니다.",
                    "<strong>단어의 의미는 무시</strong>하고, <strong>글자의 색깔만</strong> 판단해주세요."
                ],
                "button": "다음"
            },
            {
                "lines": [
                    "키보드로 색깔을 선택하세요.",
                    ""
                ],
                "button": "다음"
            },
            {
                "lines": [
                    "먼저 <strong>연습 시행</strong>을 진행합니다.",
                    "정답/오답 피드백이 제공됩니다."
                ],
                "button": "연습 시작"
            }
        ]

        current_page = st.session_state.instruction_page
        page = instruction_pages[current_page]
        is_last_page = current_page == len(instruction_pages) - 1

        # 페이지 내용 (중앙 정렬) + 3초 후 N키 안내 표시
        st.markdown(f'''
        <style>
        @keyframes fadeInPractice{current_page} {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .n-key-prompt-p{current_page} {{
            opacity: 0;
            animation: fadeInPractice{current_page} 0.5s ease-in-out 3s forwards;
            margin-top: 150px;
        }}
        .n-key-button-p{current_page} {{
            display: inline-block;
            background-color: #333;
            border: 2px solid #666;
            border-radius: 8px;
            padding: 12px 32px;
            font-size: 20px;
            color: #ccc;
        }}
        .n-key-button-p{current_page} span {{
            color: white;
            font-weight: bold;
        }}
        div[data-testid="stButton"]:has(button[kind="primary"]) {{
            display: none !important;
        }}
        </style>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    min-height: 50vh; color: white; text-align: center; padding-top: 15vh;">
            <p style="font-size: 32px; margin-bottom: 20px; line-height: 1.6;">{page["lines"][0]}</p>
            {"" if current_page == 1 else f'<p style="font-size: 32px; margin-top: 20px; margin-bottom: 0; line-height: 1.6;">{page["lines"][1]}</p>'}
            {"" if current_page != 1 else '''
            <div style="display: flex; gap: 80px; margin-top: 40px; margin-bottom: 20px;">
                <div style="text-align: center;">
                    <span style="font-size: 64px; font-weight: bold; color: #ff4444;">F</span>
                    <p style="font-size: 28px; margin-top: 15px; color: #ff4444;">빨강</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 64px; font-weight: bold; color: #44ff44;">J</span>
                    <p style="font-size: 28px; margin-top: 15px; color: #44ff44;">초록</p>
                </div>
            </div>
            '''}
            <div class="n-key-prompt-p{current_page}">
                <div class="n-key-button-p{current_page}"><span>N</span> 키를 눌러 {page["button"]}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        clicked = st.button(page["button"], key=f"instruction_btn_{current_page}", type="primary")

        if clicked:
            if is_last_page:
                st.session_state.practice_instructions_shown = True
                st.session_state.instruction_page = 0
            else:
                st.session_state.instruction_page += 1
            st.rerun()

        # N 키 리스너 (3초 후 활성화)
        components.html(f'''
        <script>
        (function() {{
            const pageNum = {current_page};
            const DELAY_MS = 3000;

            if (window.instructionKeyHandlerInstalled === pageNum) return;
            window.instructionKeyHandlerInstalled = pageNum;
            window.instructionKeyEnabled = false;

            // 3초 후 N 키 활성화
            setTimeout(() => {{
                window.instructionKeyEnabled = true;
            }}, DELAY_MS);

            function handleInstructionKey(e) {{
                if ((e.key === 'n' || e.key === 'N' || e.code === 'KeyN') && window.instructionKeyEnabled) {{
                    e.preventDefault();
                    const btn = parent.document.querySelector('button[kind="primary"]');
                    if (btn) {{
                        btn.click();
                        parent.document.removeEventListener('keydown', handleInstructionKey);
                        window.instructionKeyHandlerInstalled = null;
                    }}
                }}
            }}

            parent.document.addEventListener('keydown', handleInstructionKey);
        }})();
        </script>
        ''', height=0)

        st.stop()

    # Practice Trial 진행
    if st.session_state.practice_trial_num < len(st.session_state.practice_trials):

        trial = st.session_state.practice_trials.iloc[st.session_state.practice_trial_num]

        # 클라이언트 사이드 RT 읽기 (이전 시행에서 저장된 값)
        client_rt = read_client_rt()
        if client_rt is not None:
            st.session_state.pending_client_rt = client_rt

        # 첫 시행 여부
        is_first_trial = st.session_state.practice_trial_num == 0
        has_feedback = st.session_state.last_response_correct is not None or st.session_state.last_was_timeout
        color_hex_map = {'red': '#FF0000', 'green': '#00FF00'}

        # Timeout 체크 (연습 시행도 동일하게 적용)
        if st.session_state.start_time is not None:
            elapsed = time.time() - st.session_state.start_time
            # 첫 시행은 fixation 있음 (0.5초), 피드백 있으면 1.3초, 없으면 0.3초
            if is_first_trial:
                timeout_offset = FIXATION_DURATION
            elif has_feedback:
                timeout_offset = 1.3  # 피드백 1초 + 자극 fadeIn 0.3초
            else:
                timeout_offset = 0.3
            if elapsed >= MAX_RESPONSE_TIME + timeout_offset:
                # Timeout 발생
                record_response(trial, "timeout", is_practice=True, is_timeout=True)
                st.stop()

        if is_first_trial:
            # 첫 시행: Fixation + 자극 (기존 애니메이션)
            # 검정 오버레이로 다른 요소 숨김 + fixation + stimulus
            st.markdown(
                f'''
                <style>
                .black-overlay {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background-color: #000000;
                    z-index: 998;
                }}
                </style>
                <div class="black-overlay"></div>
                <div class="fixation-cross">+</div>
                <div class="stimulus-container" style="opacity: 0;">
                    <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
                </div>
                ''',
                unsafe_allow_html=True
            )
        elif has_feedback:
            # 이후 시행 + 피드백 있음: 피드백 먼저 표시 후 자극 (CSS 애니메이션으로 순서 제어)
            if st.session_state.last_was_timeout:
                feedback_style_class = "practice-feedback-timeout"
                feedback_text = "너무 느립니다"
            elif st.session_state.last_response_correct == 1:
                feedback_style_class = "practice-feedback-correct"
                feedback_text = "정답"
            else:
                feedback_style_class = "practice-feedback-incorrect"
                feedback_text = "오답"

            # 매 trial마다 고유한 애니메이션 이름 생성 (브라우저가 새 애니메이션으로 인식)
            trial_num = st.session_state.practice_trial_num
            st.markdown(
                f'''
                <style>
                @keyframes feedbackShow{trial_num} {{
                    0% {{ opacity: 1; }}
                    80% {{ opacity: 1; }}
                    100% {{ opacity: 0; }}
                }}
                @keyframes stimulusAfterFeedback{trial_num} {{
                    0% {{ opacity: 0; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                <div class="practice-feedback {feedback_style_class}" style="animation: feedbackShow{trial_num} 1s ease-in-out forwards;">{feedback_text}</div>
                <div class="stimulus-after-feedback" style="animation: stimulusAfterFeedback{trial_num} 0.3s ease-in-out 1s forwards;">
                    <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
                </div>
                ''',
                unsafe_allow_html=True
            )
        else:
            # 이후 시행 + 피드백 없음: 바로 자극 표시
            st.markdown(
                f'''
                <div class="stimulus-container-immediate">
                    <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
                </div>
                ''',
                unsafe_allow_html=True
            )

        # 반응시간 측정 시작
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        st.markdown("<br>", unsafe_allow_html=True)

        # 키보드 이벤트 리스너 (F, J) - 클라이언트 사이드 RT 측정 + Timeout
        from streamlit.components.v1 import html
        # 첫 시행은 fixation 500ms, 피드백 있으면 1300ms (피드백 1000ms + fadeIn 300ms), 그 외 300ms
        if is_first_trial:
            stimulus_delay = 500
        elif has_feedback:
            stimulus_delay = 1300  # 피드백 1초 + 자극 fadeIn 0.3초
        else:
            stimulus_delay = 300
        html(f"""
        <script>
        (function() {{
            const tryNum = {st.session_state.practice_trial_num};
            const MAX_RESPONSE_TIME = {int(MAX_RESPONSE_TIME * 1000)};  // ms
            const STIMULUS_DELAY = {stimulus_delay};  // ms (첫 시행 500ms, 피드백 있으면 1300ms, 그 외 300ms)

            // 반응 버튼 숨기기 (키보드로만 반응)
            function hideResponseButtons() {{
                const allButtons = parent.document.querySelectorAll('button');
                allButtons.forEach((btn) => {{
                    const text = btn.textContent || btn.innerText;
                    if (text.includes('🔴') || text.includes('🟢') || text.includes('빨강') || text.includes('초록')) {{
                        btn.style.position = 'fixed';
                        btn.style.bottom = '0';
                        btn.style.left = '0';
                        btn.style.opacity = '0.01';
                        btn.style.width = '1px';
                        btn.style.height = '1px';
                        btn.style.overflow = 'hidden';
                        btn.style.zIndex = '-1';
                    }}
                }});
            }}
            setTimeout(hideResponseButtons, 50);

            // 자극 표시 시점 기록 (첫 시행: fixation 0.5초 후, 이후: 0.3초 후)
            window.stimulusShownTime = performance.now() + STIMULUS_DELAY;
            console.log('Practice stimulus will be shown at:', window.stimulusShownTime, '(delay:', STIMULUS_DELAY, 'ms)');

            // Timeout 플래그
            window.stroopResponseMade = false;

            // Remove ALL previous listeners and timers
            if (window.stroopKeyHandler) {{
                parent.document.removeEventListener('keydown', window.stroopKeyHandler);
            }}
            if (window.stroopTimeoutTimer) {{
                clearTimeout(window.stroopTimeoutTimer);
            }}

            // Timeout 핸들러 - 3초 후 자동으로 timeout 버튼 클릭
            window.stroopTimeoutTimer = setTimeout(function() {{
                if (!window.stroopResponseMade) {{
                    console.log('Practice Timeout! No response within', MAX_RESPONSE_TIME, 'ms');
                    localStorage.setItem('stroopClientRT', 'timeout');
                    const allButtons = parent.document.querySelectorAll('button');
                    allButtons.forEach((btn) => {{
                        const text = btn.textContent || btn.innerText;
                        if (text.includes('timeout')) {{
                            btn.click();
                        }}
                    }});
                }}
            }}, STIMULUS_DELAY + MAX_RESPONSE_TIME);

            // Define new handler
            window.stroopKeyHandler = function(event) {{
                const code = event.code;  // Physical key code (KeyF, KeyJ)

                // Use event.code to detect physical keys (works with Korean/English keyboard)
                if (code !== 'KeyF' && code !== 'KeyJ') {{
                    return;
                }}

                // 이미 응답한 경우 무시 (빠른 더블 클릭 방지)
                if (window.stroopResponseMade) {{
                    console.log('Response already made, ignoring key:', code);
                    return;
                }}

                event.preventDefault();
                event.stopPropagation();

                // 응답 완료 플래그
                window.stroopResponseMade = true;
                if (window.stroopTimeoutTimer) {{
                    clearTimeout(window.stroopTimeoutTimer);
                }}

                // 클라이언트 사이드 RT 계산
                const keyPressTime = performance.now();
                const clientRT = Math.max(0, keyPressTime - window.stimulusShownTime);
                console.log('Practice Client RT:', clientRT.toFixed(2), 'ms');

                // RT를 localStorage에 저장 (Python에서 읽기 위함)
                localStorage.setItem('stroopClientRT', clientRT.toString());

                // Find and click buttons (with retry and fallback to timeout)
                function findAndClickButton(color, retryCount) {{
                    const allButtons = parent.document.querySelectorAll('button');
                    let redBtn = null, greenBtn = null, timeoutBtn = null;

                    allButtons.forEach((btn) => {{
                        const text = btn.textContent || btn.innerText;
                        if (text.includes('🔴') || text.includes('빨강')) redBtn = btn;
                        if (text.includes('🟢') || text.includes('초록')) greenBtn = btn;
                        if (text === 'timeout') timeoutBtn = btn;
                    }});

                    console.log('Practice buttons found - Red:', !!redBtn, 'Green:', !!greenBtn, 'Timeout:', !!timeoutBtn, 'Total:', allButtons.length);

                    let targetBtn = (color === 'red') ? redBtn : greenBtn;

                    if (targetBtn) {{
                        console.log('Practice clicking', color, 'button');
                        targetBtn.click();

                        // Backup: 클릭 후 500ms 내에 페이지가 안 바뀌면 timeout 버튼 클릭
                        setTimeout(() => {{
                            console.error('Practice button click did not trigger page change! Clicking timeout as backup.');
                            const backupTimeoutBtn = [...parent.document.querySelectorAll('button')].find(btn => btn.textContent === 'timeout');
                            if (backupTimeoutBtn) {{
                                backupTimeoutBtn.click();
                            }} else {{
                                console.error('Backup timeout button not found! Forcing page reload.');
                                parent.location.reload();
                            }}
                        }}, 500);
                    }} else if (retryCount < 3) {{
                        console.log('Practice button not found, retrying... (attempt', retryCount + 1, ')');
                        setTimeout(() => findAndClickButton(color, retryCount + 1), 100);
                    }} else {{
                        // Fallback: 버튼 못 찾으면 timeout 버튼 클릭해서 다음으로 넘어감
                        console.error('Practice FAILED to find button after 3 retries! Clicking timeout as fallback.');
                        if (timeoutBtn) {{
                            timeoutBtn.click();
                        }} else {{
                            console.error('Timeout button also not found! Forcing page reload.');
                            parent.location.reload();
                        }}
                    }}
                }}

                // Click the appropriate button based on physical key code
                const color = (code === 'KeyF') ? 'red' : 'green';
                findAndClickButton(color, 0);
            }};

            // Add the new listener
            parent.document.addEventListener('keydown', window.stroopKeyHandler);
            console.log('Practice keyboard handler installed for trial', tryNum, 'with timeout:', MAX_RESPONSE_TIME, 'ms');
        }})();
        </script>
        """, height=0)

        # 반응 버튼
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if st.button("🔴 빨강 (F)", key=f"practice_red_{st.session_state.practice_trial_num}", use_container_width=True, type="primary"):
                client_rt = st.session_state.pending_client_rt
                st.session_state.pending_client_rt = None
                record_response(trial, "red", is_practice=True, client_rt=client_rt)

        with col2:
            if st.button("🟢 초록 (J)", key=f"practice_green_{st.session_state.practice_trial_num}", use_container_width=True, type="primary"):
                client_rt = st.session_state.pending_client_rt
                st.session_state.pending_client_rt = None
                record_response(trial, "green", is_practice=True, client_rt=client_rt)

        with col3:
            # 숨겨진 timeout 버튼 (연습 시행)
            if st.button("timeout", key=f"practice_timeout_{st.session_state.practice_trial_num}"):
                record_response(trial, "timeout", is_practice=True, is_timeout=True)

    else:
        # 마지막 trial 피드백 표시 후 자동 진행
        has_feedback = st.session_state.last_response_correct is not None or st.session_state.last_was_timeout

        if has_feedback:
            # 마지막 피드백 표시
            if st.session_state.last_was_timeout:
                feedback_style_class = "practice-feedback-timeout"
                feedback_text = "너무 느립니다"
            elif st.session_state.last_response_correct == 1:
                feedback_style_class = "practice-feedback-correct"
                feedback_text = "정답"
            else:
                feedback_style_class = "practice-feedback-incorrect"
                feedback_text = "오답"

            # 마지막 피드백용 고유 애니메이션
            st.markdown(
                f'''
                <style>
                @keyframes feedbackShowLast {{
                    0% {{ opacity: 1; }}
                    80% {{ opacity: 1; }}
                    100% {{ opacity: 0; }}
                }}
                </style>
                <div class="practice-feedback {feedback_style_class}" style="animation: feedbackShowLast 1s ease-in-out forwards;">{feedback_text}</div>
                ''',
                unsafe_allow_html=True
            )

            # 숨겨진 버튼 + 1초 후 JavaScript로 자동 클릭 (time.sleep 대신)
            if st.button("practice_complete", key="practice_complete_btn"):
                # Practice 정확도 계산
                practice_responses = st.session_state.practice_responses
                if len(practice_responses) > 0:
                    correct_count = sum(1 for r in practice_responses if r['accuracy'] == 1)
                    practice_accuracy = correct_count / len(practice_responses)
                else:
                    practice_accuracy = 0

                # 정확도 50% 미만이면 다시 연습
                if practice_accuracy < 0.5:
                    st.session_state.showing_practice_redo = True
                else:
                    st.session_state.practice_completed = True

                st.session_state.last_response_correct = None
                st.session_state.last_was_timeout = False
                st.rerun()

            # 버튼 숨기기 + 1초 후 자동 클릭
            components.html("""
            <script>
            (function() {
                // 버튼 즉시 숨기기
                const hideBtn = () => {
                    const btn = [...parent.document.querySelectorAll('button')].find(b => b.textContent === 'practice_complete');
                    if (btn) {
                        btn.style.display = 'none';
                    }
                };
                hideBtn();
                setTimeout(hideBtn, 50);  // 렌더링 후에도 숨기기

                // 1초 후 클릭
                setTimeout(() => {
                    const btn = [...parent.document.querySelectorAll('button')].find(b => b.textContent === 'practice_complete');
                    if (btn) {
                        btn.click();
                    }
                }, 1000);
            })();
            </script>
            """, height=0)
        else:
            # 피드백 없이 도달한 경우 - 마지막 피드백 버튼이 클릭되길 기다림
            # (정상적으로는 has_feedback이 True여야 하지만, 엣지 케이스 방지)
            st.markdown('''
            <div style="display: flex; align-items: center; justify-content: center; height: 60vh;">
                <p style="color: white; font-size: 24px;">잠시만 기다려 주세요...</p>
            </div>
            ''', unsafe_allow_html=True)

            # 1초 후 자동으로 완료 처리
            if st.button("auto_complete", key="auto_complete_btn"):
                practice_responses = st.session_state.practice_responses
                if len(practice_responses) > 0:
                    correct_count = sum(1 for r in practice_responses if r['accuracy'] == 1)
                    practice_accuracy = correct_count / len(practice_responses)
                else:
                    practice_accuracy = 0

                if practice_accuracy < 0.5:
                    st.session_state.showing_practice_redo = True
                else:
                    st.session_state.practice_completed = True

                st.session_state.last_response_correct = None
                st.session_state.last_was_timeout = False
                st.rerun()

            # 버튼 숨기기 + 1초 후 자동 클릭
            components.html("""
            <script>
            (function() {
                // 버튼 즉시 숨기기
                const hideBtn = () => {
                    const btn = [...parent.document.querySelectorAll('button')].find(b => b.textContent === 'auto_complete');
                    if (btn) {
                        btn.style.display = 'none';
                    }
                };
                hideBtn();
                setTimeout(hideBtn, 50);

                // 1초 후 클릭
                setTimeout(() => {
                    const btn = [...parent.document.querySelectorAll('button')].find(b => b.textContent === 'auto_complete');
                    if (btn) {
                        btn.click();
                    }
                }, 1000);
            })();
            </script>
            """, height=0)

    st.stop()


# 2.5 Practice Redo 화면 (정확도 50% 미만)
if st.session_state.showing_practice_redo:
    st.markdown('''
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 60vh; color: white; text-align: center;">
        <p style="font-size: 32px; margin-bottom: 30px;">정답률이 낮아</p>
        <p style="font-size: 32px; margin-bottom: 30px;">연습을 다시 시행합니다.</p>
        <p style="font-size: 24px; color: #888;"><span style="color: white; font-weight: bold;">N</span> 키를 눌러 다시 연습하기</p>
    </div>
    ''', unsafe_allow_html=True)

    # 숨겨진 버튼 (JavaScript에서 트리거)
    st.markdown('''
    <style>
    div[data-testid="stButton"]:has(button[kind="primary"]) {
        display: none !important;
    }
    </style>
    ''', unsafe_allow_html=True)

    if st.button("다시 연습하기", key=f"redo_practice_{st.session_state.practice_attempt}", type="primary"):
        # 연습 초기화 (지시사항부터 다시)
        st.session_state.practice_trial_num = 0
        st.session_state.practice_responses = []
        st.session_state.practice_trials = create_practice_trials()
        st.session_state.showing_practice_redo = False
        st.session_state.practice_instructions_shown = False  # 지시사항부터 다시
        st.session_state.practice_started = False
        st.session_state.practice_attempt += 1
        st.session_state.last_response_correct = None
        st.session_state.last_was_timeout = False
        st.rerun()

    # N 키 리스너
    components.html(f'''
    <script>
    (function() {{
        const attempt = {st.session_state.practice_attempt};
        if (window.redoKeyHandlerInstalled === attempt) return;
        window.redoKeyHandlerInstalled = attempt;

        function handleRedoKey(e) {{
            if (e.key === 'n' || e.key === 'N' || e.code === 'KeyN') {{
                e.preventDefault();
                const btn = parent.document.querySelector('button[kind="primary"]');
                if (btn) {{
                    btn.click();
                    parent.document.removeEventListener('keydown', handleRedoKey);
                    window.redoKeyHandlerInstalled = null;
                }}
            }}
        }}

        parent.document.addEventListener('keydown', handleRedoKey);
    }})();
    </script>
    ''', height=0)

    st.stop()


# 3. Experimental Instructions (페이지별 표시)
if not st.session_state.instructions_exp_shown:
    exp_instruction_pages = [
        {
            "lines": [
                "연습이 끝났습니다! 이제 <strong>본 과제</strong>를 진행합니다.",
                "본 과제에서는 <strong>피드백이 제공되지 않습니다.</strong>"
            ],
            "button": "다음"
        },
        {
            "lines": [
                "🔴 <strong>빨강</strong>: <strong>F</strong> 키 &nbsp;&nbsp;&nbsp; 🟢 <strong>초록</strong>: <strong>J</strong> 키",
                "연습과 동일하게 <strong>글자의 색깔만</strong> 판단해주세요."
            ],
            "button": "본 과제 시작"
        }
    ]

    current_page = st.session_state.exp_instruction_page
    page = exp_instruction_pages[current_page]
    is_last_page = current_page == len(exp_instruction_pages) - 1

    # 페이지 내용 (중앙 정렬) + 3초 후 N키 안내 표시
    st.markdown(f'''
    <style>
    @keyframes fadeInExp{current_page} {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .n-key-prompt-e{current_page} {{
        opacity: 0;
        animation: fadeInExp{current_page} 0.5s ease-in-out 3s forwards;
        margin-top: 150px;
    }}
    .n-key-button-e{current_page} {{
        display: inline-block;
        background-color: #333;
        border: 2px solid #666;
        border-radius: 8px;
        padding: 12px 32px;
        font-size: 20px;
        color: #ccc;
    }}
    .n-key-button-e{current_page} span {{
        color: white;
        font-weight: bold;
    }}
    div[data-testid="stButton"]:has(button[kind="primary"]) {{
        display: none !important;
    }}
    </style>
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                min-height: 50vh; color: white; text-align: center; padding-top: 15vh;">
        <p style="font-size: 32px; margin-bottom: 20px; line-height: 1.6;">{page["lines"][0]}</p>
        <p style="font-size: 32px; margin-top: 20px; margin-bottom: 0; line-height: 1.6;">{page["lines"][1]}</p>
        <div class="n-key-prompt-e{current_page}">
            <div class="n-key-button-e{current_page}"><span>N</span> 키를 눌러 {page["button"]}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    clicked = st.button(page["button"], key=f"exp_instruction_btn_{current_page}", type="primary")

    if clicked:
        if is_last_page:
            st.session_state.instructions_exp_shown = True
            st.session_state.exp_instruction_page = 0
            # Experimental trials 생성
            st.session_state.exp_trials = create_exp_trials(n_per_condition=N_PER_CONDITION)
            # 본 시행 시작 시간 기록
            st.session_state.experiment_start_time = datetime.now()
        else:
            st.session_state.exp_instruction_page += 1
        st.rerun()

    # N 키 리스너 (3초 후 활성화)
    components.html(f'''
    <script>
    (function() {{
        const pageNum = {current_page};
        const DELAY_MS = 3000;

        if (window.expInstructionKeyHandlerInstalled === pageNum) return;
        window.expInstructionKeyHandlerInstalled = pageNum;
        window.expInstructionKeyEnabled = false;

        // 3초 후 N 키 활성화
        setTimeout(() => {{
            window.expInstructionKeyEnabled = true;
        }}, DELAY_MS);

        function handleExpInstructionKey(e) {{
            if ((e.key === 'n' || e.key === 'N' || e.code === 'KeyN') && window.expInstructionKeyEnabled) {{
                e.preventDefault();
                const btn = parent.document.querySelector('button[kind="primary"]');
                if (btn) {{
                    btn.click();
                    parent.document.removeEventListener('keydown', handleExpInstructionKey);
                    window.expInstructionKeyHandlerInstalled = null;
                }}
            }}
        }}

        parent.document.addEventListener('keydown', handleExpInstructionKey);
    }})();
    </script>
    ''', height=0)

    st.stop()


# 4. Task 완료 화면
if st.session_state.task_completed:
    st.title("✅ 과제 완료!")
    st.markdown("모든 시행을 완료했습니다. 감사합니다!")

    # 데이터 저장 (한 번만 실행)
    if 'final_df' not in st.session_state:
        saved_file, df = save_data()
        if df is not None:
            st.session_state.final_df = df
            # Google Sheets 백업 (한 번만)
            backup_success, backup_msg = backup_to_google_sheets(df)
            st.session_state.backup_result = (backup_success, backup_msg)

    # 저장된 결과 표시
    if 'final_df' in st.session_state:
        df = st.session_state.final_df

        # 백업 결과 표시
        if 'backup_result' in st.session_state:
            backup_success, backup_msg = st.session_state.backup_result
            if backup_success:
                st.info("📊 데이터가 자동으로 백업되었습니다.")
            else:
                st.warning(f"⚠️ Google Sheets 백업 실패: {backup_msg}")

        # CSV 다운로드 버튼 (Excel 호환 인코딩)
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 결과 CSV 다운로드",
            data=csv_data,
            file_name=f"{st.session_state.participant_id}_result.csv",
            mime="text/csv"
        )

    st.stop()


# 5. Experimental Trials 진행
if st.session_state.trial_num < len(st.session_state.exp_trials):

    # 블록 간 휴식 체크
    trials_per_block = TRIALS_PER_BLOCK_PILOT if st.session_state.experiment_mode == "pilot" else TRIALS_PER_BLOCK_FULL
    num_blocks = 2 if st.session_state.experiment_mode == "pilot" else 4
    current_block = st.session_state.trial_num // trials_per_block + 1
    completed_block = st.session_state.trial_num // trials_per_block
    is_block_start = (st.session_state.trial_num > 0 and
                      st.session_state.trial_num % trials_per_block == 0 and
                      st.session_state.trial_num < len(st.session_state.exp_trials) and
                      completed_block not in st.session_state.breaks_shown)  # 아직 안 보여준 블록만

    # 블록 시작 시 휴식 화면 표시
    if is_block_start and not st.session_state.showing_break:
        st.session_state.showing_break = True
        st.session_state.break_start_time = time.time()
        st.rerun()

    # 휴식 화면 표시 중
    if st.session_state.showing_break:
        # break_start_time이 없으면 지금 시작
        if st.session_state.break_start_time is None:
            st.session_state.break_start_time = time.time()
        elapsed_break = time.time() - st.session_state.break_start_time
        remaining_min = int(max(0, BREAK_MIN - elapsed_break))
        remaining_max = int(max(0, BREAK_MAX - elapsed_break))
        can_continue = elapsed_break >= BREAK_MIN

        # 최대 시간 초과 시 자동 진행
        if elapsed_break >= BREAK_MAX:
            new_breaks = st.session_state.breaks_shown.copy()
            new_breaks.add(completed_block)
            st.session_state.breaks_shown = new_breaks
            st.session_state.showing_break = False
            st.session_state.break_start_time = None
            st.session_state.show_block_key_reminder = True  # 키 안내 화면 표시
            st.rerun()

        # 휴식 화면 UI (단순 버전)
        if can_continue:
            st.markdown(f'''
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                        height: 70vh; color: white; text-align: center;">
                <h1 style="font-size: 48px; margin-bottom: 40px;">블록 {completed_block}/{num_blocks} 완료!</h1>
                <p style="font-size: 24px; color: #4CAF50; margin-bottom: 40px;">준비되면 <span style="color: white; font-weight: bold;">N</span> 키를 눌러 다음 블록을 시작하세요</p>
                <p style="font-size: 20px; color: #666;">{remaining_max}초 후 자동 시작</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                        height: 70vh; color: white; text-align: center;">
                <h1 style="font-size: 48px; margin-bottom: 40px;">블록 {completed_block}/{num_blocks} 완료!</h1>
                <p style="font-size: 28px; margin-bottom: 60px;">잠시 휴식하세요.</p>
                <p style="font-size: 28px; color: #888;">{remaining_min}초 후에 시작할 수 있습니다</p>
            </div>
            ''', unsafe_allow_html=True)

        # 숨겨진 버튼
        st.markdown('''
        <style>
        div[data-testid="stButton"]:has(button[kind="primary"]) {
            display: none !important;
        }
        </style>
        ''', unsafe_allow_html=True)

        if st.button("continue_break", key=f"continue_block_{completed_block}", type="primary"):
            new_breaks = st.session_state.breaks_shown.copy()
            new_breaks.add(completed_block)
            st.session_state.breaks_shown = new_breaks
            st.session_state.showing_break = False
            st.session_state.break_start_time = None
            st.session_state.show_block_key_reminder = True  # 키 안내 화면 표시
            st.rerun()

        # N 키 리스너 (자동 새로고침 제거)
        components.html(f'''
        <script>
        (function() {{
            const blockNum = {completed_block};
            const canContinue = {'true' if can_continue else 'false'};

            if (window.breakKeyHandlerInstalled !== blockNum) {{
                window.breakKeyHandlerInstalled = blockNum;

                function handleBreakKey(e) {{
                    if ((e.key === 'n' || e.key === 'N' || e.code === 'KeyN') && canContinue) {{
                        e.preventDefault();
                        const btn = parent.document.querySelector('button[kind="primary"]');
                        if (btn) {{
                            btn.click();
                            parent.document.removeEventListener('keydown', handleBreakKey);
                            window.breakKeyHandlerInstalled = null;
                        }}
                    }}
                }}

                parent.document.addEventListener('keydown', handleBreakKey);
            }}
        }})();
        </script>
        ''', height=0)

        # Streamlit 기반 자동 새로고침 (1초마다)
        time.sleep(1)
        st.rerun()

    # 블록 시작 전 키 안내 화면
    if st.session_state.show_block_key_reminder:
        st.markdown('''
        <style>
        .n-key-button-block {
            display: inline-block;
            background-color: #333;
            border: 2px solid #666;
            border-radius: 8px;
            padding: 12px 32px;
            font-size: 20px;
            color: #ccc;
            margin-top: 40px;
        }
        .n-key-button-block span {
            color: white;
            font-weight: bold;
        }
        </style>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    height: 70vh; color: white; text-align: center;">
            <h2 style="font-size: 36px; margin-bottom: 50px;">키 안내</h2>
            <div style="display: flex; gap: 80px; margin-bottom: 40px;">
                <div style="text-align: center;">
                    <span style="font-size: 64px; font-weight: bold; color: #ff4444;">F</span>
                    <p style="font-size: 28px; margin-top: 15px; color: #ff4444;">빨강</p>
                </div>
                <div style="text-align: center;">
                    <span style="font-size: 64px; font-weight: bold; color: #44ff44;">J</span>
                    <p style="font-size: 28px; margin-top: 15px; color: #44ff44;">초록</p>
                </div>
            </div>
            <div class="n-key-button-block"><span>N</span> 키를 눌러 시작</div>
        </div>
        ''', unsafe_allow_html=True)

        # 숨겨진 버튼
        st.markdown('''
        <style>
        div[data-testid="stButton"]:has(button[kind="secondary"]) {
            display: none !important;
        }
        </style>
        ''', unsafe_allow_html=True)

        if st.button("start_block", key="start_block_after_break", type="secondary"):
            st.session_state.show_block_key_reminder = False
            st.rerun()

        # N 키 리스너
        components.html('''
        <script>
        (function() {
            if (!window.blockKeyReminderHandlerInstalled) {
                window.blockKeyReminderHandlerInstalled = true;

                function handleKey(e) {
                    if (e.key === 'n' || e.key === 'N' || e.code === 'KeyN') {
                        e.preventDefault();
                        const btn = parent.document.querySelector('button[kind="secondary"]');
                        if (btn) {
                            btn.click();
                            parent.document.removeEventListener('keydown', handleKey);
                            window.blockKeyReminderHandlerInstalled = false;
                        }
                    }
                }

                parent.document.addEventListener('keydown', handleKey);
            }
        })();
        </script>
        ''', height=0)
        st.stop()

    # ITI 표시 중인 경우
    if st.session_state.showing_iti:
        # ITI 완료 체크
        elapsed_iti = time.time() - st.session_state.iti_start_time
        if elapsed_iti >= st.session_state.current_iti_duration:
            # ITI 완료 → 다음 trial로
            st.session_state.showing_iti = False
            st.session_state.iti_start_time = None
            st.session_state.last_was_timeout = False
            st.rerun()
        else:
            # ITI 중: 검은 화면 또는 timeout 피드백
            if st.session_state.last_was_timeout:
                st.markdown('''
                <div style="position: fixed; top: 50px; left: 50%; transform: translateX(-50%);
                            background-color: rgba(255, 165, 0, 0.2);
                            border: 2px solid #FFA500;
                            color: #FFA500;
                            padding: 15px 30px;
                            border-radius: 8px;
                            font-size: 24px;
                            font-weight: bold;
                            z-index: 999;">
                    너무 느립니다
                </div>
                ''', unsafe_allow_html=True)
            # 잠시 후 rerun (ITI 대기)
            time.sleep(0.1)
            st.rerun()
        st.stop()

    trial = st.session_state.exp_trials.iloc[st.session_state.trial_num]

    # 클라이언트 사이드 RT 읽기 (이전 시행에서 저장된 값)
    client_rt = read_client_rt()
    if client_rt is not None:
        st.session_state.pending_client_rt = client_rt

    # 첫 시행 여부 (블록 내 첫 시행)
    is_first_trial = st.session_state.trial_num == 0

    # Timeout 체크 (서버 사이드)
    if st.session_state.start_time is not None:
        elapsed = time.time() - st.session_state.start_time
        timeout_offset = FIXATION_DURATION if is_first_trial else 0.3
        if elapsed >= MAX_RESPONSE_TIME + timeout_offset:
            # Timeout 발생
            record_response(trial, "timeout", is_timeout=True)
            st.stop()

    # 첫 시행만 Fixation cross, 이후는 바로 자극 표시
    color_hex_map = {'red': '#FF0000', 'green': '#00FF00'}

    if is_first_trial:
        # 첫 시행: Fixation + 자극 (기존 애니메이션)
        # 검정 오버레이로 다른 요소 숨김 + fixation + stimulus
        st.markdown(
            f'''
            <style>
            .black-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: #000000;
                z-index: 998;
            }}
            </style>
            <div class="black-overlay"></div>
            <div class="fixation-cross">+</div>
            <div class="stimulus-container" style="opacity: 0;">
                <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        # 이후 시행: Fixation 없이 바로 자극
        st.markdown(
            f'''
            <div class="stimulus-container-immediate">
                <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # 반응시간 측정 시작
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.markdown("<br>", unsafe_allow_html=True)

    # 키보드 이벤트 리스너 (F, J) - 클라이언트 사이드 RT 측정 + Timeout
    from streamlit.components.v1 import html
    # 첫 시행은 fixation 500ms, 이후 시행은 300ms
    stimulus_delay = 500 if is_first_trial else 300
    html(f"""
    <script>
    (function() {{
        const tryNum = {st.session_state.trial_num};
        const MAX_RESPONSE_TIME = {int(MAX_RESPONSE_TIME * 1000)};  // ms
        const STIMULUS_DELAY = {stimulus_delay};  // ms (첫 시행 500ms, 이후 300ms)

        // 자극 표시 시점 기록 (첫 시행: fixation 0.5초 후, 이후: 0.3초 후)
        window.stimulusShownTime = performance.now() + STIMULUS_DELAY;
        console.log('Stimulus will be shown at:', window.stimulusShownTime, '(delay:', STIMULUS_DELAY, 'ms)');

        // Timeout 플래그
        window.stroopResponseMade = false;

        // Remove ALL previous listeners and timers
        if (window.stroopKeyHandler) {{
            parent.document.removeEventListener('keydown', window.stroopKeyHandler);
        }}
        if (window.stroopTimeoutTimer) {{
            clearTimeout(window.stroopTimeoutTimer);
        }}

        // Timeout 핸들러 - 3초 후 자동으로 timeout 버튼 클릭
        window.stroopTimeoutTimer = setTimeout(function() {{
            if (!window.stroopResponseMade) {{
                console.log('Timeout! No response within', MAX_RESPONSE_TIME, 'ms');
                // Timeout으로 localStorage에 저장
                localStorage.setItem('stroopClientRT', 'timeout');
                // timeout 버튼 찾아서 클릭
                const allButtons = parent.document.querySelectorAll('button');
                allButtons.forEach((btn) => {{
                    const text = btn.textContent || btn.innerText;
                    if (text.includes('timeout')) {{
                        btn.click();
                    }}
                }});
            }}
        }}, STIMULUS_DELAY + MAX_RESPONSE_TIME);

        // Define new handler
        window.stroopKeyHandler = function(event) {{
            const code = event.code;  // Physical key code (KeyF, KeyJ)

            // Use event.code to detect physical keys (works with Korean/English keyboard)
            if (code !== 'KeyF' && code !== 'KeyJ') {{
                return;
            }}

            // 이미 응답한 경우 무시 (빠른 더블 클릭 방지)
            if (window.stroopResponseMade) {{
                console.log('Response already made, ignoring key:', code);
                return;
            }}

            event.preventDefault();
            event.stopPropagation();

            // 응답 완료 플래그
            window.stroopResponseMade = true;
            if (window.stroopTimeoutTimer) {{
                clearTimeout(window.stroopTimeoutTimer);
            }}

            // 클라이언트 사이드 RT 계산
            const keyPressTime = performance.now();
            const clientRT = Math.max(0, keyPressTime - window.stimulusShownTime);
            console.log('Client RT:', clientRT.toFixed(2), 'ms');

            // RT를 localStorage에 저장 (Python에서 읽기 위함)
            localStorage.setItem('stroopClientRT', clientRT.toString());

            // Find and click buttons (with retry and fallback to timeout)
            function findAndClickButton(color, retryCount) {{
                const allButtons = parent.document.querySelectorAll('button');
                let redBtn = null, greenBtn = null, timeoutBtn = null;

                allButtons.forEach((btn) => {{
                    const text = btn.textContent || btn.innerText;
                    if (text.includes('🔴') || text.includes('빨강')) redBtn = btn;
                    if (text.includes('🟢') || text.includes('초록')) greenBtn = btn;
                    if (text === 'timeout') timeoutBtn = btn;
                }});

                console.log('Buttons found - Red:', !!redBtn, 'Green:', !!greenBtn, 'Timeout:', !!timeoutBtn, 'Total:', allButtons.length);

                let targetBtn = (color === 'red') ? redBtn : greenBtn;

                if (targetBtn) {{
                    console.log('Clicking', color, 'button');
                    targetBtn.click();

                    // Backup: 클릭 후 500ms 내에 페이지가 안 바뀌면 timeout 버튼 클릭
                    setTimeout(() => {{
                        console.error('Button click did not trigger page change! Clicking timeout as backup.');
                        const backupTimeoutBtn = [...parent.document.querySelectorAll('button')].find(btn => btn.textContent === 'timeout');
                        if (backupTimeoutBtn) {{
                            backupTimeoutBtn.click();
                        }} else {{
                            console.error('Backup timeout button not found! Forcing page reload.');
                            parent.location.reload();
                        }}
                    }}, 500);
                }} else if (retryCount < 3) {{
                    console.log('Button not found, retrying... (attempt', retryCount + 1, ')');
                    setTimeout(() => findAndClickButton(color, retryCount + 1), 100);
                }} else {{
                    // Fallback: 버튼 못 찾으면 timeout 버튼 클릭해서 다음으로 넘어감
                    console.error('FAILED to find button after 3 retries! Clicking timeout as fallback.');
                    if (timeoutBtn) {{
                        timeoutBtn.click();
                    }} else {{
                        console.error('Timeout button also not found! Forcing page reload.');
                        parent.location.reload();
                    }}
                }}
            }}

            // Click the appropriate button based on physical key code
            const color = (code === 'KeyF') ? 'red' : 'green';
            findAndClickButton(color, 0);
        }};

        // Add the new listener
        parent.document.addEventListener('keydown', window.stroopKeyHandler);
        console.log('Keyboard handler installed for trial', tryNum, 'with timeout:', MAX_RESPONSE_TIME, 'ms');
    }})();
    </script>
    """, height=0)

    # 반응 버튼
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("🔴 빨강 (F)", key=f"red_{st.session_state.trial_num}", use_container_width=True, type="primary"):
            client_rt = st.session_state.pending_client_rt
            st.session_state.pending_client_rt = None
            record_response(trial, "red", client_rt=client_rt)

    with col2:
        if st.button("🟢 초록 (J)", key=f"green_{st.session_state.trial_num}", use_container_width=True, type="primary"):
            client_rt = st.session_state.pending_client_rt
            st.session_state.pending_client_rt = None
            record_response(trial, "green", client_rt=client_rt)

    with col3:
        # 숨겨진 timeout 버튼
        if st.button("timeout", key=f"timeout_{st.session_state.trial_num}"):
            record_response(trial, "timeout", is_timeout=True)

else:
    st.session_state.task_completed = True
    st.rerun()
