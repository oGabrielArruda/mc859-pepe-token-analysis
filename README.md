# Análise Topológica da Rede de Transações do Token PEPE sob Choques Geopolíticos e de Mercado

Repositório do projeto da disciplina **MC859 — Projeto em Teoria da Computação (UNICAMP, 2026S1)**.
O estudo modela a rede de transferências do token **PEPE** (Ethereum) como um grafo direcionado e
ponderado e aplica algoritmos de **extração de conhecimento** e **detecção de padrões** para investigar
como a topologia da rede se reconfigura diante de choques externos.

O relatório final está em [`deliverables/report/`](deliverables/report/).

## Sobre o projeto

Transferências on-chain são modeladas como um multi-dígrafo ponderado (vértices = endereços,
arestas = transferências, peso = volume de PEPE). Comparam-se três janelas temporais:

1. **Baseline** — período de controle de baixa volatilidade (16–23/out/2025).
2. **Maduro** — sequestro de Nicolás Maduro, janela D−3…D+3 (31/dez/2025 a 06/jan/2026).
3. **Khamenei** — assassinato de Ali Khamenei, janela D−3…D+3 (25/fev a 03/mar/2026).

| Instância | Vértices | Arestas (multigrafo) | Maior SCC |
|---|---|---|---|
| Baseline | 15.311 | 38.760 | 3.315 |
| Maduro   | 22.799 | 111.380 | 5.756 |
| Khamenei | 18.469 | 42.510 | 2.319 |

## Algoritmos

**Extração de conhecimento:** (1) PageRank ponderado por volume, (2) distribuição de grau / lei de
potência, (3) decomposição bow-tie, (4) agregação temporal de métricas.
**Detecção de padrões:** (5) k-core, (6) motifs / censo de tríades, (7) detecção de anomalia via
z-score, (8) HITS (hubs e authorities).

> A proposta inicial previa detecção de comunidades (Louvain); optou-se por k-core, motifs e HITS,
> mais informativos em grafos com milhares de nós de grau 1 na periferia. Ver Seção 3 do relatório.

## Estrutura do repositório

```
data/                       CSVs extraídos do Google BigQuery (token_transfers) + preço CoinGecko
result/                     Grafos das três instâncias em formato .gexf
algorithms/
  NN_<nome>/
    run.py / run_gexf.py    Script do algoritmo (run_gexf.py opera sobre os grafos finais .gexf)
    conclusoes.md           Análise e interpretação dos resultados do algoritmo
    results/                CSVs e figuras gerados
  algoritmos.md             Visão geral e motivação dos algoritmos
deliverables/report/        Relatório final (LaTeX + PDF + figuras)
MC859_pepe_token.ipynb      Notebook de extração e construção inicial dos grafos
```

## Reprodução

Execução local (os grafos têm no máximo ~22k vértices; não requer GPU nem Colab):

```bash
pip install networkx pandas matplotlib scipy powerlaw
python3 algorithms/01_pagerank_centralidade/run_gexf.py
# ... e analogamente para os demais algoritmos
```

Os dados são extraídos do dataset público `bigquery-public-data.crypto_ethereum.token_transfers`
(ver query na Seção 2 do relatório) e os preços via CoinGecko (`data/pepe-usd-max.csv`).

## Autores

* **Gabriel Alves de Arruda** — RA: 248132
* **Guilherme Brentan de Oliveira** — RA: 252764

Disciplina MC859 Projeto em Teoria da Computação — Universidade Estadual de Campinas (UNICAMP).
