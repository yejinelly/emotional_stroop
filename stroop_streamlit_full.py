import streamlit as st
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

# ========== Block 구조 ==========
TRIALS_PER_BLOCK = 36  # 블록당 시행 수
NUM_BLOCKS = 4  # 총 블록 수

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

    /* 반응 버튼만 숨기기 (키보드만 사용) - 시각적으로만 숨김 */
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

    /* Stimulus word - 화면 중앙 고정 */
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

    @keyframes fadeOut {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }

    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
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
    summary = {
        'participant_id': st.session_state.participant_id,
        'date': datetime.now().strftime("%Y-%m-%d"),
        'timestamp': datetime.now().isoformat(),
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
    for i, (_, row) in enumerate(exp_df.iterrows(), 1):
        summary[f't{i}_word'] = row['word']
        summary[f't{i}_cond'] = row['condition'][:3]  # pos/neg/neu
        summary[f't{i}_color'] = row['color']
        summary[f't{i}_resp'] = row['response']
        summary[f't{i}_acc'] = row['accuracy']
        summary[f't{i}_rt'] = round(row['rt'], 4)

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
        st.caption(f"📊 Full 모드: {TOTAL_TRIALS} trials ({N_PER_CONDITION} × 3 conditions, {NUM_BLOCKS} blocks)")

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
if not st.session_state.practice_completed:
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
                    "🔴 <strong>빨강</strong>: <strong>F</strong> 키 &nbsp;&nbsp;&nbsp; 🟢 <strong>초록</strong>: <strong>J</strong> 키"
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

        # 페이지 내용 표시
        st.markdown(f'''
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    height: 50vh; color: white; text-align: center;">
            <p style="font-size: 32px; margin-bottom: 20px; line-height: 1.6;">{page["lines"][0]}</p>
            <p style="font-size: 32px; margin-top: 20px; line-height: 1.6;">{page["lines"][1]}</p>
        </div>
        ''', unsafe_allow_html=True)

        # 버튼 표시 (중앙 정렬)
        st.markdown('<div style="display: flex; justify-content: center; margin-top: 30px;">', unsafe_allow_html=True)
        if st.button(page["button"], key=f"instruction_btn_{current_page}", type="primary"):
            if is_last_page:
                st.session_state.practice_instructions_shown = True
                st.session_state.instruction_page = 0  # 리셋
            else:
                st.session_state.instruction_page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.stop()

    # Practice Trial 진행
    if st.session_state.practice_trial_num < len(st.session_state.practice_trials):
        trial = st.session_state.practice_trials.iloc[st.session_state.practice_trial_num]

        # 클라이언트 사이드 RT 읽기 (이전 시행에서 저장된 값)
        client_rt = read_client_rt()
        if client_rt is not None:
            st.session_state.pending_client_rt = client_rt

        # 피드백 표시 (이전 trial) - 박스 안에
        if st.session_state.last_response_correct is not None:
            if st.session_state.last_response_correct == 1:
                st.markdown('''
                <div style="position: fixed; top: 50px; left: 50%; transform: translateX(-50%);
                            background-color: rgba(76, 175, 80, 0.2);
                            border: 2px solid #4CAF50;
                            color: #4CAF50;
                            padding: 15px 30px;
                            border-radius: 8px;
                            font-size: 24px;
                            font-weight: bold;
                            z-index: 999;">
                    정답
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div style="position: fixed; top: 50px; left: 50%; transform: translateX(-50%);
                            background-color: rgba(244, 67, 54, 0.2);
                            border: 2px solid #f44336;
                            color: #f44336;
                            padding: 15px 30px;
                            border-radius: 8px;
                            font-size: 24px;
                            font-weight: bold;
                            z-index: 999;">
                    오답
                </div>
                ''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # Fixation cross + 자극 제시
        color_hex_map = {'red': '#FF0000', 'green': '#00FF00'}
        st.markdown(
            f'''
            <div class="fixation-cross">+</div>
            <div class="stimulus-container">
                <h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold; text-align:center;">{trial["text"]}</h1>
            </div>
            ''',
            unsafe_allow_html=True
        )

        # 반응시간 측정 시작
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        st.markdown("<br>", unsafe_allow_html=True)

        # 키보드 이벤트 리스너 (F, J) - 클라이언트 사이드 RT 측정
        from streamlit.components.v1 import html
        html(f"""
        <script>
        (function() {{
            const tryNum = {st.session_state.practice_trial_num};

            // 자극 표시 시점 기록 (CSS 애니메이션 0.5초 후 = 실제 자극 표시 시점)
            const FIXATION_DURATION = 500;  // ms
            window.stimulusShownTime = performance.now() + FIXATION_DURATION;
            console.log('Stimulus will be shown at:', window.stimulusShownTime);

            // Remove ALL previous listeners
            if (window.stroopKeyHandler) {{
                parent.document.removeEventListener('keydown', window.stroopKeyHandler);
            }}

            // Define new handler
            window.stroopKeyHandler = function(event) {{
                const code = event.code;  // Physical key code (KeyF, KeyJ)

                // Use event.code to detect physical keys (works with Korean/English keyboard)
                if (code !== 'KeyF' && code !== 'KeyJ') {{
                    return;
                }}

                event.preventDefault();
                event.stopPropagation();

                // 클라이언트 사이드 RT 계산
                const keyPressTime = performance.now();
                const clientRT = Math.max(0, keyPressTime - window.stimulusShownTime);
                console.log('Client RT:', clientRT.toFixed(2), 'ms');

                // RT를 localStorage에 저장 (Python에서 읽기 위함)
                localStorage.setItem('stroopClientRT', clientRT.toString());

                // Find and click buttons
                const allButtons = parent.document.querySelectorAll('button');
                let redBtn = null, greenBtn = null;

                allButtons.forEach((btn) => {{
                    const text = btn.textContent || btn.innerText;
                    if (text.includes('🔴') || text.includes('빨강')) redBtn = btn;
                    else if (text.includes('🟢') || text.includes('초록')) greenBtn = btn;
                }});

                // Click the appropriate button based on physical key code
                let targetBtn = null;
                if (code === 'KeyF') targetBtn = redBtn;
                else if (code === 'KeyJ') targetBtn = greenBtn;

                if (targetBtn) {{
                    targetBtn.click();
                }}
            }};

            // Add the new listener
            parent.document.addEventListener('keydown', window.stroopKeyHandler);
            console.log('Keyboard handler installed for trial', tryNum);
        }})();
        </script>
        """, height=0)

        # 반응 버튼
        col1, col2 = st.columns(2)

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

    이제 **본 과제**를 진행합니다.

    - **정답/오답 피드백은 제공되지 않습니다.**
    - 앞의 연습과 동일하게, **글자의 색깔만** 판단해주세요.
    - 키보드로 색깔을 선택하세요:
       - 🔴 **빨강**: **F** 키
       - 🟢 **초록**: **J** 키

    준비가 되면 아래 버튼을 눌러주세요.
    """)

    if st.button("본 과제 시작"):
        st.session_state.instructions_exp_shown = True
        # Experimental trials 생성
        st.session_state.exp_trials = create_exp_trials(n_per_condition=N_PER_CONDITION)
        st.rerun()

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

    # 블록 간 휴식 체크 (full 모드에서만 적용)
    current_block = st.session_state.trial_num // TRIALS_PER_BLOCK + 1
    is_block_start = (st.session_state.experiment_mode == "full" and
                      st.session_state.trial_num > 0 and
                      st.session_state.trial_num % TRIALS_PER_BLOCK == 0 and
                      st.session_state.trial_num < len(st.session_state.exp_trials))

    # 블록 시작 시 휴식 화면 표시
    if is_block_start and not st.session_state.showing_break:
        st.session_state.showing_break = True
        st.rerun()

    # 휴식 화면 표시 중
    if st.session_state.showing_break:
        completed_block = st.session_state.trial_num // TRIALS_PER_BLOCK
        st.markdown(f'''
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                    height: 60vh; color: white; text-align: center;">
            <h1 style="font-size: 48px; margin-bottom: 30px;">블록 {completed_block}/{NUM_BLOCKS} 완료!</h1>
            <p style="font-size: 28px; margin-bottom: 50px;">잠시 휴식하세요.</p>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("다음 블록 시작", key="continue_block", type="primary"):
            st.session_state.showing_break = False
            st.rerun()
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

    # Timeout 체크 (서버 사이드)
    if st.session_state.start_time is not None:
        elapsed = time.time() - st.session_state.start_time
        if elapsed >= MAX_RESPONSE_TIME + FIXATION_DURATION:
            # Timeout 발생
            record_response(trial, "timeout", is_timeout=True)
            st.stop()

    # Fixation cross + 자극 제시
    color_hex_map = {'red': '#FF0000', 'green': '#00FF00'}
    st.markdown(
        f'''
        <div class="fixation-cross">+</div>
        <div class="stimulus-container">
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
    html(f"""
    <script>
    (function() {{
        const tryNum = {st.session_state.trial_num};
        const MAX_RESPONSE_TIME = {int(MAX_RESPONSE_TIME * 1000)};  // ms

        // 자극 표시 시점 기록 (CSS 애니메이션 0.5초 후 = 실제 자극 표시 시점)
        const FIXATION_DURATION = 500;  // ms
        window.stimulusShownTime = performance.now() + FIXATION_DURATION;
        console.log('Stimulus will be shown at:', window.stimulusShownTime);

        // Timeout 플래그
        window.stroopResponseMade = false;

        // Remove ALL previous listeners and timers
        if (window.stroopKeyHandler) {{
            parent.document.removeEventListener('keydown', window.stroopKeyHandler);
        }}
        if (window.stroopTimeoutTimer) {{
            clearTimeout(window.stroopTimeoutTimer);
        }}

        // Timeout 핸들러 - 2초 후 자동으로 timeout 버튼 클릭
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
        }}, FIXATION_DURATION + MAX_RESPONSE_TIME);

        // Define new handler
        window.stroopKeyHandler = function(event) {{
            const code = event.code;  // Physical key code (KeyF, KeyJ)

            // Use event.code to detect physical keys (works with Korean/English keyboard)
            if (code !== 'KeyF' && code !== 'KeyJ') {{
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

            // Find and click buttons
            const allButtons = parent.document.querySelectorAll('button');
            let redBtn = null, greenBtn = null;

            allButtons.forEach((btn) => {{
                const text = btn.textContent || btn.innerText;
                if (text.includes('🔴') || text.includes('빨강')) redBtn = btn;
                else if (text.includes('🟢') || text.includes('초록')) greenBtn = btn;
            }});

            // Click the appropriate button based on physical key code
            let targetBtn = null;
            if (code === 'KeyF') targetBtn = redBtn;
            else if (code === 'KeyJ') targetBtn = greenBtn;

            if (targetBtn) {{
                targetBtn.click();
            }}
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
