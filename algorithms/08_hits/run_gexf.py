"""Algoritmo 8 — HITS (grafos completos .gexf)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gexf_utils import load_digraph, GRAFOS, CORES, WHALES, gini
import networkx as nx, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker as mticker

OUT = os.path.join(os.path.dirname(__file__), "results"); os.makedirs(OUT, exist_ok=True)
TOP = 20
resumo, whale_rows, tops_all = [], [], {}

for nome in GRAFOS:
    print(f"\n{'='*50}\n{nome}")
    G = load_digraph(nome)

    hubs, auths = nx.hits(G, normalized=True, max_iter=500)

    top_h = sorted(hubs.items(),  key=lambda x:x[1], reverse=True)[:TOP]
    top_a = sorted(auths.items(), key=lambda x:x[1], reverse=True)[:TOP]
    set_h = {a for a,_ in top_h}; set_a = {a for a,_ in top_a}
    overlap = set_h & set_a
    tops_all[nome] = {"h":set_h,"a":set_a,"overlap":overlap}

    gini_h = gini(list(hubs.values()))
    gini_a = gini(list(auths.values()))

    rk_h = {a:r+1 for r,(a,_) in enumerate(sorted(hubs.items(),  key=lambda x:x[1],reverse=True))}
    rk_a = {a:r+1 for r,(a,_) in enumerate(sorted(auths.items(), key=lambda x:x[1],reverse=True))}

    print(f"  Gini_hub={gini_h:.4f} Gini_auth={gini_a:.4f} overlap={len(overlap)}")
    print(f"  Top-1 Hub: {top_h[0][0][:14]}… score={top_h[0][1]:.5f}")
    print(f"  Top-1 Auth:{top_a[0][0][:14]}… score={top_a[0][1]:.5f}")

    for addr, desc in WHALES.items():
        if addr in hubs:
            rh,ra = rk_h[addr], rk_a[addr]
            hs,as_ = hubs[addr], auths[addr]
            role = "Hub" if hs>as_ else "Auth"
            print(f"  [{desc}] rk_hub={rh} rk_auth={ra} → {role}")
            whale_rows.append({"Grafo":nome,"descricao":desc,"address":addr,
                                "rank_hub":rh,"rank_auth":ra,
                                "hub_score":round(hs,7),"auth_score":round(as_,7),"role":role})

    resumo.append({"Grafo":nome,"Nos":G.number_of_nodes(),
                   "Gini_hub":round(gini_h,4),"Gini_auth":round(gini_a,4),
                   "Overlap":len(overlap),
                   "Top1_hub":top_h[0][0],"Top1_auth":top_a[0][0]})

    pd.DataFrame([(a,s) for a,s in top_h], columns=["address","hub_score"]).to_csv(
        f"{OUT}/top_hubs_{nome}_gexf.csv",  index=False)
    pd.DataFrame([(a,s) for a,s in top_a], columns=["address","auth_score"]).to_csv(
        f"{OUT}/top_auths_{nome}_gexf.csv", index=False)

# Endereços exclusivos
base_h = tops_all["Baseline"]["h"]; base_a = tops_all["Baseline"]["a"]
excl = []
for nome in ["Maduro","Khamenei"]:
    eh = tops_all[nome]["h"]-base_h; ea = tops_all[nome]["a"]-base_a
    print(f"\n  {nome}: +{len(eh)} hubs exclusivos, +{len(ea)} auths exclusivas")
    for addr in tops_all[nome]["overlap"]-(base_h|base_a):
        excl.append({"Grafo":nome,"address":addr,"tipo":"hub+auth"})
pd.DataFrame(excl).to_csv(f"{OUT}/exclusivos_hits_gexf.csv", index=False)

df_res = pd.DataFrame(resumo); df_res.to_csv(f"{OUT}/resumo_hits_gexf.csv", index=False)
pd.DataFrame(whale_rows).to_csv(f"{OUT}/whales_hits_gexf.csv", index=False)
print("\n=== RESUMO ==="); print(df_res[["Grafo","Gini_hub","Gini_auth","Overlap"]].to_string(index=False))

# ── Plots ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False})
fig, axes = plt.subplots(1,2,figsize=(12,5))

# Gini Hub vs Auth
ax = axes[0]
x = np.arange(3); w=0.35
ax.bar(x-w/2,[r["Gini_hub"]  for r in resumo],w,color="#e74c3c",alpha=0.85,label="Gini Hub")
ax.bar(x+w/2,[r["Gini_auth"] for r in resumo],w,color="#2980b9",alpha=0.85,label="Gini Auth")
ax.set_xticks(x); ax.set_xticklabels(GRAFOS); ax.set_ylim(0.5,1.05)
ax.set_ylabel("Coeficiente de Gini"); ax.set_title("Concentração Hub vs Authority")
ax.legend(fontsize=9)
for i,r in enumerate(resumo):
    ax.text(i-w/2, r["Gini_hub"] +0.005, f"{r['Gini_hub']:.3f}",  ha="center",fontsize=9,color="#e74c3c")
    ax.text(i+w/2, r["Gini_auth"]+0.005, f"{r['Gini_auth']:.3f}", ha="center",fontsize=9,color="#2980b9")

# Rank Hub vs Auth das whales
ax2 = axes[1]
df_wh = pd.DataFrame(whale_rows)
for nome in GRAFOS:
    sub = df_wh[df_wh["Grafo"]==nome]
    for _,row in sub.iterrows():
        ax2.scatter(row["rank_hub"], row["rank_auth"],
                    color=CORES[nome], s=80, zorder=4, alpha=0.85)
        ax2.annotate(row["descricao"][:12], (row["rank_hub"],row["rank_auth"]),
                     textcoords="offset points",xytext=(4,2),fontsize=7,alpha=0.8)

from matplotlib.patches import Patch
handles = [Patch(color=CORES[g],label=g) for g in GRAFOS]
ax2.legend(handles=handles, fontsize=9)
ax2.set_xlabel("Rank Hub (↓ = mais distribuidor)")
ax2.set_ylabel("Rank Authority (↓ = mais acumulador)")
ax2.set_title("Posição das Whales: Hub × Authority")
ax2.axvline(TOP,color="gray",ls=":",lw=0.8,alpha=0.5); ax2.axhline(TOP,color="gray",ls=":",lw=0.8,alpha=0.5)
ax2.grid(True,alpha=0.3)

plt.suptitle("HITS — Grafos completos", fontsize=13)
plt.tight_layout()
fig.savefig(f"{OUT}/report_hits_gexf.png", dpi=200, bbox_inches="tight")
print("Plot salvo."); plt.close()
