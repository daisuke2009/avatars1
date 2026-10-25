#!/usr/bin/env python3
"""REINS土地探し: 条件判定とボリューム・利回り簡易試算。

使い方: python3 tools/reins_screen.py 面積㎡ 価格万円 建蔽% 容積% 賃料円/戸 [階数]
例:     python3 tools/reins_screen.py 170 3500 60 150 55000
前提は下の定数。賃料はエリア実績から都度入力する。
"""
import sys

BUILD_COST_TSUBO = 90      # 万円/坪 (指示: 坪90万)
EXPENSE_RATE = 0.07        # 諸費用率(土地建物合計に対する仮置き。要確認)
# 階数→戸数: 3階6室 / 4階8室 / 5階10室 (2階は4室と仮置き)
UNITS = {2: 4, 3: 6, 4: 8, 5: 10}  # 旧パターン(参考)
FLOORS = (2, 3)  # 2026-10-25確認: 木造2〜3階、1フロア2〜5室のどれかで9%なら合格
MIN_UNIT_SQM = 15          # CLAUDE.md の設計基準
RENTABLE = 0.80
TARGET_YIELD = 9.0


def land_class(area, price):
    c = []
    if area >= 180 and price <= 4000: c.append("A:180㎡以上/4000万以下")
    if 130 <= area <= 160 and price <= 700: c.append("B:130-160㎡/700万以下")
    if area >= 200 and price <= 1000: c.append("C:200㎡以上/1000万以下")
    return c


def plan(area, price, bcr, far, rent, floors, upf):
    floor_area = min(area * bcr / 100 * floors, area * far / 100)  # ㎡
    # 戸数は階数パターンと、15㎡×有効率の面積制約の小さい方
    by_area = int(floor_area * RENTABLE // MIN_UNIT_SQM)
    units = min(upf * floors, by_area)
    tsubo = floor_area / 3.305785
    build = tsubo * BUILD_COST_TSUBO
    total = (price + build) * (1 + EXPENSE_RATE)
    income = units * rent * 12 / 10000  # 万円
    return floor_area, units, build, total, income / total * 100 if total else 0


if __name__ == "__main__":
    a, p, bcr, far, rent = map(float, sys.argv[1:6])
    print("該当区分:", land_class(a, p) or "条件外")
    best = 0
    for f in ([int(sys.argv[6])] if len(sys.argv) > 6 else FLOORS):
        for upf in (2, 3, 4, 5):
            fa, u, b, t, y = plan(a, p, bcr, far, rent, f, upf)
            best = max(best, y)
            ok = "◎" if y >= TARGET_YIELD else "×"
            print(f"{f}階×{upf}室/階 延床{fa:.0f}㎡ {u}戸 建築{b:,.0f}万 総額{t:,.0f}万 利回り{y:.2f}% {ok}")
    print("判定:", "合格" if best >= TARGET_YIELD else "不合格", f"(最高{best:.2f}%)")
