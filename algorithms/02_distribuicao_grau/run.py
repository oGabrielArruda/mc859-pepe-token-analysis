"""
Algoritmo 2 — Distribuição de Grau (Lei de Potência)
Ajusta lei de potência ao in-degree e out-degree de cada janela.
Conecta com Alg.1: verifica se as janelas com maior concentração de volume
(Maduro_Choque) e PageRank anômalo (Khamenei_Antes) apresentam expoente γ
menor, indicando cauda mais pesada e dominância de hubs.
Destaca os endereços "whale" identificados no Algoritmo 1.
"""

import os
import warnings
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import powerlaw

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "../../data")
ALG1 = os.path.join(BASE, "../01_pagerank_centralidade/results")
OUT  = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)

# ── Whales do Algoritmo 1 (endereços exclusivos de eventos, presença persistente)
WHALES_MADURO    = {
    "0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4",
    "0xfbd4cdb413e45a52e2c8312f670e9ce67e794c37",
    "0xf977814e90da44bfa03b6295a0616a897441acec",
}
WHALES_KHAMENEI  = {
    "0xb334a61a6209f14b5fa5f1684a4ed7621f66e1ef",
    "0xeb9ca8fdfac0652a97c0e1a48c1178d32d3a6b8f",
    "0x9b0c45d46d386cedd98873168c36efd0dcba8d46",
}
ALL_WHALES = WHALES_MADURO | WHALES_KHAMENEI

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

# ── Helpers ───────────────────────────────────────────────────────────────────
def fit_powerlaw(seq):
    """Ajusta lei de potência e retorna (alpha, xmin, R vs lognormal, p-value)."""
    data = [x for x in seq if x > 0]
    if len(data) < 10:
        return None, None, None, None
    fit = powerlaw.Fit(data, discrete=True, verbose=False)
    R, p = fit.distribution_compare("power_law", "lognormal")
    return fit.alpha, fit.xmin, R, p


def whale_degrees(G, whale_set, weight=None):
    """Retorna {addr: (in_deg, out_deg)} para whales presentes no grafo."""
    result = {}
    for addr in whale_set:
        if G.has_node(addr):
            result[addr] = (
                G.in_degree(addr, weight=weight),
                G.out_degree(addr, weight=weight),
            )
    return result


# ── Processamento ─────────────────────────────────────────────────────────────
resumo_rows = []
# Para o plot comparativo multi-janela
fig_all, axes_all = plt.subplots(2, 7, figsize=(28, 8))

