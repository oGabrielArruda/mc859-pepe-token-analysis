"""Algoritmo 2 — Distribuição de Grau (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES
import networkx as nx, pandas as pd, numpy as np, powerlaw, warnings
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
warnings.filterwarnings("ignore")

OUT = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUT, exist_ok=True)

def fit_pl(seq):
    data = [x for x in seq if x > 0]
    if len(data) < 10: return None, None, None, None
    fit = powerlaw.Fit(data, discrete=True, verbose=False)
    R, p = fit.distribution_compare("power_law", "lognormal")
    return fit.alpha, fit.xmin, R, p

resumo, whale_rows = [], []

fig, axes = plt.subplots(2, 3, figsize=(15, 9))

for col, nome in enumerate(GRAFOS):
    print(f"\n{'='*50}\n{nome}")
    G  = load_digraph(nome)
    Gu = G.to_undirected()

    in_deg  = [d for _,d in G.in_degree()]
    out_deg = [d for _,d in G.out_degree()]
    in_vol  = [d for _,d in G.in_degree(weight="edge_weight")]
    out_vol = [d for _,d in G.out_degree(weight="edge_weight")]

    a_in, xm_in, R_in, p_in   = fit_pl(in_deg)
    a_out,xm_out,R_out,p_out  = fit_pl(out_deg)
    a_vin,*_                   = fit_pl(in_vol)
    a_vout,*_                  = fit_pl(out_vol)

    print(f"  in-deg α={a_in:.3f} xmin={xm_in} R(PL/LN)={R_in:.2f} p={p_in:.3f}")
    print(f"  out-deg α={a_out:.3f} xmin={xm_out} R={R_out:.2f} p={p_out:.3f}")
    print(f"  in-vol α={a_vin:.3f} | out-vol α={a_vout:.3f}")

    # Whales
    all_in_rank  = sorted(G.in_degree(weight="edge_weight"),  key=lambda x:x[1], reverse=True)
    rank_inv = {a:r+1 for r,(a,_) in enumerate(all_in_rank)}
    for addr, desc in WHALES.items():
        if G.has_node(addr):
            cl = nx.clustering(Gu, addr) if addr in Gu else 0
            print(f"  [{desc}] rank_in={rank_inv.get(addr,'-')} in_deg={G.in_degree(addr)} clustering={cl:.4f}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "rank_in_vol":rank_inv.get(addr),"in_degree":G.in_degree(addr),
                                "alpha_in_deg":round(a_in,3) if a_in else None})

    resumo.append({"Grafo":nome,"Nos":G.number_of_nodes(),"Arestas":G.number_of_edges(),
                   "alpha_in_deg":round(a_in,3),"alpha_out_deg":round(a_out,3),
                   "alpha_in_vol":round(a_vin,3),"alpha_out_vol":round(a_vout,3),
                   "xmin_in":xm_in,"R_in":round(R_in,3),"R_out":round(R_out,3)})

    color = CORES[nome]
    for row, seq, label in [(0, in_deg, "In-degree"), (1, out_deg, "Out-degree")]:
        ax = axes[row][col]
        data = [x for x in seq if x > 0]
        cnt  = Counter(data); xs,ys = zip(*sorted(cnt.items()))
        ax.scatter(xs, ys, s=8, alpha=0.65, color=color, edgecolors="none")
        ax.set_xscale("log"); ax.set_yscale("log")
        alpha = a_in if row==0 else a_out
        xmin  = xm_in if row==0 else xm_out
        if alpha and xmin:
            xs_fit = np.array([x for x in sorted(set(data)) if x >= xmin])
            C = len([x for x in data if x >= xmin])
            ax.plot(xs_fit, C*(xs_fit/xmin)**(-alpha), "k--", lw=1.2, alpha=0.8,
                    label=f"α={alpha:.2f}")
        ax.set_title(f"{nome}\n{label}")
        ax.set_xlabel("k"); ax.set_ylabel("Frequência" if col==0 else "")
        ax.grid(True, which="both", ls="--", alpha=0.2)
        if alpha: ax.legend(fontsize=8)

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUT}/resumo_distribuicao_gexf.csv", index=False)
pd.DataFrame(whale_rows).to_csv(f"{OUT}/whales_distribuicao_gexf.csv", index=False)
print("\n=== RESUMO ==="); print(df_res[["Grafo","alpha_in_deg","alpha_out_deg","alpha_in_vol","R_in","R_out"]].to_string(index=False))

plt.suptitle("Distribuição de Grau (log-log) — Grafos completos\n"
             "Linha tracejada = ajuste lei de potência", fontsize=12)
plt.tight_layout()
fig.savefig(f"{OUT}/report_distribuicao_gexf.png", dpi=200, bbox_inches="tight")
print("Plot salvo."); plt.close()
