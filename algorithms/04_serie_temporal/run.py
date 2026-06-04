"""
Algoritmo 4 — Série Temporal Diária
Calcula métricas de grafo por dia para Baseline, Maduro e Khamenei.
Conecta com Alg.1-3: verifica quando as anomalias estruturais surgem e
como evoluem ao longo da janela, respondendo às perguntas abertas de cada
algoritmo anterior.

Perguntas-chave que este algoritmo deve responder:
  - A transição IN=69% (Khamenei_Antes) ocorre gradualmente ou abruptamente?
  - O fluxo IN→SCC de 18% no dia do choque Khamenei aparece como pico isolado?
  - A SCC se recupera após os eventos?
  - O PageRank das whales segue o evento ou o antecipa?
"""

import os
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../../data")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# ── Whales consolidadas dos algoritmos anteriores ─────────────────────────────
WHALES = {
    "0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4": ("Maduro-Hub",         "tomato"),
    "0xf977814e90da44bfa03b6295a0616a897441acec": ("Maduro-Sink",         "darkorange"),
    "0xfbd4cdb413e45a52e2c8312f670e9ce67e794c37": ("Maduro-Hub-2",        "salmon"),
    "0xb334a61a6209f14b5fa5f1684a4ed7621f66e1ef": ("Khamenei-Antecipador","seagreen"),
    "0xeb9ca8fdfac0652a97c0e1a48c1178d32d3a6b8f": ("Khamenei-Hub",        "teal"),
    "0x9b0c45d46d386cedd98873168c36efd0dcba8d46": ("Khamenei-Hub-2",      "steelblue"),
}

# Dias dos eventos
D_MADURO    = pd.Timestamp("2026-01-03")
D_KHAMENEI  = pd.Timestamp("2026-02-28")

# ── Dados ─────────────────────────────────────────────────────────────────────
print("Carregando dados...")
df_baseline  = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
df_maduro    = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
df_khamenei  = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")

for df in [df_baseline, df_maduro, df_khamenei]:
    df["block_timestamp"] = pd.to_datetime(
        df["block_timestamp"].str.replace(" UTC", "", regex=False)
    )
    df["date"] = df["block_timestamp"].dt.date


# ── Helpers ───────────────────────────────────────────────────────────────────
def gini(values):
    arr = sorted(v for v in values if v > 0)
    n = len(arr)
    if n == 0:
        return 0.0
    cum = sum((2*(i+1) - n - 1) * v for i, v in enumerate(arr))
    return cum / (n * sum(arr))


def bowtie_ratio(G):
    """Retorna (ratio_out_in, vol_in_to_scc_pct, scc_pct) rapidamente."""
    if G.number_of_nodes() < 3:
        return np.nan, np.nan, np.nan
    all_sccs = list(nx.strongly_connected_components(G))
    giant    = max(all_sccs, key=len)
    scc_set  = set(giant)
    source   = next(iter(scc_set))
    forward  = set(nx.descendants(G, source))
    out_set  = forward - scc_set
    G_rev    = G.reverse(copy=False)
    backward = set(nx.descendants(G_rev, source))
    in_set   = backward - scc_set

    in_n, out_n = len(in_set), len(out_set)
    ratio = out_n / in_n if in_n > 0 else np.nan

    # Volume IN→SCC
    total_vol  = sum(d.get("edge_weight", 0) for _, _, d in G.edges(data=True))
    vol_i2s    = sum(
        d.get("edge_weight", 0)
        for u, v, d in G.edges(data=True)
        if u in in_set and v in scc_set
    )
    vol_pct = vol_i2s / total_vol if total_vol > 0 else 0.0
    scc_pct = len(scc_set) / G.number_of_nodes()
    return ratio, vol_pct, scc_pct


