# Emotional Word Stroop 타이밍 및 화면 설정 검토

**검토일**: 2025-12-30
**검토 대상**: stroop_streamlit_full.py, stroop_streamlit_short.py

---

## 1. 현재 타이밍 구현 상태 ❌

### GitHub 원본 (PsychoPy) 타이밍

#### Practice Trials:
```
1. Instructions
2. Fixation cross: 1.0초 ✓
3. Blank screen: 0.5초 ✓
4. Word stimulus: 반응 시까지 ✓
5. Feedback: 정답/오답 표시 ✓
```

#### Experimental Trials:
```
1. Instructions
2. Fixation cross: 0.5초 ✓
3. Blank screen: 0.5초 ✓
4. Word stimulus: 반응 시까지 ✓
5. No feedback ✓
```

---

### 우리 구현 (stroop_streamlit_full.py, stroop_streamlit_short.py) 타이밍

#### Practice Trials:
```
1. Instructions ✓
2. Fixation cross: ❌ 없음 (주석만 있음)
3. Blank screen: ❌ 없음
4. Word stimulus: 즉시 표시 (반응 시까지) ✓
5. Feedback: 정답/오답 표시 ✓
```

#### Experimental Trials:
```
1. Instructions ✓
2. Fixation cross: ❌ 없음
3. Blank screen: ❌ 없음
4. Word stimulus: 즉시 표시 (반응 시까지) ✓
5. No feedback ✓
```

---

## 2. 문제점 분석

### 2.1 Fixation Cross 미구현

**현재 코드** (app_v2.py:179-180):
```python
# Fixation cross (간단히 표시)
st.markdown("<br>" * 2, unsafe_allow_html=True)
```

**문제점**:
- 실제로 fixation cross (+)가 표시되지 않음
- 단순히 공백만 추가됨
- `st.session_state.show_fixation` 변수가 사용되지 않음

**기대 동작**:
- 화면 중앙에 **+** 표시
- Practice: 1.0초 동안 표시
- Experimental: 0.5초 동안 표시

---

### 2.2 Blank Screen (ISI) 미구현

**문제점**:
- Blank screen이 전혀 없음
- Fixation → Word로 즉시 전환

**기대 동작**:
- Fixation cross 후 0.5초 동안 빈 화면
- Inter-Stimulus Interval (ISI) 역할

---

### 2.3 타이밍 제어 불가능

**Streamlit의 근본적 한계**:
```python
# ❌ 작동하지 않음
time.sleep(1.0)  # Streamlit은 전체 스크립트를 rerun하므로 의미 없음
st.rerun()       # 페이지 전체 새로고침
```

**문제점**:
- Streamlit은 상태 변경 시 전체 스크립트를 다시 실행
- `time.sleep()`은 화면을 멈추게 하지만 사용자는 아무것도 볼 수 없음
- 정확한 밀리초 단위 제어 불가능

---

### 2.4 반응시간 측정 정확도

**현재 코드** (app_v2.py:198-199, 326-327):
```python
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()
```

**문제점**:
- `time.time()` 호출 시점이 불명확 (Streamlit rerun 시마다 변경 가능)
- 버튼 렌더링 시간이 포함됨
- 실제 자극 표시 시점과 정확히 일치하지 않을 수 있음

**측정 정확도**:
- ⚠️ 약 50-100ms 오차 가능 (웹 기반 한계)
- PsychoPy: 1-2ms 정확도
- 우리 구현: ~50-100ms 정확도 (추정)

---

## 3. 화면 설정 문제

### 3.1 화면 크기 고정 없음

**현재 상태**:
- Streamlit 기본 레이아웃 사용 (`layout="centered"`)
- 브라우저 창 크기에 따라 자극 크기 변동
- 전체화면 vs 창 모드에서 단어 크기가 달라짐

**문제점**:
```
작은 창:          큰 창:           전체화면:
  행복            행복             행복
 (작음)          (중간)           (매우 큼)
```

**기대 동작**:
- 단어 크기 고정 (예: 화면 높이의 10%)
- 자극 제시 영역 고정 (예: 800px × 600px)

---

### 3.2 전체화면 모드 없음

**현재 상태**:
- 일반 브라우저 창에서 실행
- 주소창, 탭, 사이드바 등이 보임
- 참가자가 다른 창으로 이동 가능

**문제점**:
- 주의 산만 (다른 탭, 알림 등)
- 화면 크기 일관성 없음
- 전문적이지 않은 외관

**기대 동작**:
- 전체화면 권장 (F11 안내)
- 또는 JavaScript로 전체화면 자동 전환

---

### 3.3 자극 위치 일관성 부족

