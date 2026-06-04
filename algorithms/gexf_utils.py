"""Utilitários compartilhados para carregamento dos grafos .gexf."""
import networkx as nx
import os

REPO = os.path.join(os.path.dirname(__file__), "..")
GEXF = {
    "Baseline": os.path.join(REPO, "result/Baseline.gexf"),
    "Maduro":   os.path.join(REPO, "result/Maduro_Total.gexf"),
    "Khamenei": os.path.join(REPO, "result/Khamenei_Total.gexf"),
}
GRAFOS = ["Baseline", "Maduro", "Khamenei"]
CORES  = {"Baseline": "#7f8c8d", "Maduro": "#e74c3c", "Khamenei": "#27ae60"}

# Whales identificadas na análise de sub-janelas
WHALES = {
    "0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4": "Maduro-Hub",
    "0xf977814e90da44bfa03b6295a0616a897441acec": "Maduro-Sink",
    "0xfbd4cdb413e45a52e2c8312f670e9ce67e794c37": "Maduro-Hub-2",
    "0xb334a61a6209f14b5fa5f1684a4ed7621f66e1ef": "Khamenei-Antecipador",
    "0xeb9ca8fdfac0652a97c0e1a48c1178d32d3a6b8f": "Khamenei-Hub",
    "0x9b0c45d46d386cedd98873168c36efd0dcba8d46": "Khamenei-Hub-2",
}

def load_digraph(nome):
    """Carrega .gexf como MultiDiGraph e converte para DiGraph ponderado simples."""
    G_multi = nx.read_gexf(GEXF[nome])
    G = nx.DiGraph()
    G.add_nodes_from(G_multi.nodes(data=True))
    weight_sum = {}
    for u, v, d in G_multi.edges(data=True):
        w = d.get("edge_weight", 1.0)
        key = (u, v)
        weight_sum[key] = weight_sum.get(key, 0.0) + w
    for (u, v), w in weight_sum.items():
        G.add_edge(u, v, edge_weight=w)
    return G

def gini(values):
    arr = sorted(v for v in values if v > 0)
    n = len(arr)
    if n == 0 or sum(arr) == 0:
        return 0.0
    cum = sum((2*(i+1) - n - 1) * v for i, v in enumerate(arr))
    return cum / (n * sum(arr))
