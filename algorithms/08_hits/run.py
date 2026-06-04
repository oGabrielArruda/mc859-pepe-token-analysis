"""
Algoritmo 8 — HITS (Hubs & Authorities)
Separa "distribuidores" (hubs) de "acumuladores" (authorities) em grafos dirigidos.
Conecta com Alg.1: PageRank agrupa os dois — HITS os separa.
Conecta com Alg.2+3: 0xf977814e (sink/OUT) deve ser authority máxima.
Conecta com Alg.6: Khamenei-Antecipador com clustering=0 e estrela pura deve
    ter perfis distintos de hub vs authority.
"""

import os
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

TOP_N = 20

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
all_tops    = {}

for nome, df, inicio, fim in JANELAS:
    print(f"\n{'='*55}\nProcessando: {nome}")
    mask  = (df["block_timestamp"] >= inicio) & (df["block_timestamp"] <= fim)
    df_sl = df.loc[mask].copy()
    edges = df_sl.groupby(["source_node","target_node"])["edge_weight"].sum().reset_index()

    G = nx.from_pandas_edgelist(edges, "source_node", "target_node",
                                 edge_attr="edge_weight", create_using=nx.DiGraph())
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    hubs_raw, auths_raw = nx.hits(G, normalized=True, max_iter=500)

    # Rankings
    top_hubs  = sorted(hubs_raw.items(),  key=lambda x: x[1], reverse=True)[:TOP_N]
    top_auths = sorted(auths_raw.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

    set_hubs  = {a for a, _ in top_hubs}
    set_auths = {a for a, _ in top_auths}
    overlap   = set_hubs & set_auths  # aparecem como hub E authority

    # Razão hub/authority (>1 = distribuidor; <1 = acumulador)
    all_hub_vals  = list(hubs_raw.values())
    all_auth_vals = list(auths_raw.values())

    # Gini dos scores HITS
    def gini(v):
        arr = sorted(v)
        n = len(arr)
        if n == 0 or sum(arr) == 0: return 0.
        cum = sum((2*(i+1)-n-1)*x for i, x in enumerate(arr))
        return cum / (n * sum(arr))

    gini_hub  = gini(all_hub_vals)
    gini_auth = gini(all_auth_vals)

    print(f"  Top-{TOP_N} Hub ∩ Auth (generalistas): {len(overlap)}")
    print(f"  Gini Hub score: {gini_hub:.4f} | Gini Auth score: {gini_auth:.4f}")
    print(f"  Top-1 Hub:  {top_hubs[0][0][:12]}…  score={top_hubs[0][1]:.5f}")
    print(f"  Top-1 Auth: {top_auths[0][0][:12]}…  score={top_auths[0][1]:.5f}")

    rank_hub  = {a: r+1 for r, (a, _) in enumerate(sorted(hubs_raw.items(),  key=lambda x: x[1], reverse=True))}
    rank_auth = {a: r+1 for r, (a, _) in enumerate(sorted(auths_raw.items(), key=lambda x: x[1], reverse=True))}

    for addr, (desc, color) in WHALES.items():
        if addr in hubs_raw:
            rh = rank_hub[addr];  ra = rank_auth[addr]
            hs = hubs_raw[addr];  as_ = auths_raw[addr]
            ratio = hs / as_ if as_ > 0 else float("inf")
            role  = "Distribuidor" if ratio > 1 else "Acumulador"
            print(f"  WHALE {desc}: rank_hub={rh} rank_auth={ra} ratio={ratio:.2f} → {role}")
            whale_rows.append({
                "Janela": nome, "descricao": desc, "address": addr,
                "rank_hub": rh, "rank_auth": ra,
                "hub_score": round(hs, 6), "auth_score": round(as_, 6),
                "ratio_hub_auth": round(ratio, 4),
                "role": role,
            })

    resumo_rows.append({
        "Janela":     nome,
        "Nos":        G.number_of_nodes(),
        "Overlap_top20": len(overlap),
        "Gini_hub":   round(gini_hub, 4),
        "Gini_auth":  round(gini_auth, 4),
        "Top1_hub":   top_hubs[0][0],
        "Top1_hub_score": round(top_hubs[0][1], 6),
        "Top1_auth":  top_auths[0][0],
        "Top1_auth_score": round(top_auths[0][1], 6),
        "top_hubs":   top_hubs,
        "top_auths":  top_auths,
    })
    all_tops[nome] = {"hubs": set_hubs, "auths": set_auths}

    # Salva top-N
    pd.DataFrame([(a, s, rank_auth[a]) for a, s in top_hubs],
                 columns=["address","hub_score","rank_auth"]).to_csv(
        f"{OUT}/top_hubs_{nome}.csv", index=False)
    pd.DataFrame([(a, s, rank_hub[a]) for a, s in top_auths],
                 columns=["address","auth_score","rank_hub"]).to_csv(
        f"{OUT}/top_auths_{nome}.csv", index=False)

# ── Tabelas resumo ────────────────────────────────────────────────────────────
df_res = pd.DataFrame([{k:v for k, v in r.items() if k not in ("top_hubs","top_auths")}
                        for r in resumo_rows])
df_res.to_csv(f"{OUT}/resumo_hits.csv", index=False)
print("\n\n=== RESUMO HITS ===")
print(df_res[["Janela","Nos","Overlap_top20","Gini_hub","Gini_auth","Top1_hub","Top1_auth"]].to_string(index=False))

df_wh = pd.DataFrame(whale_rows)
df_wh.to_csv(f"{OUT}/whales_hits.csv", index=False)
print("\n\n=== WHALES — HITS ===")
print(df_wh[["Janela","descricao","rank_hub","rank_auth","ratio_hub_auth","role"]].to_string(index=False))

# ── Endereços exclusivos de eventos no top hubs/auths ────────────────────────
baseline_hubs  = all_tops["Baseline"]["hubs"]
baseline_auths = all_tops["Baseline"]["auths"]
print("\n\n=== NOVOS TOPS EM EVENTOS (não no baseline) ===")
excl_rows = []
for nome in [k for k in all_tops if k != "Baseline"]:
    excl_h = all_tops[nome]["hubs"]  - baseline_hubs
    excl_a = all_tops[nome]["auths"] - baseline_auths
    if excl_h or excl_a:
        print(f"  {nome}: +{len(excl_h)} hubs, +{len(excl_a)} auths exclusivos")
    for addr in excl_h & excl_a:
        excl_rows.append({"Janela": nome, "address": addr, "tipo": "hub+auth"})
    for addr in excl_h - excl_a:
        excl_rows.append({"Janela": nome, "address": addr, "tipo": "hub"})
    for addr in excl_a - excl_h:
        excl_rows.append({"Janela": nome, "address": addr, "tipo": "auth"})

if excl_rows:
    pd.DataFrame(excl_rows).to_csv(f"{OUT}/enderecos_exclusivos_hits.csv", index=False)

# ── Plot 1: Rank de hub vs rank de authority para as whales ──────────────────
fig, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()
cores_j = ["steelblue","tomato","tomato","tomato","seagreen","seagreen","seagreen"]

for idx, r in enumerate(resumo_rows):
    ax = axes[idx]
    nome = r["Janela"]
    df_j = df_wh[df_wh["Janela"] == nome]

    # Fundo: scatter de todos os nós (amostra)
    ax.set_xlim(0, r["Nos"]); ax.set_ylim(0, r["Nos"])
    ax.plot([0, r["Nos"]], [0, r["Nos"]], "gray", linestyle="--", linewidth=0.7, alpha=0.5)
    ax.axvline(TOP_N, color="gray", linestyle=":", linewidth=0.5, alpha=0.5)
    ax.axhline(TOP_N, color="gray", linestyle=":", linewidth=0.5, alpha=0.5)

    for _, wrow in df_j.iterrows():
        desc  = wrow["descricao"]
        color = next(c for a, (d, c) in WHALES.items() if d == desc)
        rh, ra = wrow["rank_hub"], wrow["rank_auth"]
        ax.scatter(rh, ra, color=color, s=80, zorder=4, edgecolors="black", linewidths=0.5)
        ax.annotate(desc[:12], (rh, ra), textcoords="offset points",
                    xytext=(4, 2), fontsize=5.5, alpha=0.85)

    ax.set_title(f"{nome}\nOverlap={r['Overlap_top20']}", fontsize=8)
    ax.set_xlabel("Rank Hub (menor = mais distribuidor)", fontsize=7)
    ax.set_ylabel("Rank Authority (menor = mais acumulador)", fontsize=7)
    ax.tick_params(labelsize=6)
    # Destaque quadrante top-20 × top-20
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((0, 0), TOP_N, TOP_N, fill=False,
                            edgecolor="gold", linewidth=1.2, zorder=3))

