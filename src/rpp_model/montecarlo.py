"""Monte Carlo propagation of parameter uncertainty through the RPP model (vectorised version of compute_case)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .model import Params, compute_case, plus_applies, plus_cap_rt, plus_multiplier


def _tri_ppf(u, low, mode, high):
    low, mode, high = float(low), float(mode), float(high)
    if high <= low:
        return np.full_like(u, mode)
    mode = min(max(mode, low), high)
    fc = (mode - low) / (high - low)
    left = low + np.sqrt(u * (high - low) * (mode - low))
    right = high - np.sqrt((1 - u) * (high - low) * (high - mode))
    return np.where(u < fc, left, right)


def _norm_cdf(z):
    # Abramowitz & Stegun 7.1.26 erf approximation (|err| < 1.5e-7)
    t = 1.0 / (1.0 + 0.3275911 * np.abs(z) / np.sqrt(2))
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-(z / np.sqrt(2)) ** 2)
    return 0.5 * (1.0 + np.sign(z) * y)


def _beta_from_range(rng, p, lo, hi, n):
    p = min(max(p, 1e-3), 1 - 1e-3)
    sd = max(hi - lo, 0.02) / 2.56
    kappa = max(p * (1 - p) / sd**2 - 1, 2.0)
    return rng.beta(p * kappa, (1 - p) * kappa, n)


def _lognormal_from_quantiles(rng, p10, p50, p90, n):
    p10, p50, p90 = max(p10, 1e-6), max(p50, 1e-6), max(p90, 1e-6)
    sigma = max((np.log(p90) - np.log(p10)) / 2.5631, 1e-6)
    return rng.lognormal(np.log(p50), sigma, n)


def simulate_case(p: Params, carrier: str, route_id: str, cabin: str, band_id: str, profile: str = "N",
                  n: int = 20000, seed: int = 42, surcharge_sd_frac: float = 0.15, rho_own: float = 0.7) -> dict | None:
    base = compute_case(p, carrier, route_id, cabin, band_id, profile=profile)
    if base is None:
        return None
    rng = np.random.default_rng(seed)
    z1, z2 = rng.standard_normal(n), rng.standard_normal(n)
    u1 = _norm_cdf(z1)
    u2 = _norm_cdf(rho_own * z1 + np.sqrt(1 - rho_own**2) * z2)
    V = _tri_ppf(u1, base["v_real_low"], base["v_real_rt"], base["v_real_high"])
    has_own = not np.isnan(base["v_own_rt"])
    if profile == "S":
        V_own = V
    elif has_own:
        V_own = _tri_ppf(u2, base["v_own_low"], base["v_own_rt"], base["v_own_high"])
        V_own = np.maximum(V_own, V)  # own fare is never below the cheapest alternative that includes it
    else:
        V_own = None
    P = _beta_from_range(rng, base["p_award"], base["p_low"], base["p_high"], n)
    C = base["c_cash_rt"] * np.clip(rng.normal(1.0, surcharge_sd_frac, n), 0.5, 1.6) if base["c_cash_rt"] > 0 else np.zeros(n)
    r_coin, r_alt = base["r_coin"], base["r_alt"]
    m_base = base["m_base_rt"]
    km = plus_multiplier(p, carrier, base["market"], band_id) if plus_applies(carrier, base["market"], cabin) else None
    cap = plus_cap_rt(p, carrier, route_id, cabin)

    def best(paths):
        costs = np.stack([cash + miles * r_alt for _, miles, cash in paths])
        idx = np.argmin(costs, axis=0)
        miles = np.stack([m for _, m, _ in paths])[idx, np.arange(n)]
        cash = np.stack([c for _, _, c in paths])[idx, np.arange(n)]
        v = np.where(miles > 0, (V - cash) / np.where(miles > 0, miles, 1.0), r_alt)
        return v, idx

    zeros = np.zeros(n)
    common = [("keep", zeros, V)]
    if V_own is not None:
        common.append(("coins", V_own / r_coin, zeros))
    vA, iA = best([("award", np.full(n, m_base), C)] + common)
    if km is not None:
        K = _lognormal_from_quantiles(rng, km[0], km[1], km[2], n)
        m_plus = np.maximum(K, 1.0) * m_base
        if cap is not None:
            m_plus = np.minimum(m_plus, cap)
        vB, iB = best([("plus", m_plus, C)] + common)
    else:
        vB, iB = best(common)
        iB = iB + 1  # no 'plus' entry: shift so that index 0 never means plus
    rpp = P * vA + (1 - P) * vB
    rpp_award = (V - C) / m_base
    q = np.percentile(rpp, [5, 10, 25, 50, 75, 90, 95])
    return dict(carrier=carrier, route_id=route_id, route_label=base["route_label"], cabin=cabin, band_id=band_id, profile=profile,
                rpp_point=base["rpp"], rpp_mean=float(rpp.mean()),
                rpp_p05=q[0], rpp_p10=q[1], rpp_p25=q[2], rpp_p50=q[3], rpp_p75=q[4], rpp_p90=q[5], rpp_p95=q[6],
                rpp_award_p50=float(np.median(rpp_award)), prob_award_used=float((iA == 0).mean()),
                prob_plus_used=float((iB == 0).mean()) if km is not None else 0.0,
                prob_award_negative=float((rpp_award < 0).mean()), prob_below_coin_floor=float((rpp < r_coin).mean()),
                samples=rpp)


def simulate_all(p: Params, cases: list[tuple[str, str, str]], profile: str = "N", n: int = 20000, seed: int = 42):
    rows, samples = [], {}
    for i, (carrier, route_id, cabin) in enumerate(cases):
        for j, band_id in enumerate(p.bands["band_id"]):
            res = simulate_case(p, carrier, route_id, cabin, band_id, profile=profile, n=n, seed=seed + 1000 * i + j)
            if res is None:
                continue
            samples[(carrier, route_id, cabin, band_id)] = res.pop("samples")
            rows.append(res)
    return pd.DataFrame(rows), samples


def pool_samples(p: Params, samples: dict, keys: list[tuple[str, str, str]]) -> np.ndarray:
    """Traveller-weighted mixture of per-band samples for the given (carrier, route, cabin) keys."""
    w = p.bands.set_index("band_id")["traveler_weight"].to_dict()
    parts = []
    for (carrier, route_id, cabin, band_id), s in samples.items():
        if (carrier, route_id, cabin) in keys:
            parts.append(s[: int(round(len(s) * w[band_id]))])
    return np.concatenate(parts) if parts else np.array([])
