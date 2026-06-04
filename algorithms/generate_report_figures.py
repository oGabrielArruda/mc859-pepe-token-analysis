"""
Gera figuras polidas para o relatório final (report_*.png em cada pasta results/).
Carrega CSVs de resultados já existentes + dados brutos quando necessário.
DPI=200, fontes limpas, paleta consistente.
"""

import os
import warnings
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from collections import Counter
warnings.filterwarnings("ignore")

BASE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(BASE, "../data")

# ── Paleta consistente ────────────────────────────────────────────────────────
C_BASE = "#7f8c8d"   # cinza — baseline
C_MAD  = "#e74c3c"   # vermelho — Maduro
C_KHA  = "#27ae60"   # verde — Khamenei
DPI    = 200

JANELA_CORES = {
    "Baseline":          C_BASE,
    "Maduro_1_Antes":    C_MAD,
    "Maduro_2_Choque":   C_MAD,
    "Maduro_3_Depois":   C_MAD,
    "Khamenei_1_Antes":  C_KHA,
    "Khamenei_2_Choque": C_KHA,
    "Khamenei_3_Depois": C_KHA,
}
JANELA_LABELS = {
    "Baseline":          "Baseline",
    "Maduro_1_Antes":    "Maduro\nD−3…D−1",
    "Maduro_2_Choque":   "Maduro\nD",
    "Maduro_3_Depois":   "Maduro\nD+1…D+3",
    "Khamenei_1_Antes":  "Khamenei\nD−3…D−1",
    "Khamenei_2_Choque": "Khamenei\nD",
    "Khamenei_3_Depois": "Khamenei\nD+1…D+3",
}
JANELA_ORDER = list(JANELA_LABELS.keys())

RC = {
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   12,
    "axes.labelsize":   11,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "legend.fontsize":  9,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.3,
    "grid.linestyle":   "--",
}

def apply_rc():
    plt.rcParams.update(RC)

def bar_colors(janelas):
    return [JANELA_CORES[j] for j in janelas]

