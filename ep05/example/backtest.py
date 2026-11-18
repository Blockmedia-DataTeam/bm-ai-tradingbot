"""백테스트 실행기. candles.sqlite(3화)를 읽기만 한다. API 키·주문 API 를 쓰지 않는다. 시각은 3화 데이터대로 UTC."""
import math, sqlite3
from pathlib import Path
import numpy as np, pandas as pd
import strategy as S

ROOT = Path(__file__).parent
MARKETS, BTC = ["KRW-BTC", "KRW-ETH"], "KRW-BTC"
CAPITAL, DAILY_LOSS = 1_000_000, 0.10         # CLAUDE.md 4절
FEE, SLIP, MIN_ORDER = 0.0005, 0.0005, 5_000   # 수수료 매수·매도 각 0.05%, 슬리피지 0.05% 불리하게, 최소 주문 5,000원

def load():
    con = sqlite3.connect(f"file:{ROOT / 'candles.sqlite'}?mode=ro", uri=True)   # 읽기 전용
    q = "SELECT ts_utc, open, close FROM candles WHERE market=? AND unit=60 ORDER BY ts_utc"
    raw = {m: pd.read_sql(q, con, params=(m,), parse_dates=["ts_utc"]).set_index("ts_utc") for m in MARKETS}
    grid = pd.date_range(min(d.index[0] for d in raw.values()), max(d.index[-1] for d in raw.values()), freq="h")
    return {m: d.reindex(grid) for m, d in raw.items()}, grid   # 결측 봉은 NaN: 그 봉에선 판단·체결하지 않는다
def metrics(eq):
    r = np.diff(eq) / eq[:-1]
    sharpe = r.mean() / r.std() * math.sqrt(24 * 365) if r.std() > 0 else 0.0   # 1시간 수익률 기준, 연 환산
    return eq[-1] / eq[0] - 1, float((1 - eq / np.maximum.accumulate(eq)).max()), float(sharpe)
def run(data, p, start, end):
    """[start, end] 를 현금 100%로 시작해 돌린다. 봉 t 종가로 판단 → 봉 t+1 시가로 체결."""
    sl = slice(data[BTC].index.get_loc(start), data[BTC].index.get_loc(end) + 1)
    sig = {m: [s.to_numpy()[sl] for s in S.signals(data[BTC]["close"], data[m]["close"], p)] for m in MARKETS}
    op, cl, mk = ({m: f(data[m]).to_numpy()[sl] for m in MARKETS}       # mk: 평가용, 결측 봉은 직전 종가
                  for f in (lambda d: d["open"], lambda d: d["close"], lambda d: d["close"].ffill()))
    cash, pos, pend, eqs, fees, trips = CAPITAL, dict.fromkeys(MARKETS), {}, [CAPITAL], 0, dict.fromkeys(MARKETS, 0)
    halts, max_w, day, day_eq, halted = 0, 0.0, None, CAPITAL, False
    for i, t in enumerate(data[BTC].index[sl]):
        for m, act in [(m, a) for m, a in pend.items() if not math.isnan(op[m][i])]:  # 1) 직전 봉 판단을 이번 봉 시가로 체결
            del pend[m]                                                              #    (그 봉이 없으면 다음 봉으로 미룬다)
            if act == "buy" and not pos[m] and not halted and (amt := min(int(eqs[-1] * S.WEIGHT), int(cash / (1 + FEE)))) >= MIN_ORDER:
                price, fee = op[m][i] * (1 + SLIP), math.ceil(amt * FEE)
                cash, fees, pos[m] = cash - amt - fee, fees + fee, (amt / price, price)
            elif act == "sell" and pos[m] and (gross := int(pos[m][0] * op[m][i] * (1 - SLIP))) >= MIN_ORDER:
                fee = math.ceil(gross * FEE)
                cash, fees, trips[m], pos[m] = cash + gross - fee, fees + fee, trips[m] + 1, None
        vals = [int(pos[m][0] * mk[m][i]) if pos[m] else 0 for m in MARKETS]
        eqs.append(cash + sum(vals)); max_w = max(max_w, max(vals) / eqs[-1])
        if t.date() != day:                              # 2) 일일 손실 한도: UTC 하루 시작 평가액 대비 10%
            day, day_eq, halted = t.date(), eqs[-2], False
        if not halted and eqs[-1] < day_eq * (1 - DAILY_LOSS):
            halted, halts, pend = True, halts + 1, {m: "sell" for m in MARKETS if pos[m]}
        for m in MARKETS if not halted else []:          # 3) 이번 봉 종가로 판단
            if not (math.isnan(cl[m][i]) or math.isnan(cl[BTC][i])) and \
                    (act := S.decide(pos[m] is not None, pos[m][1] if pos[m] else 0, cl[m][i], *(s[i] for s in sig[m]), p)):
                pend[m] = act
    ret, mdd, sh = metrics(np.array(eqs, float))
    return dict(ret=ret, mdd=mdd, sharpe=sh, fees=fees, trips=trips, halts=halts, max_w=max_w, open_pos=[m for m in MARKETS if pos[m]])
