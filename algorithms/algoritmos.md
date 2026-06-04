# Algoritmos de Análise — MC859 PEPE Token

## Contexto

Três grafos direcionados e ponderados da rede de transações do token PEPE (Ethereum), correspondendo a três janelas temporais:

| Instância | Arquivo | Vértices | Arestas | Grau médio | Qtd SCC | Tam. maior SCC |
|---|---|---|---|---|---|---|
| Baseline | `Baseline.gexf` | 15.311 | 38.760 | 5,06 | 11.859 | 3.315 |
| Maduro | `Maduro_Total.gexf` | 22.799 | 111.380 | 9,77 | 16.929 | 5.756 |
| Khamenei | `Khamenei_Total.gexf` | 18.469 | 42.510 | 4,60 | 16.111 | 2.319 |

Eventos de choque: (A) sequestro de Nicolás Maduro em 03/01/2026 — janela 31/12–06/01; (B) assassinato de Ali Khamenei em 28/02/2026 — janela 25/02–03/03. Baseline: semana de 16/10–23/10/2025 (baixa volatilidade).

Atributos das arestas: `edge_weight` (volume de tokens), `block_timestamp`, `edge_id` (hash da transação), `gas_price`, `gas_used`.

---

## Ambiente de execução

**Rodar local.** Os grafos totalizam ~90MB e têm no máximo 22k vértices / 111k arestas — escala confortável para NetworkX em qualquer máquina moderna com ≥4GB de RAM. Colab não traz vantagem aqui (não há GPU envolvida) e adiciona fricção de upload/sessão.

```bash
pip install networkx pandas matplotlib scipy powerlaw
```

O notebook `MC859_pepe_token.ipynb` já está no repositório — continuar ali.

---

## Algoritmos — Tier 1 (fazer com certeza)

### 1. PageRank + Centralidade de Grau

**O que é:** PageRank atribui importância a cada vértice com base em quem aponta para ele e com que peso. Centralidade de grau (in-degree / out-degree) conta transações recebidas e enviadas por endereço.

**O que esperamos:** Identificar "baleias" — endereços que dominam o fluxo da rede. Durante eventos de choque, esperamos que poucos endereços concentrem uma fração desproporcional do volume (out-degree ponderado alto = grandes vendedores; in-degree alto = grandes compradores). Comparar o top-20 PageRank entre baseline e eventos pode revelar se há endereços que emergem especificamente durante crises (possíveis agentes informados).

**Hipótese:** O índice de concentração (ex: fração do volume total movimentada pelo top-1% de vértices) deve ser maior nos eventos de choque do que no baseline.

**Implementação:**
```python
import networkx as nx

G = nx.read_gexf("result/Maduro_Total.gexf")
pr = nx.pagerank(G, weight="edge_weight")
in_deg = dict(G.in_degree(weight="edge_weight"))
out_deg = dict(G.out_degree(weight="edge_weight"))
```

---

### 2. Distribuição de Grau (lei de potência)

**O que é:** Plotar o histograma de grau (in e out) em escala log-log e ajustar uma lei de potência P(k) ~ k^{-γ}.

**O que esperamos:** Redes de transações financeiras tipicamente seguem distribuição de cauda longa (scale-free). Esperamos confirmar esse padrão e comparar o expoente γ entre as três instâncias. Um γ menor indica cauda mais pesada — maior concentração em hubs — o que pode estar associado a períodos de alta atividade especulativa.

**Hipótese:** O expoente γ do grafo Maduro (maior volume, grau médio 9,77) deve ser menor que o do baseline, indicando emergência de hubs mais dominantes durante o choque.

**Implementação:**
```python
import powerlaw
import numpy as np

degrees = [d for _, d in G.in_degree()]
fit = powerlaw.Fit(degrees, discrete=True)
print(f"Expoente alpha: {fit.alpha:.3f}")
fit.plot_pdf(color='b', linewidth=2)
fit.power_law.plot_pdf(color='b', linestyle='--')
```

---

### 3. Estrutura Bow-Tie (expansão do SCC)

**O que é:** Decompor o grafo nos componentes: **SCC gigante** (nós que alcançam uns aos outros), **IN** (alcançam a SCC mas não são alcançados por ela), **OUT** (são alcançados pela SCC mas não alcançam), e **Tendrils/Tubes** (periféricos).

**O que esperamos:** A estrutura bow-tie é o modelo clássico de redes de transações. Durante choques, esperamos que o componente **OUT** cresça (muito dinheiro "saindo" sem retornar — possível fuga de capital) e que a proporção **IN** aumente (novos entrantes especulando). No baseline, esperamos estrutura mais equilibrada. Já temos `Qtd SCC` e `Tam. maior SCC` — esse é o próximo passo natural.

