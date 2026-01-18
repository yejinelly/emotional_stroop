# Emotional Word Stroop Task

**[TEST - Full]** https://emo-stroop-101.streamlit.app/ (144 trials, 4 blocks)

**[TEST - Pilot]** https://emo-stroop-101.streamlit.app/?mode=pilot (30 trials)

**[RESULT]** https://docs.google.com/spreadsheets/d/1qz17jEAWlJcP-erMPM99qRE9SPa2m7GqrYzzBnj25NE/edit

## 과제 설명

**Emotional Word Stroop Task**는 정서 단어가 색상 판단에 미치는 간섭 효과를 측정하는 심리학 실험입니다.

- **과제**: 단어 의미를 무시하고 글자 색깔만 판단
- **측정**: 반응시간 (RT), 정확도
- **반응 키**: F (빨강), J (초록)

## 실험 구성

- **Practice**: 24 trials (피드백 제공)
- **Experimental**: 144 trials (Positive 48 + Negative 48 + Neutral 48)
- **Rest breaks**: 4블록 (36 trials × 4), 블록 사이 휴식 3회

## Timing 파라미터

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| Fixation | 0.5초 | + 표시 |
| Max Response Time | 3초 | 초과 시 timeout 처리 |
| ITI | 0.8~1.2초 | Jittered inter-trial interval |
| Timeout 피드백 | "너무 느립니다" | 응답 제한 시간 초과 시 |

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
| RT 정확도 | ~1ms | ~5-10ms (client-side) |

## 참고 자료

- **원본**: [mario-bermonti/emo_stroop_task](https://github.com/mario-bermonti/emo_stroop_task) (Spanish, PsychoPy)
- **한국어 정서 단어**: [VA-KOR](https://github.com/smbslt3/VA-KOR) → 144개 선정 기준: [KOR_wordset_ARcontrolled.md](stimuli/KOR_wordset_ARcontrolled.md)
- **Timing 파라미터 참고**: [TaskBeacon/Stroop](https://github.com/TaskBeacon/Stroop) (PsychoPy)
