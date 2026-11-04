"""Run the full RPP analysis: tables, Monte Carlo, sensitivity, fuel-surcharge scenarios and figures.

Usage:
    python3 src/run_analysis.py [--params data/params] [--out output] [--n 20000] [--no-figures]
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
from rpp_model.model import (PROFILES, Params, anchored_values, award_cash_rt, compute_case, decomposition,  # noqa: E402
                             enumerate_cases, floor_rate, run_all, weighted_summary)
from rpp_model.montecarlo import pool_samples, simulate_all  # noqa: E402
from rpp_model.sensitivity import tornado  # noqa: E402


def df_to_markdown(df: pd.DataFrame, floatfmt: str = "{:,.2f}") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if pd.isna(v) else floatfmt.format(v))
            elif isinstance(v, (bool, np.bool_)):
                cells.append("True" if v else "False")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def pivot(df, value, index=("carrier", "route_label", "cabin")):
    return df.pivot_table(index=list(index), columns="band_id", values=value, aggfunc="first").reset_index()


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
    params_dir = Path(args.params)

    p = Params.load(params_dir)
    results = run_all(p)
    results["c_components"] = results["c_components"].apply(lambda d: json.dumps(d, ensure_ascii=False))
    results.to_csv(tdir / "rpp_results_all_cases.csv", index=False)

    summary = weighted_summary(results)
    anchors = anchored_values(p, results)
    summary = summary.merge(anchors[["carrier", "route_id", "cabin", "anchored_yen_per_mile", "anchor_type", "anchor_rt_jpy", "blog_claim_yen_per_mile"]],
                            on=["carrier", "route_id", "cabin"], how="left")
    summary["ratio_N_to_anchor"] = summary["rpp_N_wavg"] / summary["anchored_yen_per_mile"]
    summary["ratio_S_to_anchor"] = summary["rpp_S_wavg"] / summary["anchored_yen_per_mile"]
    summary.to_csv(tdir / "rpp_summary_by_case.csv", index=False)
    anchors.to_csv(tdir / "anchored_values.csv", index=False)

    # Alternative band weighting (calendar share of days instead of the assumed traveller share) — robustness of the headline "加重" values.
    if "calendar_share" in p.bands.columns:
        alt = results.merge(p.bands[["band_id", "calendar_share"]], on="band_id", how="left")

        def agg_alt(g):
            w = g["calendar_share"] / g["calendar_share"].sum()
            return pd.Series(dict(route_label=g["route_label"].iloc[0], rpp_N_wavg_calendar=(g["rpp_N"] * w).sum(), rpp_S_wavg_calendar=(g["rpp_S"] * w).sum()))

        alt = alt.groupby(["carrier", "route_id", "cabin"]).apply(agg_alt, include_groups=False).reset_index()
        alt = alt.merge(summary[["carrier", "route_id", "cabin", "rpp_N_wavg", "rpp_S_wavg"]], on=["carrier", "route_id", "cabin"], how="left")
        alt["diff_N_calendar_minus_traveler"] = alt["rpp_N_wavg_calendar"] - alt["rpp_N_wavg"]
        alt["diff_S_calendar_minus_traveler"] = alt["rpp_S_wavg_calendar"] - alt["rpp_S_wavg"]
        alt.to_csv(tdir / "rpp_summary_alt_weights.csv", index=False)

    piv_N = pivot(results, "rpp_N"); piv_N.to_csv(tdir / "rpp_N_by_demand_band.csv", index=False)
    piv_S = pivot(results, "rpp_S"); piv_S.to_csv(tdir / "rpp_S_by_demand_band.csv", index=False)
    piv_aw = pivot(results, "rpp_award_N"); piv_aw.to_csv(tdir / "rpp_award_N_if_seat_obtained_by_band.csv", index=False)
    piv_awS = pivot(results, "rpp_award_S"); piv_awS.to_csv(tdir / "rpp_award_S_if_seat_obtained_by_band.csv", index=False)
    piv_used = pivot(results, "award_used_N"); piv_used.to_csv(tdir / "award_used_N_by_band.csv", index=False)
    piv_path = pivot(results, "path_unavail_N"); piv_path.to_csv(tdir / "path_if_unavailable_N_by_band.csv", index=False)
    piv_m = pivot(results, "m_expected_rt"); piv_m.to_csv(tdir / "expected_miles_N_by_band.csv", index=False)

    # ---------------- Monte Carlo (both profiles) ----------------
    cases = enumerate_cases(p)
    mc_frames, pooled_frames, market_frames = [], [], []
    for prof in ("N", "S"):
        mc, samples = simulate_all(p, cases, profile=prof, n=args.n)
        mc_frames.append(mc)
        for carrier, route_id, cabin in cases:
            s = pool_samples(p, samples, [(carrier, route_id, cabin)])
            if s.size == 0:
                continue
            q = np.percentile(s, [10, 25, 50, 75, 90])
            label = results[(results.carrier == carrier) & (results.route_id == route_id)].route_label.iloc[0]
            pooled_frames.append(dict(profile=prof, carrier=carrier, route_id=route_id, route_label=label, cabin=cabin,
                                      rpp_p10=q[0], rpp_p25=q[1], rpp_p50=q[2], rpp_p75=q[3], rpp_p90=q[4], rpp_mean=s.mean()))
        for carrier in ("ANA", "JAL"):
            for market in ("domestic", "international"):
                keys = [(c, r, cab) for (c, r, cab) in cases if c == carrier and p.routes.set_index("route_id").loc[r, "market"] == market]
                s = pool_samples(p, samples, keys)
                if s.size:
                    q = np.percentile(s, [10, 25, 50, 75, 90])
                    market_frames.append(dict(profile=prof, carrier=carrier, market=market, n_cases=len(keys),
                                              rpp_p10=q[0], rpp_p25=q[1], rpp_p50=q[2], rpp_p75=q[3], rpp_p90=q[4], rpp_mean=s.mean()))
    mc_all = pd.concat(mc_frames, ignore_index=True)
    mc_all.to_csv(tdir / "montecarlo_summary.csv", index=False)
    pooled = pd.DataFrame(pooled_frames); pooled.to_csv(tdir / "montecarlo_pooled_by_case.csv", index=False)
    by_market = pd.DataFrame(market_frames); by_market.to_csv(tdir / "montecarlo_pooled_by_market.csv", index=False)

    # ---------------- sensitivity (profile N) ----------------
    rep_path = params_dir / "representative_cases.csv"
    tor_frames = []
    reps = pd.read_csv(rep_path, comment="#", skipinitialspace=True) if rep_path.exists() else pd.DataFrame()
    for _, r in reps.iterrows():
        try:
            t = tornado(p, r.carrier, r.route_id, r.cabin, r.band_id, profile="N")
        except Exception as e:  # noqa: BLE001
            print("tornado skipped", r.to_dict(), e)
            continue
        t.insert(0, "case", f"{r.carrier} {r.route_id} {r.cabin} {r.band_id}")
        tor_frames.append(t)
    if tor_frames:
        pd.concat(tor_frames).to_csv(tdir / "sensitivity_tornado_N.csv", index=False)

    # ---------------- fuel-surcharge regime scenarios (international, band D2, both profiles) ----------------
    fuel_tbl = None
    fs_path = params_dir / "fuel_scenarios.csv"
    if fs_path.exists():
        fs = pd.read_csv(fs_path, comment="#", skipinitialspace=True)
        rows_fs = []
        for carrier, route_id, cabin in cases:
            if p.routes.set_index("route_id").loc[route_id, "market"] != "international":
                continue
            C0, comp = award_cash_rt(p, carrier, route_id, cabin)
            f_now = comp.get("fuel_surcharge", 0.0)
            if f_now == 0:
                continue
            label = results[(results.carrier == carrier) & (results.route_id == route_id)].route_label.iloc[0]
            for _, srow in fs.iterrows():
                f_new = float(srow[route_id]) * 2.0
                for prof in ("N", "S"):
                    res = compute_case(p, carrier, route_id, cabin, "D2", profile=prof, c_override=C0 - f_now + f_new)
                    if res is None:
                        continue
                    rows_fs.append(dict(case=f"{carrier} {label} {cabin}", profile=prof, carrier=carrier, route_id=route_id, cabin=cabin,
                                        scenario_id=srow.scenario_id, scenario_label=srow.label_ja, fuel_ow=float(srow[route_id]),
                                        c_cash_rt=res["c_cash_rt"], rpp_award=res["rpp_award"], rpp=res["rpp"], award_used=res["award_used"]))
        fuel_all = pd.DataFrame(rows_fs)
        fuel_all.to_csv(tdir / "fuel_surcharge_scenarios.csv", index=False)
        sel = fuel_all[(fuel_all.profile == "N") & fuel_all.case.isin(["ANA 東京-ロンドン Y", "JAL 東京-ロンドン Y", "ANA 東京-ホノルル Y",
                                                                       "JAL 東京-ニューヨーク C", "ANA 東京-ニューヨーク C", "ANA 東京-バンコク Y"])]
        fuel_tbl = sel if not sel.empty else None

    # ---------------- decomposition (waterfall) for representative anchored cases ----------------
    decomp_rows, decomp_specs = [], [("ANA", "HND-OKA", "Y", "D2"), ("JAL", "HND-OKA", "Y", "D3"), ("ANA", "TYO-NYC", "C", "D2"), ("JAL", "TYO-HNL", "C", "D2"), ("ANA", "TYO-LON", "F", "D2")]
    decomps = {}
    for carrier, route_id, cabin, band_id in decomp_specs:
        try:
            steps = decomposition(p, results, carrier, route_id, cabin, band_id, profile="N")
        except Exception as e:  # noqa: BLE001
            print("decomposition skipped", carrier, route_id, cabin, e)
            continue
        decomps[(carrier, route_id, cabin, band_id)] = steps
        cum = 0.0
        for lab, v in steps:
            cum += v
            decomp_rows.append(dict(case=f"{carrier} {route_id} {cabin} {band_id}", step=lab.replace("\n", ""), delta=v, cumulative=cum))
    if decomp_rows:
        pd.DataFrame(decomp_rows).to_csv(tdir / "decomposition_anchor_to_rpp.csv", index=False)

    # ---------------- digest ----------------
    md = ["# モデル出力ダイジェスト（自動生成）", "",
          "記号: RPP_N = 最安追求プロファイル（LCC・他社・新幹線・ZIPAIRも代替、未使用マイルは現金類似交換 0.8円）, "
          "RPP_S = 同一会社利用プロファイル（ANA/JALの有償運賃が代替、未使用マイルはコイン/ポイント 1.2/1.5円）, "
          "rpp_award = 特典枠が取れて使った場合の単純値 (V_real − C)/M_base（負値あり）。各需要帯のRPPは『特典枠あり/なし』の確率加重平均（比の平均）。", ""]
    md.append("## 1. ケース別・旅客加重 RPP と見せかけ換算値")
    show = summary[["carrier", "route_label", "cabin", "v_real_N_wavg", "v_real_S_wavg", "c_cash_rt", "rpp_award_N_wavg", "rpp_N_wavg", "rpp_S_wavg",
                    "award_used_share_N", "anchored_yen_per_mile", "blog_claim_yen_per_mile", "ratio_N_to_anchor"]]
    md.append(df_to_markdown(show)); md.append("")
    md.append("## 2a. 需要帯別 RPP_N（最安追求プロファイル）"); md.append(df_to_markdown(piv_N)); md.append("")
    md.append("## 2b. 需要帯別 RPP_S（同一会社利用プロファイル）"); md.append(df_to_markdown(piv_S)); md.append("")
    md.append("## 2c. 需要帯別 特典枠が取れて使った場合の単純値 (V_real − C)/M_base（プロファイルN、負値＝現金負担が代替価格超）"); md.append(df_to_markdown(piv_aw)); md.append("")
    md.append("## 2d. 特典枠が取れたときに特典経路が最適か（プロファイルN。False＝取れても使わない方が合理的）"); md.append(df_to_markdown(piv_used)); md.append("")
    md.append("## 2e. 特典枠が無いときの最適経路（プロファイルN：plus / coins / keep）"); md.append(df_to_markdown(piv_path)); md.append("")
    md.append("## 3. 需要帯別 期待消費マイル（往復、プロファイルN）"); md.append(df_to_markdown(piv_m, "{:,.0f}")); md.append("")
    md.append("## 4. モンテカルロ（旅客加重プール、プロファイル別）"); md.append(df_to_markdown(pooled)); md.append("")
    md.append("## 5. 市場別プール分布"); md.append(df_to_markdown(by_market)); md.append("")
    if fuel_tbl is not None:
        md.append("## 5b. 燃油サーチャージ水準別シナリオ（国際線・通常期D2・プロファイルN）")
        md.append(df_to_markdown(fuel_tbl[["case", "scenario_label", "fuel_ow", "c_cash_rt", "rpp_award", "rpp", "award_used"]])); md.append("")
    if decomp_rows:
        md.append("## 5c. 見せかけ→実質の分解（プロファイルN）"); md.append(df_to_markdown(pd.DataFrame(decomp_rows))); md.append("")
    if tor_frames:
        md.append("## 6. 感応度（トルネード、プロファイルN）")
        md.append(df_to_markdown(pd.concat(tor_frames)[["case", "parameter", "low_label", "high_label", "rpp_low", "rpp_high", "swing", "rpp_base_case"]]))
    (out / "model_digest.md").write_text("\n".join(md), encoding="utf-8")

    # ---------------- figures ----------------
    if not args.no_figures:
        charts.setup_style()
        coin_floor = float(np.mean([floor_rate(p, c, "coin") for c in ("ANA", "JAL")]))
        charts.fig_anchor_vs_real(summary, anchors, fdir / "fig1_anchor_vs_real.png", floor_rate=coin_floor)
        for prof, col in (("N", "rpp_N"), ("S", "rpp_S")):
            charts.fig_band_heatmap(results[results.market == "domestic"], p.bands, fdir / f"fig2a_rpp_{prof}_domestic.png", value=col,
                                    title=f"需要帯別の実質購買力 RPP_{prof}（円/マイル）— 国内線")
            charts.fig_band_heatmap(results[results.market == "international"], p.bands, fdir / f"fig2b_rpp_{prof}_international.png", value=col,
                                    title=f"需要帯別の実質購買力 RPP_{prof}（円/マイル）— 国際線")
        charts.fig_band_heatmap(results[results.market == "international"], p.bands, fdir / "fig2c_rpp_award_if_seat_international.png",
                                value="rpp_award_N", title="特典枠が取れて使った場合の単純値 (V_real − C)/M_base — 国際線・プロファイルN（負値＝現金負担が代替価格超）")
        charts.fig_fees_vs_alternative(results, fdir / "fig6_cash_fees_vs_alternative_D1.png", band_id="D1", cabin="Y")
        charts.fig_fees_vs_alternative(results, fdir / "fig6b_cash_fees_vs_alternative_D2.png", band_id="D2", cabin="Y")
        caps = p.plus_caps.copy()
        base = p.award_miles[(p.award_miles.carrier == "JAL") & (p.award_miles.season == "base")][["route_id", "cabin", "miles"]].rename(columns={"miles": "base_ow"})
        base = base.merge(p.routes[["route_id", "label_ja"]].rename(columns={"label_ja": "route_label"}), on="route_id")
        charts.fig_plus_caps(caps[caps.carrier == "JAL"], base, fdir / "fig3_jal_plus_caps.png")
        tk_path = params_dir.parent / "observations" / "tokutabi_weekday_2026.csv"
        if tk_path.exists():
            charts.fig_tokutabi_weekday(pd.read_csv(tk_path), fdir / "fig8_ana_tokutabi_weekday.png")
        if fuel_tbl is not None:
            charts.fig_fuel_scenarios(fuel_tbl, fdir / "fig7_fuel_surcharge_scenarios.png")
        floor_by_carrier = {c: floor_rate(p, c, "coin") for c in ("ANA", "JAL")}
        charts.fig_montecarlo_ranges(pooled[pooled.profile == "N"].assign(band_id=""), fdir / "fig4_montecarlo_pooled_N.png", floor_by_carrier,
                                     band_id=None, title="モンテカルロ：旅客加重 RPP_N の不確実性レンジ（ケース別）")
        charts.fig_montecarlo_ranges(pooled[pooled.profile == "S"].assign(band_id=""), fdir / "fig4b_montecarlo_pooled_S.png", floor_by_carrier,
                                     band_id=None, title="モンテカルロ：旅客加重 RPP_S の不確実性レンジ（ケース別）")
        for t in tor_frames:
            cs = t["case"].iloc[0].split()
            lab = results[(results.carrier == cs[0]) & (results.route_id == cs[1])].route_label.iloc[0]
            charts.fig_tornado(t, fdir / f"fig_tornado_{cs[0]}_{cs[1]}_{cs[2]}_{cs[3]}.png",
                               f"感応度分析（プロファイルN）：{cs[0]} {lab} {cs[2]}（{p.bands.set_index('band_id').loc[cs[3], 'label_ja']}）")
        rep = [(r.carrier, r.route_id, r.cabin) for _, r in reps.iterrows()][:4] if not reps.empty else []
        if rep:
            charts.fig_cash_vs_miles_by_band(results, p.bands, rep, fdir / "fig5_cash_vs_miles_by_band.png")
        for (carrier, route_id, cabin, band_id), steps in decomps.items():
            lab = results[(results.carrier == carrier) & (results.route_id == route_id)].route_label.iloc[0]
            charts.fig_waterfall(steps, fdir / f"fig9_decomposition_{carrier}_{route_id}_{cabin}_{band_id}.png",
                                 f"見せかけ→実質の分解：{carrier} {lab} {cabin}（{p.bands.set_index('band_id').loc[band_id, 'label_ja']}、プロファイルN）")

    print("cases:", len(cases), "rows:", len(results))
    print(summary[["carrier", "route_label", "cabin", "rpp_N_wavg", "rpp_S_wavg", "rpp_award_N_wavg", "anchored_yen_per_mile"]].round(2).to_string())


if __name__ == "__main__":
    main()
