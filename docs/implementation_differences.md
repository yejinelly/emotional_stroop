# Emotional Word Stroop 구현 비교

**원본**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task) (PsychoPy)
**우리 버전**: Streamlit 웹 애플리케이션

---

## 1. 플랫폼 차이

| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **플랫폼** | PsychoPy 3 Builder | Streamlit |
| **실행 환경** | 로컬 Python (전용 소프트웨어) | 웹 브라우저 |
| **타이밍 정확도** | 밀리초 단위 정확 제어 | 제한적 (JavaScript 기반) |
| **설치 복잡도** | 높음 (PsychoPy 설치 필요) | 낮음 (pip install streamlit) |
| **데이터 수집 방식** | 자동 CSV 저장 | 자동 CSV 저장 + 다운로드 버튼 |

---

## 2. 언어 및 자극

### 언어
| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **단어 언어** | 스페인어 | 한국어 |
| **색상 단어** | azul, rojo, verde | 빨강, 파랑, 초록 |
| **지시사항** | 스페인어 | 한국어 |

### 단어 개수
| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **긍정 단어** | 48개 | 10개 |
| **부정 단어** | 48개 | 10개 |
| **중립 단어** | 48개 | 10개 |
| **총 단어** | 144개 | 30개 |
| **색상** | 3개 (red, blue, green) | 3개 (빨강, 파랑, 초록) |
| **총 trials** | 144 trials | 90 trials (30 × 3 colors) |

### 단어 예시

**GitHub (스페인어)**:
- Positive: luna, paseo, cantar, fortuna, sonrisa, bienestar
- Negative: pedo, herir, escupir, terremoto, repugnar, monstruo
- Neutral: giro, forma, llamar, ancho, producto, sencillo

**우리 버전 (한국어)**:
- Positive: 행복, 사랑, 기쁨, 평화, 성공, 희망, 웃음, 친구, 축제, 선물
- Negative: 슬픔, 분노, 불안, 두려움, 증오, 고통, 실패, 외로움, 질병, 죽음
- Neutral: 의자, 테이블, 연필, 종이, 시계, 창문, 문, 책상, 컵, 가방

---

## 3. 과제 구조

### Practice Trials

| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **Practice 유무** | ✅ 있음 (24 trials) | ❌ 없음 |
| **자극** | 색상 단어 (congruent) | - |
| **피드백** | ✅ 정답/오답 표시 | - |
| **블록** | 4 blocks × 6 trials | - |

### Experimental Trials

| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **총 trials** | 144 | 90 |
| **블록 구조** | 16 blocks × 9 trials | 블록 없음 (연속) |
| **Large blocks** | 4 × 36 trials | - |
| **Rest breaks** | 3회 (36 trials마다) | 없음 |
| **블록 내 구성** | 균등 배치 (3 valence × 3 colors) | 완전 무선화 |

---

## 4. 타이밍

### GitHub 원본 (PsychoPy)

**Practice trials**:
1. Instructions
2. Fixation cross: **1.0초**
3. Blank screen: **0.5초**
4. Word stimulus: **반응 시까지** (no limit)
5. Feedback: 표시

**Experimental trials**:
1. Instructions
2. Fixation cross: **0.5초**
3. Blank screen: **0.5초**
4. Word stimulus: **반응 시까지** (no limit)
5. No feedback

### 우리 버전 (Streamlit)

**모든 trials**:
1. Instructions
2. ~~Fixation cross~~ (생략)
3. ~~Blank screen~~ (생략)
4. Word stimulus: **반응 시까지** (버튼 클릭)
5. No feedback

**타이밍 생략 이유**:
- Streamlit은 정확한 밀리초 단위 제어가 어려움
- 웹 기반이라 렌더링 지연 발생 가능
- 버튼 클릭 방식으로 단순화

---

## 5. 반응 방식

| 항목 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **입력 방식** | 키보드 | 화면 버튼 클릭 |
| **빨강** | `f` key | 🔴 빨강 버튼 |
| **파랑** | `space` bar | 🔵 파랑 버튼 |
| **초록** | `j` key | 🟢 초록 버튼 |
| **반응시간 정확도** | 높음 (밀리초) | 중간 (JavaScript time.time()) |

---

## 6. 블록 및 무선화

### GitHub 원본
- **Semi-randomization**:
  - 16 blocks pre-organized
  - 각 block: 3 positive + 3 negative + 3 neutral
  - 각 valence마다 3 colors 균등 배치
  - Block order shuffled
  - Within-block order: CSV에 명시된 순서

**예시 block**:
| Word | Color | Valence |
|------|-------|---------|
| positive1 | blue | positive |
| negative1 | blue | negative |
| neutral1 | blue | neutral |
| positive2 | green | positive |
| negative2 | green | negative |
| neutral2 | green | neutral |
| positive3 | red | positive |
| negative3 | red | negative |
| neutral3 | red | neutral |

### 우리 버전
- **Complete randomization**:
  - 모든 단어 × 모든 색상 조합 생성
  - 완전 무선 셔플 (`random.shuffle`)
  - 블록 구분 없음

---

