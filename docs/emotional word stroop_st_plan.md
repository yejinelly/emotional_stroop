# Emotional Word Stroop - Streamlit 구현 계획

## 개요

**목표**: Streamlit을 사용하여 Emotional Word Stroop Task 웹 애플리케이션 구현

**참조 구현**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task)
- PsychoPy로 구현된 정서 Stroop 과제
- Trial-level randomization (ABCD EWEFS와 다름)
- 텍스트 전용 (얼굴 자극 없음)

**우리 버전의 차별점**:
- Streamlit 기반 웹 애플리케이션
- 한국어 번역 적용
- 반응시간 측정 및 CSV 저장

---

## 1단계: mario-bermonti 저장소에서 디자인 추출

### 1.1 저장소 클론
```bash
cd /Users/yejinlee/Documents/KPsych-101/정서과제
git clone https://github.com/mario-bermonti/emo_stroop_task.git
cd emo_stroop_task
```

### 1.2 핵심 파일 확인
- **`emo_stroop_task.py`**: PsychoPy 스크립트 (과제 로직)
- **`conditions/`**: Trial 조건 파일 (CSV)
- **`README.md`**: 과제 설명

### 1.3 추출할 정보
1. **단어 목록**: 긍정/부정 정서 단어
2. **색상 목록**: Stroop 과제에 사용되는 색상 (예: red, blue, green, yellow)
3. **조건 구조**: Congruent/Incongruent 정의
4. **타이밍**: 자극 제시 시간, ITI

---

## 2단계: 프로젝트 구조 설계

```
정서과제/
├── emotional_word_stroop/
│   ├── app.py                    # Streamlit 메인 앱
│   ├── stimuli/
│   │   ├── word_list.csv         # 단어 목록 (word, valence, arousal)
│   │   └── colors.csv            # 색상 목록 (color_name, hex_code)
│   ├── data/
│   │   └── responses/            # 참가자 반응 저장 폴더
│   ├── utils/
│   │   ├── trial_generator.py   # Trial 생성 로직
│   │   └── data_logger.py        # 데이터 저장 로직
│   └── requirements.txt          # Python 패키지 의존성
```

---

## 3단계: 단어 목록 준비

### 3.1 word_list.csv 구조
```csv
word,valence,arousal,word_ko
happy,positive,high,행복
sad,negative,high,슬픔
angry,negative,high,분노
calm,positive,low,평온
anxious,negative,high,불안
relaxed,positive,low,편안
```

### 3.2 단어 선정 기준
- **긍정 단어**: 25개 (예: happy, joy, love, peace, success)
- **부정 단어**: 25개 (예: sad, anger, fear, fail, loss)
- **각성 수준**: High arousal 우선 (Stroop 간섭 효과가 더 큼)
- **빈도**: 고빈도 단어 선호 (친숙도 통제)

### 3.3 colors.csv 구조
```csv
color_name,hex_code
red,#FF0000
blue,#0000FF
green,#00FF00
yellow,#FFFF00
```

---

## 4단계: Streamlit 앱 구현

### 4.1 app.py 기본 구조

