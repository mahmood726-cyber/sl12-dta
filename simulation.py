import numpy as np
import json
from pathlib import Path

import pandas as pd
from scipy.stats import kendalltau, genextreme, entropy
from scipy.spatial.distance import pdist, squareform

PROJECT_ROOT = Path(__file__).resolve().parent
PROBES_FULL_PATH = PROJECT_ROOT / "probes_full.json"

def inv_logit(l): return 1 / (1 + np.exp(-l))


def round_float(value, digits=4):
    return float(round(float(value), digits))

def simulate_complex_dta(k=60, rng=None):
    rng = rng or np.random.default_rng()
    results = []
    # 3 latent clusters (Evidence Islands)
    clusters = [[0.5, 3.0], [2.0, 0.5], [1.2, 1.8]]
    for i in range(k):
        m = clusters[i % 3]
        n = 400
        l_s, l_sp = rng.multivariate_normal(m, [[0.2, 0], [0, 0.2]])
        s, sp = inv_logit(l_s), inv_logit(l_sp)
        tp = rng.binomial(100, s)
        tn = rng.binomial(300, sp)
        results.append({'tp':tp, 'fp':300-tn, 'fn':100-tp, 'tn':tn})
    return pd.DataFrame(results)

# --- PROBES ---

def probe_wavelet(s):
    # Simplified Haar-like signal filtering on sorted studies
    s_sorted = np.sort(s)
    diffs = np.diff(s_sorted)
    return {"noise_reduction": round_float(np.mean(np.abs(diffs)))}

def probe_dirichlet(s, sp):
    # Simplified clustering (Evidence Islands)
    pts = np.column_stack([s, sp])
    dists = pdist(pts)
    islands = (dists < 0.1).sum() / len(dists)
    return {"island_density": round_float(islands)}

def probe_bottleneck(s, sp):
    # Mutual Information vs Complexity (Simplified)
    mi = np.corrcoef(s, sp)[0, 1]**2
    return {"mi_compression": round_float(mi)}

def probe_persistence(s, sp):
    # Topological lifetime of clusters
    pts = np.column_stack([s, sp])
    dists = squareform(pdist(pts))
    max_persistence = np.max(np.min(dists + np.eye(len(s))*10, axis=1))
    return {"cluster_lifetime": round_float(max_persistence)}

def probe_quantum(s, sp):
    # Von Neumann Entropy of the density matrix
    pts = np.column_stack([s, sp])
    rho = np.dot(pts.T, pts) / len(s)
    eigvals = np.linalg.eigvals(rho)
    eigvals = eigvals[eigvals > 0]
    vn_entropy = -np.sum(eigvals * np.log(eigvals))
    return {"quantum_entropy": round_float(vn_entropy)}

def probe_fisher(s, sp):
    # Information Geometry distance
    mean_s, mean_sp = np.mean(s), np.mean(sp)
    # Fisher metric for binomial is 1/(p*(1-p))
    g_s = 1 / (mean_s * (1 - mean_s))
    return {"fisher_curvature": round_float(g_s)}

def probe_gametheory(s, sp):
    # Nash Equilibrium payoff (Simplified)
    payoff = np.mean(s + sp - 1)
    return {"nash_payoff": round_float(payoff)}

def probe_exergy(s, sp):
    # Useful work potential (Distance from random state)
    kl_div = entropy([np.mean(s), 1-np.mean(s)], [0.5, 0.5])
    return {"evidence_exergy": round_float(kl_div)}

def probe_causal(s, sp):
    # Causal Transport (Simplified Wasserstein-1 distance to uniform)
    w1 = np.mean(np.abs(np.sort(s) - np.linspace(0, 1, len(s))))
    return {"transport_cost": round_float(w1)}


def write_outputs(results, project_root=PROJECT_ROOT):
    probes_path = Path(project_root) / PROBES_FULL_PATH.name
    probes_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return probes_path


def main(seed=726, project_root=PROJECT_ROOT):
    rng = np.random.default_rng(seed)
    df = simulate_complex_dta(rng=rng)
    tp, fp, fn, tn = df['tp']+0.5, df['fp']+0.5, df['fn']+0.5, df['tn']+0.5
    s, sp = tp/(tp+fn), tn/(tn+fp)
    
    # Run all 12
    full_results = {
        "1_Copula": {"tau": round_float(kendalltau(s, sp)[0])},
        "2_EVT": {"shape": round_float(genextreme.fit(s)[0])},
        "3_Stein": {"shrunk_mean": round_float(np.mean(s) * 0.9)}, # Placeholder logic
        "4_Wavelets": probe_wavelet(s),
        "5_Dirichlet": probe_dirichlet(s, sp),
        "6_Bottleneck": probe_bottleneck(s, sp),
        "7_Persistence": probe_persistence(s, sp),
        "8_Quantum": probe_quantum(s, sp),
        "9_Fisher": probe_fisher(s, sp),
        "10_GameTheory": probe_gametheory(s, sp),
        "11_Exergy": probe_exergy(s, sp),
        "12_Causal": probe_causal(s, sp)
    }
    
    print("SL12 FULL ENGINE RESULTS:")
    for k, v in full_results.items():
        print(f" - {k}: {v}")

    write_outputs(full_results, project_root=project_root)
    return {"dataframe": df, "results": full_results}


if __name__ == "__main__":
    main()
