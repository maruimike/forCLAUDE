"""Run the full RPP analysis: tables, Monte Carlo, sensitivity and figures.

Usage:
    python3 src/run_analysis.py [--params data/params] [--out output] [--n 20000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rpp_model import charts  # noqa: E402
from rpp_model.model import Params, anchored_values, enumerate_cases, run_all, weighted_summary  # noqa: E402
from rpp_model.montecarlo import simulate_all  # noqa: E402
from rpp_model.sensitivity import tornado  # noqa: E402


def df_to_markdown(df: pd.DataFrame, floatfmt: str = "{:,.2f}") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if pd.isna(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default="data/params")
    ap.add_argument("--out", default="output")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    tdir, fdir = out / "tables", out / "figures"
    tdir.mkdir(parents=True, exist_ok=True)
    fdir.mkdir(parents=True, exist_ok=True)

    p = Params.load(args.params)
    results = run_all(p)
    results["c_components"] = results["c_components"].apply(json.dumps, ensure_ascii=False)
    results.to_csv(tdir / "rpp_results_all_cases.csv", index=False)

    summary = weighted_summary(results)
    anchors = anchored_values(p, results)
    summary = summary.merge(anchors[["carrier", "route_id", "cabin", "anchored_yen_per_mile", "anchor_type", "anchor_rt_jpy"]],
                            on=["carrier", "route_id", "cabin"], how="left")
    summary["real_to_anchor_ratio"] = summary["rpp_eff_weighted"] / summary["anchored_yen_per_mile"]
    summary.to_csv(tdir / "rpp_summary_by_case.csv", index=False)
    anchors.to_csv(tdir / "anchored_values.csv", index=False)

    # band-level pivot
    piv = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values="rpp_eff").reset_index()
    piv.to_csv(tdir / "rpp_by_demand_band.csv", index=False)
    piv_m = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values="m_eff_rt").reset_index()
    piv_m.to_csv(tdir / "effective_miles_by_demand_band.csv", index=False)

    # Monte Carlo
    cases = enumerate_cases(p)
    mc, samples = simulate_all(p, cases, n=args.n)
    mc.to_csv(tdir / "montecarlo_summary.csv", index=False)

    # pooled (traveler-weighted) distribution per case
    w = p.bands.set_index("band_id")["traveler_weight"].to_dict()
    pooled_rows = []
    for carrier, route_id, cabin in cases:
        parts = []
        for b, wt in w.items():
            s = samples.get((carrier, route_id, cabin, b))
            if s is None:
                continue
            parts.append(s[: int(round(len(s) * wt))])
        if not parts:
            continue
        s = np.concatenate(parts)
        q = np.percentile(s, [10, 25, 50, 75, 90])
        label = results[(results.carrier == carrier) & (results.route_id == route_id)].route_label.iloc[0]
        pooled_rows.append(dict(carrier=carrier, route_id=route_id, route_label=label, cabin=cabin,
                                rpp_p10=q[0], rpp_p25=q[1], rpp_p50=q[2], rpp_p75=q[3], rpp_p90=q[4],
                                rpp_mean=s.mean()))
    pooled = pd.DataFrame(pooled_rows)
    pooled.to_csv(tdir / "montecarlo_pooled_by_case.csv", index=False)

    # market-level pooled distributions
    market_rows = []
    for carrier in sorted(results.carrier.unique()):
        for market in ("domestic", "international"):
            parts = []
            for (c, rid, cab, b), s in samples.items():
                if c != carrier:
                    continue
                if results[(results.route_id == rid)].market.iloc[0] != market:
                    continue
                parts.append(s[: int(round(len(s) * w[b]))])
            if parts:
                s = np.concatenate(parts)
                q = np.percentile(s, [10, 25, 50, 75, 90])
                market_rows.append(dict(carrier=carrier, market=market, n_cases=len(parts) // len(w),
                                        rpp_p10=q[0], rpp_p25=q[1], rpp_p50=q[2], rpp_p75=q[3], rpp_p90=q[4], rpp_mean=s.mean()))
    pd.DataFrame(market_rows).to_csv(tdir / "montecarlo_pooled_by_market.csv", index=False)

    # sensitivity for representative cases (listed in params/representative_cases.csv if present)
    rep_path = Path(args.params) / "representative_cases.csv"
    tor_frames = []
    if rep_path.exists():
        reps = pd.read_csv(rep_path, comment="#", skipinitialspace=True)
        for _, r in reps.iterrows():
            try:
                t = tornado(p, r.carrier, r.route_id, r.cabin, r.band_id)
            except Exception as e:  # noqa: BLE001
                print("tornado skipped", r.to_dict(), e)
                continue
            t.insert(0, "case", f"{r.carrier} {r.route_id} {r.cabin} {r.band_id}")
            tor_frames.append(t)
            if not args.no_figures:
                lab = results[(results.carrier == r.carrier) & (results.route_id == r.route_id)].route_label.iloc[0]
                charts.setup_style()
                charts.fig_tornado(t, fdir / f"fig_tornado_{r.carrier}_{r.route_id}_{r.cabin}_{r.band_id}.png",
                                   f"感応度分析：{r.carrier} {lab} {r.cabin}（{p.bands.set_index('band_id').loc[r.band_id,'label_ja']}）")
    if tor_frames:
        pd.concat(tor_frames).to_csv(tdir / "sensitivity_tornado.csv", index=False)

    # markdown digest
    md = ["# モデル出力ダイジェスト（自動生成）", ""]
    md.append("## 1. ケース別・旅客加重 RPP と見せかけ換算値")
    show = summary[["carrier", "route_label", "cabin", "v_real_wavg", "c_expected_wavg", "m_eff_wavg",
                    "rpp_base_wavg", "rpp_eff_weighted", "rpp_eff_min", "rpp_eff_max", "anchored_yen_per_mile", "real_to_anchor_ratio"]]
    md.append(df_to_markdown(show))
    md.append("")
    md.append("## 2. 需要帯別 RPP（円/マイル）")
    md.append(df_to_markdown(piv))
    md.append("")
    md.append("## 3. 需要帯別 実効必要マイル（往復）")
    md.append(df_to_markdown(piv_m, "{:,.0f}"))
    md.append("")
    md.append("## 4. モンテカルロ（旅客加重プール）")
    md.append(df_to_markdown(pooled))
    md.append("")
    md.append("## 5. 市場別プール分布")
    md.append(df_to_markdown(pd.DataFrame(market_rows)))
    if tor_frames:
        md.append("")
        md.append("## 6. 感応度（トルネード）")
        md.append(df_to_markdown(pd.concat(tor_frames)[["case", "parameter", "low_label", "high_label", "rpp_low", "rpp_high", "swing", "rpp_base_case"]]))
    (out / "model_digest.md").write_text("\n".join(md), encoding="utf-8")

    if not args.no_figures:
        charts.setup_style()
        floor_by_carrier = {c: float(p.floor_rates[(p.floor_rates.carrier == c) & (p.floor_rates.representative == 1)].yen_per_mile.iloc[0])
                            for c in sorted(results.carrier.unique())}
        charts.fig_anchor_vs_real(summary.dropna(subset=["anchored_yen_per_mile"]), anchors, fdir / "fig1_anchor_vs_real.png",
                                  floor_rate=float(np.mean(list(floor_by_carrier.values()))))
        charts.fig_band_heatmap(results, p.bands, fdir / "fig2_rpp_by_demand_band.png")
        charts.fig_band_heatmap(results, p.bands, fdir / "fig2b_effective_miles_by_band.png", value="m_eff_rt",
                                title="需要帯別の実効必要マイル数（往復）")
        charts.fig_montecarlo_ranges(pooled.assign(band_id=""), fdir / "fig4_montecarlo_pooled.png", floor_by_carrier, band_id=None,
                                     title="モンテカルロ：旅客加重 RPP の不確実性レンジ（ケース別）")
        obs_path = Path(args.params).parent / "observations" / "jal_plus_observations.csv"
        if obs_path.exists():
            obs = pd.read_csv(obs_path, comment="#", skipinitialspace=True)
            obs = obs.merge(p.bands[["band_id", "label_ja"]].rename(columns={"label_ja": "band_label"}), on="band_id", how="left")
            charts.fig_plus_multipliers(obs, fdir / "fig3_jal_plus_multipliers.png")
        # cash vs miles elasticity small multiples
        rep = []
        if rep_path.exists():
            reps = pd.read_csv(rep_path, comment="#", skipinitialspace=True)
            rep = [(r.carrier, r.route_id, r.cabin) for _, r in reps.iterrows()][:4]
        if rep:
            charts.fig_cash_vs_miles_by_band(results, p.bands, rep, fdir / "fig5_cash_vs_miles_by_band.png")

    print("cases:", len(cases), "rows:", len(results))
    print(summary[["carrier", "route_label", "cabin", "rpp_eff_weighted", "anchored_yen_per_mile"]].to_string())


if __name__ == "__main__":
    main()