## 7. 데이터 기록

### 공통 변수
- `participant_id`: 참가자 ID
- `word`: 제시된 단어
- `valence`: 정서가 (positive/negative/neutral)
- `color`: 정답 색상
- `response`: 참가자 반응
- `accuracy`: 정확도 (1=correct, 0=incorrect)
- `rt`: 반응시간

### GitHub 원본만 있는 변수
- `letterColor`: 실제 표시된 색상 (항상 color와 동일)
- `corrAns`: 정답 키 (f/j/space)
- `session`: 세션 번호
- `date`: 실험 날짜
- `psychopyVersion`: PsychoPy 버전
- `frameRate`: 모니터 주사율

### 우리 버전만 있는 변수
- `trial_num`: Trial 번호
- `timestamp`: ISO 8601 타임스탬프
- `age`: 연령 (입력받음)
- `gender`: 성별 (입력받음)

---

## 8. 파일 구조

### GitHub 원본
```
emo_stroop_task/
├── emo_stroop.psyexp              # PsychoPy Builder 파일
├── emo_stroop_lastrun.py          # 자동 생성 Python 스크립트
├── exp_trials.csv                 # 144 trials (16 blocks)
├── practice_trials.csv            # 6 practice trials
├── choose_blocks.csv              # Block range 정의 (0:9, 9:18, ...)
├── data/                          # 반응 데이터 저장
└── README.md
```

### 우리 버전
```
emotional_word_stroop/
├── app.py                         # Streamlit 앱
├── stimuli/
│   ├── word_list.csv              # 30 단어 (한국어)
│   └── colors.csv                 # 3 색상
├── data/
│   └── responses/                 # 반응 데이터 저장
├── utils/                         # (미사용, 확장용)
├── venv/                          # 가상환경
├── requirements.txt
├── task_design_extracted.md       # GitHub 디자인 분석
└── implementation_differences.md  # 이 파일
```

---

## 9. 기능 비교

| 기능 | GitHub 원본 | 우리 버전 |
|------|------------|-----------|
| **Practice trials** | ✅ | ❌ |
| **Feedback** | ✅ (practice만) | ❌ |
| **Fixation cross** | ✅ | ❌ |
| **Blank screen (ISI)** | ✅ | ❌ |
| **Block structure** | ✅ (16 blocks) | ❌ |
| **Rest breaks** | ✅ (3회) | ❌ |
| **진행률 표시** | ❌ | ✅ (progress bar) |
| **실시간 통계** | ❌ | ✅ (완료 후) |
| **데이터 다운로드** | ❌ | ✅ (CSV download) |
| **참가자 정보 입력** | ✅ (기본) | ✅ (연령, 성별 포함) |
| **키보드 반응** | ✅ | ❌ |
| **버튼 반응** | ❌ | ✅ |

---

## 10. 장단점 비교

### GitHub 원본 (PsychoPy)

**장점**:
- ✅ 정확한 타이밍 제어 (밀리초 단위)
- ✅ 심리학 실험 표준 플랫폼
- ✅ Fixation, blank screen 등 표준 절차 준수
- ✅ Practice trials + feedback
- ✅ 키보드 반응 (더 빠른 RT)
- ✅ 144 trials로 신뢰도 높음

**단점**:
- ❌ PsychoPy 설치 필요 (복잡)
- ❌ 스페인어 (한국어 번역 필요)
- ❌ GUI 수정 어려움 (Builder 사용)
- ❌ 원격 실험 불가

### 우리 버전 (Streamlit)

**장점**:
- ✅ 웹 기반 (브라우저만 있으면 실행)
- ✅ 한국어 지원
- ✅ 설치 간단 (pip install streamlit)
- ✅ 코드 수정 용이 (Python)
- ✅ 원격 실험 가능 (배포 시)
- ✅ 진행률 표시, 즉시 결과 확인
- ✅ CSV 다운로드 기능

**단점**:
- ❌ 타이밍 정확도 낮음 (웹 기반)
- ❌ Practice trials 없음
- ❌ Fixation/blank screen 생략
- ❌ 90 trials (신뢰도 상대적으로 낮음)
- ❌ 버튼 클릭 (키보드보다 느림)

---

## 11. 구현 버전 비교

### app.py (초기 프로토타입)
- 30 단어, 90 trials
- ❌ Practice trials 없음
- ❌ Rest breaks 없음
- ❌ Feedback 없음
- CSV 파일에서 단어 로드
- 단순 테스트용

### stroop_streamlit_short.py (빠른 테스트 버전) 🚀 추천 (번역 검토 전)

**완료된 기능**:
- ✅ 30 trials (10 positive + 10 negative + 10 neutral)
- ✅ Practice trials 6개 (색상 단어)
- ✅ Feedback 추가 (practice만)
- ❌ Rest breaks 없음 (짧아서 불필요)
- ✅ 정서가별 분석 (condition: negative/neutral/positive)
- ✅ 진행률 표시, 즉시 결과 확인
- ✅ Practice + Experimental 데이터 통합 저장
- ✅ **코드 내 단어 하드코딩** (CSV 불필요, 빠른 실행)

