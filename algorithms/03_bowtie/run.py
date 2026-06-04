"""
Algoritmo 3 — Estrutura Bow-Tie
Decompõe cada grafo em SCC gigante / IN / OUT / Tendrils-Other.
Conecta com Alg.1+2:
  - testa se o acumulador 0xf977814e está no componente OUT (sink puro)
  - testa se 0xb334a61a (top-3 antes de Khamenei) está na SCC (hub bidirecional)
  - verifica se a razão OUT/IN é maior nos eventos (fluxo direcional de capital)
"""

import os
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../../data")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# ── Whales dos algoritmos anteriores ────────────────────────────────────────
WHALE_META = {
    "0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4": "Maduro-Hub (rank#2 vol)",
    "0xfbd4cdb413e45a52e2c8312f670e9ce67e794c37": "Maduro-Hub-2",
    "0xf977814e90da44bfa03b6295a0616a897441acec": "Maduro-Sink (zero out-edges)",
    "0xb334a61a6209f14b5fa5f1684a4ed7621f66e1ef": "Khamenei-Antes (rank#3 vol)",
    "0xeb9ca8fdfac0652a97c0e1a48c1178d32d3a6b8f": "Khamenei-Hub",
    "0x9b0c45d46d386cedd98873168c36efd0dcba8d46": "Khamenei-Hub-2",
}

# ── Dados ────────────────────────────────────────────────────────────────────
print("Carregando dados...")
df_baseline  = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
df_maduro    = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
df_khamenei  = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")

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


# ── Bow-Tie Decomposition ────────────────────────────────────────────────────
def bowtie(G):
    """
    Retorna dict com sets: SCC, IN, OUT, OTHER (tendrils + tubos + desconectados).
    Também retorna todas as SCCs para análise de componentes menores.
    """
    all_sccs = list(nx.strongly_connected_components(G))
    giant    = max(all_sccs, key=len)
    scc_set  = set(giant)

    source = next(iter(scc_set))

    # Nós alcançáveis A PARTIR da SCC (forward BFS no grafo original)
    forward = set(nx.descendants(G, source))
    out_set = forward - scc_set

    # Nós que alcançam a SCC (backward BFS = forward no grafo reverso)
    G_rev   = G.reverse(copy=False)
    backward = set(nx.descendants(G_rev, source))
    in_set  = backward - scc_set

    # Restante: tendrils, tubos e desconectados
    other   = set(G.nodes()) - scc_set - in_set - out_set

    return {
        "SCC":   scc_set,
        "IN":    in_set,
        "OUT":   out_set,
        "OTHER": other,
    }, all_sccs


def volume_by_component(G, components):
    """Volume total das arestas internas a cada componente e entre componentes."""
    comp_of = {}
    for name, nodes in components.items():
        for n in nodes:
            comp_of[n] = name

    vol_internal = {k: 0.0 for k in components}
    vol_in_to_scc  = 0.0
    vol_scc_to_out = 0.0
    vol_in_to_out  = 0.0  # tubos diretos

    for u, v, d in G.edges(data=True):
        cu, cv = comp_of.get(u), comp_of.get(v)
        w = d.get("edge_weight", 1.0)
        if cu == cv:
            vol_internal[cu] = vol_internal.get(cu, 0) + w
        elif cu == "IN" and cv == "SCC":
            vol_in_to_scc += w
        elif cu == "SCC" and cv == "OUT":
            vol_scc_to_out += w
        elif cu == "IN" and cv == "OUT":
            vol_in_to_out += w

    return vol_internal, vol_in_to_scc, vol_scc_to_out, vol_in_to_out


# ── Processamento ─────────────────────────────────────────────────────────────
resumo_rows = []
whale_rows  = []

