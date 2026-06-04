"""Algoritmo 1 — PageRank + Centralidade (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES, gini
import networkx as nx, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker as mticker

OUT = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUT, exist_ok=True)
TOP = 20

resumo, whale_rows, tops = [], [], {}

for nome in GRAFOS:
    print(f"\n{'='*50}\n{nome}")
    G = load_digraph(nome)
    n, e = G.number_of_nodes(), G.number_of_edges()

    pr      = nx.pagerank(G, weight="edge_weight", max_iter=500)
    in_vol  = dict(G.in_degree(weight="edge_weight"))
    out_vol = dict(G.out_degree(weight="edge_weight"))
    total_v = {nd: in_vol.get(nd,0)+out_vol.get(nd,0) for nd in G.nodes()}

    pr_vals  = list(pr.values())
    vol_vals = list(total_v.values())
    gini_pr  = gini(pr_vals)
    gini_vol = gini(vol_vals)

    top_pr  = sorted(pr.items(),     key=lambda x: x[1], reverse=True)[:TOP]
    top_vol = sorted(total_v.items(),key=lambda x: x[1], reverse=True)[:TOP]
    set_pr  = {a for a,_ in top_pr}
    set_vol = {a for a,_ in top_vol}
    overlap = set_pr & set_vol

    tops[nome] = {"pr": set_pr, "vol": set_vol, "overlap": overlap}

    share_pr  = sum(sorted(pr_vals,  reverse=True)[:TOP]) / sum(pr_vals)
    share_vol = sum(sorted(vol_vals, reverse=True)[:TOP]) / sum(vol_vals)

    rank_in  = {a:r+1 for r,(a,_) in enumerate(sorted(in_vol.items(),  key=lambda x:x[1],reverse=True))}
    rank_out = {a:r+1 for r,(a,_) in enumerate(sorted(out_vol.items(), key=lambda x:x[1],reverse=True))}

    print(f"  n={n} e={e} gini_PR={gini_pr:.4f} gini_vol={gini_vol:.4f}")
    print(f"  top-{TOP} PR share={share_pr:.2%}  vol share={share_vol:.2%}  overlap={len(overlap)}")

    for addr, desc in WHALES.items():
        if G.has_node(addr):
            ri, ro = rank_in.get(addr,'-'), rank_out.get(addr,'-')
            print(f"  [{desc}] rank_in={ri} rank_out={ro} PR_rank={sorted(pr,key=pr.get,reverse=True).index(addr)+1 if addr in pr else '-'}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "rank_in":ri,"rank_out":ro,
                                "in_vol":in_vol.get(addr,0),"out_vol":out_vol.get(addr,0),
                                "pagerank":pr.get(addr,0)})

    resumo.append({"Grafo":nome,"Nos":n,"Arestas":e,
                   "Gini_PR":round(gini_pr,4),"Gini_Vol":round(gini_vol,4),
                   f"Top{TOP}_share_PR":round(share_pr,4),f"Top{TOP}_share_Vol":round(share_vol,4),
                   "Overlap":len(overlap)})

    pd.DataFrame([(a,s) for a,s in top_pr],  columns=["address","pagerank"]).to_csv(f"{OUT}/top_pr_{nome}.csv",  index=False)
    pd.DataFrame([(a,s) for a,s in top_vol], columns=["address","vol"]).to_csv(     f"{OUT}/top_vol_{nome}.csv", index=False)

# Endereços exclusivos por evento
base_pr = tops["Baseline"]["pr"]; base_vol = tops["Baseline"]["vol"]
excl = []
for nome in ["Maduro","Khamenei"]:
    for addr in tops[nome]["overlap"] - (base_pr|base_vol):
        excl.append({"Grafo":nome,"address":addr})
pd.DataFrame(excl).to_csv(f"{OUT}/exclusivos_evento.csv", index=False)

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUT}/resumo_pagerank.csv", index=False)
df_wh  = pd.DataFrame(whale_rows); df_wh.to_csv(f"{OUT}/whales_pagerank.csv", index=False)
print("\n=== RESUMO ==="); print(df_res.to_string(index=False))

# ── Plots ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
fig, axes = plt.subplots(1,2,figsize=(11,5))

for ax,(metric,title) in zip(axes,[("Gini_Vol","Gini do Volume Transacionado"),
                                    (f"Top{TOP}_share_Vol",f"Top-{TOP} Volume Share")]):
    vals  = [r[metric] for r in resumo]
    bars  = ax.bar(GRAFOS, vals, color=[CORES[g] for g in GRAFOS], alpha=0.85, width=0.5)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel("Coeficiente / Fração")
    if "share" in metric: ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    for bar,val in zip(bars,vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                f"{val:.3f}" if val<1 else f"{val:.0%}", ha="center",va="bottom",fontsize=10,fontweight="bold")

plt.suptitle("Concentração de PageRank e Volume — 3 grafos completos", fontsize=13)
plt.tight_layout()
fig.savefig(f"{OUT}/report_pagerank_concentracao.png", dpi=200, bbox_inches="tight")
print("Plot salvo."); plt.close()