```python
import streamlit as st
import pandas as pd
import time
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="Emotional Word Stroop Task",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Session state 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.trial_num = 0
    st.session_state.responses = []
    st.session_state.trials = None
    st.session_state.start_time = None
    st.session_state.participant_id = None
    st.session_state.task_started = False

# 1. 참가자 정보 입력 화면
if not st.session_state.task_started:
    st.title("Emotional Word Stroop Task")
    st.markdown("### 참가자 정보")

    participant_id = st.text_input("참가자 ID:")
    age = st.number_input("연령:", min_value=18, max_value=100, value=25)
    gender = st.selectbox("성별:", ["남성", "여성", "기타"])

    if st.button("과제 시작"):
        if participant_id:
            st.session_state.participant_id = participant_id
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.task_started = True
            st.session_state.initialized = True
            # Trial 생성
            st.session_state.trials = generate_trials()
            st.rerun()
        else:
            st.error("참가자 ID를 입력해주세요.")

    st.stop()

# 2. Instructions 화면
if not st.session_state.initialized:
    st.title("과제 안내")
    st.markdown("""
    ### 지시사항

    1. 화면에 색깔로 표시된 **단어**가 나타납니다.
    2. **단어의 의미는 무시**하고, **글자의 색깔만** 판단해주세요.
    3. 아래 버튼을 눌러 색깔을 선택하세요:
       - 🔴 빨강
       - 🔵 파랑
       - 🟢 초록
       - 🟡 노랑
    4. 최대한 **빠르고 정확하게** 반응해주세요.
    5. 총 **50번**의 시행이 진행됩니다.

    준비가 되면 아래 버튼을 눌러주세요.
    """)

    if st.button("시작하기", type="primary"):
        st.session_state.initialized = True
        st.rerun()

    st.stop()

# 3. Task 화면
if st.session_state.trial_num < len(st.session_state.trials):
    trial = st.session_state.trials.iloc[st.session_state.trial_num]

    # Progress bar
    st.progress((st.session_state.trial_num + 1) / len(st.session_state.trials))
    st.caption(f"Trial {st.session_state.trial_num + 1} / {len(st.session_state.trials)}")

    # Fixation cross (500ms 대신 즉시 자극 제시)
    # Streamlit은 정확한 타이밍 어려워서 fixation 생략

    # 자극 제시
    st.markdown(
        f'<h1 style="text-align:center; color:{trial["color_hex"]}; font-size:72px;">{trial["word"]}</h1>',
        unsafe_allow_html=True
    )

    # 반응시간 측정 시작
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    # 반응 버튼 (4개 색상)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔴 빨강", key=f"red_{st.session_state.trial_num}"):
            record_response(trial, "red")

    with col2:
        if st.button("🔵 파랑", key=f"blue_{st.session_state.trial_num}"):
            record_response(trial, "blue")

    with col3:
        if st.button("🟢 초록", key=f"green_{st.session_state.trial_num}"):
            record_response(trial, "green")

    with col4:
        if st.button("🟡 노랑", key=f"yellow_{st.session_state.trial_num}"):
            record_response(trial, "yellow")

else:
    # 4. 완료 화면
    st.title("과제 완료!")
    st.success("모든 시행을 완료했습니다. 감사합니다!")

    # 데이터 저장
    save_data()

    # 기술통계 표시
    df_responses = pd.DataFrame(st.session_state.responses)
    st.markdown("### 수행 결과")
    st.metric("전체 정확도", f"{df_responses['accuracy'].mean():.1%}")
    st.metric("평균 반응시간", f"{df_responses['rt'].mean():.2f}초")

    # 다운로드 버튼
    csv = df_responses.to_csv(index=False)
    st.download_button(
        label="데이터 다운로드 (CSV)",
        data=csv,
        file_name=f"stroop_{st.session_state.participant_id}.csv",
        mime="text/csv"
    )


# Helper functions
def generate_trials():
    """Trial 생성 함수"""
    words_df = pd.read_csv("stimuli/word_list.csv")
    colors_df = pd.read_csv("stimuli/colors.csv")

    trials = []
    for _, word_row in words_df.iterrows():
        for _, color_row in colors_df.iterrows():
            trials.append({
                'word': word_row['word'],
                'valence': word_row['valence'],
                'color_name': color_row['color_name'],
                'color_hex': color_row['hex_code'],
                'congruency': 'congruent' if is_congruent(word_row['word'], color_row['color_name']) else 'incongruent'
            })

    trials_df = pd.DataFrame(trials)
    # Randomize
    trials_df = trials_df.sample(frac=1).reset_index(drop=True)
    return trials_df

def is_congruent(word, color):
    """Congruency 판단 (정서가-색상 매칭)"""
    # 예: positive words = warm colors (red, yellow)
    #     negative words = cool colors (blue, green)
    positive_words = ['happy', 'joy', 'love', 'peace']
    warm_colors = ['red', 'yellow']

    if word in positive_words and color in warm_colors:
        return True
    elif word not in positive_words and color not in warm_colors:
        return True
    else:
        return False

def record_response(trial, response):
    """반응 기록 및 다음 trial로 이동"""
    rt = time.time() - st.session_state.start_time

    st.session_state.responses.append({
        'trial_num': st.session_state.trial_num + 1,
        'word': trial['word'],
        'valence': trial['valence'],
        'color_name': trial['color_name'],
        'congruency': trial['congruency'],
        'response': response,
        'accuracy': 1 if response == trial['color_name'] else 0,
        'rt': rt
    })

    st.session_state.trial_num += 1
    st.session_state.start_time = None
    st.rerun()

def save_data():
    """데이터 CSV 저장"""
    df = pd.DataFrame(st.session_state.responses)
    output_dir = Path("data/responses")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{st.session_state.participant_id}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_dir / filename, index=False)
```

---

## 5단계: 핵심 기능 구현

### 5.1 Session State 관리
Streamlit은 페이지가 새로고침될 때마다 스크립트가 재실행되므로, `st.session_state`로 상태 유지:

```python
if 'trial_num' not in st.session_state:
    st.session_state.trial_num = 0
    st.session_state.responses = []
    st.session_state.start_time = None
```

### 5.2 반응시간 측정
- `time.time()`으로 자극 제시 시점 기록
- 버튼 클릭 시점과의 차이 계산
- **주의**: Streamlit은 JavaScript가 아니므로 밀리초 단위 정확도는 제한적

```python
# 자극 제시 시 시작
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()

# 반응 시 측정
rt = time.time() - st.session_state.start_time
```

