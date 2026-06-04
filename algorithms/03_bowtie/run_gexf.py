"""Algoritmo 3 — Bow-Tie (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES
import networkx as nx, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker as mticker

OUTDIR = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUTDIR, exist_ok=True)

def bowtie(G):
    sccs    = list(nx.strongly_connected_components(G))
    giant   = max(sccs, key=len); scc_set = set(giant)
    src     = next(iter(scc_set))
    out_set = set(nx.descendants(G, src)) - scc_set
    in_set  = set(nx.descendants(G.reverse(copy=False), src)) - scc_set
    other   = set(G.nodes()) - scc_set - in_set - out_set
    return scc_set, in_set, out_set, other, sccs

resumo, whale_rows = [], []

for nome in GRAFOS:
    print(f"\n{'='*50}\n{nome}")
    G = load_digraph(nome)
    n = G.number_of_nodes()

    scc, IN, OUT, OTHER, all_sccs = bowtie(G)
    ratio = len(OUT)/len(IN) if IN else float("inf")

    total_vol = sum(d.get("edge_weight",0) for _,_,d in G.edges(data=True))
    comp_of   = {nd: ("SCC" if nd in scc else "IN" if nd in IN else "OUT" if nd in OUT else "OTHER")
                 for nd in G.nodes()}

    v_i2s = v_s2o = 0.0
    for u,v,d in G.edges(data=True):
        w = d.get("edge_weight",0)
        cu,cv = comp_of[u], comp_of[v]
        if cu=="IN"  and cv=="SCC": v_i2s += w
        if cu=="SCC" and cv=="OUT": v_s2o += w

    sizes_minor = sorted([len(s) for s in all_sccs if len(s)<len(scc)], reverse=True)
    n_sing = sum(1 for s in sizes_minor if s==1)

    print(f"  SCC={len(scc)}({len(scc)/n:.1%}) IN={len(IN)}({len(IN)/n:.1%}) "
          f"OUT={len(OUT)}({len(OUT)/n:.1%}) OTHER={len(OTHER)}({len(OTHER)/n:.1%})")
    print(f"  OUT/IN={ratio:.2f} | Vol IN→SCC={v_i2s/total_vol:.1%} SCC→OUT={v_s2o/total_vol:.1%}")
    print(f"  SCCs menores: {sum(1 for s in sizes_minor if s>1)} não-singleton + {n_sing} singletons")

    for addr, desc in WHALES.items():
        if G.has_node(addr):
            comp = comp_of[addr]
            iv = G.in_degree(addr, weight="edge_weight")
            ov = G.out_degree(addr, weight="edge_weight")
            print(f"  [{desc}] {comp}  in={iv:.2e} out={ov:.2e}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "componente":comp,"in_vol":iv,"out_vol":ov})

    resumo.append({"Grafo":nome,"Nos":n,
                   "SCC_n":len(scc), "SCC_pct":round(len(scc)/n,4),
                   "IN_n": len(IN),  "IN_pct": round(len(IN)/n,4),
                   "OUT_n":len(OUT), "OUT_pct":round(len(OUT)/n,4),
                   "OTHER_n":len(OTHER),"OTHER_pct":round(len(OTHER)/n,4),
                   "Ratio_OUT_IN":round(ratio,3),
                   "Vol_pct_IN_to_SCC":round(v_i2s/total_vol,4),
                   "Vol_pct_SCC_to_OUT":round(v_s2o/total_vol,4),
                   "n_SCC_menor":sum(1 for s in sizes_minor if s>1),
                   "n_singleton":n_sing})

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUTDIR}/resumo_bowtie_gexf.csv", index=False)
pd.DataFrame(whale_rows).to_csv(f"{OUTDIR}/whales_bowtie_gexf.csv", index=False)
print("\n=== RESUMO ===")
print(df_res[["Grafo","SCC_n","SCC_pct","IN_n","IN_pct","OUT_n","OUT_pct","OTHER_n","OTHER_pct","Ratio_OUT_IN"]].to_string(index=False))

# ── Plots ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
fig, axes = plt.subplots(1,2,figsize=(13,5))

# Stacked bar
ax = axes[0]
bottom = np.zeros(3)
COMP_STYLE = [("SCC_pct","#2980b9","SCC"),("IN_pct","#27ae60","IN"),
              ("OUT_pct","#e74c3c","OUT"),("OTHER_pct","#bdc3c7","Other")]
for col,color,label in COMP_STYLE:
    vals = np.array([r[col] for r in resumo])
    bars = ax.bar(GRAFOS, vals, bottom=bottom, color=color, label=label, alpha=0.88)
    for i,(v,b) in enumerate(zip(vals,bottom)):
        if v>0.06:
            ax.text(i, b+v/2, f"{v:.0%}", ha="center",va="center",fontsize=10,color="white",fontweight="bold")
    bottom += vals
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.set_ylabel("Proporção de nós"); ax.set_title("Estrutura Bow-Tie — 3 grafos completos")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5,1.12), fontsize=9)

# OUT/IN e fluxo
ax2 = axes[1]
ratios = [r["Ratio_OUT_IN"] for r in resumo]
colors = [CORES[r["Grafo"]] for r in resumo]
bars2  = ax2.bar(GRAFOS, ratios, color=colors, alpha=0.85, width=0.5)
ax2.axhline(1.0, color="black", linestyle="--", lw=1.2, label="Equilíbrio (OUT=IN)")
ax2.set_ylabel("Razão OUT / IN"); ax2.set_title("Fluxo direcional de capital")
ax2.legend(fontsize=9)
for bar,val in zip(bars2,ratios):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02, f"{val:.2f}",
             ha="center",va="bottom",fontsize=11,fontweight="bold")

plt.tight_layout()
fig.savefig(f"{OUTDIR}/report_bowtie_gexf.png", dpi=200, bbox_inches="tight")
print("Plot salvo."); plt.close()