for nome, df, inicio, fim in JANELAS:
    print(f"\n{'='*55}\nProcessando: {nome}")

    mask  = (df["block_timestamp"] >= inicio) & (df["block_timestamp"] <= fim)
    df_sl = df.loc[mask].copy()
    edges = (df_sl.groupby(["source_node", "target_node"])["edge_weight"]
             .sum().reset_index())

    G = nx.from_pandas_edgelist(
        edges, "source_node", "target_node",
        edge_attr="edge_weight", create_using=nx.DiGraph()
    )
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    n = G.number_of_nodes()
    components, all_sccs = bowtie(G)

    scc_n   = len(components["SCC"])
    in_n    = len(components["IN"])
    out_n   = len(components["OUT"])
    other_n = len(components["OTHER"])

    scc_pct   = scc_n / n
    in_pct    = in_n  / n
    out_pct   = out_n / n
    other_pct = other_n / n
    ratio_out_in = out_n / in_n if in_n > 0 else float("inf")

    # SCCs menores (excluindo a gigante)
    sizes_minor = sorted([len(s) for s in all_sccs if len(s) < scc_n], reverse=True)
    n_singleton = sum(1 for s in sizes_minor if s == 1)
    n_non_singleton_minor = sum(1 for s in sizes_minor if s > 1)

    # Volume por componente
    vol_int, vol_i2s, vol_s2o, vol_i2o = volume_by_component(G, components)
    total_vol = sum(d.get("edge_weight", 0) for _, _, d in G.edges(data=True))

    print(f"  Nós={n} | SCC={scc_n}({scc_pct:.1%}) | IN={in_n}({in_pct:.1%}) | "
          f"OUT={out_n}({out_pct:.1%}) | OTHER={other_n}({other_pct:.1%})")
    print(f"  Razão OUT/IN = {ratio_out_in:.2f}")
    print(f"  SCCs menores: {n_non_singleton_minor} não-singleton + {n_singleton} singletons")
    print(f"  Vol IN→SCC={vol_i2s/total_vol:.1%} | Vol SCC→OUT={vol_s2o/total_vol:.1%} | "
          f"Vol IN→OUT(tubo)={vol_i2o/total_vol:.1%}")

    # Onde estão as whales?
    for addr, desc in WHALE_META.items():
        if G.has_node(addr):
            comp = next((k for k, v in components.items() if addr in v), "?")
            in_vol  = G.in_degree(addr, weight="edge_weight")
            out_vol = G.out_degree(addr, weight="edge_weight")
            print(f"  WHALE [{comp}] {addr[:10]}… ({desc}) in={in_vol:.2e} out={out_vol:.2e}")
            whale_rows.append({
                "Janela": nome, "address": addr, "descricao": desc,
                "componente": comp,
                "in_volume": in_vol, "out_volume": out_vol,
            })

    resumo_rows.append({
        "Janela":          nome,
        "Nos":             n,
        "SCC_n":           scc_n,   "SCC_pct": round(scc_pct, 4),
        "IN_n":            in_n,    "IN_pct":  round(in_pct,  4),
        "OUT_n":           out_n,   "OUT_pct": round(out_pct, 4),
        "OTHER_n":         other_n, "OTHER_pct": round(other_pct, 4),
        "Ratio_OUT_IN":    round(ratio_out_in, 3),
        "n_SCC_minor":     n_non_singleton_minor,
        "n_singleton_SCC": n_singleton,
        "Vol_pct_IN_to_SCC":  round(vol_i2s / total_vol, 4) if total_vol else 0,
        "Vol_pct_SCC_to_OUT": round(vol_s2o / total_vol, 4) if total_vol else 0,
        "Vol_pct_IN_to_OUT":  round(vol_i2o / total_vol, 4) if total_vol else 0,
    })


# ── Tabelas ───────────────────────────────────────────────────────────────────
df_resumo = pd.DataFrame(resumo_rows)
df_resumo.to_csv(f"{OUT}/resumo_bowtie.csv", index=False)
print("\n\n=== RESUMO BOW-TIE ===")
cols = ["Janela","SCC_n","SCC_pct","IN_n","IN_pct","OUT_n","OUT_pct",
        "OTHER_n","OTHER_pct","Ratio_OUT_IN"]
print(df_resumo[cols].to_string(index=False))

print("\n\n=== VOLUME ENTRE COMPONENTES ===")
vcols = ["Janela","Vol_pct_IN_to_SCC","Vol_pct_SCC_to_OUT","Vol_pct_IN_to_OUT"]
print(df_resumo[vcols].to_string(index=False))

df_whales = pd.DataFrame(whale_rows)
df_whales.to_csv(f"{OUT}/whales_componente.csv", index=False)
print("\n\n=== WHALES POR COMPONENTE ===")
print(df_whales[["Janela","componente","descricao","address","in_volume","out_volume"]]
      .to_string(index=False))


# ── Plot 1: Composição Bow-Tie por janela (stacked bar) ───────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
janela_labels = [r["Janela"] for r in resumo_rows]
x = np.arange(len(janela_labels))

COMP_COLORS = {"SCC": "#4C72B0", "IN": "#55A868", "OUT": "#C44E52", "OTHER": "#CCB974"}

