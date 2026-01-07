# Phase 1 개선사항 적용 내역

**적용일**: 2025-12-30
**적용 버전**: app_v2.py (메인 폴더) ✅

---

## Phase 1 개선사항 요약

Phase 1은 **화면 설정 개선**에 초점을 맞춘 개선안입니다.
타이밍 제어는 Streamlit의 한계로 구현하지 않고, 대신 화면 일관성과 사용자 경험을 개선했습니다.

---

## 적용된 개선사항

### 1. CSS 스타일 추가 ✅

**위치**: app_v2_improved.py 라인 16-56

```python
st.markdown("""
<style>
    /* Streamlit UI 요소 숨기기 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 자극 제시 영역 - 화면 높이 기준 고정 */
    .stimulus-word {
        font-size: 12vh;  /* 화면 높이의 12% */
        text-align: center;
        font-weight: bold;
        margin: 15vh 0;
        min-height: 15vh;
    }

    /* 버튼 스타일 개선 */
    .stButton button {
        font-size: 1.2rem;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
```

**효과**:
- ✅ 자극 크기가 화면 크기에 관계없이 일정 비율 유지
- ✅ Streamlit UI 제거로 깔끔한 실험 환경
- ✅ 버튼 크기 및 가독성 향상

---

### 2. 전체화면 안내 추가 ✅

**위치**: app_v2_improved.py 라인 178-192

```python
st.warning("""
### ⚠️ 실험 시작 전 준비사항

**1. 전체화면 모드로 전환해주세요:**
- Windows: `F11` 키
- Mac: `Control + Command + F`

**2. 조용한 환경을 확보해주세요:**
- 알림, 다른 앱을 모두 종료
- 휴대폰을 무음으로 설정
""")
```

**효과**:
- ✅ 참가자에게 전체화면 사용 권장
- ✅ 실험 환경 통제 안내
- ✅ 주의 산만 요소 최소화

---

### 3. 자극 표시 방식 변경 ✅

**기존 (app_v2_basic.py)**:
```python
st.markdown(
    f'<div style="text-align:center;"><h1 style="color:{color}; font-size:80px;">{word}</h1></div>',
    unsafe_allow_html=True
)
```

**개선 (app_v2.py - 현재 메인 버전)**:
```python
st.markdown(
    f'<div class="stimulus-word" style="color:{color};">{word}</div>',
    unsafe_allow_html=True
)
```

**차이점**:
- `font-size: 80px` → `font-size: 12vh` (CSS에서 정의)
- `h1` 태그 → `div.stimulus-word` 클래스
- 고정 픽셀 → 화면 높이 비율

**효과**:
- ✅ 전체화면 vs 작은 창에서 상대적 크기 일정
- ✅ 다양한 화면 크기에서 일관성 유지

---

## 적용 위치

### ✅ app_v2.py에 적용됨 (메인 폴더)

**파일 경로**: `/Users/yejinlee/Documents/KPsych-101/정서과제/emotional_word_stroop/app_v2.py`

**사용 방법**:
```bash
cd emotional_word_stroop
streamlit run app_v2.py
```

---

## 버전 비교

| 항목 | app_v2_basic.py (이전) | app_v2.py (현재) |
|------|----------------------|------------------|
| **자극 크기** | 80px 고정 | 12vh (화면 높이 비율) |
| **Streamlit UI** | 표시됨 (헤더, 메뉴 등) | 숨김 |
| **전체화면 안내** | ❌ 없음 | ✅ 있음 |
| **버튼 스타일** | 기본 | 개선됨 (크기, 둥근 모서리) |

---

## Phase 1을 app_v2.py에 적용하려면?

1. **CSS 블록 복사**
   - app_v2_improved.py 라인 16-56 복사
   - app_v2.py 라인 14 아래에 붙여넣기

2. **전체화면 안내 추가**
   - app_v2_improved.py 라인 178-192 복사
   - app_v2.py Practice Instructions 섹션에 추가

3. **자극 표시 방식 변경**
   - 모든 `st.markdown(...font-size:80px...)` 부분을
   - `st.markdown(...class="stimulus-word"...)` 로 변경

---

## Phase 2/3는?

Phase 2/3는 **타이밍 제어 개선**에 관한 것으로, 현재 적용하지 않았습니다.

**이유**:
- Streamlit의 근본적 한계 (웹 기반)
- 구현 복잡도 대비 효과 낮음
- 화면 깜빡임으로 사용자 경험 저하

**자세한 내용**: [phase2_phase3_improvements.md](phase2_phase3_improvements.md)

---

## 권장 사항

### ✅ 현재 권장: app_v2.py 사용
- 번역 검토 완료 후 바로 사용 가능
- Phase 1은 선택사항 (필요시 적용)

### 🔄 Phase 1 적용 고려 시기
- 다양한 화면 크기에서 테스트할 때
- 온라인 배포 시 일관성이 중요할 때
- 전문적인 실험 환경이 필요할 때

### ⚠️ 주의사항
- app_v2_improved.py는 참고용
- 실제 사용 시 app_v2.py에 직접 적용 권장
- 또는 app_v2_improved.py를 메인으로 사용해도 됨

---

## 다음 단계

1. **번역 검토 완료**
   - `stimuli/word_translation_144.csv` 수정
   - `stimuli/word_translation_144_review.csv` 참고

2. **앱 선택**
   - 빠른 테스트: `stroop_streamlit_short.py`
   - 정식 실험: `stroop_streamlit_full.py` 또는 `app_v2.py`

3. **실행 및 테스트**
   ```bash
   streamlit run stroop_streamlit_full.py
   # 또는
   streamlit run app_v2.py
   ```

---

*작성일: 2025-12-30*
*관련 문서*:
- [implementation_differences.md](implementation_differences.md) - 전체 구현 비교
- [timing_and_display_review.md](timing_and_display_review.md) - 타이밍/화면 검토
- [phase2_phase3_improvements.md](phase2_phase3_improvements.md) - 추가 개선안
