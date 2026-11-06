# 4화 논문 목록 샘플

봇이 전략 후보의 근거로 쓸 논문입니다. 지시문은 이 목록 안의 논문만 근거로 쓰라고 봇에게 지시합니다. 직접 읽지 않으셔도 됩니다. 봇이 읽고 요약합니다. 1번만 빼고 무료로 볼 수 있는 판본이 있습니다. 링크는 학술 논문 공유 사이트 SSRN, 미국 경제연구소 NBER, 저자 소속 운용사 사이트로 연결됩니다. 1번은 출판사 링크만 있고 무료본은 없습니다.

## 1. 모멘텀의 출발

**Jegadeesh, N. and Titman, S. (1993). Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency.** Journal of Finance 48(1).

과거 3개월에서 12개월 동안 많이 오른 주식을 사고 많이 내린 주식을 팔면 이후 3개월에서 12개월 동안 초과수익이 났다는 연구입니다. "오르던 건 좀 더 오른다"를 처음 데이터로 보여 준 논문이고, 이후 수십 개 시장에서 같은 결과가 반복됐습니다. 첫해에 난 초과수익의 일부는 그다음 2년 동안 사라진다는 점도 같이 적혀 있습니다.

공개본: 없습니다. 학술지 원문은 유료이고 출판사 링크는 https://doi.org/10.1111/j.1540-6261.1993.tb04702.x 입니다. 이 논문은 읽는 용도가 아니라 "모멘텀이 어디서 시작됐는지"를 봇이 바르게 인용하게 하려고 넣었습니다.

## 2. 자기 과거만 보는 모멘텀

**Moskowitz, T., Ooi, Y. H. and Pedersen, L. H. (2012). Time Series Momentum.** Journal of Financial Economics 104(2).

남과 비교하지 않고 그 자산의 과거 12개월 수익률 부호만 보고, 올랐으면 사고 내렸으면 파는 방식입니다. 선물 58개 시장에서 효과가 있었습니다. 들고 있는 양을 변동성에 반비례하게 조절한 점이 중요합니다. 종목이 하나나 둘이어도 쓸 수 있어서 소규모 봇에 맞습니다.

공개본: https://papers.ssrn.com/abstract=2089463

## 3. 한 세기 동안의 추세추종

**Hurst, B., Ooi, Y. H. and Pedersen, L. H. (2017). A Century of Evidence on Trend-Following Investing.** Journal of Portfolio Management 44(1).

1880년부터 137년 동안 67개 시장에서 추세추종이 어떤 성과를 냈는지 본 연구입니다. 1개월, 3개월, 12개월 추세를 섞고 변동성으로 양을 조절한 구조가 전 기간에서 플러스였습니다. 하락장에서 성과가 특히 좋았는데, 이는 공매도가 가능할 때 얘기라 현물만 사는 봇은 "현금으로 피하는 것"까지만 기대해야 합니다.

공개본: https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing

## 4. 암호화폐에서도 모멘텀이 있는가

**Liu, Y. and Tsyvinski, A. (2021). Risks and Returns of Cryptocurrency.** Review of Financial Studies 34(6).

비트코인 수익률이 주식이나 환율로는 설명되지 않고, 1주에서 4주 정도 단기 모멘텀이 있다는 연구입니다. 주식에서 쓰던 3개월에서 12개월보다 훨씬 짧은 기간을 봐야 한다는 뜻입니다. 표본이 2018년까지라 그 뒤 시장에서는 약해졌을 가능성이 있습니다.

공개본: https://www.nber.org/papers/w24877 (2018년 작업 논문 판)

## 5. 시장이 요동칠 때 양을 줄이기

**Moreira, A. and Muir, T. (2017). Volatility-Managed Portfolios.** Journal of Finance 72(4).

직전 기간 변동성이 높았으면 투자 비중을 줄이고 낮았으면 늘리는 단순한 규칙만으로 결과가 좋아진다는 연구입니다. 변동성은 한번 커지면 한동안 이어지는데, 그만큼 기대수익이 커지지는 않기 때문입니다. 레버리지를 못 쓰는 현물 봇은 비중을 줄이는 쪽만 가능해서 논문 수치를 그대로 기대하면 안 됩니다.

공개본: https://www.nber.org/papers/w22208 (2016년 작업 논문 판)

## 6. 백테스트에 속지 않기

**Bailey, D. H. and López de Prado, M. (2014). The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality.** Journal of Portfolio Management 40(5).

조정값을 바꿔 가며 백테스트를 여러 번 돌리면 아무 의미 없는 규칙도 좋아 보인다는 경고입니다. 시도 횟수를 감안해 결과가 우연인지 아닌지 확률로 계산하는 방법을 제시합니다. 4화에서는 "그래서 시도 횟수를 전부 기록해야 한다"는 것만 알면 됩니다. 계산은 5화에서 봇이 합니다.

공개본: https://papers.ssrn.com/abstract=2460551

---

목록에 없는 논문을 봇이 근거로 댄다면 지어낸 것일 가능성이 큽니다. 그 경우 지시문을 다시 실행하세요.
