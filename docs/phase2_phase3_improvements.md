# Phase 2 & Phase 3 개선 방안 (선택사항)

**작성일**: 2025-12-30
**상태**: 선택적 구현 (Phase 1 완료 후 필요시)

---

## 현재 상태

✅ **Phase 1 완료** (app_v2_improved.py)
- CSS로 자극 크기 vh 단위 고정
- Streamlit UI 숨기기
- 전체화면 안내 추가
- 자극 위치 일관성 확보

---

## Phase 2: 최소한의 타이밍 개선

### 목표
- Fixation cross (+) 표시
- Session state로 간단한 단계 전환
- JavaScript 없이 Streamlit만으로 구현

### 구현 방법

#### 1. Fixation Cross 표시

```python
# Session state에 단계 추가
if 'trial_phase' not in st.session_state:
    st.session_state.trial_phase = 'fixation'  # fixation → word → response
    st.session_state.phase_start_time = time.time()

if st.session_state.trial_phase == 'fixation':
    # Fixation cross 표시
    st.markdown(
        '<div class="stimulus-word" style="color: #000000;">+</div>',
        unsafe_allow_html=True
    )

    # 0.5초 경과 확인 (정확도 낮음)
    if time.time() - st.session_state.phase_start_time > 0.5:
        st.session_state.trial_phase = 'word'
        st.session_state.start_time = time.time()  # RT 측정 시작
        st.rerun()

elif st.session_state.trial_phase == 'word':
    # Word stimulus 표시
    st.markdown(
        f'<div class="stimulus-word" style="color:{color};">{word}</div>',
        unsafe_allow_html=True
    )

    # 버튼 클릭 → record_response() → trial_phase = 'fixation' (다음 trial)
```

### 장점
- Fixation cross가 실제로 표시됨
- 추가 패키지 불필요

### 단점
- ❌ 화면 깜빡임 (st.rerun() 때문)
- ❌ 타이밍 정확도 낮음 (~100-200ms 오차)
- ❌ 사용자 경험 저하 (지연 및 깜빡임)
- ❌ 코드 복잡도 증가

### 권장 여부
⚠️ **비권장**
- 화면 깜빡임이 오히려 과제에 방해가 됨
- 타이밍 정확도도 낮아서 실효성 낮음
- Phase 1만으로 충분

---

## Phase 3: JavaScript 기반 타이밍 제어 (고급)

### 목표
- 실제 타이밍 제어 (오차 ~50ms)
- Fixation cross 0.5s/1.0s 정확 제어
- Blank screen (ISI) 0.5s 추가

### 필요 패키지
```bash
pip install streamlit-javascript
```

또는

```bash
pip install streamlit-components-bridge
```

### 구현 방법 (예시)

#### 1. streamlit-javascript 사용

```python
from streamlit_javascript import st_javascript

# Trial 시작
trial = st.session_state.exp_trials.iloc[st.session_state.trial_num]

# Step 1: Fixation cross
st.markdown('<div id="fixation" class="stimulus-word">+</div>', unsafe_allow_html=True)

# JavaScript로 500ms 대기
st_javascript("""
await new Promise(r => setTimeout(r, 500));
document.getElementById('fixation').style.display = 'none';
""")

# Step 2: Blank screen
st.markdown('<div id="blank" class="stimulus-word"></div>', unsafe_allow_html=True)
st_javascript("""
await new Promise(r => setTimeout(r, 500));
document.getElementById('blank').style.display = 'none';
""")

# Step 3: Word stimulus
color_hex_map = {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}
st.markdown(
    f'<div id="word" class="stimulus-word" style="color:{color_hex_map[trial["letterColor"]]};">{trial["text"]}</div>',
    unsafe_allow_html=True
)

# RT 측정 시작 (JavaScript timestamp)
st_javascript("""
window.stimulusStartTime = performance.now();
""")

# 버튼 클릭 시 RT 계산
if st.button("🔴 빨강"):
    rt_js = st_javascript("""
    return performance.now() - window.stimulusStartTime;
    """)
    # rt_js는 밀리초 단위
    record_response(trial, "red", rt=rt_js/1000)
```

#### 2. Custom HTML Component

