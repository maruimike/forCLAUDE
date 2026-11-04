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

    # fuel-surcharge regime scenarios (international, band D2, both carriers)
    fuel_tbl = None
    fs_path = Path(args.params) / "fuel_scenarios.csv"
    if fs_path.exists():
        from rpp_model.model import award_cash_rt, compute_case
        fs = pd.read_csv(fs_path, comment="#", skipinitialspace=True)
        rows_fs = []
        base_fuel = {r.route_id: None for _, r in p.routes.iterrows()}
        for carrier, route_id, cabin in cases:
            if p.routes.set_index("route_id").loc[route_id, "market"] != "international":
                continue
            C0, comp = award_cash_rt(p, carrier, route_id, cabin)
            f_now = comp.get("fuel_surcharge", 0.0)  # RT at the baseline (Nov-Dec 2026)
            if f_now == 0:
                continue
            label = results[(results.carrier == carrier) & (results.route_id == route_id)].route_label.iloc[0]
            for _, srow in fs.iterrows():
                f_new = float(srow[route_id]) * 2.0
                res = compute_case(p, carrier, route_id, cabin, "D2", c_override=C0 - f_now + f_new)
                if res is None:
                    continue
                rows_fs.append(dict(case=f"{carrier} {label} {cabin}", carrier=carrier, route_id=route_id, cabin=cabin,
                                    scenario_id=srow.scenario_id, scenario_label=srow.label_ja, fuel_ow=float(srow[route_id]),
                                    c_cash_rt=res["c_cash_rt"], rpp_base=res["rpp_base"], rpp_eff=res["rpp_eff"], award_dominated=res["award_dominated"]))
        fuel_tbl_all = pd.DataFrame(rows_fs)
        fuel_tbl_all.to_csv(tdir / "fuel_surcharge_scenarios.csv", index=False)
        sel = fuel_tbl_all[fuel_tbl_all.case.isin(["ANA 東京-ロンドン Y", "JAL 東京-ロンドン Y", "ANA 東京-ホノルル Y", "JAL 東京-ニューヨーク C", "ANA 東京-ニューヨーク C", "ANA 東京-バンコク Y"])]
        fuel_tbl = sel if not sel.empty else None

    # markdown digest
    md = ["# モデル出力ダイジェスト（自動生成）", ""]
    md.append("## 1. ケース別・旅客加重 RPP と見せかけ換算値")
    show = summary[["carrier", "route_label", "cabin", "v_real_wavg", "c_expected_wavg", "m_eff_wavg",
                    "rpp_base_wavg", "rpp_eff_weighted", "rpp_eff_min", "rpp_eff_max", "anchored_yen_per_mile", "real_to_anchor_ratio"]]
    strict = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values="rpp_eff_strict").reset_index()
    strict.to_csv(tdir / "rpp_by_demand_band_strict_same_carrier.csv", index=False)
    basepiv = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values="rpp_base").reset_index()
    basepiv.to_csv(tdir / "rpp_base_if_seat_obtained_by_band.csv", index=False)
    dom = results.pivot_table(index=["carrier", "route_label", "cabin"], columns="band_id", values="award_dominated", aggfunc="first").reset_index()
    dom.to_csv(tdir / "award_dominated_by_band.csv", index=False)
    md.append(df_to_markdown(show))
    md.append("")
    md.append("## 2. 需要帯別 RPP（円/マイル）")
    md.append(df_to_markdown(piv))
    md.append("")
    md.append("## 2b. 需要帯別 RPP（厳格版：同一会社・同一商品の現金運賃のみを代替とみなす）")
    md.append(df_to_markdown(strict))
    md.append("")
    md.append("## 2c. 需要帯別 『特典枠が取れて使った場合』の単純値 (V_real − C)/M_base（負値＝現金負担が代替価格を超える）")
    md.append(df_to_markdown(basepiv))
    md.append("")
    md.append("## 2d. 特典経路がコイン/ポイント経路に劣後するケース（True＝特典枠が取れても使わない方が合理的）")
    md.append(df_to_markdown(dom))
    md.append("")
    md.append("## 3. 需要帯別 実効必要マイル（往復）")
    md.append(df_to_markdown(piv_m, "{:,.0f}"))
    md.append("")
    md.append("## 4. モンテカルロ（旅客加重プール）")
    md.append(df_to_markdown(pooled))
    md.append("")
    md.append("## 5. 市場別プール分布")
    md.append(df_to_markdown(pd.DataFrame(market_rows)))
    if fuel_tbl is not None:
        md.append("")
        md.append("## 5b. 燃油サーチャージ水準別シナリオ（国際線・通常期D2）")
        md.append(df_to_markdown(fuel_tbl[["case", "scenario_label", "fuel_ow", "c_cash_rt", "rpp_base", "rpp_eff", "award_dominated"]]))
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
        charts.fig_band_heatmap(results[results.market == "domestic"], p.bands, fdir / "fig2a_rpp_by_demand_band_domestic.png",
                                title="需要帯別の実質購買力 RPP（円/マイル）— 国内線")
        charts.fig_band_heatmap(results[results.market == "international"], p.bands, fdir / "fig2b_rpp_by_demand_band_international.png",
                                title="需要帯別の実質購買力 RPP（円/マイル）— 国際線")
        charts.fig_band_heatmap(results[results.market == "international"], p.bands, fdir / "fig2c_rpp_base_if_seat_international.png",
                                value="rpp_base", title="特典枠が取れた場合の単純値 (V_real − C)/M_base — 国際線（負値＝現金負担が代替価格超）")
        charts.fig_fees_vs_alternative(results, fdir / "fig6_cash_fees_vs_alternative_D1.png", band_id="D1", cabin="Y")
        charts.fig_fees_vs_alternative(results, fdir / "fig6b_cash_fees_vs_alternative_D2.png", band_id="D2", cabin="Y")
        caps = p.plus_caps.copy()
        base = p.award_miles[(p.award_miles.carrier == "JAL") & (p.award_miles.season == "base")][["route_id", "cabin", "miles"]].rename(columns={"miles": "base_ow"})
        base = base.merge(p.routes[["route_id", "label_ja"]].rename(columns={"label_ja": "route_label"}), on="route_id")
        charts.fig_plus_caps(caps[caps.carrier == "JAL"], base, fdir / "fig3b_jal_plus_caps.png")
        tk_path = Path(args.params).parent / "observations" / "tokutabi_weekday_2026.csv"
        if tk_path.exists():
            charts.fig_tokutabi_weekday(pd.read_csv(tk_path), fdir / "fig8_ana_tokutabi_weekday.png")
        if fuel_tbl is not None:
            charts.fig_fuel_scenarios(fuel_tbl, fdir / "fig7_fuel_surcharge_scenarios.png")
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