def daily_metrics(df_raw, label):
    """Computa métricas por dia para um dataset."""
    rows = []
    for date, group in df_raw.groupby("date"):
        edges_df = (group.groupby(["source_node", "target_node"])["edge_weight"]
                    .sum().reset_index())
        G = nx.from_pandas_edgelist(
            edges_df, "source_node", "target_node",
            edge_attr="edge_weight", create_using=nx.DiGraph()
        )
        G.remove_edges_from(list(nx.selfloop_edges(G)))

        n = G.number_of_nodes()
        e = G.number_of_edges()
        if n == 0:
            continue

        avg_deg = 2 * e / n
        vol_vals = [d for _, _, d in G.edges(data="edge_weight") if d]
        gini_vol = gini(vol_vals)

        # PageRank
        pr = nx.pagerank(G, weight="edge_weight", max_iter=200)
        pr_sorted = sorted(pr.values(), reverse=True)
        top1_share  = pr_sorted[0]
        top20_share = sum(pr_sorted[:20]) / sum(pr_sorted) if pr_sorted else 0

        # Bow-tie
        ratio_oi, vol_i2s, scc_pct = bowtie_ratio(G)

        # Volume médio por aresta
        avg_vol = np.mean(vol_vals) if vol_vals else 0

        # Whales: rank de in-volume por dia
        all_in_vol = sorted(G.in_degree(weight="edge_weight"), key=lambda x: x[1], reverse=True)
        rank_inv   = {addr: rank+1 for rank, (addr, _) in enumerate(all_in_vol)}

        whale_ranks = {}
        for addr in WHALES:
            whale_ranks[f"rank_{addr[:8]}"] = rank_inv.get(addr, np.nan)
            whale_ranks[f"invol_{addr[:8]}"] = G.in_degree(addr, weight="edge_weight") if G.has_node(addr) else 0

        row = {
            "dataset": label,
            "date":    pd.Timestamp(date),
            "n_nodes": n,
            "n_edges": e,
            "avg_deg": round(avg_deg, 3),
            "gini_vol": round(gini_vol, 4),
            "top1_pr_share":  round(top1_share, 5),
            "top20_pr_share": round(top20_share, 4),
            "ratio_out_in":   round(ratio_oi, 3) if not np.isnan(ratio_oi) else np.nan,
            "vol_in_to_scc":  round(vol_i2s, 4),
            "scc_pct":        round(scc_pct, 4),
            "avg_vol":        avg_vol,
        }
        row.update(whale_ranks)
        rows.append(row)
        print(f"  {label} {date}: nodes={n} edges={e} gini={gini_vol:.3f} "
              f"ratio_oi={ratio_oi:.2f} vol_i2s={vol_i2s:.1%} scc={scc_pct:.1%}")
    return pd.DataFrame(rows)


# ── Execução ──────────────────────────────────────────────────────────────────
print("\n=== BASELINE ===")
df_base_m = daily_metrics(df_baseline,  "Baseline")

print("\n=== MADURO ===")
df_mad_m  = daily_metrics(df_maduro,    "Maduro")

print("\n=== KHAMENEI ===")
df_kha_m  = daily_metrics(df_khamenei,  "Khamenei")

df_all = pd.concat([df_base_m, df_mad_m, df_kha_m], ignore_index=True)
df_all.to_csv(f"{OUT}/metricas_diarias.csv", index=False)

# Adiciona coluna "dias relativos ao evento D" para Maduro e Khamenei
df_mad_m["d_rel"] = (df_mad_m["date"] - D_MADURO).dt.days
df_kha_m["d_rel"] = (df_kha_m["date"] - D_KHAMENEI).dt.days

# Baseline: centrado no meio da janela para referência visual
baseline_mid = df_base_m["date"].median()
df_base_m["d_rel"] = (df_base_m["date"] - baseline_mid).dt.days


# ── Plot 1: Métricas estruturais (eixo = dias relativos a D) ─────────────────
METRICS = [
    ("n_nodes",        "Nós ativos por dia",                    "Nós"),
    ("scc_pct",        "SCC gigante (% dos nós)",               "% nós na SCC"),
    ("ratio_out_in",   "Razão OUT/IN (bow-tie)",                "OUT / IN"),
    ("vol_in_to_scc",  "Volume IN→SCC (% do total)",           "Fração volume"),
    ("gini_vol",       "Gini do volume transacionado",          "Coef. Gini"),
    ("top20_pr_share", "Top-20 PageRank share",                 "Fração PR"),
]

fig, axes = plt.subplots(3, 2, figsize=(16, 13))
axes = axes.flatten()

for ax, (metric, title, ylabel) in zip(axes, METRICS):
    # Baseline: banda de referência (min-max)
    bv = df_base_m[metric].dropna().values
    if len(bv):
        ax.axhspan(bv.min(), bv.max(), alpha=0.12, color="gray", label="Baseline (faixa)")
        ax.axhline(bv.mean(), color="gray", linestyle=":", linewidth=1, alpha=0.7, label="Baseline (média)")

    for df_ev, color, label_ev, D_mark in [
        (df_mad_m, "tomato",   "Maduro",   D_MADURO),
        (df_kha_m, "seagreen", "Khamenei", D_KHAMENEI),
    ]:
        sub = df_ev[["d_rel", metric]].dropna()
        if sub.empty:
            continue
        ax.plot(sub["d_rel"], sub[metric], "o-", color=color, label=label_ev,
                linewidth=2, markersize=6)
        # Linha vertical em D=0
        ax.axvline(0, color=color, linestyle="--", linewidth=0.8, alpha=0.5)

    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_xlabel("Dias relativos ao evento (D=0)", fontsize=8)
    ax.set_xticks(range(-3, 4))
    ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in range(-3, 4)], fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7)

plt.suptitle("Série Temporal Diária — Métricas de Grafo por Evento\n"
             "(D = dia do evento geopolítico)", fontsize=12, y=1.01)
plt.tight_layout()
fig.savefig(f"{OUT}/serie_temporal_metricas.png", dpi=150, bbox_inches="tight")
print(f"\nPlot métricas salvo.")


