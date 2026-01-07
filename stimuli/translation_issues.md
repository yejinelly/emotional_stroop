# 번역 검토 및 수정 내역

**작성일**: 2025-12-30

---

# PART 1: ✅ 수정 완료

### 1. 중복 단어 해결

**pasear vs paseo** (둘 다 "산책"이었음):
- pasear (walk) → **걷기** ✅
- paseo (stroll) → 산책

**aplaudir vs aplausos** (둘 다 "박수"였음):
- aplaudir (applaud) → 박수
- aplausos (applause) → **갈채** ✅

### 2. 정서가 맞춤

**arriesgado (risky)**:
- 기존: 위험한 (neutral) - 한국어로 negative 느낌
- 수정: **모험적인** (neutral) ✅

### 3. 의미 수정

**metro (meter/subway)**:
- 기존: 미터 (meter) - 추상적 단위
- 수정: **지하철** (subway) - 구체적 명사 ✅

### 4. 단어 형태 수정

**armar (arm)**:
- 기존: 무장 (명사)
- 수정: **무장시키다** (동사) - negative 유지 ✅

**estrangular (strangle)**:
- 기존: 목졸라 (3글자)
- 수정: **목조르다** (4글자) - 동사 형태 ✅

### 5. 정서가 맞는 번역 선택

**fortaleza (fortress/strength)**:
- 기존: 요새 (fortress) - 중립적 건축물
- 수정: **강함** (strength) - positive 정서가 맞춤 ✅

---

# PART 2: 🔍 검토 필요

### 1. 속된 표현

| 스페인어 | 영어 | 현재 번역 | Valence | 문제점 |
|---------|------|---------|---------|--------|
| pedo | fart | 방귀 | negative | 너무 속되고 유치한 표현 |

### 2. 폭력/자살 관련

| 스페인어 | 영어 | 현재 번역 | Valence |
|---------|------|---------|---------|
| estrangular | strangle | 목조르다 | negative |
| ahorcar | hang | 목매달다 | negative |

**권장**: IRB 승인 여부에 따라 유지/교체 결정

### 3. 민감한 주제

| 스페인어 | 영어 | 현재 번역 | Valence | 문제점 |
|---------|------|---------|---------|--------|
| racial | racial | 인종의 | neutral | 민감한 사회적 주제 |
| nazi | nazi | 나치 | negative | 역사적/정치적 민감 |

### 4. 정서가 모호

| 스페인어 | 영어 | 현재 번역 | GitHub Valence | 문제점 |
|---------|------|---------|---------------|--------|
| muro | wall | 벽 | negative | 중립적일 수도 |
| agua | water | 물 | positive | 중립적임 |
| noche | night | 밤 | positive | 왜 positive? |
| estricto | strict | 엄격한 | negative | 중립적일 수 있음 |

### 5. 문화 적합성

**긴 단어**:
- hidromasaje → 수압마사지 (5글자, 생소함)

**문화 차이**:
- clavel → 카네이션 (positive) - 한국에서도 긍정적인지?
- torear → 투우 (negative) - 한국 문화에 없음
- paella → 빠에야 (positive) - 스페인 음식, 생소함

### 6. 의학 용어

| 스페인어 | 영어 | 현재 번역 | Valence | 문제점 |
|---------|------|---------|---------|--------|
| metástasis | metastasis | 전이 | negative | 전문용어, 일반인에게 생소 |
| muñón | stump | 절단 | negative | 전문용어, 일반인에게 생소 |
| apendicitis | appendicitis | 맹장염 | negative | 전문용어, 일반인에게 생소 |
| quimioterapia | chemotherapy | 항암치료 | negative | 전문용어, 일반인에게 생소 |

---

## 💡 검토 가이드

### 좋은 정서 단어 기준:
1. **친숙도**: 일상에서 자주 사용
2. **명확성**: 정서가가 명확
3. **길이**: 2-3글자 (최대 4글자)
4. **구체성**: 추상적보다는 구체적
5. **문화 적절성**: 한국 문화에서 자연스러움

---

## 📝 검토 요약

### 필수 검토 (5개):
1. **속된 표현** (1개): 방귀
2. **폭력/자살** (2개): 목조르다, 목매달다 - IRB 확인 필요
3. **민감 주제** (2개): 인종의, 나치

### 선택 검토 (12개):
1. **정서가 모호** (4개): 벽, 물, 밤, 엄격한
2. **문화 적합성** (4개): 수압마사지, 카네이션, 투우, 빠에야
3. **의학 용어** (4개): 전이, 절단, 맹장염, 항암치료

---

*참고 파일*:
- `word_translation_144.csv` - 번역표
- `exp_trials_korean.csv` - 실험 trial 파일
- `word_translation_144_review.csv` - 검토용 (⚠️ 21개 표시)