axes[-1].axis("off")
plt.suptitle("Rank Hub × Rank Authority das Whales por Janela\n"
             "Quadrado dourado = top-20 em ambos | Diagonal = Hub=Auth (generalista)",
             fontsize=10)
plt.tight_layout()
fig.savefig(f"{OUT}/whales_hub_vs_auth.png", dpi=150, bbox_inches="tight")
print(f"\nPlot hub vs auth salvo.")

# ── Plot 2: Razão hub/auth das whales por janela (role ao longo do tempo) ─────
fig2, ax2 = plt.subplots(figsize=(14, 6))
janela_x = {nome: i for i, (nome, *_) in enumerate(JANELAS)}
ax2.axhline(1.0, color="gray", linestyle="--", linewidth=1, label="Equilíbrio (hub=auth)")

WHALE_DESCS = [d for _, (d, _) in WHALES.items()]
for desc in WHALE_DESCS:
    sub = df_wh[df_wh["descricao"] == desc]
    if sub.empty: continue
    color = next(c for a, (d, c) in WHALES.items() if d == desc)
    xs = [janela_x[r["Janela"]] for _, r in sub.iterrows()]
    ys = [min(r["ratio_hub_auth"], 50) for _, r in sub.iterrows()]  # cap para visualização
    ax2.plot(xs, ys, "o-", color=color, label=desc, linewidth=2, markersize=7)

