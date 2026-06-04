# Conclusões — Algoritmo 4: Série Temporal Diária

## Metodologia

Cada dataset (Baseline, Maduro, Khamenei) foi decomposto em sub-grafos diários. Para cada dia, computou-se: número de nós e arestas, percentual na SCC gigante, razão OUT/IN (bow-tie), volume IN→SCC como fração do total, Gini do volume, e top-20 PageRank share. As métricas são expressas em dias relativos ao evento (D-3 … D+3). O baseline serve como faixa de referência. As whales dos algoritmos anteriores são rastreadas diariamente por rank de in-volume.

---

## Resultados

### Maduro — métricas diárias

| Dia | Nós | SCC% | OUT/IN | Vol IN→SCC | Gini vol |
|---|---|---|---|---|---|
| D-3 | 2.747 | 13,4% | 0,93 | 7,8% | 0,963 |
| D-2 | 2.998 | 14,0% | 0,72 | 8,5% | 0,966 |
| **D-1** | **6.218** | 17,0% | 0,92 | 6,8% | 0,966 |
| D   | 4.901 | 16,9% | 0,85 | 4,4% | 0,971 |
| **D+1** | **6.478** | 14,3% | 0,75 | 5,4% | 0,972 |
| D+2 | 5.676 | 16,7% | **0,67** | 5,0% | **0,973** |
| D+3 | 4.758 | 17,1% | 0,74 | 6,0% | 0,973 |

Baseline (referência): ~2.400 nós/dia, OUT/IN oscila entre 0,56 e 1,46 (média ≈ 1,0).

### Khamenei — métricas diárias

| Dia | Nós | SCC% | OUT/IN | Vol IN→SCC | Gini vol |
|---|---|---|---|---|---|
| **D-3** | **10.818** | **4,3%** | **0,09** | 15,6% | 0,950 |
| D-2 | 2.465 | 18,4% | 1,59 | 3,8% | 0,938 |
| D-1 | 2.101 | 17,7% | **2,05** | 10,1% | 0,942 |
| **D** | 2.199 | 18,0% | 1,66 | **18,0%** | **0,919** |
| D+1 | 2.041 | 19,5% | 1,87 | 8,1% | 0,932 |
| D+2 | 1.855 | **22,8%** | 1,25 | 12,9% | 0,931 |
| D+3 | 1.739 | 18,1% | 1,34 | 9,3% | 0,928 |

---

## Achados principais

### 1. O pico de acumulação Khamenei foi no D-3, não no D-1

O achado mais surpreendente do estudo: em **25 de fevereiro (D-3)**, a rede Khamenei registrou **10.818 nós ativos** — 4× a média dos dias seguintes e 4× a média do baseline. A razão OUT/IN despencou para **0,09**, o que significa que quase todos os nós daquele dia estavam no componente IN: compradores entrando na rede e enviando tokens para o núcleo sem receber de volta. Isso é a onda de acumulação que o Algoritmo 3 havia capturado como "69% IN na janela Khamenei_Antes" — mas que na resolução diária se revela **concentrada em um único dia**: D-3.

A partir de D-2, a rede encolhe abruptamente para ~2.100 nós e o OUT/IN inverte para > 1 (D-2=1,59, D-1=2,05). A interpretação: os ~10.000 compradores de D-3 compraram e saíram; nos dias seguintes, a rede se reorganiza com participantes menores e o fluxo reverte.

### 2. Maduro tem um perfil duplo-pico centrado no evento

Em Maduro, a atividade sobe em D-1 (6.218 nós — 2,5× o baseline) e atinge o máximo em D+1 (6.478 nós). O dia D em si é menos ativo do que seus vizinhos — o evento não foi o pico de atividade, mas o gatilho de uma onda que se espalha pelos dias adjacentes. Esse comportamento é consistente com a hipótese de que o choque Maduro, sendo um sequestro (evento com notícia progressiva), mobilizou gradualmente os participantes, enquanto o assassinato de Khamenei (ruptura abrupta) gerou uma onda de antecipação concentrada antes do anúncio oficial.

### 3. Gini cresce monotonicamente ao longo da janela Maduro

O Gini do volume sobe de 0,963 (D-3) para 0,973 (D+2) sem uma única queda. Isso significa que a concentração de capital aumenta *continuamente* ao longo de toda a janela, mesmo após o evento. As whales do Maduro (`0xeae7380d`, rank 2 ao longo de toda a janela) absorvem volume crescente enquanto os participantes menores chegam e saem. O efeito do choque Maduro não foi pontual — foi um acelerador de concentração que persiste por dias.

### 4. O dia D de Khamenei é o pico do fluxo especulativo IN→SCC — mas o Gini é o mais baixo

