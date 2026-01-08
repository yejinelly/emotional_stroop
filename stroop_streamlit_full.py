import streamlit as st
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import random

# Google Sheets 백업용
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

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


def create_practice_trials():
    """Practice trials 생성 - 6 trials (색상 단어, congruent)"""
    color_words = [
        {'text': '빨강', 'letterColor': 'red', 'corrAns': 'red', 'condition': 'practice'},
        {'text': '파랑', 'letterColor': 'blue', 'corrAns': 'blue', 'condition': 'practice'},
        {'text': '초록', 'letterColor': 'green', 'corrAns': 'green', 'condition': 'practice'},
        {'text': '빨강', 'letterColor': 'red', 'corrAns': 'red', 'condition': 'practice'},
        {'text': '파랑', 'letterColor': 'blue', 'corrAns': 'blue', 'condition': 'practice'},
        {'text': '초록', 'letterColor': 'green', 'corrAns': 'green', 'condition': 'practice'},
    ]
    trials = pd.DataFrame(color_words)
    return trials.sample(frac=1).reset_index(drop=True)


def create_exp_trials(n_per_condition=10):
    """Experimental trials 생성 - final_144_words.csv에서 조건별 n개씩 선택

    Args:
        n_per_condition: 조건별 단어 수 (기본 10 = pilot, 최대 48 = full)
    """

    # final_144_words.csv에서 단어 로드
    stimuli_path = Path("stimuli/final_144_words.csv")
    df = pd.read_csv(stimuli_path)

    colors = ['red', 'blue', 'green']

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


