"""Algoritmo 5 — K-core Decomposition (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES
import networkx as nx, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

OUT = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUT, exist_ok=True)
resumo, whale_rows = [], []

fig, axes = plt.subplots(1,3,figsize=(15,5))

for col, nome in enumerate(GRAFOS):
    print(f"\n{'='*50}\n{nome}")
    G  = load_digraph(nome)
    Gu = G.to_undirected()
    cn = nx.core_number(Gu)
    n  = G.number_of_nodes()

    k_max    = max(cn.values())
    k_median = np.median(list(cn.values()))
    k_mean   = np.mean(list(cn.values()))
    cnt      = Counter(cn.values())
    pct_k1   = cnt[1]/n

    # Volume por k-core
    vol_by_k = {}
    for node, k in cn.items():
        v = G.in_degree(node,weight="edge_weight") + G.out_degree(node,weight="edge_weight")
        vol_by_k.setdefault(k,[]).append(v)
    vol_k_mean = {k:np.mean(v) for k,v in vol_by_k.items()}

    print(f"  k_max={k_max} k_median={k_median} k_mean={k_mean:.2f} k1%={pct_k1:.1%}")

    for addr, desc in WHALES.items():
        if addr in cn:
            k = cn[addr]
            pct = sum(1 for v in cn.values() if v<=k)/n
            vol = G.in_degree(addr,weight="edge_weight")+G.out_degree(addr,weight="edge_weight")
            print(f"  [{desc}] k={k} (pct={pct:.1%}) vol={vol:.2e}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "k_core":k,"k_max":k_max,"percentil_k":round(pct,4),"vol":vol})

    resumo.append({"Grafo":nome,"Nos":n,"k_max":k_max,
                   "k_median":round(k_median,1),"k_mean":round(k_mean,2),
                   "pct_k1":round(pct_k1,4),"n_kmax":cnt[k_max]})

    ax = axes[col]
    ks = sorted(cnt.keys()); freqs = [cnt[k] for k in ks]
    ax.bar(ks, freqs, color=CORES[nome], alpha=0.8)
    ax.set_yscale("log")
    ax.set_title(f"{nome}\nk_max={k_max}  k_med={k_median}", fontsize=10)
    ax.set_xlabel("k-core"); ax.set_ylabel("Frequência (log)" if col==0 else "")
    ax.axvline(k_max, color="black", ls="--", lw=1, alpha=0.6, label=f"k_max={k_max}")
    # Marca whales
    whale_ks = set(r["k_core"] for r in whale_rows if r["Grafo"]==nome)
    for wk in whale_ks:
        ax.axvline(wk, color="red", ls=":", lw=1.5, alpha=0.6)
    ax.legend(fontsize=8)

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUT}/resumo_kcore_gexf.csv", index=False)
pd.DataFrame(whale_rows).to_csv(f"{OUT}/whales_kcore_gexf.csv", index=False)
print("\n=== RESUMO ==="); print(df_res.to_string(index=False))

plt.suptitle("Distribuição K-core — Grafos completos\n"
             "Tracejado preto = k_max | Pontilhado vermelho = k das whales", fontsize=11)
plt.tight_layout()
fig.savefig(f"{OUT}/report_kcore_gexf.png", dpi=200, bbox_inches="tight")

# Volume por k-core — plot separado
fig2, ax2 = plt.subplots(figsize=(10,5))
for nome in GRAFOS:
    G  = load_digraph(nome)
    Gu = G.to_undirected()
    cn = nx.core_number(Gu)
    vk = {}
    for node, k in cn.items():
        v = G.in_degree(node,weight="edge_weight")+G.out_degree(node,weight="edge_weight")
        vk.setdefault(k,[]).append(v)
    ks = sorted(vk.keys())
    ax2.plot(ks, [np.mean(vk[k]) for k in ks], "o-", color=CORES[nome], label=nome, lw=2, ms=6)
ax2.set_yscale("log"); ax2.set_xlabel("Nível de k-core"); ax2.set_ylabel("Volume médio (log)")
ax2.set_title("Volume médio transacionado por nível de k-core")
ax2.legend(fontsize=10); ax2.grid(True, alpha=0.3)
plt.tight_layout()
fig2.savefig(f"{OUT}/report_volume_kcore_gexf.png", dpi=200, bbox_inches="tight")
print("Plots salvos."); plt.close("all")