**Hipótese:** A razão `|OUT| / |IN|` deve ser maior nos eventos de choque, indicando fluxo direcional dominante (saída ou entrada líquida de capital).

**Implementação:**
```python
largest_scc = max(nx.strongly_connected_components(G), key=len)
scc_set = set(largest_scc)

# Nós que alcançam a SCC (forward BFS no grafo reverso)
G_rev = G.reverse()
reach_to_scc = set(nx.single_source_shortest_path_length(G_rev, next(iter(scc_set))).keys())
IN = reach_to_scc - scc_set

# Nós alcançáveis da SCC (forward BFS)
reach_from_scc = set(nx.single_source_shortest_path_length(G, next(iter(scc_set))).keys())
OUT = reach_from_scc - scc_set

TENDRILS = set(G.nodes()) - scc_set - IN - OUT
```

---

## Algoritmos — Tier 2 (recomendado se tiver tempo)

### 4. Análise Temporal (série temporal diária de métricas)

**O que é:** Dividir cada janela em sub-grafos por dia usando o atributo `block_timestamp` e plotar métricas (número de vértices ativos, arestas, grau médio, tamanho da maior SCC) ao longo do tempo.

**O que esperamos:** Detectar o momento exato em que a rede muda de comportamento em resposta ao evento. Esperamos um pico abrupto de atividade no dia D (evento) e decaimento nos dias seguintes, formando um perfil assimétrico. O baseline deve mostrar série estacionária sem picos.

**Hipótese:** O tamanho da maior SCC e o grau médio devem apresentar pico pronunciado no dia do evento geopolítico, com retorno gradual ao valor pré-choque em D+2 ou D+3.

**Implementação:**
```python
import pandas as pd

df = pd.read_csv("data/maduro_window_31-12_06-01.csv", parse_dates=["block_timestamp"])
df["date"] = df["block_timestamp"].dt.date

metrics = []
for date, group in df.groupby("date"):
    G_day = nx.from_pandas_edgelist(group, "source_node", "target_node",
                                    edge_attr="edge_weight", create_using=nx.DiGraph())
    sccs = list(nx.strongly_connected_components(G_day))
    metrics.append({
        "date": date,
        "nodes": G_day.number_of_nodes(),
        "edges": G_day.number_of_edges(),
        "largest_scc": max(len(s) for s in sccs),
    })
```

---

### 5. Coeficiente de Clustering (local e global)

**O que é:** Mede a proporção de triângulos fechados na vizinhança de cada vértice. Para grafos dirigidos, considera o sentido das arestas.

**O que esperamos:** Clustering alto em sub-redes específicas pode indicar wash trading (endereços trocando tokens entre si para inflar volume artificialmente) ou movimentação coordenada de grupos. Esperamos encontrar clustering mais alto em endereços de alto volume durante os eventos de choque.

**Hipótese:** Alguns hubs identificados no PageRank devem apresentar clustering local elevado, sugerindo atuação em circuitos fechados e não em modo "distribuidor" linear.

**Implementação:**
```python
# NetworkX usa grafo não-dirigido para clustering global; para dirigido:
clustering = nx.clustering(G.to_undirected(), weight="edge_weight")
avg_clustering = nx.average_clustering(G.to_undirected(), weight="edge_weight")
```

---

## Tier 3 — Bônus

### 6. Identificação de Hubs Anômalos

**O que é:** Cruzar o top-k por PageRank com o top-k por volume transacionado (soma de `edge_weight` nos arcos incidentes). Endereços presentes em ambos os rankings são candidatos a grandes agentes informados.

**O que esperamos:** Um conjunto pequeno de endereços que aparecem consistentemente no topo de ambas as métricas. Verificar se esses endereços aparecem **somente** nos grafos de evento (e não no baseline) reforçaria a hipótese de agentes que atuam oportunisticamente em janelas de choque.

---

## Algoritmos — Tier 2 (detecção de padrões)

> Adicionados após reflexão sobre o escopo de "detecção de padrões em grafos" exigido pelo PDD.
> Os algoritmos 1–4 são extração de conhecimento; os abaixo são detecção de padrão em sentido estrito.
> Louvain foi descartado: grafos scale-free com ~11k nós singleton produzem milhares de comunidades de tamanho 1, não interpretáveis. K-core, motifs e HITS são mais adequados para esta estrutura.

### 5. K-core Decomposition

