# PHQ-9 Demographics 설계

## 1. 현재 포함 필드

| 카테고리 | 필드명 | 설명 |
|---------|--------|------|
| **인구통계학적 변인** | `age` | 참가자 연령 (18-65세) |
| | `gender` | 성별 (M/F) |
| | `education` | 교육 연한 (년) |
| | `employment_status` | 근무 형태 (전일제, 시간제, 임시직/일용직, 은퇴, 장애/질병 휴직, 학생, 무직 (구직 중), 무직 (비구직), 기타) |
| | `income_level` | 주관적 계층의식 (1~10) |
| | `marital_status` | 미혼 (미혼모 포함), 기혼 (재혼 포함), 사별, 이혼, 별거 |
| **임상 변인** | `is_clinical` | 임상군 여부 (1/0) |
| | `diagnosis` | 진단명 (6개 범주: 우울장애, 불안장애, ADHD, 중독, 성격장애, 기타) |
| | `current_treatment` | 현재 치료 여부 (예/아니오) |
| **동의** | `consent` | 데이터 수집 동의 (KPsych-101 100% 포함) |

---

## 2. Diagnosis

### 2.1 현재 설정
8개 진단: 우울장애, 양극성장애, 불안장애, ADHD, PTSD, 강박장애, 성격장애, 기타

### 2.2 심각도별 배분 (generate_PHQ9_data.py 기준)

**중고도/고도 (moderately_severe, severe)**:
| 진단 | 비율 |
|------|------|
| 우울장애 | 50% |
| 양극성장애 | 20% |
| PTSD | 20% |
| 불안장애 | 10% |

**경도/중등도 (mild, moderate)**:
| 진단 | 비율 |
|------|------|
| 우울장애 | 40% |
| 불안장애 | 30% |
| ADHD | 15% |
| 강박장애 | 10% |
| 성격장애 | 5% |

**비임상군**: diagnosis = '없음'

### 2.3 논의 필요성
**현재 상태**: 심각도별 진단 분포 가중치가 임의로 설정됨 (실제 역학 데이터 근거 없음)

**고려 사항**:
- 한국 정신건강 역학 데이터 기반 가중치 조정 필요성
- 심각도별 진단 분리 로직의 타당성
- 균등 분포 vs 차등 가중치 선택

---

## 3. Current Treatment

### 3.1 현재 설정
```json
"current_treatment": "예" 또는 "아니오"
```

### 3.2 확장 옵션

**Option 1 - 구조화**:
```json
"current_treatment": {
  "medication": {
    "status": true,
    "type": "SSRI",
    "duration_months": 6
  },
  "psychotherapy": {
    "status": true,
    "type": "CBT",
    "duration_months": 3
  }
}
```

**Option 2 - 문자열**:
```json
"current_treatment": "약물치료(SSRI 6개월) + 심리치료(CBT 3개월)"
```

### 3.3 논의 필요성
**찬성**:
- 치료 이력은 우울증 평가에서 중요한 맥락 정보
- 임상 연구에서 자주 수집됨
- 치료 효과 분석 시 필요

**반대**:
- 모든 PHQ-9 데이터셋에 포함되지 않을 수 있음
- 구조 복잡도 증가
- 개인정보 민감도 증가

**결정 필요**:
- [ ] Option 1: 구조화된 객체로 확장
- [ ] Option 2: 문자열로 유지하되 포맷 가이드 제공
- [ ] 현재 상태 유지 (간단한 문자열)

---

## 4. Employment

### 4.1 후보 1: Time-based (Employment Status, 근무 형태 중심)

