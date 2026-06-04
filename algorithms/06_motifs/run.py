"""
Algoritmo 6 — Motifs: Triângulos e Censo de Tríades
Detecta padrões estruturais de ordem 3: triângulos fechados (A→B→C→A = wash trading),
feed-forward loops, e outros micro-padrões.
Conecta com Alg.5: as whales no k-core mais alto deveriam ter clustering local alto
(pois k-core alto implica muitas conexões mútuas).
Conecta com Alg.1: candidatos a wash trading são endereços com alto volume E
alta clustering local.
"""

import os
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../../data")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

WHALES = {
    "0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4": ("Maduro-Hub",          "tomato"),
    "0xf977814e90da44bfa03b6295a0616a897441acec": ("Maduro-Sink",          "darkorange"),
    "0xfbd4cdb413e45a52e2c8312f670e9ce67e794c37": ("Maduro-Hub-2",         "salmon"),
    "0xb334a61a6209f14b5fa5f1684a4ed7621f66e1ef": ("Khamenei-Antecipador", "seagreen"),
    "0xeb9ca8fdfac0652a97c0e1a48c1178d32d3a6b8f": ("Khamenei-Hub",         "teal"),
    "0x9b0c45d46d386cedd98873168c36efd0dcba8d46": ("Khamenei-Hub-2",       "steelblue"),
}

print("Carregando dados...")
df_baseline = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
df_maduro   = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
df_khamenei = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")
for df in [df_baseline, df_maduro, df_khamenei]:
    df["block_timestamp"] = pd.to_datetime(df["block_timestamp"].str.replace(" UTC", "", regex=False))

JANELAS = [
    ("Baseline",          df_baseline,  "2025-10-16", "2025-10-23 23:59:59"),
    ("Maduro_1_Antes",    df_maduro,    "2025-12-31", "2026-01-02 23:59:59"),
    ("Maduro_2_Choque",   df_maduro,    "2026-01-03", "2026-01-03 23:59:59"),
    ("Maduro_3_Depois",   df_maduro,    "2026-01-04", "2026-01-06 23:59:59"),
    ("Khamenei_1_Antes",  df_khamenei,  "2026-02-25", "2026-02-27 23:59:59"),
    ("Khamenei_2_Choque", df_khamenei,  "2026-02-28", "2026-02-28 23:59:59"),
    ("Khamenei_3_Depois", df_khamenei,  "2026-03-01", "2026-03-03 23:59:59"),
]

# Tríades com ciclos dirigidos (padrão de wash trading)
# Tipos relevantes do censo de tríades NetworkX:
#   030C = A→B→C→A (ciclo de 3)
#   120C = ciclo bidirecional
#   300  = grafo completo bidirecional (triângulo com todas as 6 arestas)
CYCLE_TRIADS = ["030C", "120C", "300"]
FF_TRIADS    = ["030T", "120U", "120D"]  # feed-forward

resumo_rows = []
whale_rows  = []

for nome, df, inicio, fim in JANELAS:
    print(f"\n{'='*55}\nProcessando: {nome}")
    mask  = (df["block_timestamp"] >= inicio) & (df["block_timestamp"] <= fim)
    df_sl = df.loc[mask].copy()
    edges = df_sl.groupby(["source_node","target_node"])["edge_weight"].sum().reset_index()

    G  = nx.from_pandas_edgelist(edges, "source_node", "target_node",
                                  edge_attr="edge_weight", create_using=nx.DiGraph())
    G.remove_edges_from(list(nx.selfloop_edges(G)))
    Gu = G.to_undirected()

    n = G.number_of_nodes()
    e = G.number_of_edges()

    # ── Triângulos (não-dirigidos) ──────────────────────────────────────────
    triangles_dict = nx.triangles(Gu)
    total_triangles = sum(triangles_dict.values()) // 3
    nodes_in_triangle = sum(1 for v in triangles_dict.values() if v > 0)
    pct_nodes_in_tri = nodes_in_triangle / n

    # Clustering global (transitivity) e médio
    transitivity   = nx.transitivity(Gu)
    avg_clustering = nx.average_clustering(Gu, weight="edge_weight")

    print(f"  Triângulos: {total_triangles} | Nós em triângulo: {nodes_in_triangle} ({pct_nodes_in_tri:.1%})")
    print(f"  Transitivity (global): {transitivity:.4f} | Avg clustering: {avg_clustering:.4f}")

    # ── Censo de tríades dirigidas ──────────────────────────────────────────
    census = nx.triadic_census(G)
    n_cycles = sum(census.get(t, 0) for t in CYCLE_TRIADS)
    n_ff     = sum(census.get(t, 0) for t in FF_TRIADS)
    total_triads = sum(census.values())
    pct_cycle = n_cycles / total_triads if total_triads else 0
    pct_ff    = n_ff    / total_triads if total_triads else 0

    print(f"  Tríades totais: {total_triads:,} | Ciclos (030C+120C+300): {n_cycles:,} ({pct_cycle:.3%})")
    print(f"  Feed-forward (030T+120U+120D): {n_ff:,} ({pct_ff:.3%})")
    for t in CYCLE_TRIADS + FF_TRIADS:
        if census.get(t, 0) > 0:
            print(f"    {t}: {census[t]:,}")

    # ── Clustering e triângulos locais das whales ───────────────────────────
    for addr, (desc, color) in WHALES.items():
        if addr in Gu:
            cl   = nx.clustering(Gu, addr, weight="edge_weight")
            tri  = triangles_dict.get(addr, 0)
            vol  = G.in_degree(addr, weight="edge_weight") + G.out_degree(addr, weight="edge_weight")
            deg  = Gu.degree(addr)
            # Percentil de clustering na rede
            all_cl = [nx.clustering(Gu, n) for n in Gu.nodes() if Gu.degree(n) >= 2]
            pct_cl = sum(1 for c in all_cl if c <= cl) / len(all_cl) if all_cl else 0
            print(f"  WHALE {desc}: clustering={cl:.4f} (pct={pct_cl:.1%}) tri={tri} deg={deg}")
            whale_rows.append({
                "Janela": nome, "descricao": desc, "address": addr,
                "clustering": round(cl, 4), "percentil_clustering": round(pct_cl, 4),
                "triangulos": tri, "degree": deg, "vol_total": vol,
            })

    resumo_rows.append({
        "Janela":          nome,
        "Nos":             n, "Arestas": e,
        "Triangulos":      total_triangles,
        "Nos_em_tri":      nodes_in_triangle,
        "Pct_nos_em_tri":  round(pct_nodes_in_tri, 4),
        "Transitivity":    round(transitivity, 4),
        "Avg_clustering":  round(avg_clustering, 4),
        "N_ciclos_dir":    n_cycles,
        "N_ff_dir":        n_ff,
        "Pct_ciclos":      round(pct_cycle, 6),
        "Pct_ff":          round(pct_ff, 6),
        "census_030C":     census.get("030C", 0),
        "census_300":      census.get("300",  0),
        "census_030T":     census.get("030T", 0),
    })