for ax, metric_base, title in [
    (axes[0], "pct", "Composição estrutural (% de nós)"),
    (axes[1], "n",   "Composição estrutural (nós absolutos)"),
]:
    bottom = np.zeros(len(janela_labels))
    for comp in ["SCC", "IN", "OUT", "OTHER"]:
        vals = np.array([r[f"{comp}_{metric_base}"] for r in resumo_rows])
        ax.bar(x, vals, bottom=bottom, label=comp, color=COMP_COLORS[comp], alpha=0.85)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            label_val = f"{v:.1%}" if metric_base == "pct" else str(int(v))
            if (metric_base == "pct" and v > 0.04) or (metric_base == "n" and v > 200):
                ax.text(x[i], b + v/2, label_val, ha="center", va="center",
                        fontsize=6.5, color="white", fontweight="bold")
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(title)
    ax.set_ylabel("% de nós" if metric_base == "pct" else "Número de nós")
    ax.legend(loc="upper right", fontsize=8)
    if metric_base == "pct":
        ax.set_ylim(0, 1.05)

plt.tight_layout()
fig.savefig(f"{OUT}/bowtie_composicao.png", dpi=150)
print(f"\nPlot composição salvo.")


# ── Plot 2: Razão OUT/IN e fluxo de volume ────────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
cores = ["steelblue","tomato","tomato","tomato","seagreen","seagreen","seagreen"]

# Razão OUT/IN
ax = axes2[0]
ratio_vals = [r["Ratio_OUT_IN"] for r in resumo_rows]
bars = ax.bar(x, ratio_vals, color=cores)
ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8, label="OUT=IN (equilíbrio)")
ax.set_xticks(x); ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
ax.set_title("Razão OUT/IN — fluxo direcional de capital")
ax.set_ylabel("OUT / IN  (>1 = mais saída que entrada)")
ax.legend(fontsize=8)
for bar, val in zip(bars, ratio_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f"{val:.2f}", ha="center", va="bottom", fontsize=8)

# Volume entre componentes (IN→SCC e SCC→OUT)
ax2 = axes2[1]
w_i2s = [r["Vol_pct_IN_to_SCC"]  for r in resumo_rows]
w_s2o = [r["Vol_pct_SCC_to_OUT"] for r in resumo_rows]
w_i2o = [r["Vol_pct_IN_to_OUT"]  for r in resumo_rows]
width = 0.28
ax2.bar(x - width, w_i2s, width, label="IN → SCC", color="#55A868", alpha=0.85)
ax2.bar(x,         w_s2o, width, label="SCC → OUT", color="#C44E52", alpha=0.85)
ax2.bar(x + width, w_i2o, width, label="IN → OUT (tubo)", color="#CCB974", alpha=0.85)
ax2.set_xticks(x); ax2.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
ax2.set_title("Fluxo de volume entre componentes Bow-Tie")
ax2.set_ylabel("Fração do volume total")
ax2.legend(fontsize=8)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))

plt.tight_layout()
fig2.savefig(f"{OUT}/bowtie_fluxo.png", dpi=150)
print(f"Plot fluxo salvo.")


# ── Plot 3: Componente das whales por janela ─────────────────────────────────
COMP_ORDER = ["SCC", "IN", "OUT", "OTHER"]
comp_y = {c: i for i, c in enumerate(COMP_ORDER)}
colors_w = {
    "Maduro-Hub (rank#2 vol)":       "#e74c3c",
    "Maduro-Hub-2":                  "#e67e22",
    "Maduro-Sink (zero out-edges)":  "#8e44ad",
    "Khamenei-Antes (rank#3 vol)":   "#27ae60",
    "Khamenei-Hub":                  "#2980b9",
    "Khamenei-Hub-2":                "#16a085",
}
janela_x = {nome: i for i, (nome, *_) in enumerate(JANELAS)}

fig3, ax3 = plt.subplots(figsize=(13, 5))
for desc in WHALE_META.values():
    subset = df_whales[df_whales["descricao"] == desc]
    if subset.empty:
        continue
    xs = [janela_x[row["Janela"]] for _, row in subset.iterrows()]
    ys = [comp_y.get(row["componente"], -1) for _, row in subset.iterrows()]
    ax3.plot(xs, ys, "o-", color=colors_w[desc], linewidth=1.5,
             markersize=8, label=desc[:30], alpha=0.85)

ax3.set_xticks(range(len(janela_labels)))
ax3.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
ax3.set_yticks(range(len(COMP_ORDER)))
ax3.set_yticklabels(COMP_ORDER, fontsize=9)
ax3.set_title("Componente Bow-Tie das Whales por Janela")
ax3.grid(True, axis="both", alpha=0.3)
ax3.legend(fontsize=7, loc="upper right")
plt.tight_layout()
fig3.savefig(f"{OUT}/whales_componente_bowtie.png", dpi=150)
print(f"Plot whales bow-tie salvo.")

print("\nAlgoritmo 3 concluído.")
