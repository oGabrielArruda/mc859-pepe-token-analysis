"""Algoritmo 6 — Motifs / Triângulos (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES
import networkx as nx, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker as mticker

OUT = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUT, exist_ok=True)
CYCLE_T = ["030C","120C","300"]; FF_T = ["030T","120U","120D"]
resumo, whale_rows = [], []

for nome in GRAFOS:
    print(f"\n{'='*50}\n{nome}")
    G  = load_digraph(nome)
    Gu = G.to_undirected()
    n, e = G.number_of_nodes(), G.number_of_edges()

    tri_dict = nx.triangles(Gu)
    n_tri    = sum(tri_dict.values())//3
    nodes_in_tri = sum(1 for v in tri_dict.values() if v>0)
    transit  = nx.transitivity(Gu)
    avg_cl   = nx.average_clustering(Gu, weight="edge_weight")

    census   = nx.triadic_census(G)
    n_cycles = sum(census.get(t,0) for t in CYCLE_T)
    n_ff     = sum(census.get(t,0) for t in FF_T)
    total_t  = sum(census.values())

    print(f"  Triângulos={n_tri} nós_em_tri={nodes_in_tri}({nodes_in_tri/n:.1%})")
    print(f"  Transitivity={transit:.5f} avg_cl={avg_cl:.5f}")
    print(f"  030C={census.get('030C',0)} 300={census.get('300',0)} 030T={census.get('030T',0)}")

    for addr, desc in WHALES.items():
        if addr in Gu:
            cl  = nx.clustering(Gu, addr, weight="edge_weight")
            tri = tri_dict.get(addr,0)
            deg = Gu.degree(addr)
            print(f"  [{desc}] clustering={cl:.4f} tri={tri} deg={deg}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "clustering":round(cl,4),"triangulos":tri,"degree":deg})

    resumo.append({"Grafo":nome,"Nos":n,"Arestas":e,"Triangulos":n_tri,
                   "Pct_nos_em_tri":round(nodes_in_tri/n,4),
                   "Transitivity":round(transit,5),"Avg_clustering":round(avg_cl,6),
                   "N_ciclos":n_cycles,"N_ff":n_ff,
                   "030C":census.get("030C",0),"300":census.get("300",0),
                   "030T":census.get("030T",0)})

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUT}/resumo_motifs_gexf.csv", index=False)
pd.DataFrame(whale_rows).to_csv(f"{OUT}/whales_motifs_gexf.csv", index=False)
print("\n=== RESUMO ===")
print(df_res[["Grafo","Triangulos","Pct_nos_em_tri","Transitivity","030C","300","030T"]].to_string(index=False))

# ── Plot ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
fig, axes = plt.subplots(1,3,figsize=(15,5))

for ax,(metric,title,ylabel) in zip(axes,[
    ("Triangulos",       "Triângulos totais",              "Contagem"),
    ("Transitivity",     "Transitivity (clustering global)","Coef."),
    ("Pct_nos_em_tri",  "Nós em triângulo",               "Fração"),
]):
    vals  = [r[metric] for r in resumo]
    bars  = ax.bar(GRAFOS, vals, color=[CORES[r["Grafo"]] for r in resumo], alpha=0.85, width=0.5)
    ax.set_title(title); ax.set_ylabel(ylabel)
    if "pct" in metric.lower() or "tri" in metric.lower() and "Pct" in metric:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    for bar,val in zip(bars,vals):
        lbl = f"{int(val):,}" if val>10 else f"{val:.5f}"
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01,
                lbl, ha="center",va="bottom",fontsize=9,fontweight="bold")

plt.suptitle("Análise de Motifs — Grafos completos", fontsize=13)
plt.tight_layout()
fig.savefig(f"{OUT}/report_motifs_gexf.png", dpi=200, bbox_inches="tight")
print("Plot salvo."); plt.close()