ax2.set_xticks(range(len(JANELAS)))
ax2.set_xticklabels([n for n, *_ in JANELAS], rotation=30, ha="right", fontsize=8)
ax2.set_yscale("log")
ax2.set_title("Razão Hub/Authority das Whales por Janela (log scale)\n"
              "> 1 = distribuidor | < 1 = acumulador", fontsize=10)
ax2.set_ylabel("Hub score / Auth score (log)")
ax2.legend(fontsize=8, loc="upper right")
ax2.grid(True, alpha=0.3)
plt.tight_layout()
fig2.savefig(f"{OUT}/whales_role_temporal.png", dpi=150)
print(f"Plot role temporal salvo.")

# ── Plot 3: Gini de Hub e Auth por janela ─────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(12, 5))
x = np.arange(len(resumo_rows))
width = 0.35
ax3.bar(x - width/2, [r["Gini_hub"]  for r in resumo_rows], width, label="Gini Hub",  color="#e74c3c", alpha=0.8)
ax3.bar(x + width/2, [r["Gini_auth"] for r in resumo_rows], width, label="Gini Auth", color="#3498db", alpha=0.8)
ax3.set_xticks(x)
ax3.set_xticklabels([r["Janela"] for r in resumo_rows], rotation=30, ha="right", fontsize=8)
ax3.set_title("Concentração (Gini) dos scores Hub e Authority por janela")
ax3.set_ylabel("Coeficiente de Gini")
ax3.set_ylim(0.9, 1.0)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
fig3.savefig(f"{OUT}/gini_hits.png", dpi=150)
print(f"Plot Gini HITS salvo.")

print("\nAlgoritmo 8 concluído.")