```python
import streamlit.components.v1 as components

# Custom HTML with timing
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 12vh;
            font-weight: bold;
            background-color: #f5f5f5;
        }}
        #stimulus {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div id="stimulus"></div>

    <script>
        const stimulus = document.getElementById('stimulus');

        // Step 1: Fixation (500ms)
        stimulus.textContent = '+';
        stimulus.style.color = '#000000';

        setTimeout(() => {{
            // Step 2: Blank (500ms)
            stimulus.textContent = '';

            setTimeout(() => {{
                // Step 3: Word stimulus
                stimulus.textContent = '{trial["text"]}';
                stimulus.style.color = '{color_hex_map[trial["letterColor"]]}';

                // RT 측정 시작
                window.stimulusStartTime = performance.now();
            }}, 500);
        }}, 500);

        // 키보드 입력 처리
        document.addEventListener('keydown', (e) => {{
            const rt = performance.now() - window.stimulusStartTime;
            let response = null;

            if (e.key === 'f') response = 'red';
            else if (e.key === 'j') response = 'green';
            else if (e.key === ' ') response = 'blue';

            if (response) {{
                // Streamlit으로 데이터 전송 (postMessage 사용)
                window.parent.postMessage({{
                    type: 'stroop_response',
                    response: response,
                    rt: rt
                }}, '*');
            }}
        }});
    </script>
</body>
</html>
"""

components.html(html_code, height=600)
```

### 장점
- ✅ 실제 타이밍 제어 가능 (오차 ~50ms)
- ✅ 화면 깜빡임 없음
- ✅ 키보드 입력 지원 가능
- ✅ 전문적인 실험 환경

### 단점
- ❌ 구현 복잡도 매우 높음
- ❌ Streamlit과 JavaScript 간 통신 복잡
- ❌ 디버깅 어려움
- ❌ Session state 관리 복잡
- ❌ 추가 패키지 의존성

### 권장 여부
⚠️ **고급 사용자만 권장**
- 타이밍이 절대적으로 중요한 경우에만
- JavaScript/HTML 경험 필요
- 디버깅에 시간이 많이 소요될 수 있음

---

## Phase 2/3 구현 시 고려사항

### 1. 타이밍 정확도의 중요성

**Emotional Stroop Task에서**:
- **Fixation/Blank 타이밍**: 상대적으로 덜 중요
  - 참가자마다 약간의 차이는 큰 영향 없음
  - 조건 간 균등하게 적용되면 됨

- **반응시간 측정**: 중요
  - 하지만 **조건 간 상대 비교**가 핵심
  - 절대값의 50-100ms 오차는 허용 가능

### 2. 실험 목적에 따른 선택

| 실험 목적 | 권장 버전 | 이유 |
|-----------|----------|------|
| **학부 과제, 데모** | Phase 1 | 충분함 |
| **온라인 연구, 대규모 수집** | Phase 1 | 사용자 경험 우선 |
| **실험실 연구 (대조군)** | Phase 1 | 웹 기반의 한계 인정 |
| **정밀 타이밍 필수 (fMRI 등)** | PsychoPy 원본 | Streamlit 부적합 |

### 3. 대안: PsychoPy 사용 고려

만약 타이밍이 절대적으로 중요하다면:
- GitHub 원본 (PsychoPy) 사용
- 한국어 번역만 적용
- PsychoJS로 온라인 배포 가능 (Pavlovia)

---

## 결론 및 권장사항

### ✅ 권장: Phase 1만 사용
- 화면 설정 개선 (app_v2_improved.py)
- 전체화면 안내
- 자극 크기 일관성 확보

### ⚠️ Phase 2/3는 비권장
- 구현 복잡도 대비 효과 낮음
- 화면 깜빡임으로 사용자 경험 저하
- 타이밍 개선 효과도 제한적 (웹 기반 한계)

### 💡 타이밍이 중요하다면
→ **PsychoPy 원본** 사용 (한국어 번역 적용)

---

## Phase 2/3 구현을 원할 경우

만약 그래도 구현하고 싶다면 다음 순서로 진행:

1. **Phase 2 시도** (app_v2_phase2.py)
   - Session state로 fixation 추가
   - 화면 깜빡임 확인
   - 사용자 테스트

2. **효과 평가**
   - 깜빡임이 과제에 방해되는지 확인
   - 타이밍 정확도 측정

3. **Phase 3는 신중히**
   - JavaScript 경험이 있는 경우에만
   - 충분한 테스트 시간 확보
   - 디버깅 각오

---

*작성일: 2025-12-30*
*권장: Phase 1 (app_v2_improved.py) 사용*