**현재 코드** (app_v2.py:192-195):
```python
st.markdown(
    f'<div style="text-align:center;"><h1 style="color:{color_hex_map[trial["letterColor"]]}; font-size:80px; font-weight:bold;">{trial["text"]}</h1></div>',
    unsafe_allow_html=True
)
```

**문제점**:
- `font-size: 80px` 고정 → 화면 크기에 따라 상대적 위치 변동
- Progress bar, caption 등이 위에 있어서 자극 위치가 매번 달라짐

**기대 동작**:
- 자극은 항상 화면 중앙에 고정
- 다른 UI 요소와 분리

---

## 4. 개선 방안

### 4.1 타이밍 개선 (Streamlit-JavaScript 활용)

**방법 1**: `streamlit-javascript` 컴포넌트 사용

```python
import streamlit as st
from streamlit_javascript import st_javascript

# Fixation cross 표시
st.markdown('<div style="text-align:center; font-size:80px;">+</div>', unsafe_allow_html=True)

# JavaScript로 1000ms 대기
st_javascript("""
await new Promise(r => setTimeout(r, 1000));
""")

# Blank screen
st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
st_javascript("""
await new Promise(r => setTimeout(r, 500));
""")

# Word stimulus
st.markdown(f'<div style="text-align:center; font-size:80px; color:red;">단어</div>', unsafe_allow_html=True)
```

**장점**:
- 실제 시간 제어 가능
- 비동기 처리

**단점**:
- Streamlit rerun과 충돌 가능
- 복잡한 상태 관리 필요
- `streamlit-javascript` 패키지 설치 필요

---

**방법 2**: Session state + Timer (제한적)

```python
# Session state에 timestamp 저장
if 'fixation_start' not in st.session_state:
    st.session_state.fixation_start = time.time()
    st.session_state.phase = 'fixation'

elapsed = time.time() - st.session_state.fixation_start

if st.session_state.phase == 'fixation':
    st.markdown('<div style="text-align:center; font-size:80px;">+</div>', unsafe_allow_html=True)
    if elapsed > 0.5:
        st.session_state.phase = 'blank'
        st.session_state.fixation_start = time.time()
        st.rerun()

elif st.session_state.phase == 'blank':
    st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
    if elapsed > 0.5:
        st.session_state.phase = 'word'
        st.rerun()

elif st.session_state.phase == 'word':
    # Show word and buttons
    pass
```

**장점**:
- 추가 패키지 불필요
- Streamlit 네이티브 방식

**단점**:
- rerun으로 인한 깜빡임
- 정확도 낮음 (~100ms 오차)
- 화면 전환이 부드럽지 않음

---

**방법 3**: 현실적 절충안 (권장)

**Practice trials**:
- ✅ Fixation cross 표시 (시간 제어 없이 "준비" 버튼으로 전환)
- ❌ Blank screen 생략
- ✅ Word stimulus
- ✅ Feedback

**Experimental trials**:
- ❌ Fixation cross 생략 (또는 매우 짧게)
- ❌ Blank screen 생략
- ✅ Word stimulus

**이유**:
- Streamlit의 근본적 한계 인정
- 사용자 경험 우선 (깜빡임, 지연 최소화)
- 반응시간 측정은 여전히 유효 (절대값보다 조건 간 차이가 중요)

---

### 4.2 화면 설정 개선

#### Option 1: 고정 크기 컨테이너

```python
st.markdown("""
<style>
    .main .block-container {
        max-width: 800px;
        padding: 2rem;
    }

    .stApp {
        background-color: #f0f0f0;
    }

    /* 자극 제시 영역 고정 */
    .stimulus-container {
        width: 800px;
        height: 600px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# 자극 제시
st.markdown(f"""
<div class="stimulus-container">
    <h1 style="color:{color}; font-size:80px; font-weight:bold;">{word}</h1>
</div>
""", unsafe_allow_html=True)
```

---

#### Option 2: 반응형 크기 (vw/vh 단위)

```python
st.markdown("""
<style>
    /* 단어 크기를 화면 높이의 15%로 고정 */
    .stimulus-word {
        font-size: 15vh;
        text-align: center;
        font-weight: bold;
        margin: 20vh 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="stimulus-word" style="color:{color};">{word}</div>', unsafe_allow_html=True)
```

---

#### Option 3: 전체화면 안내

```python
# Instructions에 추가
st.markdown("""
### 실험 전 준비

1. **전체화면 모드로 전환**해주세요:
   - Windows: `F11` 키
   - Mac: `Command + Control + F`
2. 알림, 다른 앱을 모두 종료해주세요.
3. 조용한 환경에서 진행해주세요.

준비가 되면 아래 버튼을 눌러주세요.
""")
```

**또는 JavaScript로 자동 전체화면**:
```python
from streamlit.components.v1 import html

html("""
<script>
function requestFullscreen() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    }
}
</script>
<button onclick="requestFullscreen()">전체화면으로 시작</button>
""", height=100)
```