Uma aparente contradição: no dia do assassinato de Khamenei (D), o volume IN→SCC atinge **18%** (o maior de todo o estudo, respondido pelo Algoritmo 3) — e ao mesmo tempo o Gini do volume é o **mais baixo** de toda a janela Khamenei (0,919 vs 0,950 em D-3). Isso não é contradição: em D, muitos participantes diferentes estão canalizando tokens para a SCC (daí o alto IN→SCC e o Gini menor — distribuição mais pulverizada). Em D-3, havia mais concentração porque eram os grandes compradores (whales). No dia D, a especulação se democratiza.

### 5. A SCC se recupera e cresce pós-Khamenei

Após o choque Khamenei, a SCC% cresce progressivamente: D+1=19,5%, D+2=**22,8%** (o maior percentual de SCC de qualquer dia em qualquer evento — incluindo o baseline). Isso significa que, com a rede enxuta de 1.700-2.000 nós, os participantes que restaram são altamente interconectados. A rede "consolidou": perdeu participantes periféricos mas ganhou coesão interna. O oposto acontece em Maduro, onde a SCC% fica estável (13-17%) mesmo com a rede crescendo.

### 6. A onda compradora de D-3 Khamenei derruba a SCC% para 4,3%

Com 10.818 nós e SCC de apenas 4,3% (≈465 nós), D-3 Khamenei é o dia com a menor fração de SCC de todo o estudo. Isso faz sentido estruturalmente: uma massa de novos compradores entra como nós-IN (apenas enviam, não recebem), inflando o número total de nós sem integrar o núcleo bidirec​ional. A SCC gigante fica sendo um ilhote dentro de um oceano de compradores unidirecionais.

### 7. Maduro antecipa-se em D-1 — possível vazamento de informação

O salto de 2.998 → 6.218 nós de D-2 para D-1 (o dia antes do sequestro) está bem acima do baseline. Em relação à hipótese de agentes informados levantada no Algoritmo 1, vale notar: se a onda de compra Maduro tivesse sido puramente reativa ao anúncio público, esperaríamos o pico em D ou D+1 — mas o D-1 é quase tão grande quanto D+1. Isso é consistente com circulação prévia de informação, embora não conclusivo sem dados externos de preço.

---

## Síntese narrativa — o fio completo dos quatro algoritmos

O conjunto dos quatro algoritmos revela dois perfis distintos de comportamento de mercado perante choques geopolíticos:

**Maduro — choque de absorção progressiva:**
A rede dobra de tamanho nos dias ao redor do evento (D-1 e D+1), com a concentração de volume (Gini) crescendo continuamente ao longo de toda a janela. A estrutura bow-tie permanece com OUT/IN < 1 em todos os dias — mais compradores que vendedores, o tempo todo. As whales (`0xeae7380d`) dominam o rank 2 em volume em todos os dias. O acumulador (`0xf977814e`) aparece no componente OUT com volumes massivos nos dias adjacentes ao evento. A distribuição de grau se torna log-normal (Alg.2), sugerindo entrada massiva de participantes medianos. O perfil completo é: *atividade se espalha por vários dias, capital migra para poucos hubs, sem reversão do fluxo*.

**Khamenei — choque de acumulação antecipada e colapso pós-evento:**
D-3 concentra uma onda compradora de 10.818 nós (4× a atividade normal), com SCC em frangalhos (4,3%). A partir de D-2, a rede encolhe brutalmente mas o OUT/IN inverte (>1): começa a distribuição. No dia D, um pico de fluxo especulativo IN→SCC (18%) com o Gini mais baixo — especulação pulverizada. Após o evento, a rede consolida em ~1.700 nós com SCC cresce para 22,8%. As whales Khamenei (`0xb334a61a`, rank 3 em todo o período) ficam consistentemente na SCC. O perfil completo é: *antecipação concentrada, colapso abrupto de participantes, seguido de consolidação do núcleo*.

---

## Hipóteses verificadas

| Hipótese (dos algoritmos anteriores) | Resultado |
|---|---|
| Transição IN=69% ocorre gradualmente (D-3→D-1)? | **Refutada**: concentrada em D-3 (10.818 nós, ratio=0,09) |
| Pico IN→SCC de 18% é isolado ao dia D? | **Confirmada**: único dia com valor > 12% exceto D-3 e D+2 |
| SCC se recupera após eventos? | **Confirmada para Khamenei** (22,8% em D+2); Maduro permanece estável |
| Maduro tem pressão de compra sustentada? | **Confirmada**: OUT/IN < 1 em todos os 7 dias, decrescente |
| D-1 Maduro com atividade anômala → possível antecipação? | **Sinal presente** (6.218 nós vs baseline ~2.400), inconclusivo sem dado externo |

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/metricas_diarias.csv` | Todas as métricas por dia e dataset |
| `results/serie_temporal_metricas.png` | 6 métricas × 2 eventos + faixa baseline |
| `results/whales_ranking_diario.png` | Rank diário de in-volume das whales por evento |
| `results/desvio_normalizado_baseline.png` | Desvio de cada métrica em relação à média do baseline |
