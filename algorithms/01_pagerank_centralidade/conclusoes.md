# Conclusões — Algoritmo 1: PageRank + Centralidade de Grau

## Metodologia

Análise realizada sobre os três grafos direcionados e ponderados completos (`.gexf`): Baseline (15.311 nós / 38.760 arestas brutas), Maduro (22.799 / 111.380) e Khamenei (18.469 / 42.510). Após conversão de MultiDiGraph para DiGraph simples com soma de pesos por par (source, target), os grafos resultantes têm 20.478, 38.576 e 23.190 arestas únicas, respectivamente. Para cada grafo calculou-se PageRank ponderado por `edge_weight`, ranking de in/out volume, Gini dos scores, e top-20 share.

---

## Resultados

| Grafo | Nós | Arestas únicas | Gini PR | Gini Vol | Top-20 Vol | Overlap PR∩Vol |
|---|---|---|---|---|---|---|
| Baseline | 15.311 | 20.478 | 0,677 | 0,983 | 41,2% | 12 |
| Maduro | 22.799 | 38.576 | 0,698 | **0,992** | **53,1%** | 14 |
| Khamenei | 18.469 | 23.190 | **0,770** | 0,989 | 46,7% | 13 |

### Posição das whales nos grafos completos

| Whale | Grafo principal | rank_in_vol | rank_out_vol | PR rank |
|---|---|---|---|---|
| Maduro-Hub (`0xeae7…`) | Maduro | **2** | **2** | **2** |
| Maduro-Sink (`0xf977…`) | Maduro | 6 | 16.964 | 8 |
| Maduro-Hub-2 (`0xfbd4…`) | Maduro | 11 | 11 | 14 |
| Khamenei-Antecipador (`0xb334…`) | Khamenei | **5** | **6** | **3** |
| Khamenei-Hub (`0xeb9c…`) | Khamenei | 24 | 22 | 27 |

---

## Achados principais

### 1. Khamenei concentra mais influência estrutural; Maduro concentra mais capital

O Gini de PageRank no grafo Khamenei (0,770) supera o de Maduro (0,698) e o baseline (0,677). Isso indica que a *influência de rede* — medida pela estrutura de quem aponta para quem — está mais concentrada no Khamenei. Porém, o Gini de volume em Maduro (0,992) supera o de Khamenei (0,989): o *capital financeiro* fluiu de forma mais concentrada durante o Maduro.

A distinção é relevante: eventos de choque podem aumentar concentração de influência (Khamenei) sem necessariamente aumentar proporcionalmente a concentração financeira — ou vice-versa. No Khamenei, poucos endereços dominam a estrutura da rede; no Maduro, poucos endereços dominam o volume. São duas formas distintas de concentração de poder numa rede financeira.

### 2. Maduro dobrou o volume financeiro concentrado no topo

O top-20 de volume salta de 41,2% no baseline para 53,1% no Maduro (+11,9 p.p.). No Khamenei o aumento é menor (46,7%, +5,5 p.p.). Isso é consistente com o perfil que se confirmará nos algoritmos subsequentes: o evento Maduro foi um evento de *concentração financeira*, enquanto o Khamenei foi um evento de *concentração estrutural* com mais participantes dispersos em termos de volume.

Por que a diferença? Uma hipótese é que o sequestro de Maduro gerou reação mais dirigida — traders profissionais e grandes posições se movendo coordenadamente. O assassinato de Khamenei, por ser um choque mais abrupto e inesperado, atraiu reação mais pulverizada (mais pequenos investidores), diluindo a concentração financeira absoluta mesmo que concentrando a estrutura de rede.

### 3. Maduro-Sink: rank_in=6 com rank_out=16.964 — a assimetria mais extrema do estudo

No grafo completo do Maduro, `0xf977814e` recebe como o 6º maior endereço em volume (4,36 trilhões de tokens) mas envia como o 16.964º — praticamente zero saídas em um grafo de 22.799 nós. Nenhum outro endereço no top-10 de in-volume tem rank de out-volume acima de 1.000. Essa assimetria extrema de rank_in vs rank_out é a assinatura operacional de uma **cold wallet de exchange** ou **vault de custódia**: recebe de múltiplas fontes, nunca redistribui na cadeia. O fato de aparecer especificamente no evento Maduro — e não no baseline ou Khamenei com a mesma magnitude — sugere que o fluxo para essa custódia foi extraordinário durante aquele período, possivelmente relacionado a saques em escala de uma plataforma centralizada.

### 4. Khamenei-Antecipador: top-5 em volume E top-3 em PageRank no grafo Khamenei

`0xb334a61a` tem rank_in=5 (volume) e PR_rank=3 no grafo completo Khamenei. No grafo Maduro, o mesmo endereço cai para rank_in=22 e PR_rank=66 — ainda relevante, mas fora do topo. No baseline, é rank_in=29. O padrão é claro: esse endereço é *especificamente* proeminente no Khamenei, não em geral. Combinado com os resultados de K-core (Alg.5) e Bow-Tie (Alg.3), que mostrarão esse endereço no núcleo mais profundo do grafo Khamenei, o perfil aponta para um agente ou plataforma que sistematicamente concentrou atividade durante aquele evento específico.

### 5. O overlap PR∩Vol aumenta de 12 (baseline) para 13–14 nos eventos

O número de endereços que aparecem simultaneamente no top-20 de PageRank E top-20 de volume sobe ligeiramente nos eventos. Isso indica que, durante choques, a estrutura de rede e o volume financeiro alinham-se mais: quem é influente também move mais dinheiro. No baseline, é mais comum que influência e volume estejam em endereços diferentes (exchanges, por exemplo, têm alto PR mas volume não necessariamente entre os mais altos). Nos choques, os grandes operadores financeiros assumem também o papel de hubs de rede.

---

## Síntese investigativa

Por que o PageRank de Khamenei é mais concentrado, mas o volume de Maduro é mais concentrado? A resposta provavelmente está na *composição de participantes*: Khamenei atraiu uma massa de compradores novos (que vai aparecer como 57% IN no Alg.3) que enviaram tokens para poucos endereços de destino, tornando esses destinos muito influentes (PageRank alto). Maduro, por outro lado, concentrou volume bruto em fewer players, mas a rede foi mais conectada ao longo do evento. Os dois perfis revelam tipos diferentes de choque: Khamenei = compra unidirecional por muitos → concentração de influência. Maduro = movimentação bilateral de grandes agentes → concentração de capital.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_pagerank.csv` | Gini, Top-20 share e overlap por grafo |
| `results/whales_pagerank.csv` | Rank e volume das whales em cada grafo |
| `results/exclusivos_evento.csv` | Endereços no overlap PR∩Vol exclusivos dos eventos |
| `results/top_pr_*.csv` | Top-20 PageRank por grafo |
| `results/top_vol_*.csv` | Top-20 volume por grafo |
| `results/report_pagerank_concentracao.png` | Gini e Top-20 share comparativo |
