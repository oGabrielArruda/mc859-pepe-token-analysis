"""
Algoritmo 5 — K-core Decomposition
Detecta padrão de profundidade estrutural: quem é núcleo vs periferia.
Conecta com Alg.1: as whales identificadas devem estar no k-core mais interno.
Conecta com Alg.3: a SCC gigante deve ter k-core > 1; o componente OUT
    (onde 0xf977814e residia) deve ter k-cores baixos.
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
    Gu = G.to_undirected()  # k-core requer não-dirigido

    core_num = nx.core_number(Gu)
    k_max    = max(core_num.values())
    k_median = np.median(list(core_num.values()))
    k_mean   = np.mean(list(core_num.values()))

    # Distribuição dos k-cores
    cnt = Counter(core_num.values())
    pct_k1 = cnt[1] / G.number_of_nodes()   # periféricos puros
    pct_kmax = sum(v for k, v in cnt.items() if k == k_max) / G.number_of_nodes()

    print(f"  k_max={k_max}  k_median={k_median:.1f}  k_mean={k_mean:.2f}")
    print(f"  Nós em k=1 (periferia): {cnt[1]} ({pct_k1:.1%})")
    print(f"  Nós em k=k_max={k_max}: {cnt[k_max]} ({pct_kmax:.1%})")

    # Volume médio por k-core (quem está no núcleo movimenta mais?)
    vol_by_k = {}
    for node, k in core_num.items():
        vol = G.in_degree(node, weight="edge_weight") + G.out_degree(node, weight="edge_weight")
        vol_by_k.setdefault(k, []).append(vol)
    vol_k_mean = {k: np.mean(v) for k, v in vol_by_k.items()}

    # Posição das whales
    for addr, (desc, color) in WHALES.items():
        if addr in core_num:
            k = core_num[addr]
            pct_rank = sum(1 for v in core_num.values() if v <= k) / len(core_num)
            vol = G.in_degree(addr, weight="edge_weight") + G.out_degree(addr, weight="edge_weight")
            print(f"  WHALE {desc}: k={k} (percentil {pct_rank:.1%} da rede)  vol={vol:.2e}")
            whale_rows.append({"Janela": nome, "descricao": desc, "address": addr,
                                "k_core": k, "k_max": k_max, "percentil_k": round(pct_rank, 4),
                                "vol_total": vol})

    resumo_rows.append({
        "Janela":   nome,
        "Nos":      G.number_of_nodes(),
        "k_max":    k_max,
        "k_median": round(k_median, 2),
        "k_mean":   round(k_mean, 3),
        "pct_k1":   round(pct_k1, 4),
        "n_k_max":  cnt[k_max],
        "pct_kmax": round(pct_kmax, 4),
        "core_num": core_num,   # guardado para plot
        "vol_k_mean": vol_k_mean,
    })

# ── Tabelas ───────────────────────────────────────────────────────────────────
df_res = pd.DataFrame([{k: v for k, v in r.items() if k not in ("core_num","vol_k_mean")}
                        for r in resumo_rows])
df_res.to_csv(f"{OUT}/resumo_kcore.csv", index=False)
print("\n\n=== RESUMO K-CORE ===")
print(df_res.to_string(index=False))

df_wh = pd.DataFrame(whale_rows)
df_wh.to_csv(f"{OUT}/whales_kcore.csv", index=False)
print("\n\n=== WHALES — K-CORE ===")
print(df_wh[["Janela","descricao","k_core","k_max","percentil_k"]].to_string(index=False))

# ── Plot 1: Distribuição k-core por janela (violin-style como scatter) ────────
fig, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()
cores_janela = ["steelblue","tomato","tomato","tomato","seagreen","seagreen","seagreen"]

for idx, r in enumerate(resumo_rows):
    ax = axes[idx]
    k_vals = list(r["core_num"].values())
    cnt    = Counter(k_vals)
    ks     = sorted(cnt.keys())
    freqs  = [cnt[k] for k in ks]

    ax.bar(ks, freqs, color=cores_janela[idx], alpha=0.75, edgecolor="white", linewidth=0.3)
    ax.set_yscale("log")
    ax.set_title(f"{r['Janela']}\nk_max={r['k_max']}  k_med={r['k_median']}", fontsize=8)
    ax.set_xlabel("k-core", fontsize=7)
    ax.set_ylabel("Frequência (log)", fontsize=7)
    ax.tick_params(labelsize=6)
    ax.axvline(r["k_max"], color="black", linestyle="--", linewidth=0.8, alpha=0.6, label=f"k_max={r['k_max']}")
    ax.legend(fontsize=6)

    # Marca whales
    for wh in whale_rows:
        if wh["Janela"] == r["Janela"]:
            ax.axvline(wh["k_core"], color="red", linestyle=":", linewidth=1.2, alpha=0.5)

axes[-1].axis("off")  # último painel vazio
plt.suptitle("Distribuição K-core por Janela (log scale)\n"
             "Linha tracejada preta = k_max | Linha pontilhada vermelha = k das whales",
             fontsize=10)
plt.tight_layout()
fig.savefig(f"{OUT}/distribuicao_kcore.png", dpi=150, bbox_inches="tight")
print(f"\nPlot distribuição k-core salvo.")

# ── Plot 2: k_max e k_median por janela ───────────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
janela_labels = [r["Janela"] for r in resumo_rows]
x = range(len(janela_labels))

for ax, metric, title in [
    (axes2[0], "k_max",    "K-core máximo por janela"),
    (axes2[1], "k_median", "K-core mediano por janela"),
]:
    vals = [r[metric] for r in resumo_rows]
    bars = ax.bar(x, vals, color=cores_janela)
    ax.set_xticks(x); ax.set_xticklabels(janela_labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(title); ax.set_ylabel(metric)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(val), ha="center", va="bottom", fontsize=8)

plt.tight_layout()
fig2.savefig(f"{OUT}/kcore_por_janela.png", dpi=150)

# ── Plot 3: Volume médio por k-core (núcleo vs periferia) ─────────────────────
fig3, axes3 = plt.subplots(2, 4, figsize=(18, 8))
axes3 = axes3.flatten()

for idx, r in enumerate(resumo_rows):
    ax = axes3[idx]
    vk = r["vol_k_mean"]
    ks = sorted(vk.keys())
    vs = [vk[k] for k in ks]
    ax.plot(ks, vs, "o-", color=cores_janela[idx], linewidth=1.8, markersize=5)
    ax.set_yscale("log")
    ax.set_title(f"{r['Janela']}", fontsize=8)
    ax.set_xlabel("k-core", fontsize=7); ax.set_ylabel("Volume médio (log)", fontsize=7)
    ax.tick_params(labelsize=6); ax.grid(True, alpha=0.3)

axes3[-1].axis("off")
plt.suptitle("Volume médio transacionado por nível de k-core\n(núcleo = mais volume?)", fontsize=10)
plt.tight_layout()
fig3.savefig(f"{OUT}/volume_por_kcore.png", dpi=150, bbox_inches="tight")
print(f"Plots k-core salvos.")
print("\nAlgoritmo 5 concluído.")