---

#### Option 4: Streamlit 사이드바/헤더 숨기기

```python
st.markdown("""
<style>
    /* Streamlit 헤더 숨기기 */
    header {visibility: hidden;}

    /* Streamlit 메뉴 버튼 숨기기 */
    #MainMenu {visibility: hidden;}

    /* Footer 숨기기 */
    footer {visibility: hidden;}

    /* Padding 제거 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
</style>
""", unsafe_allow_html=True)
```

---

## 5. 권장 개선 사항 우선순위

### 🔴 필수 (High Priority):
1. **화면 크기 일관성 확보**
   - CSS로 자극 크기를 `vh` 단위로 고정
   - 예: `font-size: 12vh` (화면 높이의 12%)

2. **전체화면 안내 추가**
   - Instructions에 전체화면 권장 메시지
   - F11 / Command+Control+F 안내

3. **Streamlit UI 요소 숨기기**
   - 헤더, 메뉴, footer 제거
   - 깔끔한 실험 화면

### 🟡 권장 (Medium Priority):
4. **자극 위치 고정**
   - Progress bar를 자극 아래로 이동
   - 또는 고정 높이 컨테이너 사용

5. **Fixation cross 추가 (간단히)**
   - 시간 제어 없이 + 기호만 표시
   - "다음" 버튼으로 전환 (또는 자동 전환)

### 🟢 선택 (Low Priority):
6. **타이밍 정확도 개선**
   - `streamlit-javascript` 시도 (복잡함)
   - 또는 현재대로 유지 (반응시간 상대 비교는 여전히 유효)

7. **Blank screen 추가**
   - 우선순위 낮음 (Streamlit에서 구현 어려움)

---

## 6. 구현 계획

### Phase 1: 화면 설정 개선 (즉시 적용 가능)
- [ ] CSS로 자극 크기 `vh` 단위로 변경
- [ ] Streamlit UI 요소 숨기기 (헤더, 메뉴, footer)
- [ ] 전체화면 안내 메시지 추가
- [ ] 고정 컨테이너 추가

→ **app_v2_improved.py** 생성

### Phase 2: 최소한의 타이밍 개선 (선택)
- [ ] Fixation cross 추가 (+ 기호 표시)
- [ ] Session state로 간단한 단계 전환

→ **app_v2_timing.py** 생성 (실험적)

### Phase 3: JavaScript 기반 타이밍 (고급, 선택)
- [ ] `streamlit-javascript` 설치 및 테스트
- [ ] Fixation cross 1.0s/0.5s 제어
- [ ] Blank screen 0.5s 제어

→ **app_v2_advanced.py** 생성 (연구용)

---

## 7. 타이밍 정확도 비교

| 구현 | Fixation | Blank | RT 정확도 | 사용자 경험 | 난이도 |
|------|----------|-------|-----------|------------|--------|
| **GitHub 원본 (PsychoPy)** | ✅ 1.0s/0.5s | ✅ 0.5s | ✅ ~1ms | ⭐⭐⭐⭐⭐ | 높음 (전용 SW) |
| **현재 (app_v2.py)** | ❌ 없음 | ❌ 없음 | ⚠️ ~50-100ms | ⭐⭐⭐⭐ | 낮음 |
| **개선안 Phase 1** | ⚠️ 표시만 | ❌ 없음 | ⚠️ ~50-100ms | ⭐⭐⭐⭐⭐ | 낮음 |
| **개선안 Phase 2** | ⚠️ ~200ms 오차 | ❌ 없음 | ⚠️ ~50-100ms | ⭐⭐⭐ | 중간 (깜빡임) |
| **개선안 Phase 3** | ✅ ~50ms 오차 | ⚠️ ~50ms 오차 | ⚠️ ~50-100ms | ⭐⭐⭐⭐ | 높음 (복잡) |

**결론**: Phase 1 권장 (화면 설정만 개선)

---

## 8. 반응시간 데이터 해석 시 주의사항

### Streamlit 구현의 한계:
- 절대 반응시간: ±50-100ms 오차 가능
- 조건 간 상대 비교: ✅ 여전히 유효

### 분석 시 권장:
1. **조건 간 차이 분석 우선**
   - Negative vs Neutral vs Positive RT 비교
   - 각 조건 내 일관성 확인

2. **절대값 해석 주의**
   - "평균 RT 500ms"보다는
   - "Negative가 Neutral보다 50ms 느림"

3. **이상치 제거**
   - 극단적으로 빠른 반응 (<200ms) 제거
   - 극단적으로 느린 반응 (>3000ms) 제거

---

*작성일: 2025-12-30*
*검토자: Claude*
*다음 단계: 개선안 구현 여부 결정*