# ── Plot 2: Ranking diário das whales (in-volume) ─────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))

for ax, df_ev, title, event_whales, other_whales in [
    (axes2[0], df_mad_m,  "Maduro — Ranking diário de in-volume das Whales",
     ["0xeae7380d", "0xf977814e", "0xfbd4cdb4"],
     ["0xb334a61a", "0xeb9ca8fd", "0x9b0c45d4"]),
    (axes2[1], df_kha_m, "Khamenei — Ranking diário de in-volume das Whales",
     ["0xb334a61a", "0xeb9ca8fd", "0x9b0c45d4"],
     ["0xeae7380d", "0xfbd4cdb4"]),
]:
    ax.axvline(0, color="black", linestyle="--", linewidth=1, alpha=0.6, label="Dia D")

    for addr_full, (desc, color) in WHALES.items():
        key = f"rank_{addr_full[:8]}"
        if key not in df_ev.columns:
            continue
        sub = df_ev[["d_rel", key]].dropna()
        if sub.empty or sub[key].isna().all():
            continue
        prefix = addr_full[:8]
        linestyle = "-" if prefix in event_whales else "--"
        alpha     = 0.9 if prefix in event_whales else 0.45
        lw        = 2.2 if prefix in event_whales else 1.2
        ax.plot(sub["d_rel"], sub[key], marker="o", markersize=5,
                color=color, linestyle=linestyle, linewidth=lw,
                alpha=alpha, label=f"{desc} ({addr_full[:8]}…)")

    ax.invert_yaxis()  # rank 1 no topo
    ax.set_xticks(range(-3, 4))
    ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in range(-3, 4)], fontsize=8)
    ax.set_title(title, fontsize=9, fontweight="bold")
    ax.set_ylabel("Rank de in-volume (1 = maior receptor)", fontsize=8)
    ax.set_xlabel("Dias relativos ao evento", fontsize=8)
    ax.legend(fontsize=7, loc="lower right")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
fig2.savefig(f"{OUT}/whales_ranking_diario.png", dpi=150)
print(f"Plot whales ranking salvo.")


# ── Plot 3: Comparação evento normalizado — radar de desvio do baseline ───────
# Normaliza cada métrica pelo valor médio do baseline
baseline_means = df_base_m[["n_nodes","scc_pct","gini_vol","top20_pr_share",
                              "vol_in_to_scc","ratio_out_in"]].mean()

def normalized_profile(df_ev, d_rel_val):
    row = df_ev[df_ev["d_rel"] == d_rel_val]
    if row.empty:
        return None
    r = row.iloc[0]
    return {m: r[m] / baseline_means[m] if baseline_means[m] != 0 else np.nan
            for m in baseline_means.index}

fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
labels_rel = range(-3, 4)
metric_cols = ["n_nodes","scc_pct","gini_vol","top20_pr_share","vol_in_to_scc","ratio_out_in"]
metric_labels = ["Nós ativos","SCC%","Gini vol","PR top-20","Vol IN→SCC","OUT/IN"]

for ax, df_ev, color, label_ev in [
    (axes3[0], df_mad_m,  "tomato",   "Maduro"),
    (axes3[1], df_kha_m, "seagreen",  "Khamenei"),
]:
    for metric, mlabel in zip(metric_cols, metric_labels):
        sub = df_ev[["d_rel", metric]].dropna()
        norm_vals = sub[metric] / baseline_means[metric]
        ax.plot(sub["d_rel"], norm_vals, "o-", linewidth=1.5, markersize=4,
                label=mlabel, alpha=0.85)

    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1, label="Nível baseline")
    ax.axvline(0,   color="black", linestyle=":",  linewidth=1.2, alpha=0.7)
    ax.set_xticks(range(-3, 4))
    ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in range(-3, 4)], fontsize=8)
    ax.set_title(f"{label_ev} — Desvio normalizado pelo baseline", fontsize=9)
    ax.set_ylabel("Valor / Média baseline  (1.0 = normal)", fontsize=8)
    ax.set_xlabel("Dias relativos ao evento", fontsize=8)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
fig3.savefig(f"{OUT}/desvio_normalizado_baseline.png", dpi=150)
print(f"Plot desvio normalizado salvo.")


# ── Resumo textual ────────────────────────────────────────────────────────────
print("\n\n=== MÉTRICAS DIÁRIAS RELATIVAS — MADURO ===")
cols_show = ["d_rel","n_nodes","scc_pct","ratio_out_in","vol_in_to_scc","gini_vol","top20_pr_share"]
print(df_mad_m[cols_show].to_string(index=False))

print("\n\n=== MÉTRICAS DIÁRIAS RELATIVAS — KHAMENEI ===")
print(df_kha_m[cols_show].to_string(index=False))

print("\n\n=== BASELINE (referência) ===")
print(df_base_m[cols_show].to_string(index=False))

print("\nAlgoritmo 4 concluído.")
