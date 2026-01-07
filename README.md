# Emotional Word Stroop Task (Streamlit)

한국어 Emotional Word Stroop Task Streamlit 구현

**GitHub 원본**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task) (Spanish, PsychoPy)

---

## 📋 과제 설명

**Emotional Word Stroop Task**는 정서 단어가 색상 판단에 미치는 간섭 효과를 측정하는 심리학 실험입니다.

- **과제**: 단어 의미를 무시하고 글자 색깔만 판단
- **측정**: 반응시간 (RT), 정확도
- **예상**: Negative 단어에서 더 느린 반응시간

---

## 🚀 빠른 시작

### 1. 가상환경 활성화
```bash
cd emotional_word_stroop
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 앱 실행

**빠른 테스트** (30 trials):
```bash
streamlit run stroop_streamlit_short.py
```

**정식 실험** (144 trials):
```bash
streamlit run app_v2.py
```

---

## 📁 폴더 구조

```
emotional_word_stroop/
├── stroop_streamlit_short.py  # 빠른 테스트 버전 (30 trials)
├── stroop_streamlit_full.py   # 정식 실험 버전 (144 trials) ⭐
├── app_v2.py                  # 정식 실험 버전 (144 trials, 이전 이름)
├── requirements.txt           # Python 패키지 목록
├── README.md                  # 이 파일
│
├── stimuli/              # 자극 파일
│   ├── word_translation_144.csv       # 번역표 (검토 필요)
│   ├── word_translation_144_review.csv # 검토용 (⚠️ 표시)
│   ├── exp_trials_korean.csv          # 144 실험 trials
│   └── practice_trials_korean.csv     # 6 연습 trials
│
├── data/                 # 실험 데이터
│   └── responses/        # 반응 데이터 저장 (.csv)
│
├── docs/                 # 문서
│   ├── emotional word stroop_st_plan.md  # 초기 계획
│   ├── implementation_differences.md     # 구현 비교
│   ├── task_design_extracted.md          # GitHub 원본 분석
│   ├── timing_and_display_review.md      # 타이밍/화면 검토
│   ├── phase1_applied.md                 # Phase 1 적용 내역
│   └── phase2_phase3_improvements.md     # Phase 2/3 개선안
│
├── old_versions/         # 이전 버전
│   ├── app.py            # 초기 프로토타입
│   ├── app_v2_basic.py   # Phase 1 적용 전 버전
│   └── README.md
│
├── streamlit_tutorial/   # Streamlit 학습용
├── utils/                # 유틸리티 (미사용)
└── venv/                 # 가상환경
```

---

## 🎯 버전 선택 가이드

### stroop_streamlit_short.py 🚀
- **용도**: 빠른 테스트, UI/UX 확인
- **특징**: 30 trials (6 practice + 30 experimental)
- **소요 시간**: 약 2-3분
- **권장 대상**: 번역 검토 전, 앱 동작 테스트

### stroop_streamlit_full.py ⭐ (권장)
- **용도**: 정식 실험
- **특징**: 168 trials (24 practice + 144 experimental)
- **소요 시간**: 약 10-15분
- **Phase 1 개선사항 적용**:
  - CSS로 자극 크기 vh 단위 고정
  - Streamlit UI 숨김
  - 전체화면 안내 추가
- **권장 대상**: 실제 데이터 수집

---

## ⚠️ 사용 전 준비사항

### 1. 번역 검토 (필수!)

**파일**: `stimuli/word_translation_144.csv`

현재 자동 번역된 144개 단어를 검토하고 수정해야 합니다:
- 정서가(valence) 적절성 확인
- 문화적 적절성 확인
- 단어 길이, 친숙도 고려

**검토 도움**: `stimuli/word_translation_144_review.csv` 참고 (⚠️ 표시된 21개 단어)

### 2. 실험 전 안내사항

참가자에게 다음을 안내하세요:
- **전체화면 모드** 사용 (F11 또는 Cmd+Ctrl+F)
- 조용한 환경 확보
- 알림, 다른 앱 종료

---

## 📊 데이터 수집

### 저장 위치
`data/responses/{participant_id}_{timestamp}.csv`

### 데이터 항목
- `trial_num`: Trial 번호
- `participant_id`: 참가자 ID
- `word`: 제시된 단어
- `condition`: 정서가 (positive/negative/neutral)
- `color`: 정답 색상
- `response`: 참가자 반응
- `accuracy`: 정확도 (1=correct, 0=incorrect)
- `rt`: 반응시간 (초)
- `timestamp`: ISO 8601 타임스탬프
- `phase`: practice / experimental

---

## 🔧 기술 세부사항

### GitHub 원본과의 차이점

| 항목 | GitHub 원본 (PsychoPy) | 우리 구현 (Streamlit) |
|------|----------------------|---------------------|
| **언어** | 스페인어 | 한국어 |
| **플랫폼** | PsychoPy 3 (로컬) | Streamlit (웹) |
| **Trials** | 144 | 144 (동일) |
| **Practice** | 24 trials | 24 trials (동일) |
| **Rest breaks** | 3회 (36 trials마다) | 3회 (동일) |
| **Fixation cross** | 0.5s/1.0s 정확 제어 | ❌ 미구현 (웹 한계) |
| **Blank screen** | 0.5s ISI | ❌ 미구현 |
| **반응 방식** | 키보드 (f/j/space) | 버튼 클릭 |
| **RT 정확도** | ~1ms | ~50-100ms |

**자세한 내용**: [docs/implementation_differences.md](docs/implementation_differences.md)

---

## 📚 문서

- **[implementation_differences.md](docs/implementation_differences.md)**: 전체 구현 비교
- **[task_design_extracted.md](docs/task_design_extracted.md)**: GitHub 원본 과제 디자인
- **[timing_and_display_review.md](docs/timing_and_display_review.md)**: 타이밍/화면 검토
- **[phase1_applied.md](docs/phase1_applied.md)**: Phase 1 화면 개선 적용 내역
- **[phase2_phase3_improvements.md](docs/phase2_phase3_improvements.md)**: 추가 개선안 (선택)

---

## 🐛 문제 해결

### 한글이 깨져 보일 때
- **Excel**: 데이터 → 텍스트/CSV 가져오기 → UTF-8 선택
- **Numbers** (Mac): 자동으로 UTF-8 인식
- **Google Sheets**: 업로드 시 자동 인식

### 화면 크기가 이상할 때
- 전체화면 모드 사용 (F11)
- 브라우저 확대/축소 100%로 설정

### 데이터가 저장되지 않을 때
- `data/responses/` 폴더 존재 확인
- 쓰기 권한 확인

---

## 📝 다음 단계

1. **번역 검토**: `stimuli/word_translation_144.csv` 수정
2. **테스트 실행**: `stroop_streamlit_short.py` 로 동작 확인
3. **정식 실험**: `stroop_streamlit_full.py` 로 데이터 수집
4. **데이터 분석**: `data/responses/*.csv` 파일 분석

---

## 🙏 Credits

- **GitHub 원본**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task)
- **플랫폼**: [Streamlit](https://streamlit.io)
- **구현**: Claude + 사용자

---

*마지막 업데이트: 2025-12-30*
