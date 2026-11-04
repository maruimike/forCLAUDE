"""Static charts (matplotlib) following the project's data-viz conventions:
one hue for magnitude, emphasis (accent + gray) when one number is the story,
thin marks, hairline grid, text in ink colours, Japanese font.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib import font_manager  # noqa: E402

# reference palette (light mode)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
RED = "#e34948"
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
GRAY_DEEMPH = "#b9b8b1"
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]

FONT_PATH = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"


def setup_style():
    try:
        font_manager.fontManager.addfont(FONT_PATH)
        name = font_manager.FontProperties(fname=FONT_PATH).get_name()
    except Exception:  # pragma: no cover
        name = "sans-serif"
    plt.rcParams.update({
        "font.family": name,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.6, "grid.linestyle": "-", "axes.axisbelow": True,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK2, "text.color": INK,
        "axes.titlecolor": INK, "axes.titlesize": 12, "axes.titleweight": "normal", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "legend.frameon": False, "legend.fontsize": 9, "font.size": 10,
        "figure.dpi": 150,
    })


def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


def _case_label(r) -> str:
    return f"{r['carrier']} {r['route_label']} {r['cabin']}"


# ----------------------------------------------------------------------
def fig_anchor_vs_real(summary: pd.DataFrame, anchors: pd.DataFrame, out: Path, floor_rate: float | None = None, title: str | None = None):
    """Dumbbell: anchored (regular-fare) yen/mile vs traveler-weighted real RPP."""
    if "anchored_yen_per_mile" in summary.columns:
        df = summary.dropna(subset=["anchored_yen_per_mile"]).copy()
    else:
        df = summary.merge(anchors[["carrier", "route_id", "cabin", "anchored_yen_per_mile", "anchor_type"]],
                           on=["carrier", "route_id", "cabin"], how="inner")
    df = df.sort_values("anchored_yen_per_mile", ascending=True).reset_index(drop=True)
    n = len(df)
    fig, ax = plt.subplots(figsize=(9, 0.42 * n + 1.8))
    y = np.arange(n)
    for i, r in df.iterrows():
        ax.plot([r.rpp_eff_weighted, r.anchored_yen_per_mile], [i, i], color=GRID, lw=2, zorder=1)
    ax.scatter(df.anchored_yen_per_mile, y, s=46, color=GRAY_DEEMPH, zorder=2, label="見せかけの換算価値（正規運賃 ÷ 最低マイル、現金負担控除なし）")
    ax.scatter(df.rpp_eff_weighted, y, s=52, color=BLUE, zorder=3, label="実質購買力 RPP（代替最安価格 − 現金負担）÷ 実効マイル")
    bbox = dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none", alpha=0.9)
    for i, r in df.iterrows():
        ax.text(r.anchored_yen_per_mile + 0.15, i, f"{r.anchored_yen_per_mile:.1f}", va="center", fontsize=8, color=INK2)
        ax.text(r.rpp_eff_weighted + 0.15, i + 0.02, f"{r.rpp_eff_weighted:.2f}", va="center", ha="left", fontsize=8, color=INK, bbox=bbox)
    if floor_rate:
        ax.axvline(floor_rate, color=AXIS, lw=1, ls="-", label=f"現金等価フロア（コイン/ポイント交換）≈ {floor_rate:.1f}円")
    ax.set_yticks(y)
    ax.set_yticklabels([_case_label(r) for _, r in df.iterrows()], fontsize=9)
    ax.set_xlabel("1マイルあたりの円換算値（円/マイル）")
    ax.set_xlim(left=0)
    ax.set_title(title or "「見せかけ」の1マイル価値と実質購買力の乖離")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    _save(fig, out)
    return df


def fig_band_heatmap(results: pd.DataFrame, bands: pd.DataFrame, out: Path, value="rpp_eff", title=None):
    piv = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values=value)
    piv = piv[list(bands["band_id"])]
    piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index]
    labels = [f"{c} {r} {k}" for c, r, k in piv.index]
    fig, ax = plt.subplots(figsize=(8.5, 0.38 * len(piv) + 1.8))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seqblue", [SEQ[0], SEQ[-1]])
    vmax = np.nanpercentile(piv.values, 97)
    im = ax.imshow(piv.values, cmap=cmap, aspect="auto", vmin=0, vmax=vmax)
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([bands.set_index("band_id").loc[b, "label_ja"] for b in piv.columns], fontsize=9)
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.grid(False)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if np.isnan(v):
                continue
            color = "#ffffff" if v > vmax * 0.55 else INK
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, color=color)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.ax.tick_params(labelsize=8, color=MUTED, labelcolor=MUTED)
    cb.outline.set_visible(False)
    cb.set_label("円/マイル", color=INK2, fontsize=9)
    ax.set_title(title or "需要帯別の実質購買力 RPP（円/マイル）")
    for s in ax.spines.values():
        s.set_visible(False)
    _save(fig, out)
    return piv


def fig_plus_multipliers(obs: pd.DataFrame, out: Path):
    """Observed JAL 特典航空券PLUS multipliers by demand band (strip plot + median)."""
    order = [b for b in ["D1", "D2", "D3", "D4"] if b in set(obs.band_id)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    rng = np.random.default_rng(0)
    for i, b in enumerate(order):
        s = obs.loc[obs.band_id == b, "multiplier"].astype(float)
        x = i + rng.uniform(-0.18, 0.18, len(s))
        ax.scatter(x, s, s=34, color=BLUE, alpha=0.75, edgecolor=SURFACE, linewidth=1, zorder=3)
        med = s.median()
        ax.plot([i - 0.3, i + 0.3], [med, med], color=INK, lw=2, zorder=4)
        ax.text(i + 0.33, med, f"中央値 {med:.2f}x (n={len(s)})", va="center", fontsize=8.5, color=INK2)
    ax.axhline(1.0, color=AXIS, lw=1)
    ax.text(len(order) - 0.55, 1.02, "基本マイル (1.0x)", fontsize=8, color=MUTED, va="bottom", ha="right")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([obs.loc[obs.band_id == b, "band_label"].iloc[0] for b in order], fontsize=9)
    ax.set_ylabel("必要マイル数 ÷ 基本マイル数（倍）")
    ax.set_ylim(bottom=0.8)
    ax.set_title("JAL 特典航空券PLUS：観測された必要マイル倍率（需要帯別）")
    ax.grid(axis="x", visible=False)
    _save(fig, out)


def fig_montecarlo_ranges(mc: pd.DataFrame, out: Path, floor_rate_by_carrier: dict, band_id: str | None = None, title=None):
    df = mc.copy()
    if band_id:
        df = df[df.band_id == band_id]
    df["label"] = df.apply(lambda r: f"{r.carrier} {r.route_label} {r.cabin}" + (f" / {r.band_id}" if str(r.band_id) else ""), axis=1)
    df = df.sort_values("rpp_p50", ascending=True).reset_index(drop=True)
    n = len(df)
    fig, ax = plt.subplots(figsize=(9, 0.36 * n + 1.8))
    y = np.arange(n)
    ax.hlines(y, df.rpp_p10, df.rpp_p90, color=SEQ[3], lw=5, zorder=2, label="10–90パーセンタイル")
    ax.hlines(y, df.rpp_p25, df.rpp_p75, color=BLUE, lw=5, zorder=3, label="25–75パーセンタイル")
    ax.scatter(df.rpp_p50, y, s=30, color=INK, zorder=4, label="中央値")
    for i, r in df.iterrows():
        ax.text(r.rpp_p90 + 0.08, i, f"{r.rpp_p50:.2f}", va="center", fontsize=8, color=INK2)
    for carrier, fr in floor_rate_by_carrier.items():
        ax.axvline(fr, color=ORANGE if carrier == "JAL" else AQUA, lw=1, ls="-", alpha=0.9,
                   label=f"{carrier} 現金等価フロア {fr:.1f}円/マイル")
    ax.set_yticks(y)
    ax.set_yticklabels(df.label, fontsize=8.5)
    ax.set_xlabel("実質購買力 RPP（円/マイル）")
    ax.set_xlim(left=0)
    ax.set_title(title or "モンテカルロ法による RPP の不確実性レンジ")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    _save(fig, out)


def fig_tornado(tor: pd.DataFrame, out: Path, title: str):
    df = tor.sort_values("swing", ascending=True).reset_index(drop=True)
    base = df["rpp_base_case"].iloc[0]
    fig, ax = plt.subplots(figsize=(8.5, 0.55 * len(df) + 1.6))
    y = np.arange(len(df))
    ax.barh(y, df.rpp_low - base, left=base, color=SEQ[3], height=0.55, label="低位入力")
    ax.barh(y, df.rpp_high - base, left=base, color=BLUE, height=0.55, label="高位入力")
    ax.axvline(base, color=INK, lw=1)
    for i, r in df.iterrows():
        ax.text(r.rpp_low - 0.03, i, f"{r.rpp_low:.2f}", ha="right", va="center", fontsize=8, color=INK2)
        ax.text(r.rpp_high + 0.03, i, f"{r.rpp_high:.2f}", ha="left", va="center", fontsize=8, color=INK2)
    span = max(df.rpp_high.max() - df.rpp_low.min(), 0.1)
    ax.set_xlim(df.rpp_low.min() - 0.12 * span, df.rpp_high.max() + 0.12 * span)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.parameter}\n({r.low_label} ↔ {r.high_label})" for _, r in df.iterrows()], fontsize=8.5)
    ax.set_xlabel(f"RPP（円/マイル）　基準ケース = {base:.2f}")
    ax.set_title(title)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8)
    _save(fig, out)


def fig_waterfall(steps: list[tuple[str, float]], out: Path, title: str, unit="円/マイル"):
    """steps: [(label, value)] where the first is the starting total and the rest are deltas; a final total is appended."""
    labels = [s[0] for s in steps] + ["実質購買力 RPP"]
    vals = [s[1] for s in steps]
    total = sum(vals)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    cum = 0.0
    for i, (lab, v) in enumerate(steps):
        if i == 0:
            ax.bar(i, v, color=GRAY_DEEMPH, width=0.6)
            ax.text(i, v + 0.15, f"{v:.2f}", ha="center", fontsize=9, color=INK)
            cum = v
        else:
            color = RED if v < 0 else BLUE
            bottom = cum if v >= 0 else cum + v
            ax.bar(i, abs(v), bottom=bottom, color=color, width=0.6)
            ax.text(i, cum + (v if v >= 0 else 0) + 0.15, f"{v:+.2f}", ha="center", fontsize=9, color=INK)
            cum += v
    ax.bar(len(steps), total, color=BLUE, width=0.6)
    ax.text(len(steps), total + 0.15, f"{total:.2f}", ha="center", fontsize=9, color=INK)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.5, rotation=0)
    ax.set_ylabel(unit)
    ax.set_ylim(bottom=0)
    ax.set_title(title)
    ax.grid(axis="x", visible=False)
    _save(fig, out)


def fig_cash_vs_miles_by_band(results: pd.DataFrame, bands: pd.DataFrame, cases: list[tuple[str, str, str]], out: Path):
    """Small multiples: for selected cases, cash alternative price and effective miles by band (indexed to D1 = 100)."""
    n = len(cases)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n + 1, 3.6), sharey=True)
    if n == 1:
        axes = [axes]
    blabels = bands.set_index("band_id")["label_ja"].to_dict()
    for ax, (carrier, route_id, cabin) in zip(axes, cases):
        sub = results[(results.carrier == carrier) & (results.route_id == route_id) & (results.cabin == cabin)].set_index("band_id")
        sub = sub.loc[list(bands["band_id"])]
        x = np.arange(len(sub))
        v_idx = sub.v_real_rt / sub.v_real_rt.iloc[0] * 100
        m_idx = sub.m_eff_rt / sub.m_eff_rt.iloc[0] * 100
        ax.plot(x, v_idx, marker="o", color=BLUE, lw=2, ms=6, label="現金代替価格")
        ax.plot(x, m_idx, marker="o", color=ORANGE, lw=2, ms=6, label="実効必要マイル")
        ax.set_xticks(x)
        ax.set_xticklabels([blabels[b][:6] for b in sub.index], fontsize=7.5)
        ax.set_title(f"{carrier} {sub.route_label.iloc[0]} {cabin}", fontsize=10)
        ax.axhline(100, color=AXIS, lw=0.8)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("閑散平日昼 = 100 とした指数")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle("需要帯が上がると現金価格より必要マイルの方が速く膨らむか", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    _save(fig, out)


def fig_fees_vs_alternative(results: pd.DataFrame, out: Path, band_id: str = "D1", cabin: str = "Y"):
    """Award cash out-of-pocket (fuel + fees + taxes) versus the cheapest realistic cash ticket, international economy."""
    df = results[(results.market == "international") & (results.cabin == cabin) & (results.band_id == band_id)].copy()
    df = df.drop_duplicates(subset=["carrier", "route_label"]).sort_values("v_real_rt", ascending=True)
    df["label"] = df.carrier + " " + df.route_label
    n = len(df)
    fig, ax = plt.subplots(figsize=(9, 0.4 * n + 1.8))
    y = np.arange(n)
    ax.barh(y + 0.18, df.v_real_rt / 1e4, height=0.34, color=BLUE, label="現実的な代替最安価格 V_real（往復・税込）")
    ax.barh(y - 0.18, df.c_cash_rt / 1e4, height=0.34, color=ORANGE, label="特典航空券の現金持ち出し C（燃油＋諸税、往復）")
    for i, r in df.iterrows():
        pass
    ax.set_yticks(y)
    ax.set_yticklabels(df.label, fontsize=8.5)
    ax.set_xlabel("万円（往復・1名）")
    ax.set_title(f"特典の現金負担は代替チケット価格に迫る・上回る（{band_id}・エコノミー・2026年11〜12月発券）")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    _save(fig, out)


def fig_fuel_scenarios(tbl: pd.DataFrame, out: Path):
    """RPP under fuel-surcharge regimes: one line per case, x = scenario (ordered by surcharge level)."""
    cases = tbl["case"].unique()
    scen = list(tbl["scenario_label"].unique())
    fig, ax = plt.subplots(figsize=(9, 4.8))
    palette = [BLUE, ORANGE, AQUA, YELLOW, "#e87ba4", "#008300", "#6250d6", RED]
    for i, cs in enumerate(cases):
        sub = tbl[tbl.case == cs].set_index("scenario_label").loc[scen]
        ax.plot(range(len(scen)), sub.rpp_base, marker="o", ms=6, lw=2, color=palette[i % len(palette)], label=cs)
        ax.text(len(scen) - 1 + 0.08, sub.rpp_base.iloc[-1], f"{sub.rpp_base.iloc[-1]:.2f}", fontsize=8, va="center", color=INK2)
    ax.axhline(0, color=AXIS, lw=0.8)
    ax.set_xticks(range(len(scen)))
    ax.set_xticklabels(scen, fontsize=8.5)
    ax.set_ylabel("(V_real − C)/M_base　円/マイル（通常期 D2）")
    ax.set_title("燃油サーチャージの水準がマイルの実質価値を左右する")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.grid(axis="x", visible=False)
    _save(fig, out)


def fig_plus_caps(caps: pd.DataFrame, base: pd.DataFrame, out: Path):
    """Dumbbell: JAL base miles vs PLUS cap (one-way), with multiplier labels."""
    df = caps.merge(base, on=["route_id", "cabin"], how="inner")
    df["label"] = df.route_label + " " + df.cabin
    df["mult"] = df.cap_miles / df.base_ow
    df = df.sort_values("mult", ascending=True).reset_index(drop=True)
    n = len(df)
    fig, ax = plt.subplots(figsize=(9, 0.36 * n + 1.8))
    y = np.arange(n)
    for i, r in df.iterrows():
        ax.plot([r.base_ow / 1e3, r.cap_miles / 1e3], [i, i], color=GRID, lw=2, zorder=1)
    ax.scatter(df.base_ow / 1e3, y, s=40, color=BLUE, zorder=3, label="基本マイル（片道）")
    ax.scatter(df.cap_miles / 1e3, y, s=40, color=ORANGE, zorder=3, label="特典航空券PLUS 上限（片道）")
    for i, r in df.iterrows():
        ax.text(r.cap_miles / 1e3 + 6, i, f"{r.mult:.1f}倍", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels(df.label, fontsize=8.5)
    ax.set_xlabel("必要マイル数（千マイル・片道）")
    ax.set_xlim(left=0)
    ax.set_title("JAL 特典航空券PLUS：基本マイルの4〜9倍まで上がる『二重価格』")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    _save(fig, out)


def fig_tokutabi_weekday(tk: pd.DataFrame, out: Path):
    """Grouped bars: regular R-season miles vs トクたび Wed–Fri vs Sat–Tue by distance band."""
    n = len(tk)
    x = np.arange(n)
    w = 0.26
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.bar(x - w, tk.regular_R_miles_ow, width=w - 0.02, color=GRAY_DEEMPH, label="通常チャート（Rシーズン）")
    ax.bar(x, tk.tokutabi_sat_tue_ow, width=w - 0.02, color=SEQ[4], label="トクたびマイル 土〜火 搭乗")
    ax.bar(x + w, tk.tokutabi_wed_fri_ow, width=w - 0.02, color=BLUE, label="トクたびマイル 水〜金 搭乗")
    for i, r in tk.iterrows():
        ax.text(i + w, r.tokutabi_wed_fri_ow + 150, f"{r.tokutabi_wed_fri_ow:,}", ha="center", fontsize=8, color=INK)
        ax.text(i, r.tokutabi_sat_tue_ow + 150, f"{r.tokutabi_sat_tue_ow:,}", ha="center", fontsize=8, color=INK2)
        ax.text(i - w, r.regular_R_miles_ow + 150, f"{r.regular_R_miles_ow:,}", ha="center", fontsize=8, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{b}区間マイル" for b in tk.distance_band], fontsize=9)
    ax.set_ylabel("必要マイル（片道）")
    ax.set_title("ANAも曜日で値付けしている：トクたびマイルの水〜金 vs 土〜火（2026年9月スナップショット）")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="x", visible=False)
    _save(fig, out)