출처: [Firth et al. (2024) - PMC12327771](https://pmc.ncbi.nlm.nih.gov/articles/PMC12327771/) (Naturalistic cohort study)

| 영어 | 한국어 |
|------|--------|
| Full-time | 전일제 |
| Part-time | 시간제 |
| Casual | 임시직/일용직 |
| Retired | 은퇴 |
| On disability leave | 장애/질병 휴직 |
| Full-time student | 학생 |
| Not employed (looking) | 무직 (구직 중) |
| Not employed (not looking) | 무직 (비구직) |
| Other | 기타 |

출처: 이전 연구

- 학생
- 전일제 취업자
- 시간제/계약직 근로자
- 자영업자/프리랜서
- 가정주부
- 군인
- 은퇴/무직
- 기타

### 4.2 후보 2: Type-based (Occupational Type, 직업 유형 중심)

출처: [2023 한국인의 행복조사](한국인의%20행복조사(2023).pdf)

DQ2. 귀하의 직업은 다음 중 어디에 해당합니까?
| | | |
|---|---|---|
| ① 관리자 | ⑥ 농림어업 종사자 | ⑪ 가정주부 |
| ② 전문가 및 관련 종사자 | ⑦ 기능원 및 관련 기능종사자 | ⑫ 학생 |
| ③ 사무 종사자 | ⑧ 장치, 기계 조작 및 조립종사자 | ⑬ 없음(무직) |
| ④ 서비스 종사자 | ⑨ 단순 노무 종사자 | ⑭ 기타(적을 것: ____) |
| ⑤ 판매 종사자 | ⑩ 군인 | |

### 4.3 논의 필요성

- **Time-based vs. Type-based**: 전일제/시간제 같은 근무 형태가 중요한지, 직업 유형(관리자, 전문가 등)이 중요한지
- **예시 추가 여부**: "관리자(예: )" 형식으로 구체적 예시를 제공할지

**[2024 제8차 한국표준직업분류](제8차+한국표준직업분류+개정+분류+항목표.hwpx) (예시 출처):**
1. 관리자 (예: 기업 부서장, 학교 교감, 시설 관리자)
2. 전문가 및 관련 종사자 (예: 연구원, 개발자, 의사, 교사, 변호사)
3. 사무 종사자 (예: 사무원, 상담원, 비서)
4. 서비스 종사자 (예: 미용사, 조리사, 승무원, 간병인)
5. 판매 종사자 (예: 매장 판매원, 영업사원)
6. 농림어업 종사자 (예: 농부, 어부)
7. 기능원 및 관련 기능종사자 (예: 용접공, 배관공, 목수)
8. 장치, 기계 조작 및 조립종사자 (예: 기계 조작원, 운전원)
9. 단순 노무 종사자 (예: 청소원, 경비원, 배달원)
10. 군인
11. 가정주부
12. 학생
13. 없음(무직)
14. 기타

---

## 5. Income Level

### 5.1 후보 1: [2023 한국인의 행복조사](한국인의%20행복조사(2023).pdf) (6단계)

귀하의 사회 경제적 지위(소득, 직업, 교육, 재산 등을 고려)는 어디에 속한다고 생각하십니까?
1. 상상
2. 상하
3. 중상
4. 중하
5. 하상
6. 하하

### 5.2 후보 2: MacArthur Scale (10단계)

출처: [SPARQtools](MacArthur-Scale-of-Subjective-Social-Status-Adult-Version.doc), 한국 연구 ([Hong & Yi, 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5269493/))

이 사다리가 우리나라에서 사람들이 서 있는 위치를 나타낸다고 생각해 보세요. 사다리의 맨 위에는 가장 잘 사는 사람들—돈이 가장 많고, 교육을 가장 많이 받고, 가장 존경받는 직업을 가진 사람들이 있습니다. 맨 아래에는 가장 못 사는 사람들—돈이 가장 적고, 교육을 가장 적게 받고, 가장 존경받지 못하는 직업을 가졌거나 직업이 없는 사람들이 있습니다. 이 사다리에서 높이 올라갈수록 맨 위에 있는 사람들에게 가까워지고, 낮을수록 맨 아래에 있는 사람들에게 가까워집니다.

이 사다리에서 본인은 어디에 위치한다고 생각하십니까?
현재 본인의 삶에서, 우리나라의 다른 사람들과 비교했을 때 본인이 서 있다고 생각하는 칸에 큰 "X"를 표시해 주세요.

> **영어 원문 (SPARQtools):** "Think of this ladder as representing where people stand in the United States. At the top of the ladder are the people who are the best off – those who have the most money, the most education, and the most respected jobs. At the bottom are the people who are the worst off – those who have the least money, least education, the least respected jobs, or no job. The higher up you are on this ladder, the closer you are to the people at the very top; the lower you are, the closer you are to the people at the very bottom. Where would you place yourself on this ladder? Please place a large "X" on the rung where you think you stand at this time in your life relative to other people in the United States."

```
10 ═══
 9 ───
 8 ───
 7 ───
 6 ───
 5 ───
 4 ───
 3 ───
 2 ───
 1 ═══
```

---

## 6. Marital Status

### 6.1 후보 1: [통계청 사회조사](https://kostat.go.kr/statDesc.es?act=view&mid=a10501010000&sttr_cd=S004002) / [2024 경제활동인구조사](2024년%20경제활동인구조사%20지침서_외부용.pdf) (4단계)

- 미혼
- 배우자 있음 (유배우)
- 사별
- 이혼

### 6.2 후보 2: [2023 한국인의 행복조사](한국인의%20행복조사(2023).pdf) (5단계)

- 미혼 (미혼모 포함)
- 기혼 (재혼 포함)
- 사별
- 이혼
- 별거

### 6.3 논의 필요성

- **별거 포함 여부**: 후보 2는 별거를 별도 범주로 분리
- **미혼모/재혼 구분**: 후보 2는 괄호로 세부 상태 명시

---

## 참고 자료

**Reviews:**

- Kohler CA, Evangelou E, Stubbs B, et al. Mapping risk factors for depression across the lifespan: An umbrella review of evidence from meta-analyses and Mendelian randomization studies. *Journal of Psychiatric Research*. 2018;103:189-207. DOI: 10.1016/j.jpsychires.2018.05.020
- Solmi M, Cortese S, Vita G, et al. An umbrella review of candidate predictors of response, remission, recovery, and relapse across mental disorders. *Molecular Psychiatry*. 2023;28(9):3671-3687. DOI: 10.1038/s41380-023-02298-3
- Hong J, Yi JH. The relationship of subjective social status to mental health in South Korean adults. *World Psychiatry*. 2017;16(1):107. PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC5269493/

**조사표:**

- 통계청 사회조사: https://kostat.go.kr/statDesc.es?act=view&mid=a10501010000&sttr_cd=S004002 (3단계 계층의식: 상층/중층/하층)
- [한국인의 행복조사(2023).pdf](한국인의%20행복조사(2023).pdf)
- [2024년 경제활동인구조사 지침서_외부용.pdf](2024년%20경제활동인구조사%20지침서_외부용.pdf)
- [제8차 한국표준직업분류](제8차+한국표준직업분류+개정+분류+항목표.hwpx)
- [MacArthur Scale (SPARQtools)](MacArthur-Scale-of-Subjective-Social-Status-Adult-Version.doc)

**내부 문서:**

- [psych101_201_dataset_search.md](../psych101_201_dataset_search.md)
- [Depression_Risk_Factors_Umbrella_Reviews_2015-2025.md](../PHQ9/Depression_Risk_Factors_Umbrella_Reviews_2015-2025.md)
- [251030_data_prompt.md](../../kpsych-101-hub/docs/plan/proposal-ver2/seonu/251030_data_prompt.md)
- [PHQ9_KOR.pdf](../PHQ9/PHQ9_KOR.pdf) (An et al., 2013)

**데이터셋:**

- Psych-101: https://huggingface.co/datasets/marcelbinz/Psych-101
- Psych-201: https://github.com/marcelbinz/Psych-201
