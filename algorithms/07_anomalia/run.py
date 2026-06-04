"""
Algoritmo 7 — Detecção de Anomalia Estatística Formal
Usa as métricas diárias do Alg.4 e constrói distribuição de referência
com o baseline. Calcula z-score por dia por métrica. Dias com |z| > 2
são formalmente anômalos. Computa também anomaly score combinado.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE = os.path.dirname(os.path.abspath(__file__))
ALG4 = os.path.join(BASE, "../04_serie_temporal/results/metricas_diarias.csv")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

METRICS = {
    "n_nodes":        "Nós ativos",
    "scc_pct":        "SCC% (fração da rede)",
    "ratio_out_in":   "Razão OUT/IN",
    "vol_in_to_scc":  "Volume IN→SCC",
    "gini_vol":       "Gini do volume",
    "top20_pr_share": "Top-20 PageRank share",
}

D_MADURO   = pd.Timestamp("2026-01-03")
D_KHAMENEI = pd.Timestamp("2026-02-28")

df = pd.read_csv(ALG4, parse_dates=["date"])

baseline = df[df["dataset"] == "Baseline"]
maduro   = df[df["dataset"] == "Maduro"].copy()
khamenei = df[df["dataset"] == "Khamenei"].copy()

maduro["d_rel"]   = (maduro["date"]   - D_MADURO).dt.days
khamenei["d_rel"] = (khamenei["date"] - D_KHAMENEI).dt.days

# ── Estatísticas do baseline ──────────────────────────────────────────────────
baseline_stats = {}
for m in METRICS:
    vals = baseline[m].dropna().values
    baseline_stats[m] = {"mean": vals.mean(), "std": vals.std(ddof=1), "vals": vals}

print("=== BASELINE — Distribuição de referência ===")
for m, s in baseline_stats.items():
    print(f"  {METRICS[m]}: mean={s['mean']:.4f}  std={s['std']:.4f}")

# ── Z-score por dia por evento ────────────────────────────────────────────────
def zscore_df(df_ev, label):
    rows = []
    for _, row in df_ev.iterrows():
        zs = {}
        anomaly_count = 0
        anomaly_score = 0.0
        for m in METRICS:
            val = row[m]
            if pd.isna(val):
                zs[f"z_{m}"] = np.nan
                continue
            mean = baseline_stats[m]["mean"]
            std  = baseline_stats[m]["std"]
            z    = (val - mean) / std if std > 0 else 0.0
            zs[f"z_{m}"] = round(z, 3)
            if abs(z) > 2:
                anomaly_count += 1
            anomaly_score += abs(z)
        rows.append({
            "dataset": label,
            "date":    row["date"],
            "d_rel":   row.get("d_rel", np.nan),
            **{m: row[m] for m in METRICS},
            **zs,
            "anomaly_count":  anomaly_count,
            "anomaly_score":  round(anomaly_score, 3),
        })
    return pd.DataFrame(rows)

df_mad_z = zscore_df(maduro,   "Maduro")
df_kha_z = zscore_df(khamenei, "Khamenei")
df_base_z = zscore_df(baseline, "Baseline")

df_all_z = pd.concat([df_base_z, df_mad_z, df_kha_z], ignore_index=True)
df_all_z.to_csv(f"{OUT}/zscores_diarios.csv", index=False)

print("\n\n=== MADURO — Z-scores por dia ===")
zcols = ["d_rel"] + [f"z_{m}" for m in METRICS] + ["anomaly_count","anomaly_score"]
print(df_mad_z[zcols].to_string(index=False))

print("\n\n=== KHAMENEI — Z-scores por dia ===")
print(df_kha_z[zcols].to_string(index=False))

# ── Dias formalmente anômalos (|z| > 2 em ≥ 1 métrica) ──────────────────────
print("\n\n=== DIAS ANÔMALOS (|z| > 2) ===")
for df_ev, label in [(df_mad_z, "Maduro"), (df_kha_z, "Khamenei")]:
    print(f"\n  {label}:")
    for _, row in df_ev.iterrows():
        anomalias = [METRICS[m] for m in METRICS if abs(row.get(f"z_{m}", 0) or 0) > 2]
        if anomalias:
            print(f"    D{int(row['d_rel']):+d} ({row['date'].date()}): "
                  f"score={row['anomaly_score']:.1f} | anomalias em: {', '.join(anomalias)}")

# ── Plot 1: Heatmap de z-scores ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
metric_labels = list(METRICS.values())

for ax, df_ev, label, D_mark in [
    (axes[0], df_mad_z,  "Maduro",   D_MADURO),
    (axes[1], df_kha_z, "Khamenei",  D_KHAMENEI),
]:
    df_ev_sorted = df_ev.sort_values("d_rel")
    z_matrix = df_ev_sorted[[f"z_{m}" for m in METRICS]].values.T  # (metrics × days)
    day_labels = [f"D{int(d):+d}" if d != 0 else "D" for d in df_ev_sorted["d_rel"]]

    im = ax.imshow(z_matrix, aspect="auto", cmap="RdBu_r",
                   vmin=-5, vmax=5, interpolation="nearest")
    ax.set_xticks(range(len(day_labels))); ax.set_xticklabels(day_labels, fontsize=9)
    ax.set_yticks(range(len(metric_labels))); ax.set_yticklabels(metric_labels, fontsize=8)
    ax.set_title(f"{label} — Z-score por dia e métrica\n(vermelho = acima do baseline, azul = abaixo)",
                 fontsize=9)

    # Anotações de valor
    for i in range(z_matrix.shape[0]):
        for j in range(z_matrix.shape[1]):
            v = z_matrix[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        fontsize=7, color="white" if abs(v) > 2.5 else "black")

    plt.colorbar(im, ax=ax, label="Z-score", shrink=0.8)

plt.suptitle("Detecção de Anomalia — Z-score diário relativo ao baseline", fontsize=11)
plt.tight_layout()
fig.savefig(f"{OUT}/heatmap_zscores.png", dpi=150, bbox_inches="tight")
print(f"\nPlot heatmap z-scores salvo.")

# ── Plot 2: Anomaly score total por dia ───────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(12, 5))
x_mad = df_mad_z["d_rel"].values
x_kha = df_kha_z["d_rel"].values

ax2.bar(x_mad - 0.2, df_mad_z["anomaly_score"], width=0.35,
        color="tomato", alpha=0.8, label="Maduro")
ax2.bar(x_kha + 0.2, df_kha_z["anomaly_score"], width=0.35,
        color="seagreen", alpha=0.8, label="Khamenei")

# Referência: score médio do baseline
base_scores = df_base_z["anomaly_score"].values
ax2.axhline(base_scores.mean(), color="gray", linestyle="--",
            linewidth=1, label=f"Média baseline ({base_scores.mean():.1f})")
ax2.axhline(base_scores.mean() + 2*base_scores.std(), color="gray", linestyle=":",
            linewidth=0.8, label="Baseline +2σ")

ax2.set_xticks(sorted(set(list(x_mad) + list(x_kha))))
ax2.set_xticklabels([f"D{int(d):+d}" if d != 0 else "D" for d in sorted(set(list(x_mad)+list(x_kha)))],
                     fontsize=9)
ax2.set_title("Anomaly Score combinado por dia\n(soma dos |z-score| de todas as métricas)", fontsize=10)
ax2.set_ylabel("Anomaly Score (soma |z|)")
ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
fig2.savefig(f"{OUT}/anomaly_score_por_dia.png", dpi=150)
print(f"Plot anomaly score salvo.")

# ── Plot 3: Z-score por métrica ao longo do tempo (multi-linha) ───────────────
fig3, axes3 = plt.subplots(3, 2, figsize=(16, 12))
axes3 = axes3.flatten()

for ax, (m, mlabel) in zip(axes3, METRICS.items()):
    for df_ev, color, label_ev in [
        (df_mad_z,  "tomato",   "Maduro"),
        (df_kha_z, "seagreen",  "Khamenei"),
    ]:
        sub = df_ev[["d_rel", f"z_{m}"]].dropna()
        ax.plot(sub["d_rel"], sub[f"z_{m}"], "o-", color=color,
                label=label_ev, linewidth=2, markersize=6)

    ax.axhline( 2, color="gray", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.axhline(-2, color="gray", linestyle="--", linewidth=0.7, alpha=0.7, label="|z|=2")
    ax.axhline( 0, color="black", linestyle="-", linewidth=0.5, alpha=0.3)
    ax.set_title(mlabel, fontsize=9, fontweight="bold")
    ax.set_ylabel("Z-score", fontsize=8)
    ax.set_xlabel("Dias relativos ao evento", fontsize=8)
    ax.set_xticks(range(-3, 4))
    ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in range(-3, 4)], fontsize=8)
    ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
    ax.fill_between(range(-3, 4), -2, 2, alpha=0.05, color="gray")

plt.suptitle("Z-score por métrica e por evento\n(faixa cinza = zona normal ±2σ do baseline)",
             fontsize=11, y=1.01)
plt.tight_layout()
fig3.savefig(f"{OUT}/zscore_por_metrica.png", dpi=150, bbox_inches="tight")
print(f"Plot z-score por métrica salvo.")

print("\nAlgoritmo 7 concluído.")