def hold_btc(data, start, end):   # 벤치마크: 구간 첫 봉 시가에 자본 전부로 BTC 매수(비용 포함) 후 보유, 종가로 평가
    d = data[BTC].loc[start:end]
    qty = CAPITAL * (1 - FEE) / (d["open"].dropna().iloc[0] * (1 + SLIP))
    return metrics(np.concatenate([[CAPITAL], (qty * d["close"].ffill()).to_numpy().astype(int)]).astype(float))
def periods(grid):
    split = (grid[-1] - pd.DateOffset(months=3)).normalize()           # 뒤 3개월 = 검증 구간(UTC 0시부터)
    warm = grid[0] + pd.Timedelta(weeks=max(S.GRID["trend_weeks"]))   # 가장 긴 되돌아보기만큼은 준비 기간
    return (warm, split - pd.Timedelta(hours=1)), (split, grid[-1])
def write(rows, bp, bt, bv, tune, val, first, bh_t, bh_v):
    f, pct = lambda d: d.strftime("%Y-%m-%d %H:%M"), lambda x: f"{x * 100:.2f}%"
    line = lambda n, r: (f"| {n} | {pct(r['ret'])} | {pct(r['mdd'])} | {r['sharpe']:.2f} | "
        f"{sum(r['trips'].values())} | {r['fees']:,}원 | " + ", ".join(f"{m} {k}" for m, k in r["trips"].items()) + " |")
    ok = [("샤프 1.0 이상", bv["sharpe"] >= 1.0, f"{bv['sharpe']:.2f}"), ("최대 낙폭 15% 이내", bv["mdd"] <= 0.15, pct(bv["mdd"])),
          ("종목별 왕복 거래 30회 이상", min(bv["trips"].values()) >= 30, ", ".join(f"{m} {k}회" for m, k in bv["trips"].items()))]
    L = ["# 백테스트 리포트", "", "backtest.py 가 자동으로 쓴 파일이다. 실제 주문은 내지 않았다.", "", "## 용어",
         "- 수익률: 원금 100만 원이 구간 끝에 몇 % 늘거나 줄었나. 최대 낙폭: 가장 높았던 평가액에서 가장 많이 떨어진 폭",
         "- 샤프: 출렁인 정도에 비해 얼마나 벌었나(1시간 수익률 평균÷표준편차를 1년으로 환산). 0보다 작으면 손실 쪽",
         "- 왕복 거래: 사고 판 것을 1회로 센다. 슬리피지: 원하는 가격보다 불리하게 체결되는 차이. 여기선 0.05%로 가정",
         "- 체결: 봉(1시간 묶음)이 닫힌 뒤 종가로 판단하고, 다음 봉 시가에 사고판다. 수수료는 매수·매도 각 0.05%", "",
         f"## 전략\n- 이름: {S.NAME}\n- 근거 논문: {S.PAPERS}\n- 매매 종목: {', '.join(MARKETS)} / 큰 추세 판단: 비트코인 가격",
         f"- 매수 비중: 자본(그 시점 평가액)의 {S.WEIGHT:.0%} 고정 (CLAUDE.md 4절 종목당 최대 비중)", "",
         "## 기간 (UTC, 3화 데이터 기준)", f"- 데이터 전체: {f(first)} ~ {f(val[1])}",
         f"- 조정 구간(조정값을 고르는 구간, 앞 9개월): {f(first)} ~ {f(tune[1])}. 이 중 처음 4주는 4주 전 가격이 없어 "
         f"준비 기간으로만 쓰고, 성적은 {f(tune[0])} 부터 잰다", f"- 검증 구간(고른 값을 한 번만 확인하는 구간, 뒤 3개월): {f(val[0])} ~ {f(val[1])}", "",
         "## 조정값", "| 조정값 | 후보 값 | 고른 값 | 범위를 이렇게 잡은 이유 |", "|---|---|---|---|"] + \
        [f"| {S.LABEL[k]} | {', '.join(map(str, v))} | {bp[k]} | {S.WHY[k]} |" for k, v in S.GRID.items()]
    L += ["", f"## 돌린 조합: {len(rows)}개 (27개 중 결과를 보기 전에 고정 시드 {S.SEED}로 무작위 선택)",
          "| 큰 추세(주) | 진입 신호(시간) | 손절폭(%) | 조정 구간 샤프 | 수익률 | 최대 낙폭 | 왕복 거래 |", "|---|---|---|---|---|---|---|"] + \
        [f"| {p['trend_weeks']} | {p['entry_hours']} | {p['stop_pct']} | {r['sharpe']:.2f} | {pct(r['ret'])} | {pct(r['mdd'])} | {sum(r['trips'].values())} |" for p, r in rows]
    L += ["", "## 결과 (고른 조합 하나)", "| 구간 | 수익률 | 최대 낙폭 | 샤프 | 왕복 거래 | 수수료 총액 | 종목별 왕복 거래 |",
          "|---|---|---|---|---|---|---|", line("조정 구간", bt), line("검증 구간", bv), "",
          f"- 일일 손실 한도(10%) 발동: 조정 {bt['halts']}회, 검증 {bv['halts']}회 / 한 종목이 평가액에서 차지한 최대 비중: "
          f"조정 {pct(bt['max_w'])}, 검증 {pct(bv['max_w'])} (살 때 40%, 이후 가격이 오르면 40%를 넘을 수 있음)",
          f"- 구간 끝에 들고 있던 종목: 조정 {bt['open_pos'] or '없음'}, 검증 {bv['open_pos'] or '없음'} (팔지 않고 마지막 종가로 평가, 거래 횟수엔 미포함)", "",
          "## 벤치마크: 같은 기간 비트코인을 사서 들고만 있었을 때 (매수 비용 포함)", "| 구간 | 수익률 | 최대 낙폭 |", "|---|---|---|",
          f"| 조정 구간 | {pct(bh_t[0])} | {pct(bh_t[1])} |", f"| 검증 구간 | {pct(bh_v[0])} | {pct(bh_v[1])} |", "",
          "## 채택 기준 (검증 구간)"] + [f"- {n}: {v} → {'통과' if o else '미달'}" for n, o, v in ok]
    L += [f"- 판정: **{'통과' if all(o for _, o, _ in ok) else '미달 (' + ', '.join(n for n, o, _ in ok if not o) + ')'}**",
          "- 통과 여부와 관계없이 실전 투입은 권하지 않는다. 다음 단계는 CLAUDE.md 2절 순서대로 모의투자 2주 이상이다.", ""]
    (ROOT / "research" / "backtest_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

if __name__ == "__main__":
    data, grid = load(); tune, val = periods(grid)
    rows = [(p, run(data, p, *tune)) for p in S.combos()]
    bp, bt = max(rows, key=lambda x: x[1]["sharpe"])        # 조정 구간 샤프로만 고른다
    bv = run(data, bp, *val)                                # 검증 구간은 이 조합으로 딱 한 번만 계산한다
    write(rows, bp, bt, bv, tune, val, grid[0], hold_btc(data, *tune), hold_btc(data, *val))
    print(f"리포트 작성: research/backtest_report.md (조합 {len(rows)}개, 고른 조합 {bp})")