**O que é:** Atribui a cada nó um número k = maior subgrafo onde todos os nós têm grau ≥ k. Detecta o padrão de "profundidade" na rede — quem é núcleo vs periferia.

**O que esperamos:** As whales identificadas no Alg.1 devem estar no k-core mais interno. Durante eventos, esperamos que o k-core máximo aumente (núcleo se adensa) ou que mais nós atinjam k alto. O perfil de distribuição dos k-cores muda entre baseline e eventos.

**Hipótese:** Os endereços exclusivos de eventos (candidatos a agentes informados) devem ter k-core maior que a mediana da rede, confirmando integração estrutural profunda — não são participantes esporádicos.

---

### 6. Análise de Motifs — Triângulos e Censo de Tríades

**O que é:** Conta padrões estruturais de tamanho 3 — triângulos fechados (A→B→C→A = ciclo), feed-forward loops, fan-in/fan-out. O censo de tríades (`nx.triadic_census`) classifica todos os padrões de 3 nós em 16 tipos.

**O que esperamos:** Triângulos fechados em redes de transação sugerem wash trading — circulação artificial de tokens entre contas coordenadas. Esperamos mais triângulos (ou maior coeficiente de clustering) nos eventos de choque, especialmente nos sub-grafos das whales.

**Hipótese:** O coeficiente de clustering local das whales identificadas no Alg.1 é significativamente maior que a mediana da rede, indicando que operam em circuitos fechados e não apenas como distribuidores lineares.

---

### 7. Detecção de Anomalia Estatística Formal

**O que é:** Usa as métricas diárias do Alg.4 (nós, SCC%, OUT/IN, vol IN→SCC, Gini) para construir uma distribuição de referência com o baseline e calcula o z-score de cada dia dos eventos. Dias com |z| > 2 são formalmente anômalos.

**O que esperamos:** O D-3 do Khamenei (10.818 nós, OUT/IN=0,09) deve aparecer como anomalia de múltiplos sigmas em várias métricas simultaneamente. O D-1 do Maduro (6.218 nós) deve ser anomalia em nós ativos mas não em Gini. Isso converte a análise visual do Alg.4 em detecção formal de padrão anômalo.

**Hipótese:** Cada evento deve ter pelo menos um dia com z-score > 3 em múltiplas métricas simultâneas — sinal de que o evento geopolítico causou ruptura estrutural, não apenas variação natural.

---

### 8. HITS — Hubs e Authorities

**O que é:** Algoritmo de Kleinberg para grafos dirigidos. Hubs = endereços que enviam para muitas autoridades; Authorities = endereços que recebem de muitos hubs. Complementa PageRank separando "distribuidores" de "acumuladores" de forma mais precisa.

**O que esperamos:** O sink `0xf977814e` (zero saídas, rank_in=3 em Maduro) deve ser a maior authority. Endereços bidirecionais como `0xeae7380d` (rank 2 em PageRank e volume) devem ter scores altos em ambos. O ranking de authorities deve separar carteiras frias de exchanges (recebem muito, pouco distribuem) de hubs de redistribuição.

**Hipótese:** Os top-10 de authority e hub são conjuntos majoritariamente distintos, revelando uma separação funcional clara na rede: acumuladores vs redistribuidores. Essa separação deve ser mais pronunciada nos eventos que no baseline.

---

## Tabela resumo completa

| # | Algoritmo | Categoria | Biblioteca | Resultado principal |
|---|---|---|---|---|
| 1 | PageRank + Centralidade de Grau | Extração de conhecimento | `networkx` | Ranking de baleias por janela |
| 2 | Distribuição de Grau (lei de potência) | Extração de conhecimento | `powerlaw` | Expoente γ, escala da rede |
| 3 | Estrutura Bow-Tie | Extração de conhecimento | `networkx` | Proporções IN/SCC/OUT, fluxo direcional |
| 4 | Série Temporal Diária | Extração de conhecimento | `pandas` + `networkx` | Curva de métricas por dia, picos |
| 5 | K-core Decomposition | **Detecção de padrão** | `networkx` | Profundidade estrutural, posição das whales |
| 6 | Motifs / Triângulos | **Detecção de padrão** | `networkx` | Wash trading, clustering local |
| 7 | Detecção de Anomalia Estatística | **Detecção de padrão** | `scipy` + `pandas` | Z-score por dia, dias formalmente anômalos |
| 8 | HITS (Hubs & Authorities) | **Detecção de padrão** | `networkx` | Separação acumuladores vs distribuidores |

**Ordem de implementação:** 1 → 2 → 3 → 4 (concluídos) → 5 → 6 → 7 → 8.
