"""
Algoritmo 1 — PageRank + Centralidade de Grau
Identifica "baleias" e compara concentração de poder entre baseline e eventos de choque.
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../../data")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# ── Carrega CSVs ────────────────────────────────────────────────────────────
print("Carregando dados...")
df_baseline   = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
df_maduro     = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
df_khamenei   = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")

for df in [df_baseline, df_maduro, df_khamenei]:
    df["block_timestamp"] = pd.to_datetime(
        df["block_timestamp"].str.replace(" UTC", "", regex=False)
    )

JANELAS = [
    ("Baseline",          df_baseline,  "2025-10-16", "2025-10-23 23:59:59"),
    ("Maduro_1_Antes",    df_maduro,    "2025-12-31", "2026-01-02 23:59:59"),
    ("Maduro_2_Choque",   df_maduro,    "2026-01-03", "2026-01-03 23:59:59"),
    ("Maduro_3_Depois",   df_maduro,    "2026-01-04", "2026-01-06 23:59:59"),
    ("Khamenei_1_Antes",  df_khamenei,  "2026-02-25", "2026-02-27 23:59:59"),
    ("Khamenei_2_Choque", df_khamenei,  "2026-02-28", "2026-02-28 23:59:59"),
    ("Khamenei_3_Depois", df_khamenei,  "2026-03-01", "2026-03-03 23:59:59"),
]

TOP_N = 20

# ── Métricas de concentração ─────────────────────────────────────────────────
def gini(values):
    """Coeficiente de Gini — 0 = igualdade total, 1 = concentração máxima."""
    arr = sorted(values)
    n = len(arr)
    if n == 0 or sum(arr) == 0:
        return 0.0
    cum = 0.0
    for i, v in enumerate(arr):
        cum += (2 * (i + 1) - n - 1) * v
    return cum / (n * sum(arr))


def top_k_share(values, k=20):
    """Fração do total detida pelos top-k vértices."""
    arr = sorted(values, reverse=True)
    total = sum(arr)
    return sum(arr[:k]) / total if total > 0 else 0.0


# ── Processamento por janela ─────────────────────────────────────────────────
resumo_rows = []
all_tops = {}

for nome, df, inicio, fim in JANELAS:
    print(f"\n{'='*50}\nProcessando: {nome}")

    mask   = (df["block_timestamp"] >= inicio) & (df["block_timestamp"] <= fim)
    df_sl  = df.loc[mask].copy()

    edges  = (df_sl
              .groupby(["source_node", "target_node"])["edge_weight"]
              .sum()
              .reset_index())

    G = nx.from_pandas_edgelist(
        edges, "source_node", "target_node",
        edge_attr="edge_weight", create_using=nx.DiGraph()
    )
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    print(f"  Nós: {n_nodes} | Arestas: {n_edges}")

    # PageRank ponderado
    pr = nx.pagerank(G, weight="edge_weight", max_iter=500)

    # Centralidade de grau ponderada (volume)
    in_vol  = dict(G.in_degree(weight="edge_weight"))
    out_vol = dict(G.out_degree(weight="edge_weight"))
    total_vol = {n: in_vol.get(n, 0) + out_vol.get(n, 0) for n in G.nodes()}

    pr_vals  = list(pr.values())
    vol_vals = list(total_vol.values())

    # Top-N por PageRank
    top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    # Top-N por volume total
    top_vol = sorted(total_vol.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    # Interseção: aparecem em ambos os rankings
    set_pr  = {addr for addr, _ in top_pr}
    set_vol = {addr for addr, _ in top_vol}
    overlap = set_pr & set_vol

    gini_pr  = gini(pr_vals)
    gini_vol = gini(vol_vals)
    share_pr  = top_k_share(pr_vals, TOP_N)
    share_vol = top_k_share(vol_vals, TOP_N)

    print(f"  Gini PageRank: {gini_pr:.4f} | Gini Volume: {gini_vol:.4f}")
    print(f"  Top-{TOP_N} share PageRank: {share_pr:.2%} | Volume: {share_vol:.2%}")
    print(f"  Overlap top-{TOP_N} PR ∩ Vol: {len(overlap)} endereços")

    resumo_rows.append({
        "Janela":           nome,
        "Nos":              n_nodes,
        "Arestas":          n_edges,
        "Gini_PageRank":    round(gini_pr, 4),
        "Gini_Volume":      round(gini_vol, 4),
        f"Top{TOP_N}_share_PR":  round(share_pr, 4),
        f"Top{TOP_N}_share_Vol": round(share_vol, 4),
        "Overlap_PR_Vol":   len(overlap),
    })

    # Salva top-N por PageRank
    df_top_pr = pd.DataFrame(
        [(addr, score, in_vol.get(addr, 0), out_vol.get(addr, 0))
         for addr, score in top_pr],
        columns=["address", "pagerank", "in_volume", "out_volume"]
    )
    df_top_pr["in_pr_and_vol"] = df_top_pr["address"].isin(overlap)
    df_top_pr.to_csv(f"{OUT}/top_pagerank_{nome}.csv", index=False)

    # Salva top-N por volume
    df_top_vol = pd.DataFrame(
        [(addr, vol, in_vol.get(addr, 0), out_vol.get(addr, 0))
         for addr, vol in top_vol],
        columns=["address", "total_volume", "in_volume", "out_volume"]
    )
    df_top_vol["in_pr_and_vol"] = df_top_vol["address"].isin(overlap)
    df_top_vol.to_csv(f"{OUT}/top_volume_{nome}.csv", index=False)

    all_tops[nome] = {"pr": set_pr, "vol": set_vol, "overlap": overlap}


# ── Tabela resumo ────────────────────────────────────────────────────────────
df_resumo = pd.DataFrame(resumo_rows)
df_resumo.to_csv(f"{OUT}/resumo_metricas.csv", index=False)
print("\n\n=== RESUMO GERAL ===")
print(df_resumo.to_string(index=False))


# ── Endereços que aparecem APENAS nos eventos (não no baseline) ───────────────
baseline_pr  = all_tops["Baseline"]["pr"]
baseline_vol = all_tops["Baseline"]["vol"]

print("\n\n=== ENDEREÇOS EXCLUSIVOS DE EVENTOS (não no baseline) ===")
exclusive_rows = []
for nome in [k for k in all_tops if k != "Baseline"]:
    excl_pr  = all_tops[nome]["pr"]  - baseline_pr
    excl_vol = all_tops[nome]["vol"] - baseline_vol
    excl_both = all_tops[nome]["overlap"] - (baseline_pr | baseline_vol)
    print(f"  {nome}: {len(excl_both)} endereços no overlap PR∩Vol não vistos no baseline")
    for addr in sorted(excl_both):
        exclusive_rows.append({"Janela": nome, "address": addr})

if exclusive_rows:
    pd.DataFrame(exclusive_rows).to_csv(f"{OUT}/enderecos_exclusivos_eventos.csv", index=False)


# ── Plot: Gini por janela ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
janela_labels = [r["Janela"] for r in resumo_rows]
cores = ["steelblue", "tomato", "tomato", "tomato", "seagreen", "seagreen", "seagreen"]

for ax, metric, title in [
    (axes[0], "Gini_PageRank",  "Gini do PageRank por Janela"),
    (axes[1], "Gini_Volume",    "Gini do Volume Transacionado por Janela"),
]:
    vals = [r[metric] for r in resumo_rows]
    bars = ax.bar(range(len(janela_labels)), vals, color=cores)
    ax.set_xticks(range(len(janela_labels)))
    ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_title(title)
    ax.set_ylabel("Coeficiente de Gini")
    ax.axhline(0.9, color="gray", linestyle="--", linewidth=0.8, label="ref 0.9")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=7)

axes[0].legend()
plt.tight_layout()
plt.savefig(f"{OUT}/gini_por_janela.png", dpi=150)
print(f"\nPlot salvo: {OUT}/gini_por_janela.png")


# ── Plot: Top-20 share por janela ────────────────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

for ax, metric, title in [
    (axes2[0], f"Top{TOP_N}_share_PR",  f"Fração do PR detida pelo Top-{TOP_N}"),
    (axes2[1], f"Top{TOP_N}_share_Vol", f"Fração do Volume detida pelo Top-{TOP_N}"),
]:
    vals = [r[metric] for r in resumo_rows]
    bars = ax.bar(range(len(janela_labels)), vals, color=cores)
    ax.set_xticks(range(len(janela_labels)))
    ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_title(title)
    ax.set_ylabel("Fração do total")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.1%}", ha="center", va="bottom", fontsize=7)

plt.tight_layout()
plt.savefig(f"{OUT}/top_share_por_janela.png", dpi=150)
print(f"Plot salvo: {OUT}/top_share_por_janela.png")

print("\nAlgoritmo 1 concluído.")
