# 한국어 정서 단어 자료

[VA-KOR GitHub](https://github.com/smbslt3/VA-KOR)

## 자료 목록

### 1. 민경환 (2005)
**한국어 감정단어의 목록 작성과 차원 탐색**
- 434개 단어 (Valence, Arousal, 원형성, 친숙성)
- 척도: 1~7
- 박인조, & 민경환. (2005). 한국심리학회지: 사회및성격, 19(1), 109-129.
- [Hugging Face](https://huggingface.co/datasets/jonghwanhyeon/korean-emotion-lexicon)
- 파일: `VA_KOR_2005_MIN.csv`

### 2. 고일주 (2013)
**소셜 미디어에서 사용되는 한국어 정서 단어의 정서가, 활성화 차원 측정**
- 267개 단어 (Valence, Activation)
- 척도: 1~7
- 이신영, & 고일주. (2013). 소셜 미디어에서 사용되는 한국어 정서 단어의 정서가, 활성화 차원 측정. 감성과학, 16(2), 167-176.
- 파일: `VA_KOR_2013_KO.csv`

### 3. 이윤형 (2016)
**정서가, 각성가 및 구체성 평정을 통한 한국어 정서단어 목록 개발**
- 450개 단어 (Valence, Arousal, Concreteness)
- 척도: 1~9
- 홍영지, 남예은, & 이윤형. (2016). 인지과학, 27(3), 377-406.
- [KCI](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART002149809) | [Korea Science](https://koreascience.kr/article/JAKO201630932329075.page)
- 파일: `VA_KOR_2016_LEE.csv`
- **Emotional Stroop task 검증 완료** (논문 내 연구2에서 42명 대상 검증)

### 4. 김청택 (2022)
**Emotion Evaluator: Expanding the Affective Lexicon with Neural Network Model**
- 257개 단어 (Valence, Arousal)
- 척도: -3~3
- Lee, J., Lim, J., Park, J., & Kim, C. (2022). Proceedings of the Annual Meeting of the Cognitive Science Society (Vol. 44, No. 44).
- 파일: `VA_KOR_2022_KIM.csv`

### 5. 통합 자료
**VA_KOR_annot.csv**
- 상기 4개 자료 통합 + 중복 처리 + 뜻풀이 추가
- 정규화: -3~3
- Lee et al. (2022) 연구에서 사용

## Stroop 단어 선정 과정

### 기본 자료
- **통합 자료 (VA_KOR_annot.csv)** 기준
- 민경환 (2005) 친숙성 데이터 참고

### 필터링 단계

| 단계 | 기준 | 총 | Negative | Neutral | Positive |
|------|------|-----|----------|---------|----------|
| 1. 원본 | 전체 | 1,339 | - | - | - |
| 2. 글자 수 | 2-4글자 | 1,249 | - | - | - |
| 3. Valence 분류 | Neg<-1, Neu±0.5, Pos>1 | 1,079 | 479 | 257 | 343 |
| 4. 친숙성 | ≥3.5 (민경환 매칭) | 210 | 142 | 20 | 48 |

### Valence 기준 (정규화 척도 -3~3)
- **Negative**: V < -1.0
- **Neutral**: -0.5 ≤ V ≤ 0.5
- **Positive**: V > 1.0

### 선정 전략
1. **친숙성 ≥ 3.5** 단어 우선 포함
2. 부족분은 친숙성 정보 없는 단어에서 보충
3. 수동으로 부적절한 단어 제외 (비표준어, 전문용어 등)
4. 최종 각 조건 48개씩 선정

### 제한점
- Neutral 단어 중 친숙성 정보 있는 것이 20개뿐
- Neutral 28개는 친숙성 통제 없이 선정 필요

## 인용
통합 자료 사용 시:
```
Lee, J., Lim, J., Park, J., & Kim, C. (2022). Emotion Evaluator: Expanding the Affective Lexicon with Neural Network Model. In Proceedings of the Annual Meeting of the Cognitive Science Society (Vol. 44, No. 44).
```
