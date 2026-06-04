# Conclusões — Algoritmo 5: K-core Decomposition

## Metodologia

K-core calculado sobre a projeção não-dirigida de cada grafo completo. O número k de um nó é o maior k tal que ele pertence ao subgrafo maximal onde todos têm grau ≥ k. Métricas: k_max, k_median, % em k=1 (periferia pura), volume médio por nível de k-core.

---

## Resultados

| Grafo | Nós | k_max | k_median | k=1 (%) | n no k_max |
|---|---|---|---|---|---|
| Baseline | 15.311 | 8 | 1,0 | 71,5% | 64 |
| Maduro | 22.799 | **10** | 1,0 | 51,9% | 73 |
| Khamenei | 18.469 | 8 | 1,0 | **81,9%** | 54 |

### K-core das whales

| Whale | Baseline | Maduro | Khamenei | Interpretação |
|---|---|---|---|---|
| Maduro-Hub | k=5 (99,2%) | **k=9 (99,7%)** | k=6 (99,4%) | Núcleo profundo, amplificado no Maduro |
| Maduro-Sink | — | **k=1 (51,9%)** | — | Periferia pura — zero integração bidirecional |
| Maduro-Hub-2 | k=7 (99,6%) | k=7 (99,1%) | k=6 (99,4%) | Estável no núcleo interno |
| Khamenei-Antecipador | k=5 (99,2%) | k=9 (99,7%) | **k=8=k_max (100%)** | Núcleo máximo no evento Khamenei |
| Khamenei-Hub | k=2 (95,3%) | k=4 (97,3%) | k=3 (97,7%) | Camada interna mas não máxima |
| Khamenei-Hub-2 | k=2 (95,3%) | k=4 (97,3%) | k=3 (97,7%) | Idem |

---

## Achados principais

### 1. Maduro elevou o k_max de 8 para 10 — o evento mais profundo estruturalmente

O núcleo mais interno do grafo Maduro tem k=10 (vs. k=8 no baseline). Isso significa que existem 73 endereços no grafo Maduro que têm pelo menos 10 vizinhos mútuos na projeção não-dirigida — uma integração recíproca extrema. Para atingir k=10, cada membro do k-core precisa ter conexões com pelo menos outros 10 membros do mesmo grupo; é uma estrutura de clique quase-completa.

Por que o Maduro aprofundou o núcleo? Com 7 dias de atividade intensa (22.799 nós, 38.576 arestas únicas), os agentes mais ativos — exchanges, market-makers, DEXs — acumularam conexões com múltiplos parceiros de forma suficientemente densa para elevar o k_max. O Maduro, ao atrair mais volume e mais transações únicas, permitiu que o núcleo existente *adensasse suas conexões internas*.

### 2. Khamenei tem 81,9% dos nós em k=1 — o mais periférico dos três grafos

Mais de 4 em cada 5 nós do grafo Khamenei têm k-core = 1. No baseline, são 71,5%; no Maduro, 51,9%. Esse resultado é a tradução estrutural direta da descoberta do Alg.3: os 57,6% de nós IN (compradores unidirecionais) são majoritariamente k=1 — transacionaram com uma única contraparte e pararam. Nós k=1 são os "folhas" da rede: conectados por exatamente uma relação, sem integração ao núcleo.

Isso tem uma implicação importante para a interpretação do evento Khamenei: a atividade observada (18.469 nós, 42.510 transações) foi *superficialmente ampla mas estruturalmente rasa*. Muitos participantes, mas poucos com integração genuína. O evento mobilizou varejo, não profissionais.

### 3. Khamenei-Antecipador está no k_max=8 do grafo Khamenei — percentil 100%

`0xb334a61a` está literalmente no grupo de 54 endereços que formam o núcleo mais interno do grafo Khamenei completo. Com percentil 100%, não existe nenhum outro nó mais integrado na rede durante o período Khamenei. Combinando com rank_in=5 (Alg.1), PR_rank=3 (Alg.1), SCC em todos os grafos (Alg.3), e clustering=0 (Alg.6), o quadro estrutural é inequívoco: é um **hub de estrela pura** no núcleo máximo — um endereço que conecta diretamente com muitos outros, sem que esses outros se conectem entre si. Esse é exatamente o padrão de uma exchange ou aggregador de liquidez: o ponto central que interliga compradores e vendedores que não se conhecem.

A questão que permanece aberta é: por que esse endereço específico domina no Khamenei mas não com a mesma magnitude no Maduro? A análise HITS (Alg.8) tentará responder.

### 4. Maduro-Sink confirmado como k=1 no grafo Maduro

`0xf977814e` tem k=1 no grafo completo Maduro. Isso é matematicamente necessário dado que ele tem zero arestas de saída: na projeção não-dirigida, cada aresta para ele se torna uma aresta sem direção, mas se ele não tem saídas, seus únicos vizinhos são os que enviaram para ele — e esses vizinhos provavelmente não se conectam entre si (afinal, são de fontes diversas enviando para o mesmo destino). Sem ciclos fechados, k=1.

O fato de k=1 coexistir com rank_in=6 (volume enorme) é o caso mais extremo de dissociação entre *relevância financeira* e *integração estrutural* em todos os dados. É possível ser o 6º maior receptor de volume da rede e ao mesmo tempo ser o nó com menor nível de integração possível. Isso só acontece quando um endereço é um *sink terminal* — relevante pelo que acumula, irrelevante pela estrutura que gera.

### 5. Volume escala super-linearmente com k-core em todos os grafos

Em todos os três grafos, o volume médio por nível de k-core cresce mais que linearmente — virtualmente de forma exponencial — à medida que k aumenta. O nó médio de k=10 no grafo Maduro move ordens de magnitude mais volume que o nó médio de k=1. Isso confirma que estar no núcleo da rede não é acidente: é a consequência de processos de ligação preferencial que fazem os mesmos endereços acumularem tanto conexões quanto volume.

Para o projeto, isso valida a escolha dos algoritmos de centralidade (Alg.1): os endereços que dominam em PageRank e volume são os mesmos que dominam em k-core. As três métricas convergem para identificar os mesmos agentes, o que fortalece a robustez das conclusões.

---

## Síntese investigativa

O K-core revela a *arquitetura de profundidade* das três redes. Maduro aprofundou o núcleo (k_max 8→10), criando um grupo ainda mais integrado de agentes de alta frequência. Khamenei saturou a periferia (81,9% em k=1) sem necessariamente fortalecer o núcleo existente (k_max mantido em 8). Os dois eventos perturbaram a rede em dimensões opostas: Maduro na profundidade, Khamenei na largura. Essa assimetria de perturbação — profundidade vs. largura — é uma das descobertas estruturais mais claras do projeto.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_kcore_gexf.csv` | k_max, k_median, distribuição por grafo |
| `results/whales_kcore_gexf.csv` | K-core e percentil das whales |
| `results/report_kcore_gexf.png` | Histograma k-core (3 grafos) |
| `results/report_volume_kcore_gexf.png` | Volume médio por nível k-core |