def record_response(trial, response, is_practice=False):
    """반응 기록 함수"""
    rt = time.time() - st.session_state.start_time

    correct_answer = trial.get('corrAns', trial.get('letterColor'))
    accuracy = 1 if response == correct_answer else 0

    response_data = {
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
    st.caption("🧪 Pilot: 30 trials (10 × 3 conditions)")

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


# 2. Practice Instructions
if not st.session_state.practice_completed:
    if not st.session_state.practice_instructions_shown:
        st.title("📋 연습 과제 안내")
        st.markdown("""
        ### 지시사항

        1. 화면에 **색깔로 표시된 단어**가 나타납니다.
        2. **단어의 의미는 무시**하고, **글자의 색깔만** 판단해주세요.
        3. 키보드로 색깔을 선택하세요:
           - 🔴 **빨강**: **F** 키
           - 🟢 **초록**: **J** 키
           - 🔵 **파랑**: **Space bar**

        먼저 **연습 시행 6번**을 진행합니다. 정답/오답 피드백이 제공됩니다.

        준비가 되면 아래 버튼을 눌러주세요.
        """)

        if st.button("연습 시작"):
            st.session_state.practice_instructions_shown = True
            st.rerun()

        st.stop()

    # Practice Trial 진행
    if st.session_state.practice_trial_num < len(st.session_state.practice_trials):
        trial = st.session_state.practice_trials.iloc[st.session_state.practice_trial_num]

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
        color_hex_map = {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}
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

        # 키보드 이벤트 리스너 (F, J, Space)
        from streamlit.components.v1 import html
        html(f"""
        <script>
        (function() {{
            const tryNum = {st.session_state.practice_trial_num};

            // Remove ALL previous listeners
            if (window.stroopKeyHandler) {{
                parent.document.removeEventListener('keydown', window.stroopKeyHandler);
            }}

            // Define new handler
            window.stroopKeyHandler = function(event) {{
                const code = event.code;  // Physical key code (KeyF, KeyJ, Space)

                console.log('Key code:', code, 'Key:', event.key);

                // Use event.code to detect physical keys (works with Korean/English keyboard)
                if (code !== 'Space' && code !== 'KeyF' && code !== 'KeyJ') {{
                    return;
                }}

                event.preventDefault();
                event.stopPropagation();

                console.log('Handling key code:', code);

                // Wait for DOM to be ready, then find buttons
                setTimeout(function() {{
                    // Try multiple methods to find buttons
                    const allButtons = parent.document.querySelectorAll('button');
                    console.log('Total buttons found:', allButtons.length);

                    let redBtn = null, blueBtn = null, greenBtn = null;

                    allButtons.forEach((btn, idx) => {{
                        const text = btn.textContent || btn.innerText;
                        console.log('Button', idx, ':', text);

                        if (text.includes('🔴') || text.includes('빨강')) {{
                            redBtn = btn;
                            console.log('Found RED button');
                        }} else if (text.includes('🔵') || text.includes('파랑')) {{
                            blueBtn = btn;
                            console.log('Found BLUE button');
                        }} else if (text.includes('🟢') || text.includes('초록')) {{
                            greenBtn = btn;
                            console.log('Found GREEN button');
                        }}
                    }});

                    // Click the appropriate button based on physical key code
                    let targetBtn = null;
                    if (code === 'KeyF') {{
                        targetBtn = redBtn;
                        console.log('F key (KeyF) -> Red button:', !!redBtn);
                    }} else if (code === 'Space') {{
                        targetBtn = blueBtn;
                        console.log('Space key -> Blue button:', !!blueBtn);
                    }} else if (code === 'KeyJ') {{
                        targetBtn = greenBtn;
                        console.log('J key (KeyJ) -> Green button:', !!greenBtn);
                    }}

                    if (targetBtn) {{
                        console.log('Clicking button!');
                        targetBtn.click();
                    }} else {{
                        console.log('No button to click!');
                    }}
                }}, 100);
            }};

            // Add the new listener
            parent.document.addEventListener('keydown', window.stroopKeyHandler);
            console.log('Keyboard handler installed for trial', tryNum);
        }})();
        </script>
        """, height=0)

        # 반응 버튼
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔴 빨강", key=f"practice_red_{st.session_state.practice_trial_num}", use_container_width=True, type="primary"):
                record_response(trial, "red", is_practice=True)

        with col2:
            if st.button("🔵 파랑", key=f"practice_blue_{st.session_state.practice_trial_num}", use_container_width=True, type="primary"):
                record_response(trial, "blue", is_practice=True)

        with col3:
            if st.button("🟢 초록", key=f"practice_green_{st.session_state.practice_trial_num}", use_container_width=True, type="primary"):
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

    이제 **본 과제 30번**을 진행합니다.

    - **정답/오답 피드백은 제공되지 않습니다.**
    - 앞의 연습과 동일하게, **글자의 색깔만** 판단해주세요.
    - 키보드로 색깔을 선택하세요:
       - 🔴 **빨강**: **F** 키
       - 🟢 **초록**: **J** 키
       - 🔵 **파랑**: **Space bar**

    준비가 되면 아래 버튼을 눌러주세요.
    """)

    if st.button("본 과제 시작"):
        st.session_state.instructions_exp_shown = True
        # Experimental trials 생성
        st.session_state.exp_trials = create_exp_trials()
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
    trial = st.session_state.exp_trials.iloc[st.session_state.trial_num]

    # Fixation cross + 자극 제시
    color_hex_map = {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}
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

    # 키보드 이벤트 리스너 (F, J, Space)
    from streamlit.components.v1 import html
    html(f"""
    <script>
    (function() {{
        const tryNum = {st.session_state.trial_num};

        // Remove ALL previous listeners
        if (window.stroopKeyHandler) {{
            parent.document.removeEventListener('keydown', window.stroopKeyHandler);
        }}

        // Define new handler
        window.stroopKeyHandler = function(event) {{
            const code = event.code;  // Physical key code (KeyF, KeyJ, Space)

            console.log('Key code:', code, 'Key:', event.key);

            // Use event.code to detect physical keys (works with Korean/English keyboard)
            if (code !== 'Space' && code !== 'KeyF' && code !== 'KeyJ') {{
                return;
            }}

            event.preventDefault();
            event.stopPropagation();

            console.log('Handling key code:', code);

            // Wait for DOM to be ready, then find buttons
            setTimeout(function() {{
                // Try multiple methods to find buttons
                const allButtons = parent.document.querySelectorAll('button');
                console.log('Total buttons found:', allButtons.length);

                let redBtn = null, blueBtn = null, greenBtn = null;

                allButtons.forEach((btn, idx) => {{
                    const text = btn.textContent || btn.innerText;
                    console.log('Button', idx, ':', text);

                    if (text.includes('🔴') || text.includes('빨강')) {{
                        redBtn = btn;
                        console.log('Found RED button');
                    }} else if (text.includes('🔵') || text.includes('파랑')) {{
                        blueBtn = btn;
                        console.log('Found BLUE button');
                    }} else if (text.includes('🟢') || text.includes('초록')) {{
                        greenBtn = btn;
                        console.log('Found GREEN button');
                    }}
                }});

                // Click the appropriate button based on physical key code
                let targetBtn = null;
                if (code === 'KeyF') {{
                    targetBtn = redBtn;
                    console.log('F key (KeyF) -> Red button:', !!redBtn);
                }} else if (code === 'Space') {{
                    targetBtn = blueBtn;
                    console.log('Space key -> Blue button:', !!blueBtn);
                }} else if (code === 'KeyJ') {{
                    targetBtn = greenBtn;
                    console.log('J key (KeyJ) -> Green button:', !!greenBtn);
                }}

                if (targetBtn) {{
                    console.log('Clicking button!');
                    targetBtn.click();
                }} else {{
                    console.log('No button to click!');
                }}
            }}, 100);
        }};

        // Add the new listener
        parent.document.addEventListener('keydown', window.stroopKeyHandler);
        console.log('Keyboard handler installed for trial', tryNum);
    }})();
    </script>
    """, height=0)

    # 반응 버튼
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 빨강", key=f"red_{st.session_state.trial_num}", use_container_width=True, type="primary"):
            record_response(trial, "red")

    with col2:
        if st.button("🔵 파랑", key=f"blue_{st.session_state.trial_num}", use_container_width=True, type="primary"):
            record_response(trial, "blue")

    with col3:
        if st.button("🟢 초록", key=f"green_{st.session_state.trial_num}", use_container_width=True, type="primary"):
            record_response(trial, "green")

else:
    st.session_state.task_completed = True
    st.rerun()