def xtick_labels(janelas):
    return [JANELA_LABELS[j] for j in janelas]

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1 — Top-20 Volume Share por janela  (Alg.1)
# ─────────────────────────────────────────────────────────────────────────────
def fig_top_share():
    csv = os.path.join(BASE, "01_pagerank_centralidade/results/resumo_metricas.csv")
    df  = pd.read_csv(csv)
    df  = df.set_index("Janela").loc[JANELA_ORDER].reset_index()

    apply_rc()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x   = np.arange(len(df))
    w   = 0.38
    c   = bar_colors(df["Janela"])

    b1 = ax.bar(x - w/2, df["Top20_share_PR"],  w, color=c, alpha=0.60, label="Top-20 PageRank share")
    b2 = ax.bar(x + w/2, df["Top20_share_Vol"], w, color=c, alpha=0.92, label="Top-20 Volume share")

    for bar, val in zip(b2, df["Top20_share_Vol"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.0%}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels(df["Janela"]), fontsize=9)
    ax.set_ylabel("Fração do total detida pelo Top-20")
    ax.set_title("Concentração de volume e PageRank — Top-20 endereços por janela")
    ax.legend(framealpha=0.8)

    from matplotlib.patches import Patch
    handles = [Patch(color=C_BASE, label="Baseline"),
               Patch(color=C_MAD,  label="Maduro"),
               Patch(color=C_KHA,  label="Khamenei")]
    ax.legend(handles=handles + ax.get_legend_handles_labels()[0][:2],
              labels=["Baseline","Maduro","Khamenei",
                      "Top-20 PageRank share","Top-20 Volume share"], fontsize=9)

    plt.tight_layout()
    out = os.path.join(BASE, "01_pagerank_centralidade/results/report_top_share.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 2 — Distribuição de Grau log-log: Baseline vs Maduro_Choque vs Khamenei_Choque
# ─────────────────────────────────────────────────────────────────────────────
def fig_distribuicao_grau():
    print("  Carregando dados para distribuição de grau…")
    df_b = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
    df_m = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
    df_k = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")
    for df in [df_b, df_m, df_k]:
        df["block_timestamp"] = pd.to_datetime(df["block_timestamp"].str.replace(" UTC","",regex=False))

    configs = [
        ("Baseline",        df_b, "2025-10-16","2025-10-23 23:59:59", C_BASE),
        ("Maduro (dia D)",  df_m, "2026-01-03","2026-01-03 23:59:59", C_MAD),
        ("Khamenei (dia D)",df_k, "2026-02-28","2026-02-28 23:59:59", C_KHA),
    ]

    apply_rc()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    for ax, (label, df, ini, fim, color) in zip(axes, configs):
        mask  = (df["block_timestamp"] >= ini) & (df["block_timestamp"] <= fim)
        edges = (df.loc[mask].groupby(["source_node","target_node"])["edge_weight"]
                 .sum().reset_index())
        G  = nx.from_pandas_edgelist(edges,"source_node","target_node",
                                      create_using=nx.DiGraph())
        G.remove_edges_from(list(nx.selfloop_edges(G)))

        in_deg = [d for _,d in G.in_degree() if d > 0]
        cnt    = Counter(in_deg)
        xs, ys = zip(*sorted(cnt.items()))

        ax.scatter(xs, ys, s=14, alpha=0.7, color=color, edgecolors="none")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(label)
        ax.set_xlabel("In-degree (k)")
        ax.set_ylabel("Frequência" if ax == axes[0] else "")
        ax.grid(True, which="both", ls="--", alpha=0.25)

        n = G.number_of_nodes()
        e = G.number_of_edges()
        ax.text(0.97, 0.97, f"n={n:,}\nm={e:,}", transform=ax.transAxes,
                ha="right", va="top", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7))

    fig.suptitle("Distribuição de In-degree (escala log-log)", fontsize=13)
    plt.tight_layout()
    out = os.path.join(BASE, "02_distribuicao_grau/results/report_distribuicao_grau.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 3 — Bow-Tie composição % por janela  (Alg.3)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bowtie_composicao():
    csv = os.path.join(BASE, "03_bowtie/results/resumo_bowtie.csv")
    df  = pd.read_csv(csv).set_index("Janela").loc[JANELA_ORDER].reset_index()

    apply_rc()
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(df))
    bottom = np.zeros(len(df))

    COMP_STYLE = [
        ("SCC_pct",   "#2980b9", "SCC"),
        ("IN_pct",    "#27ae60", "IN"),
        ("OUT_pct",   "#e74c3c", "OUT"),
        ("OTHER_pct", "#bdc3c7", "Other"),
    ]

    for col, color, label in COMP_STYLE:
        vals = df[col].values
        bars = ax.bar(x, vals, bottom=bottom, color=color, label=label, alpha=0.88)
        for i, (v, b) in enumerate(zip(vals, bottom)):
            if v > 0.05:
                ax.text(x[i], b + v/2, f"{v:.0%}", ha="center", va="center",
                        fontsize=8.5, color="white", fontweight="bold")
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels(df["Janela"]), fontsize=9.5)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_ylabel("Proporção de nós")
    ax.set_title("Estrutura Bow-Tie — composição da rede por janela temporal")
    ax.legend(loc="upper right", framealpha=0.85, ncol=4)
    ax.set_ylim(0, 1.08)

    # Anota o Khamenei_1_Antes
    idx = JANELA_ORDER.index("Khamenei_1_Antes")
    in_pct = df.loc[df["Janela"]=="Khamenei_1_Antes","IN_pct"].values[0]
    ax.annotate("69% IN", xy=(idx, 0.50), fontsize=10, ha="center",
                color="white", fontweight="bold")

    plt.tight_layout()
    out = os.path.join(BASE, "03_bowtie/results/report_bowtie_composicao.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 4 — Bow-Tie razão OUT/IN por janela  (Alg.3)
# ─────────────────────────────────────────────────────────────────────────────
def fig_bowtie_fluxo():
    csv = os.path.join(BASE, "03_bowtie/results/resumo_bowtie.csv")
    df  = pd.read_csv(csv).set_index("Janela").loc[JANELA_ORDER].reset_index()

    apply_rc()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Razão OUT/IN
    ax = axes[0]
    vals  = df["Ratio_OUT_IN"].values
    colors = bar_colors(df["Janela"])
    bars  = ax.bar(range(len(df)), vals, color=colors, alpha=0.85)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="Equilíbrio (OUT=IN)")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(xtick_labels(df["Janela"]), fontsize=9)
    ax.set_ylabel("Razão OUT / IN")
    ax.set_title("Direção do fluxo de capital\n(> 1 = mais saída que entrada)")
    ax.legend(fontsize=9)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.03, f"{val:.2f}",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Volume IN→SCC vs SCC→OUT
    ax2 = axes[1]
    w   = 0.35
    x   = np.arange(len(df))
    b1  = ax2.bar(x - w/2, df["Vol_pct_IN_to_SCC"],  w, color="#27ae60", alpha=0.85, label="IN → SCC")
    b2  = ax2.bar(x + w/2, df["Vol_pct_SCC_to_OUT"], w, color="#e74c3c", alpha=0.85, label="SCC → OUT")
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax2.set_xticks(x)
    ax2.set_xticklabels(xtick_labels(df["Janela"]), fontsize=9)
    ax2.set_ylabel("Fração do volume total")
    ax2.set_title("Fluxo de volume entre componentes")
    ax2.legend(fontsize=9)

    # Destaca o Khamenei_Choque no vol IN→SCC
    idx = JANELA_ORDER.index("Khamenei_2_Choque")
    v   = df.loc[df["Janela"]=="Khamenei_2_Choque","Vol_pct_IN_to_SCC"].values[0]
    ax2.annotate(f"{v:.0%}", xy=(idx - w/2, v), xytext=(idx - w/2, v + 0.02),
                 ha="center", fontsize=9, fontweight="bold", color="#27ae60")

    plt.tight_layout()
    out = os.path.join(BASE, "03_bowtie/results/report_bowtie_fluxo.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 5 — Série temporal: 6 métricas dias relativos  (Alg.4)
# ─────────────────────────────────────────────────────────────────────────────
def fig_serie_temporal():
    csv = os.path.join(BASE, "04_serie_temporal/results/metricas_diarias.csv")
    df  = pd.read_csv(csv, parse_dates=["date"])

    D_MAD = pd.Timestamp("2026-01-03")
    D_KHA = pd.Timestamp("2026-02-28")
    df_b  = df[df["dataset"]=="Baseline"].copy()
    df_m  = df[df["dataset"]=="Maduro"].copy()
    df_k  = df[df["dataset"]=="Khamenei"].copy()
    df_m["d_rel"] = (df_m["date"] - D_MAD).dt.days
    df_k["d_rel"] = (df_k["date"] - D_KHA).dt.days

    METRICS = [
        ("n_nodes",       "Nós ativos"),
        ("scc_pct",       "SCC (% dos nós)"),
        ("ratio_out_in",  "Razão OUT / IN"),
        ("vol_in_to_scc", "Volume IN→SCC (%)"),
        ("gini_vol",      "Gini do volume"),
        ("top20_pr_share","Top-20 PageRank share"),
    ]

    apply_rc()
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for ax, (metric, label) in zip(axes, METRICS):
        bv = df_b[metric].dropna().values
        if len(bv):
            ax.axhspan(bv.min(), bv.max(), alpha=0.10, color=C_BASE, label="Baseline (faixa)")
            ax.axhline(bv.mean(), color=C_BASE, linestyle=":", linewidth=1.3,
                       alpha=0.8, label=f"Baseline (média)")

        for df_ev, color, lbl in [(df_m, C_MAD, "Maduro"), (df_k, C_KHA, "Khamenei")]:
            sub = df_ev[["d_rel", metric]].dropna()
            ax.plot(sub["d_rel"], sub[metric], "o-", color=color, label=lbl,
                    linewidth=2.2, markersize=7)
            ax.axvline(0, color=color, linestyle="--", linewidth=0.9, alpha=0.45)

        ax.set_title(label)
        ax.set_ylabel(label, fontsize=9)
        ax.set_xlabel("Dias relativos ao evento (D = 0)", fontsize=9)
        ax.set_xticks(range(-3, 4))
        ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in range(-3, 4)])
        ax.legend(fontsize=8)

        if metric in ("scc_pct","vol_in_to_scc","top20_pr_share"):
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))

    fig.suptitle("Evolução diária de métricas estruturais — eventos vs baseline",
                 fontsize=13, y=1.01)
    plt.tight_layout()
    out = os.path.join(BASE, "04_serie_temporal/results/report_serie_temporal.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 6 — Volume médio por k-core  (Alg.5)
# ─────────────────────────────────────────────────────────────────────────────
def fig_volume_kcore():
    print("  Carregando dados para k-core…")
    df_b = pd.read_csv(f"{DATA}/baseline_window_16-10_23-10.csv")
    df_m = pd.read_csv(f"{DATA}/maduro_window_31-12_06-01.csv")
    df_k = pd.read_csv(f"{DATA}/alikhamenei_window_25-02_03-03.csv")
    for df in [df_b, df_m, df_k]:
        df["block_timestamp"] = pd.to_datetime(df["block_timestamp"].str.replace(" UTC","",regex=False))

    configs = [
        ("Baseline",        df_b, "2025-10-16","2025-10-23 23:59:59", C_BASE),
        ("Maduro D−3…D−1",  df_m, "2025-12-31","2026-01-02 23:59:59", C_MAD),
        ("Maduro D",        df_m, "2026-01-03","2026-01-03 23:59:59", C_MAD),
        ("Khamenei D−3…D−1",df_k, "2026-02-25","2026-02-27 23:59:59", C_KHA),
        ("Khamenei D",      df_k, "2026-02-28","2026-02-28 23:59:59", C_KHA),
    ]

    apply_rc()
    fig, ax = plt.subplots(figsize=(10, 5))

    for label, df, ini, fim, color in configs:
        mask  = (df["block_timestamp"] >= ini) & (df["block_timestamp"] <= fim)
        edges = (df.loc[mask].groupby(["source_node","target_node"])["edge_weight"]
                 .sum().reset_index())
        G  = nx.from_pandas_edgelist(edges,"source_node","target_node",
                                      edge_attr="edge_weight", create_using=nx.DiGraph())
        G.remove_edges_from(list(nx.selfloop_edges(G)))
        Gu = G.to_undirected()
        cn = nx.core_number(Gu)

        vol_by_k = {}
        for node, k in cn.items():
            v = G.in_degree(node, weight="edge_weight") + G.out_degree(node, weight="edge_weight")
            vol_by_k.setdefault(k, []).append(v)
        vk_mean = {k: np.mean(v) for k, v in vol_by_k.items()}
        ks = sorted(vk_mean.keys())
        linestyle = "--" if "D−3" in label else "-"
        ax.plot(ks, [vk_mean[k] for k in ks], marker="o", markersize=5,
                color=color, linestyle=linestyle, linewidth=1.8, label=label)

    ax.set_yscale("log")
    ax.set_xlabel("Nível de k-core")
    ax.set_ylabel("Volume médio transacionado (log)")
    ax.set_title("Volume médio por nível de k-core\n(nós do núcleo movimentam mais?)")
    ax.legend(fontsize=9, ncol=2)
    plt.tight_layout()
    out = os.path.join(BASE, "05_kcore/results/report_volume_kcore.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 7 — Heatmap z-scores  (Alg.7)
# ─────────────────────────────────────────────────────────────────────────────
def fig_heatmap_zscores():
    csv = os.path.join(BASE, "07_anomalia/results/zscores_diarios.csv")
    df  = pd.read_csv(csv, parse_dates=["date"])

    METRICS_Z = {
        "z_n_nodes":       "Nós ativos",
        "z_scc_pct":       "SCC %",
        "z_ratio_out_in":  "OUT / IN",
        "z_vol_in_to_scc": "Vol IN→SCC",
        "z_gini_vol":      "Gini volume",
        "z_top20_pr_share":"PR Top-20",
    }

    apply_rc()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, dataset, title in [
        (axes[0], "Maduro",   "Maduro"),
        (axes[1], "Khamenei", "Khamenei"),
    ]:
        sub = df[df["dataset"]==dataset].sort_values("d_rel")
        zmat = sub[[c for c in METRICS_Z]].values.T
        xlabs = [f"D{int(d):+d}" if d != 0 else "D" for d in sub["d_rel"]]
        ylabs = list(METRICS_Z.values())

        im = ax.imshow(zmat, aspect="auto", cmap="RdBu_r",
                       vmin=-6, vmax=6, interpolation="nearest")
        ax.set_xticks(range(len(xlabs))); ax.set_xticklabels(xlabs, fontsize=10)
        ax.set_yticks(range(len(ylabs))); ax.set_yticklabels(ylabs, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight="bold")
        cb = plt.colorbar(im, ax=ax, shrink=0.85)
        cb.set_label("Z-score", fontsize=9)

        for i in range(zmat.shape[0]):
            for j in range(zmat.shape[1]):
                v = zmat[i, j]
                if not np.isnan(v):
                    fw = "bold" if abs(v) > 2 else "normal"
                    fc = "white" if abs(v) > 3 else "black"
                    ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                            fontsize=8.5, color=fc, fontweight=fw)

    fig.suptitle("Detecção de Anomalia — Z-score diário relativo ao baseline\n"
                 "(vermelho = acima | azul = abaixo | negrito = |z| > 2)",
                 fontsize=11)
    plt.tight_layout()
    out = os.path.join(BASE, "07_anomalia/results/report_heatmap_zscores.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 8 — Anomaly score por dia  (Alg.7)
# ─────────────────────────────────────────────────────────────────────────────
def fig_anomaly_score():
    csv = os.path.join(BASE, "07_anomalia/results/zscores_diarios.csv")
    df  = pd.read_csv(csv, parse_dates=["date"])
    df_m = df[df["dataset"]=="Maduro"].sort_values("d_rel")
    df_k = df[df["dataset"]=="Khamenei"].sort_values("d_rel")
    df_b = df[df["dataset"]=="Baseline"]

    base_mean = df_b["anomaly_score"].mean()
    base_std  = df_b["anomaly_score"].std()

    apply_rc()
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(-3, 4)
    w = 0.38

    ax.bar(x - w/2, df_m["anomaly_score"].values, w,
           color=C_MAD, alpha=0.85, label="Maduro")
    ax.bar(x + w/2, df_k["anomaly_score"].values, w,
           color=C_KHA, alpha=0.85, label="Khamenei")

    ax.axhline(base_mean,           color=C_BASE, linestyle="--", linewidth=1.3,
               label=f"Baseline médio ({base_mean:.1f})")
    ax.axhline(base_mean+2*base_std, color=C_BASE, linestyle=":",  linewidth=1,
               label=f"Baseline +2σ ({base_mean+2*base_std:.1f})")

    # Anota D-3 Khamenei
    ax.annotate("D-3 Khamenei\n(score = 32,8)", xy=(-3 + w/2, df_k.iloc[0]["anomaly_score"]),
                xytext=(-2.1, 29),
                arrowprops=dict(arrowstyle="->", color=C_KHA, lw=1.5),
                fontsize=9, color=C_KHA, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([f"D{d:+d}" if d != 0 else "D" for d in x], fontsize=10)
    ax.set_ylabel("Anomaly Score (Σ |z-score|)")
    ax.set_title("Score de anomalia diário — soma dos desvios em relação ao baseline")
    ax.legend(fontsize=9)
    plt.tight_layout()
    out = os.path.join(BASE, "07_anomalia/results/report_anomaly_score.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 9 — Gini Hub vs Authority  (Alg.8)
# ─────────────────────────────────────────────────────────────────────────────
def fig_gini_hits():
    csv = os.path.join(BASE, "08_hits/results/resumo_hits.csv")
    df  = pd.read_csv(csv).set_index("Janela").loc[JANELA_ORDER].reset_index()

    apply_rc()
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(df))
    w = 0.38

    b1 = ax.bar(x - w/2, df["Gini_hub"],  w, color="#e74c3c", alpha=0.85, label="Gini Hub (distribuidores)")
    b2 = ax.bar(x + w/2, df["Gini_auth"], w, color="#2980b9", alpha=0.85, label="Gini Authority (acumuladores)")

    for bar, val in zip(b1, df["Gini_hub"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=7.5, color="#e74c3c")
    for bar, val in zip(b2, df["Gini_auth"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=7.5, color="#2980b9")

    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels(df["Janela"]), fontsize=9.5)
    ax.set_ylim(0.3, 1.05)
    ax.set_ylabel("Coeficiente de Gini")
    ax.set_title("Concentração dos scores HITS — Hub vs Authority por janela\n"
                 "(Khamenei D−3…D−1: inversão — Hub disperso, Authority ultrac​oncentrada)")
    ax.legend(fontsize=9)

    # Anota inversão
    idx = JANELA_ORDER.index("Khamenei_1_Antes")
    ax.annotate("Inversão", xy=(idx, 0.40), fontsize=9, ha="center",
                fontweight="bold", color="#e74c3c",
                arrowprops=dict(arrowstyle="->", color="#e74c3c"))

    plt.tight_layout()
    out = os.path.join(BASE, "08_hits/results/report_gini_hits.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Executa tudo
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.chdir(BASE)
    print("Gerando figuras para o relatório...\n")
    fig_top_share()
    fig_distribuicao_grau()
    fig_bowtie_composicao()
    fig_bowtie_fluxo()
    fig_serie_temporal()
    fig_volume_kcore()
    fig_heatmap_zscores()
    fig_anomaly_score()
    fig_gini_hits()
    print("\nTodas as figuras geradas.")
