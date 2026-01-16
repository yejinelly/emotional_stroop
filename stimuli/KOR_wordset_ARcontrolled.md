# 한국어 정서 단어 자료 (Arousal 통제 버전)

[VA-KOR GitHub](https://github.com/smbslt3/VA-KOR)

## Stroop 단어 선정 과정

### 기본 자료
- **통합 자료 (VA_KOR_annot.csv)** 기준
- 민경환 (2005) 친숙성 데이터 참고

### 필터링 단계

| 단계 | 기준 | 총 | Negative | Neutral | Positive |
|------|------|-----|----------|---------|----------|
| 1. 원본 | 전체 | 1,339 | - | - | - |
| 2. 글자 수 | 2-4글자 | 1,249 | - | - | - |
| 3. Valence 분류 | Neg<-1, Neu±0.5, Pos>1 | 1,081 | 485 | 253 | 343 |
| 4. 친숙성 (1-7점) | ≥3.0 (민경환 매칭) | - | 211 | 28 | 70 |
| 5. Pos 선정 | 친숙성 우선 + arousal 순 보충 | - | - | - | - |
| 6. Neg 선정 | 친숙성 순 선별 | - | - | - | - |
| 7. 품사 통제 | 명사 32 + 술어 16 | 144 | 48 | 48 | 48 |

---

## 4. Positive 선정 과정

친숙성 ≥3.0: 70개 (명사 18, 술어 52)

- **명사**: 친숙성 ≥3.0 통과한 18개 전부 포함 + 친숙성 없는 pool에서 외래어/속어 제외 후 arousal 높은 순 14개 보충
- **술어**: 친숙성 ≥3.0 통과한 52개 중 친숙성 높은 순 16개 선택
- **제외**: 외래어/속어 (아싸, 브라보, 앙코르, 아이디어, 보디빌더, 화이팅 등)

---

## 5. Negative 선정 과정

친숙성 ≥3.0: 211개 (명사 47, 술어 164)

- **명사**: 친숙성 ≥3.0 통과한 47개 중 사자성어(전전긍긍, 노발대발) 제외, 친숙성 높은 순 32개 선택
- **술어**: 친숙성 ≥3.0 통과한 164개 중 친숙성 높은 순 16개 선택
- **제외**: 사자성어 (전전긍긍, 노발대발)

---

## Arousal 매칭 방법 (참고용)

### 참고 문헌
- [Emotional Stroop task: effect of word arousal and subject anxiety](https://link.springer.com/article/10.1007/s00426-008-0154-6) - Arousal이 emotional interference 결정
- [ERP Correlates of Valence, Arousal, and Subjective Significance](https://pmc.ncbi.nlm.nih.gov/articles/PMC7947367/) - Valence × Arousal orthogonal design
- [N450 and LPC in Emotional Stroop](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.00880/full) - High/Low arousal 층화 샘플링

---

## 참고: 자료 목록

### 1. 민경환 (2005)
**한국어 감정단어의 목록 작성과 차원 탐색**
- 434개 단어 (Valence, Arousal, 원형성, 친숙성)
- 척도: 1~7
- 박인조, & 민경환. (2005). 한국심리학회지: 사회및성격, 19(1), 109-129.
- 파일: `VA_KOR_2005_MIN.csv`

### 2. 고일주 (2013)
**소셜 미디어에서 사용되는 한국어 정서 단어의 정서가, 활성화 차원 측정**
- 267개 단어 (Valence, Activation)
- 척도: 1~7
- 이신영, & 고일주. (2013). 감성과학, 16(2), 167-176.
- 파일: `VA_KOR_2013_KO.csv`

### 3. 이윤형 (2016)
**정서가, 각성가 및 구체성 평정을 통한 한국어 정서단어 목록 개발**
- 450개 단어 (Valence, Arousal, Concreteness)
- 척도: 1~9
- 홍영지, 남예은, & 이윤형. (2016). 인지과학, 27(3), 377-406.
- 파일: `VA_KOR_2016_LEE.csv`
- **Emotional Stroop task 검증 완료** (논문 내 연구2에서 42명 대상 검증)

### 4. 김청택 (2022)
**Emotion Evaluator: Expanding the Affective Lexicon with Neural Network Model**
- 257개 단어 (Valence, Arousal)
- 척도: -3~3
- Lee, J., Lim, J., Park, J., & Kim, C. (2022). Proceedings of the Annual Meeting of the Cognitive Science Society (Vol. 44, No. 44).
- 파일: `VA_KOR_2022_KIM.csv`

### 5. 통합 자료 (VA_KOR_annot.csv)
- 상기 4개 자료 통합 + 중복 처리 + 뜻풀이 추가
- 정규화: -3~3
- Lee et al. (2022) 연구에서 사용
