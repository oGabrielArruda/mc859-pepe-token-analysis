# Conclusões — Algoritmo 6: Motifs — Triângulos e Censo de Tríades

## Metodologia

Contagem de triângulos (projeção não-dirigida), coeficiente de clustering global (transitivity), clustering médio ponderado e censo completo de tríades dirigidas sobre os três grafos completos. Tríades de interesse: 030C (ciclo A→B→C→A), 300 (triângulo bidirecional completo, todas as 6 arestas), 030T (feed-forward). Clustering local das whales identificado individualmente.

---

## Resultados

| Grafo | Triângulos | Nós em tri (%) | Transitivity | 030C | 300 | 030T |
|---|---|---|---|---|---|---|
| Baseline | 1.935 | 7,3% | 0,00209 | 441 | 78 | 627 |
| Maduro | **5.601** | **8,8%** | 0,00179 | 504 | **494** | **1.865** |
| Khamenei | 1.605 | 3,9% | **0,00011** | 209 | 78 | 580 |

---

## Achados principais

### 1. Maduro triplicou os triângulos: de 1.935 para 5.601 (+190%)

O grafo Maduro tem quase três vezes mais triângulos que o baseline. Como o grafo Maduro tem apenas 1,5× mais nós e 1,9× mais arestas únicas, o aumento de triângulos não é proporcional ao crescimento da rede — há uma aceleração não-linear na formação de estruturas triangulares. Triângulos surgem quando A conecta com B, B conecta com C, e C conecta com A — ou seja, quando há *circuitos fechados de troca*.

O que gera esses circuitos adicionais? Existem dois mecanismos plausíveis, não mutuamente exclusivos:

**Mecanismo 1 — Arbitragem entre DEXs:** Durante alta volatilidade (evento Maduro), arbitragistas compram em uma DEX e vendem em outra, criando circuitos A→B→C→A entre contratos de DEX. Esses circuitos são exatamente triângulos na rede de transações.

**Mecanismo 2 — Wash trading ou liquidez sintética:** Grupos pequenos de endereços trocam tokens entre si para sustentar preço ou aparência de liquidez. Cada rodada de troca cria um triângulo no grafo agregado do período.

Os dados não permitem distinguir entre os dois mecanismos sem informação externa de preço e DEX. Mas o achado — triângulos quase triplicam especificamente no Maduro, e retornam ao nível do baseline no Khamenei — é um sinal forte de que o evento Maduro ativou algum desses comportamentos de forma específica.

### 2. Tríades 300 explodem de 78 para 494 no Maduro (+534%)

O tipo de tríade 300 — onde A↔B, B↔C e A↔C (todas as 6 arestas dirigidas presentes) — salta de 78 no baseline para **494 no Maduro** (+534%), e volta para 78 no Khamenei. A tríade 300 é o padrão mais completo de ciclo bidirecional entre três agentes: cada par troca em ambas as direções.

Esse aumento não pode ser explicado apenas por mais arestas: o grafo Maduro tem 1,9× mais arestas que o baseline, mas 6,3× mais tríades 300. O crescimento é desproporcionalmente concentrado nesse padrão específico. A tríade 300 é a "impressão digital" de um grupo coeso de agentes que comercializam intensamente entre si — seja por arbitragem, seja por coordenação.

O retorno ao nível do baseline (78) no Khamenei é igualmente revelador: o evento Khamenei, apesar de ter mais arestas que o baseline (23.190 vs 20.478), não gerou mais tríades 300. Isso é mais um indicador de que os participantes do Khamenei eram predominantemente *unidirecionais* (compradores), enquanto os do Maduro incluíam agentes com comportamento *bidirecional e cíclico*.

### 3. Transitivity do Khamenei cai para 0,00011 — próximo de zero absoluto

A transitivity do grafo Khamenei (0,00011) é **19× menor** que a do baseline (0,00209) e **16× menor** que a do Maduro (0,00179). Esse valor está próximo do que se esperaria de uma rede aleatória com os mesmos parâmetros — a rede Khamenei, em termos de clustering global, é virtualmente indistinguível de um grafo aleatório.

Por que isso acontece? A transitivity mede a fração de triângulos possíveis que estão fechados. Com 81,9% dos nós em k=1 (Alg.5) e 57,6% no componente IN (Alg.3), a rede Khamenei é dominada por nós que conectam com apenas uma ou duas contrapartes e não participam de ciclos. Matematicamente, nós de grau 1 contribuem zero triângulos. Uma rede onde a maioria esmagadora dos nós tem grau efetivo 1 terá transitivity necessariamente próxima de zero, independentemente do que acontece no núcleo.

O fato de 3,9% dos nós do Khamenei participarem de triângulos (vs 7,3% no baseline e 8,8% no Maduro) confirma que a atividade cíclica é um fenômeno de nicho no Khamenei, restrito ao núcleo SCC (12,6% dos nós), não uma característica geral da rede.

### 4. Khamenei-Antecipador tem clustering=0 em TODOS os grafos — padrão exchange confirmado

`0xb334a61a` tem clustering local = 0 no baseline, no Maduro e no Khamenei, apesar de estar no k_max do grafo Khamenei. Esse resultado, que poderia parecer contraditório — como um nó pode ser k=8 (muito conectado) mas ter clustering=0? — é matematicamente consistente e estruturalmente revelador.

Um nó pode ter alto k-core com clustering=0 se seus vizinhos nunca se conectam entre si. Na projeção não-dirigida, esse endereço conecta com muitos outros (132 vizinhos únicos no grafo Khamenei), mas nenhum par desses 132 vizinhos transaciona diretamente entre si. Cada um dos 132 contatos desse endereço é uma contraparte isolada que *só aparece na rede por meio desse endereço*.

Esse é o padrão de **estrela pura**: um hub central ligado a satélites que não se conhecem. É estruturalmente idêntico ao funcionamento de uma exchange centralizada (CEX): todos os clientes da exchange interagem *com a exchange*, mas não entre si diretamente. Cada depósito e saque na CEX aparece como uma aresta no grafo de transações, mas os clientes não são visíveis como pares.

### 5. Feed-forward dominante em todos os grafos — padrão de cascata hierárquica

O tipo 030T (feed-forward: A→B, A→C, B→C — alguém envia para dois destinos, e um desses envia para o outro) é consistentemente mais frequente que os ciclos 030C em todos os grafos. No Maduro: 030T=1.865 vs 030C=504. Esse padrão descreve o fluxo *em cascata hierárquica* da rede: um agente distribui para dois, e um desses redistribui para o outro. É o modelo de como exchanges distribuem liquidez — sell orders cascateando entre níveis de participantes.

---

## Síntese investigativa

A análise de motifs com grafos completos produziu resultados mais dramáticos e mais interpretáveis do que com sub-grafos. O Maduro emerge como o período de maior atividade cíclica e coordenada (5.601 triângulos, 494 tríades-300). O Khamenei é a antítese: baixíssima conectividade cíclica, transitivity quase nula, dominado por fluxo unidirecional. O Maduro parece ter ativado estratégias de arbitragem ou trading cíclico entre profissionais; o Khamenei ativou principalmente compra de varejo em modo unidirecional. Essa distinção entre *tipo de participante* mobilizado por cada evento é central para entender por que as estruturas de grafo divergem tanto entre os dois choques.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_motifs_gexf.csv` | Triângulos, transitivity, censo de tríades |
| `results/whales_motifs_gexf.csv` | Clustering local das whales |
| `results/report_motifs_gexf.png` | Triângulos, transitivity e % em triângulo |
