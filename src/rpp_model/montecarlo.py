"""Monte Carlo propagation of parameter uncertainty through the RPP identity."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .model import Params, compute_case


def _triangular(rng, low, mode, high, n):
    low, mode, high = float(low), float(mode), float(high)
    if high <= low:
        return np.full(n, mode)
    mode = min(max(mode, low), high)
    return rng.triangular(low, mode, high, n)


def _beta_from_range(rng, p, lo, hi, n):
    """Beta draw whose central 80% roughly spans [lo, hi] around p."""
    p = min(max(p, 1e-3), 1 - 1e-3)
    width = max(hi - lo, 0.02)
    # choose concentration so that sd ~ width / 2.56 (80% interval of a normal)
    sd = width / 2.56
    kappa = max(p * (1 - p) / sd**2 - 1, 2.0)
    return rng.beta(p * kappa, (1 - p) * kappa, n)


def simulate_case(p: Params, carrier: str, route_id: str, cabin: str, band_id: str,
                  n: int = 20000, seed: int = 42, surcharge_sd_frac: float = 0.15) -> dict | None:
    base = compute_case(p, carrier, route_id, cabin, band_id)
    if base is None:
        return None
    rng = np.random.default_rng(seed)
    V = _triangular(rng, base["v_real_low"], base["v_real_rt"], base["v_real_high"], n)
    P = _beta_from_range(rng, base["p_award"], base["p_low"], base["p_high"], n)
    km = None
    from .model import plus_multiplier
    km = plus_multiplier(p, carrier, base["market"], band_id)
    if km is not None:
        K = _triangular(rng, km[0], km[1], km[2], n)
    else:
        K = None
    # fuel surcharge / fees vary by period: lognormal-ish jitter around the point value
    C = base["c_cash_rt"] * np.clip(rng.normal(1.0, surcharge_sd_frac, n), 0.5, 1.6) if base["c_cash_rt"] > 0 else np.zeros(n)
    r = base["floor_rate"]
    V_own = base["v_own_rt"] * (V / base["v_real_rt"])  # own-carrier fare co-moves with demand
    m_base = base["m_base_rt"]
    m_points = V_own / r
    if K is not None:
        m_plus = K * m_base
        use_plus = (m_plus + C / r) < m_points
        m_fb = np.where(use_plus, m_plus, m_points)
        c_fb = np.where(use_plus, C, 0.0)
    else:
        m_fb = m_points
        c_fb = np.zeros(n)
    m_eff = P * m_base + (1 - P) * m_fb
    c_exp = P * C + (1 - P) * c_fb
    rpp = (V - c_exp) / m_eff
    rpp_base = (V - C) / m_base
    q = np.percentile(rpp, [5, 10, 25, 50, 75, 90, 95])
    return dict(
        carrier=carrier, route_id=route_id, route_label=base["route_label"], cabin=cabin, band_id=band_id,
        rpp_point=base["rpp_eff"], rpp_mean=float(rpp.mean()),
        rpp_p05=q[0], rpp_p10=q[1], rpp_p25=q[2], rpp_p50=q[3], rpp_p75=q[4], rpp_p90=q[5], rpp_p95=q[6],
        rpp_base_p50=float(np.median(rpp_base)),
        prob_below_floor=float((rpp < r).mean()),
        prob_below_1yen=float((rpp < 1.0).mean()),
        samples=rpp,
    )


def simulate_all(p: Params, cases: list[tuple[str, str, str]], n: int = 20000, seed: int = 42) -> tuple[pd.DataFrame, dict]:
    rows, samples = [], {}
    for i, (carrier, route_id, cabin) in enumerate(cases):
        for j, band_id in enumerate(p.bands["band_id"]):
            res = simulate_case(p, carrier, route_id, cabin, band_id, n=n, seed=seed + 1000 * i + j)
            if res is None:
                continue
            samples[(carrier, route_id, cabin, band_id)] = res.pop("samples")
            rows.append(res)
    return pd.DataFrame(rows), samples


def pooled_distribution(p: Params, samples: dict, weights: dict | None = None) -> np.ndarray:
    """Pool per-band samples into a traveler-weighted mixture for a (carrier, route, cabin)."""
    w = p.bands.set_index("band_id")["traveler_weight"].to_dict()
    out = []
    for (carrier, route_id, cabin, band_id), s in samples.items():
        k = int(round(len(s) * w[band_id]))
        out.append(s[:k])
    return np.concatenate(out) if out else np.array([])
