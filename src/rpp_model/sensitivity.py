"""One-at-a-time sensitivity (tornado) analysis for a representative case."""
from __future__ import annotations

import pandas as pd

from .model import Params, compute_case, plus_multiplier


def tornado(p: Params, carrier: str, route_id: str, cabin: str, band_id: str) -> pd.DataFrame:
    base = compute_case(p, carrier, route_id, cabin, band_id)
    if base is None:
        raise ValueError("case not computable")
    rows = []

    def add(name, lo_kwargs, hi_kwargs, lo_label, hi_label):
        lo = compute_case(p, carrier, route_id, cabin, band_id, **lo_kwargs)["rpp_eff"]
        hi = compute_case(p, carrier, route_id, cabin, band_id, **hi_kwargs)["rpp_eff"]
        rows.append(dict(parameter=name, low_label=lo_label, high_label=hi_label,
                         rpp_low=min(lo, hi), rpp_high=max(lo, hi), rpp_at_low_input=lo, rpp_at_high_input=hi,
                         swing=abs(hi - lo)))

    add("現金代替価格 V_real", dict(v_override=base["v_real_low"]), dict(v_override=base["v_real_high"]),
        f"{base['v_real_low']:,.0f}円", f"{base['v_real_high']:,.0f}円")
    add("特典枠の空席確率 p", dict(p_override=base["p_low"]), dict(p_override=base["p_high"]),
        f"{base['p_low']:.0%}", f"{base['p_high']:.0%}")
    km = plus_multiplier(p, carrier, base["market"], band_id)
    if km is not None:
        add("PLUS倍率 k", dict(k_override=km[0]), dict(k_override=km[2]), f"{km[0]:.2f}x", f"{km[2]:.2f}x")
    if base["c_cash_rt"] > 0:
        add("現金持ち出し C（燃油・諸税）", dict(c_override=base["c_cash_rt"] * 0.7), dict(c_override=base["c_cash_rt"] * 1.3),
            f"{base['c_cash_rt']*0.7:,.0f}円", f"{base['c_cash_rt']*1.3:,.0f}円")
    fr = p.floor_rates[p.floor_rates.carrier == carrier]
    add("フロア換算率（コイン/ポイント）", dict(r_override=fr.yen_per_mile.min()), dict(r_override=fr.yen_per_mile.max()),
        f"{fr.yen_per_mile.min():.1f}円", f"{fr.yen_per_mile.max():.1f}円")
    df = pd.DataFrame(rows).sort_values("swing", ascending=False)
    df["rpp_base_case"] = base["rpp_eff"]
    return df