# ── Tabelas ───────────────────────────────────────────────────────────────────
df_res = pd.DataFrame(resumo_rows)
df_res.to_csv(f"{OUT}/resumo_motifs.csv", index=False)
print("\n\n=== RESUMO MOTIFS ===")
cols = ["Janela","Triangulos","Pct_nos_em_tri","Transitivity","Avg_clustering",
        "N_ciclos_dir","Pct_ciclos","census_030C","census_300"]
print(df_res[cols].to_string(index=False))

df_wh = pd.DataFrame(whale_rows)
df_wh.to_csv(f"{OUT}/whales_clustering.csv", index=False)
print("\n\n=== WHALES — CLUSTERING LOCAL ===")
print(df_wh[["Janela","descricao","clustering","percentil_clustering","triangulos","degree"]]
      .to_string(index=False))

# ── Plot 1: Triângulos e Transitivity por janela ──────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
janela_labels = [r["Janela"] for r in resumo_rows]
cores_j = ["steelblue","tomato","tomato","tomato","seagreen","seagreen","seagreen"]
x = range(len(janela_labels))

for ax, key, title, ylabel in [
    (axes[0], "Triangulos",     "Triângulos totais",               "Contagem"),
    (axes[1], "Transitivity",   "Transitivity (clustering global)", "Coef. transitivity"),
    (axes[2], "Pct_nos_em_tri", "Nós participando de triângulos",  "Fração de nós"),
]:
    vals = [r[key] for r in resumo_rows]
    bars = ax.bar(x, vals, color=cores_j)
    ax.set_xticks(x); ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(title); ax.set_ylabel(ylabel)
    for bar, val in zip(bars, vals):
        label = f"{int(val):,}" if isinstance(val, (int, float)) and val > 1 else f"{val:.4f}"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                label, ha="center", va="bottom", fontsize=7)

plt.tight_layout()
fig.savefig(f"{OUT}/triangulos_por_janela.png", dpi=150)
print(f"\nPlot triângulos salvo.")

# ── Plot 2: Composição das tríades dirigidas ──────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(14, 5))
triad_keys = ["census_030C", "census_300", "census_030T"]
triad_labels = ["030C (ciclo simples)", "300 (ciclo completo)", "030T (feed-forward)"]
triad_colors = ["#e74c3c", "#c0392b", "#3498db"]
bottom = np.zeros(len(janela_labels))
for tk, tl, tc in zip(triad_keys, triad_labels, triad_colors):
    vals = np.array([r[tk] for r in resumo_rows], dtype=float)
    ax2.bar(x, vals, bottom=bottom, label=tl, color=tc, alpha=0.85)
    bottom += vals
ax2.set_xticks(x); ax2.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
ax2.set_title("Tríades dirigidas cíclicas e feed-forward por janela")
ax2.set_ylabel("Contagem de tríades")
ax2.legend(fontsize=8)
plt.tight_layout()
fig2.savefig(f"{OUT}/triades_dirigidas.png", dpi=150)

# ── Plot 3: Clustering local das whales por janela ───────────────────────────
fig3, ax3 = plt.subplots(figsize=(13, 5))
janela_x = {nome: i for i, (nome, *_) in enumerate(JANELAS)}
for desc in set(df_wh["descricao"]):
    sub = df_wh[df_wh["descricao"] == desc]
    color = next(c for a, (d, c) in WHALES.items() if d == desc)
    xs = [janela_x[r["Janela"]] for _, r in sub.iterrows()]
    ys = [r["clustering"] for _, r in sub.iterrows()]
    ax3.plot(xs, ys, "o-", color=color, label=desc, linewidth=1.8, markersize=6)

# Linha de referência: avg_clustering do baseline
baseline_avg = resumo_rows[0]["Avg_clustering"]
ax3.axhline(baseline_avg, color="gray", linestyle="--", linewidth=0.9,
            label=f"Avg clustering baseline ({baseline_avg:.4f})")
ax3.set_xticks(range(len(janela_labels)))
ax3.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
ax3.set_title("Clustering local das Whales por janela")
ax3.set_ylabel("Coeficiente de clustering local")
ax3.legend(fontsize=7); ax3.grid(True, alpha=0.3)
plt.tight_layout()
fig3.savefig(f"{OUT}/whales_clustering.png", dpi=150)
print(f"Plots motifs salvos.")
print("\nAlgoritmo 6 concluído.")
