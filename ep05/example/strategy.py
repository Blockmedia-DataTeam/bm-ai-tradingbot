"""4화 노트 '추천 하나'(후보 2) 전략 규칙. 주문을 내지 않는다. 봉이 닫힌 뒤의 판단(살지/팔지)만 돌려준다."""
import itertools, random

NAME = "큰 추세 안에서만 짧게 사기"
PAPERS = ("4번 Risks and Returns of Cryptocurrency (Liu, Y. and Tsyvinski, A., 2021), "
          "3번 A Century of Evidence on Trend-Following Investing (Hurst, B., Ooi, Y. H. and Pedersen, L. H., 2017)")
WEIGHT = 0.40   # 매수 비중. CLAUDE.md 4절 종목당 최대 비중. 고정값이며 조정하지 않는다
HOURS_PER_WEEK = 168

# 노트에 적힌 조정값 셋(매수 비중 제외)과 각 후보 값 셋. 이유는 리포트에 그대로 옮긴다
GRID = {"trend_weeks": (1, 2, 4), "entry_hours": (6, 12, 24), "stop_pct": (2, 3, 5)}
LABEL = {"trend_weeks": "큰 추세 기간(주)", "entry_hours": "진입 신호 기간(시간)", "stop_pct": "손절폭(%)"}
WHY = {
    "trend_weeks": "노트가 '몇 주 전'으로 정의했고 근거 논문의 추세는 주~월 단위다. 4주를 넘기면 9개월 조정 구간에서 "
                   "준비 기간이 길어지고 추세 전환 표본이 줄어 1·2·4주로 잡았다.",
    "entry_hours": "1시간봉에서 하루 안쪽을 본다. 6시간보다 짧으면 잡음에 따른 잦은 매매로 수수료가 커지고, 24시간보다 "
                   "길면 큰 추세 기간과 겹치고 3개월 검증 구간에서 거래 30회를 채우기 어렵다.",
    "stop_pct": "비트코인 1시간 움직임이 보통 1% 안팎이라 2% 미만은 잡음에 잘린다. 비중 40%에서 5% 손절은 거래당 계좌 "
                "약 2% 손실로, 일일 손실 한도 10%(CLAUDE.md 4절) 안에 여유를 남기는 상한이다.",
}
SEED, N_COMBOS = 5, 20   # 27개 조합 중 20개를 결과를 보기 전에 고정 시드로 무작위 선택


def combos():
    """돌릴 조정값 조합 목록. 결과와 무관하게 시드로만 정해진다."""
    every = list(itertools.product(*GRID.values()))
    picked = sorted(random.Random(SEED).sample(every, N_COMBOS))
    return [dict(zip(GRID, c)) for c in picked]


def signals(btc_close, close, p):
    """봉 t 종가와 그 이전 값만 쓴다(shift 는 과거로만 민다). 결측 봉의 과거 값은 직전 종가로 채운 값을 쓴다.
    반환: 큰 추세 오름, 큰 추세 내림, 진입 신호 오름, 진입 신호 내림 (봉 t 종가 기준 True/False)."""
    btc, own = btc_close.ffill(), close.ffill()
    trend_past = btc.shift(p["trend_weeks"] * HOURS_PER_WEEK)
    entry_past = own.shift(p["entry_hours"])
    return btc > trend_past, btc < trend_past, own > entry_past, own < entry_past


def decide(holding, entry_price, close, trend_up, trend_down, entry_up, entry_down, p):
    """한 봉이 닫힌 뒤의 판단. 'buy' / 'sell' / None. 체결은 다음 봉 시가에서 backtest.py 가 한다.
    규칙 1: 큰 추세가 오름일 때만 산다. 규칙 2: 진입 신호가 오름이면 산다(이미 들고 있으면 그대로 둔다).
    규칙 3: 손절폭만큼 내림, 진입 신호 내림, 큰 추세 내림 중 하나면 전부 판다."""
    if holding:
        stop_hit = close <= entry_price * (1 - p["stop_pct"] / 100)
        return "sell" if (stop_hit or entry_down or trend_down) else None
    return "buy" if (trend_up and entry_up) else None
