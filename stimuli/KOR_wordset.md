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

## 인용
통합 자료 사용 시:
```
Lee, J., Lim, J., Park, J., & Kim, C. (2022). Emotion Evaluator: Expanding the Affective Lexicon with Neural Network Model. In Proceedings of the Annual Meeting of the Cognitive Science Society (Vol. 44, No. 44).
```