**특징**:
- **CSV 파일 불필요**: 단어가 코드에 직접 포함됨
- **빠른 완료**: 약 2-3분 소요
- **번역 검토 전 테스트용**: word_translation_144.csv 검토 전에 앱 동작 확인
- 각 단어는 랜덤 색상 1회만 제시

### stroop_streamlit_full.py (GitHub 유사 버전) ⭐ 권장 (정식 실험용)

**완료된 기능**:
- ✅ 한국어 단어 144개 (48 positive + 48 negative + 48 neutral)
- ✅ Practice trials 24개 (6 base × 4 blocks)
- ✅ Feedback 추가 (practice만)
- ✅ Rest breaks 추가 (36 trials마다, 총 3회)
- ✅ 정서가별 분석 (condition: negative/neutral/positive)
- ✅ 진행률 표시, 즉시 결과 확인
- ✅ Practice + Experimental 데이터 통합 저장

**파일 구조**:
```
stimuli/
├── word_translation_144.csv       # 스페인어 → 영어 → 한국어 번역표 (수정 필요)
├── exp_trials_korean.csv          # 144 experimental trials (한국어)
├── practice_trials_korean.csv     # 6 practice trials (색상 단어)
├── colors.csv                     # 3 colors (red/blue/green)
└── word_list.csv                  # 30 words (초기 버전, 사용 안 함)
```

**남은 차이점** (Streamlit 한계):
- ⚠️ Fixation cross 타이밍 제어 제한적
- ⚠️ Blank screen (ISI) 생략
- ⚠️ 키보드 입력 대신 버튼 클릭
- ⚠️ 완전 무선화 (GitHub은 semi-randomization)

---

## 12. 향후 개선 사항 (선택)

### Phase 1: 한국어 번역 검토 ⚠️ 중요
- [ ] **word_translation_144.csv 검토 및 수정**
  - 현재: 자동 번역 (검토 필요!)
  - 각 단어가 정서가(valence)에 적합한지 확인
  - 단어 길이, 빈도, 친숙도 고려
  - 문화적 적절성 확인
- [ ] 한국어 정서 단어 규준 참조 (Park et al., K-PANAS 등)

### Phase 2: 블록 구조 개선
- [ ] 16 blocks × 9 trials 구조 구현
- [ ] Block 간 균등 배치 (valence × color)
- [ ] choose_blocks.csv 방식 적용

### Phase 3: 타이밍 개선
- [ ] `streamlit-javascript` 활용하여 타이밍 정확도 향상
- [ ] Fixation cross 시간 제어
- [ ] Blank screen (ISI) 추가

### Phase 4: 키보드 지원
- [ ] 키보드 입력 옵션 추가 (f/j/space)
- [ ] 버튼/키보드 선택 가능하게 설정

---

## 13. 사용 권장

### stroop_streamlit_short.py 사용 권장 상황 (🚀 빠른 테스트)
- **번역 검토 전** 앱 동작 테스트
- 2-3분 내 빠른 완료 필요
- UI/UX 확인
- 참가자 지시사항 테스트
- CSV 파일 없이 실행 가능
- 데이터 수집 흐름 확인

**실행 방법**:
```bash
streamlit run stroop_streamlit_short.py
```

### stroop_streamlit_full.py 사용 권장 상황 (⭐ 정식 실험)
- 한국어 참가자 대상 연구
- 144 trials로 신뢰도 확보 필요
- Practice trials + feedback 필요
- Rest breaks로 피로도 관리
- 온라인 원격 실험
- PsychoPy 설치가 어려운 환경
- 웹 기반 배포 필요
- **word_translation_144.csv 검토 완료 후** 사용

**실행 전 준비**:
1. `stimuli/word_translation_144.csv` 한국어 번역 검토 및 수정
2. 수정된 번역 반영 (필요시 exp_trials_korean.csv 재생성)

**실행 방법**:
```bash
streamlit run stroop_streamlit_full.py
```

### GitHub 원본 (PsychoPy) 사용 권장 상황
- 정확한 반응시간 측정이 절대 필수 (밀리초 단위)
- 대규모 실험실 연구 (fMRI, EEG 등)
- PsychoPy 사용 경험이 있는 경우
- 스페인어 참가자 대상

### app.py 사용 권장 상황
- ⚠️ 권장하지 않음 (stroop_streamlit_short.py 사용 권장)
- 초기 프로토타입 참고용

---

## 13. 참고 문헌

**GitHub 원본**:
- Repository: https://github.com/mario-bermonti/emo_stroop_task
- Language: Spanish
- Platform: PsychoPy 3
- License: 명시 안 됨

**관련 논문**:
- Rogers, T. B., Kuiper, N. A., & Kirker, W. S. (1977). Self-reference and the encoding of personal information. *Journal of Personality and Social Psychology*, 35(9), 677-688.
- Joyal, M., et al. (2019). Characterizing emotional Stroop interference in PTSD, MDD and anxiety disorders. *PLOS One*, 14(4), e0214998.

---

*작성일: 2025-12-30*
*용도: Emotional Word Stroop Streamlit 구현 비교 문서*