for idx, (nome, df, inicio, fim) in enumerate(JANELAS):
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

    in_deg  = [d for _, d in G.in_degree()]
    out_deg = [d for _, d in G.out_degree()]
    in_vol  = [d for _, d in G.in_degree(weight="edge_weight")]
    out_vol = [d for _, d in G.out_degree(weight="edge_weight")]

    # ── Ajuste lei de potência ────────────────────────────────────────────
    alpha_in,  xmin_in,  R_in,  p_in  = fit_powerlaw(in_deg)
    alpha_out, xmin_out, R_out, p_out = fit_powerlaw(out_deg)
    alpha_vol_in,  *_  = fit_powerlaw(in_vol)
    alpha_vol_out, *_  = fit_powerlaw(out_vol)

    print(f"  In-degree  → α={alpha_in:.3f}  xmin={xmin_in}  R(PL vs LN)={R_in:.3f}  p={p_in:.3f}")
    print(f"  Out-degree → α={alpha_out:.3f}  xmin={xmin_out}  R(PL vs LN)={R_out:.3f}  p={p_out:.3f}")
    print(f"  In-vol α={alpha_vol_in:.3f} | Out-vol α={alpha_vol_out:.3f}")

    # ── Posição das whales no ranking de grau ─────────────────────────────
    all_in  = sorted(G.in_degree(weight="edge_weight"),  key=lambda x: x[1], reverse=True)
    all_out = sorted(G.out_degree(weight="edge_weight"), key=lambda x: x[1], reverse=True)
    rank_in  = {addr: rank+1 for rank, (addr, _) in enumerate(all_in)}
    rank_out = {addr: rank+1 for rank, (addr, _) in enumerate(all_out)}

    whale_info = []
    for addr in ALL_WHALES:
        if G.has_node(addr):
            tag = "maduro" if addr in WHALES_MADURO else "khamenei"
            whale_info.append({
                "Janela": nome,
                "address": addr,
                "group": tag,
                "rank_in_vol":  rank_in.get(addr, None),
                "rank_out_vol": rank_out.get(addr, None),
                "in_vol":  G.in_degree(addr, weight="edge_weight"),
                "out_vol": G.out_degree(addr, weight="edge_weight"),
                "in_deg":  G.in_degree(addr),
                "out_deg": G.out_degree(addr),
            })

    if whale_info:
        for w in whale_info:
            print(f"  WHALE [{w['group']}] {w['address'][:10]}… "
                  f"rank_in={w['rank_in_vol']} rank_out={w['rank_out_vol']}")

    resumo_rows.append({
        "Janela":         nome,
        "Nos":            G.number_of_nodes(),
        "Arestas":        G.number_of_edges(),
        "alpha_in_deg":   round(alpha_in,  3) if alpha_in  else None,
        "alpha_out_deg":  round(alpha_out, 3) if alpha_out else None,
        "alpha_in_vol":   round(alpha_vol_in,  3) if alpha_vol_in  else None,
        "alpha_out_vol":  round(alpha_vol_out, 3) if alpha_vol_out else None,
        "xmin_in":        xmin_in,
        "xmin_out":       xmin_out,
        "R_in_PL_vs_LN":  round(R_in,  3) if R_in  else None,
        "R_out_PL_vs_LN": round(R_out, 3) if R_out else None,
        "p_in":           round(p_in,  3) if p_in  else None,
        "p_out":          round(p_out, 3) if p_out else None,
        "whale_rows":     whale_info,
    })

    # ── Plot log-log desta janela ─────────────────────────────────────────
    for ax_row, seq, alpha_val, xmin_val, label, color in [
        (0, in_deg,  alpha_in,  xmin_in,  "In-degree",  "steelblue"),
        (1, out_deg, alpha_out, xmin_out, "Out-degree", "tomato"),
    ]:
        ax = axes_all[ax_row][idx]
        data_pos = [x for x in seq if x > 0]
        from collections import Counter
        cnt = Counter(data_pos)
        xs, ys = zip(*sorted(cnt.items()))
        ax.scatter(xs, ys, s=10, alpha=0.6, color=color)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(f"{nome}\n{label} α={alpha_val:.2f}" if alpha_val else f"{nome}\n{label}", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.grid(True, which="both", ls="--", alpha=0.3)

        # Linha de referência da lei de potência ajustada
        if alpha_val and xmin_val:
            xs_arr = np.array(sorted(set(data_pos)))
            xs_fit = xs_arr[xs_arr >= xmin_val]
            if len(xs_fit) > 1:
                # normalização aproximada
                C = len([x for x in data_pos if x >= xmin_val])
                ys_fit = C * (xs_fit / xmin_val) ** (-alpha_val)
                ax.plot(xs_fit, ys_fit, "k--", linewidth=1, alpha=0.8)

fig_all.suptitle("Distribuição de Grau por Janela (log-log) — In-degree (cima) | Out-degree (baixo)",
                 fontsize=10, y=1.01)
fig_all.tight_layout()
fig_all.savefig(f"{OUT}/distribuicao_grau_todas_janelas.png", dpi=130, bbox_inches="tight")
print(f"\nPlot geral salvo.")


# ── Tabela resumo ─────────────────────────────────────────────────────────────
df_resumo = pd.DataFrame([
    {k: v for k, v in r.items() if k != "whale_rows"}
    for r in resumo_rows
])
df_resumo.to_csv(f"{OUT}/resumo_expoentes.csv", index=False)
print("\n=== RESUMO DOS EXPOENTES ===")
print(df_resumo[["Janela","alpha_in_deg","alpha_out_deg","alpha_in_vol","alpha_out_vol",
                  "R_in_PL_vs_LN","R_out_PL_vs_LN"]].to_string(index=False))


# ── Tabela de posição das whales ───────────────────────────────────────────────
all_whale_rows = [w for r in resumo_rows for w in r["whale_rows"]]
if all_whale_rows:
    df_whales = pd.DataFrame(all_whale_rows).drop(columns=["whale_rows"], errors="ignore")
    df_whales.to_csv(f"{OUT}/whales_posicao_grau.csv", index=False)
    print("\n=== POSIÇÃO DAS WHALES NO RANKING DE GRAU ===")
    print(df_whales[["Janela","group","address","rank_in_vol","rank_out_vol",
                      "in_vol","out_vol"]].to_string(index=False))


# ── Plot comparativo: expoentes α por janela ──────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
janelas_labels = [r["Janela"] for r in resumo_rows]
cores = ["steelblue","tomato","tomato","tomato","seagreen","seagreen","seagreen"]

for ax, key, title in [
    (axes2[0], "alpha_in_deg",  "Expoente α — In-degree"),
    (axes2[1], "alpha_out_deg", "Expoente α — Out-degree"),
]:
    vals = [r[key] for r in resumo_rows]
    bars = ax.bar(range(len(janelas_labels)), vals, color=cores)
    ax.set_xticks(range(len(janelas_labels)))
    ax.set_xticklabels(janelas_labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(title)
    ax.set_ylabel("α (quanto menor = cauda mais pesada)")
    # referência: α=2 = scale-free clássico
    ax.axhline(2.0, color="gray", linestyle="--", linewidth=0.8, label="α=2 (scale-free clássico)")
    ax.legend(fontsize=8)
    for bar, val in zip(bars, vals):
        if val:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=7)

plt.tight_layout()
fig2.savefig(f"{OUT}/expoentes_por_janela.png", dpi=150)
print(f"\nPlot expoentes salvo.")


# ── Plot: Posição das whales no in-degree ranking (percentil) ─────────────────
if all_whale_rows:
    df_w = pd.DataFrame(all_whale_rows)
    df_w["percentil_in"] = df_w.apply(
        lambda row: 1 - row["rank_in_vol"] / next(
            r["Nos"] for r in resumo_rows if r["Janela"] == row["Janela"]
        ), axis=1
    )

    fig3, ax3 = plt.subplots(figsize=(12, 5))
    markers  = {"maduro": "o", "khamenei": "s"}
    colors_w = {"maduro": "tomato", "khamenei": "seagreen"}
    janelas_idx = {nome: i for i, (nome, *_) in enumerate(JANELAS)}

    for _, row in df_w.iterrows():
        xi = janelas_idx[row["Janela"]]
        ax3.scatter(xi, row["percentil_in"],
                    marker=markers[row["group"]],
                    color=colors_w[row["group"]],
                    s=80, zorder=3, alpha=0.85)
        ax3.annotate(row["address"][:8]+"…",
                     (xi, row["percentil_in"]),
                     textcoords="offset points", xytext=(4, 2), fontsize=5, alpha=0.7)

    ax3.set_xticks(range(len(janelas_labels)))
    ax3.set_xticklabels(janelas_labels, rotation=30, ha="right", fontsize=8)
    ax3.set_ylabel("Percentil no ranking de In-volume (1 = maior)")
    ax3.set_title("Posição das Whales (Alg.1) na distribuição de In-degree por janela\n"
                  "● Maduro  ■ Khamenei")
    ax3.set_ylim(0.8, 1.01)
    ax3.axhline(0.99, color="gray", linestyle="--", linewidth=0.7, label="Top 1%")
    ax3.legend(fontsize=8)
    ax3.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    fig3.savefig(f"{OUT}/whales_percentil_por_janela.png", dpi=150)
    print(f"Plot whales salvo.")

print("\nAlgoritmo 2 concluído.")
