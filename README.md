# Emotional Word Stroop Task

한국어 Emotional Word Stroop Task 웹 구현

**[TEST]** https://emo-stroop-101.streamlit.app/

**[RESULT]** https://docs.google.com/spreadsheets/d/1qz17jEAWlJcP-erMPM99qRE9SPa2m7GqrYzzBnj25NE/edit

**원본**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task) (Spanish, PsychoPy)

**한국어 단어 stimuli**: [KOR_wordset.md](https://github.com/yejinelly/emotional_stroop/blob/main/stimuli/KOR_wordset.md)

## 과제 설명

**Emotional Word Stroop Task**는 정서 단어가 색상 판단에 미치는 간섭 효과를 측정하는 심리학 실험입니다.

- **과제**: 단어 의미를 무시하고 글자 색깔만 판단
- **측정**: 반응시간 (RT), 정확도

## 실험 구성

- **Practice**: 24 trials
- **Experimental**: 144 trials (Positive 48 + Negative 48 + Neutral 48)
- **Rest breaks**: 4블록 (36 trials × 4), 블록 사이 휴식 3회

## 수집 데이터

### 참가자 정보
`participant_id`, `date`, `timestamp`

### 조건별 요약
| 조건 | RT | 정확도 |
|------|-----|--------|
| Positive | `rt_positive_mean`, `rt_positive_sd` | `acc_positive`, `n_positive` |
| Negative | `rt_negative_mean`, `rt_negative_sd` | `acc_negative`, `n_negative` |
| Neutral | `rt_neutral_mean`, `rt_neutral_sd` | `acc_neutral`, `n_neutral` |

### 간섭 효과
- `interference_negative` = rt_negative_mean - rt_neutral_mean
- `interference_positive` = rt_positive_mean - rt_neutral_mean

### 전체 요약
`rt_overall_mean`, `acc_overall`, `n_total`

### Trial 데이터
- **Practice**: `p1_word`, `p1_color`, `p1_resp`, `p1_acc`, `p1_rt` ... (24개)
- **Practice 요약**: `practice_acc`, `practice_rt_mean`
- **Experimental**: `t1_word`, `t1_cond`, `t1_color`, `t1_resp`, `t1_acc`, `t1_rt` ... (144개)

## 원본과의 차이점

| 항목 | 원본 (PsychoPy) | 본 구현 (Streamlit) |
|------|----------------|-------------------|
| 언어 | 스페인어 | 한국어 |
| 플랫폼 | PsychoPy 3 (로컬) | Streamlit (웹) |
| RT 정확도 | ~1ms | ~50-100ms |