### 5.3 색상 표시
HTML/CSS로 단어에 색상 적용:

```python
st.markdown(
    f'<h1 style="color:{color_hex}; text-align:center;">{word}</h1>',
    unsafe_allow_html=True
)
```

### 5.4 데이터 저장 형식

**출력 CSV 예시** (`data/responses/P001_20250101_120000.csv`):
```csv
trial_num,word,valence,color_name,congruency,response,accuracy,rt
1,happy,positive,red,congruent,red,1,0.823
2,sad,negative,blue,congruent,green,0,1.234
3,angry,negative,yellow,incongruent,yellow,1,0.956
```

---

## 6단계: 실행 및 테스트

### 6.1 의존성 설치
```bash
# requirements.txt
streamlit>=1.28.0
pandas>=2.0.0
```

```bash
pip install -r requirements.txt
```

### 6.2 로컬 실행
```bash
cd /Users/yejinlee/Documents/KPsych-101/정서과제/emotional_word_stroop
streamlit run app.py
```

### 6.3 테스트 체크리스트
- [ ] 참가자 ID 입력 화면 작동
- [ ] Instructions 화면 표시
- [ ] 단어가 지정된 색상으로 표시
- [ ] 버튼 클릭 시 반응 기록
- [ ] 다음 trial로 자동 진행
- [ ] 50 trials 완료 후 결과 화면
- [ ] CSV 파일 저장 확인
- [ ] 정확도/반응시간 계산 정확성

---

## 7단계: 향후 확장 계획

### 7.1 Block Design 옵션 추가
- ABCD EWEFS 스타일로 congruent/incongruent 블록 분리
- `st.selectbox`로 "Trial-level randomization" vs "Block design" 선택

### 7.2 EEG 호환성
- Trial onset marker를 LSL (Lab Streaming Layer)로 전송
- `pylsl` 패키지 사용

```bash
pip install pylsl
```

```python
from pylsl import StreamInfo, StreamOutlet

# LSL 마커 스트림 생성
info = StreamInfo('StroopMarkers', 'Markers', 1, 0, 'string', 'myuid34234')
outlet = StreamOutlet(info)

# Trial 시작 시 마커 전송
outlet.push_sample([f'trial_{trial_num}_onset'])
```

---

## 타임라인

| 단계 | 소요 시간 | 산출물 |
|------|-----------|--------|
| 1. mario-bermonti 분석 | 1-2시간 | 단어 목록, 디자인 문서 |
| 2. 프로젝트 설정 | 30분 | 폴더 구조, requirements.txt |
| 3. 단어 목록 준비 | 2-3시간 | word_list.csv, colors.csv |
| 4. Streamlit 기본 구현 | 4-6시간 | app.py (기본 버전) |
| 5. 테스트 및 디버깅 | 2-3시간 | 작동하는 앱 |
| **총 예상 시간** | **1-2일** | 배포 가능한 웹앱 |

---

## 참고 자료

### Emotional Word Stroop 관련 논문
- Baskin-Sommers et al. (2022). The Emotional Word-Emotional Face Stroop task in the ABCD study. *Developmental Cognitive Neuroscience*, 53, 101054.
- Joyal et al. (2019). Characterizing emotional Stroop interference in PTSD, MDD, and anxiety. *PLOS One*, 14(4), e0214998.

### Streamlit 문서
- [Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Custom CSS](https://docs.streamlit.io/library/api-reference/utilities/st.markdown)
- [File Upload/Download](https://docs.streamlit.io/library/api-reference/widgets/st.download_button)

---

## 주의사항

### Streamlit 제약사항
1. **반응시간 정확도**: JavaScript 기반 PsychoPy/jsPsych보다 10-50ms 오차 가능
   - 연구용으로 사용 시 pilot test로 검증 필요
2. **타이밍 제어**: 정확한 자극 제시 시간(예: 250ms) 구현 어려움
   - 웹 브라우저 렌더링 지연 변동성
3. **전체화면 모드**: Streamlit은 기본적으로 전체화면 지원 안 함
   - Custom JavaScript로 구현 가능하나 복잡함

### 권장 사항
- **파일럿 테스트**: 5-10명으로 반응시간 신뢰도 확인
- **PsychoPy와 비교**: 동일 조건에서 RT 차이 측정
- **연구용 vs 교육용**: 교육/데모용으로는 충분, 정밀 연구용은 PsychoPy/jsPsych 권장

---

## 다음 단계

1. **즉시 시작 가능**:
   - mario-bermonti 저장소 클론
   - 단어 목록 작성 (word_list.csv)
   - Streamlit 기본 앱 구현

2. **완료 후**:
   - Emotional Inference Task (EIT) 구현 준비
   - DCAM 프로토콜 기반 재구현
