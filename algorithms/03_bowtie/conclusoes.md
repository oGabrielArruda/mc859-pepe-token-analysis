# Conclusões — Algoritmo 3: Estrutura Bow-Tie

## Metodologia

Decomposição bow-tie dos três grafos completos: SCC gigante (nós que se alcançam mutuamente), IN (enviam para a SCC mas não recebem de volta), OUT (recebem da SCC mas não retornam), OTHER (tendrils e desconectados). Volume entre componentes medido como fração do total. As whales são rastreadas em qual componente residem.

---

## Resultados

| Grafo | SCC % | IN % | OUT % | OTHER % | OUT/IN | Vol IN→SCC | Vol SCC→OUT |
|---|---|---|---|---|---|---|---|
| Baseline | 21,7% | 30,0% | 34,2% | 14,2% | 1,14 | 7,2% | 7,1% |
| Maduro | **25,2%** | 32,2% | 32,8% | 9,7% | **1,02** | 3,4% | 5,4% |
| Khamenei | 12,6% | **57,6%** | 21,6% | 8,2% | **0,38** | 3,6% | 3,5% |

### Componente das whales

| Whale | Baseline | Maduro | Khamenei |
|---|---|---|---|
| Maduro-Hub | SCC | SCC | SCC |
| Maduro-Sink | — | **OUT** | — |
| Maduro-Hub-2 | SCC | SCC | SCC |
| Khamenei-Antecipador | SCC | SCC | SCC |
| Khamenei-Hub | SCC | SCC | SCC |
| Khamenei-Hub-2 | SCC | SCC | SCC |

---

## Achados principais

### 1. O grafo Khamenei completo tem 57,6% IN — a maior fração de compradores de todo o estudo

No grafo completo Khamenei (7 dias inteiros), mais da metade de todos os nós estão no componente IN — endereços que enviaram tokens para o núcleo da rede mas nunca receberam de volta. Com OUT/IN = **0,38**, a assimetria direcional é extrema: para cada nó que recebe da SCC sem retornar (OUT), há 2,6 nós que enviam sem receber (IN). Esse valor de 0,38 é menos da metade do baseline (1,14) e sem paralelo em qualquer outro período.

Por que isso importa? O componente IN numa rede de transações representa fluxo unidirecional de capital entrando no núcleo — economicamente, isso é o equivalente a uma onda de compra ou depósito. A magnitude (57,6% de todos os nós) sugere que o evento Khamenei mobilizou uma massa desproporcional de endereços que realizaram *uma ou poucas transações* de envio e então cessaram a atividade. Isso é consistente com compradores de varejo reagindo ao choque: compram PEPE rapidamente (em DEX ou CEX), movimentando tokens para os hubs centrais, e não aparecem mais na cadeia naquele período.

A análise temporal (Alg.4) revelou que essa massa se concentrou especialmente no D-3, mas mesmo com os dias subsequentes (D-2 a D+3) incluídos, o grafo completo ainda mostra 57,6% IN — o pulso de D-3 domina a estrutura de toda a janela.

### 2. Maduro fortaleceu a SCC; Khamenei fragmentou-a

A fração de nós na SCC gigante segue padrão oposto nos dois eventos:
- Baseline: 21,7%
- Maduro: 25,2% (+3,5 p.p.)
- Khamenei: 12,6% (−9,1 p.p.)

O evento Maduro *densificou* o núcleo: mais endereços estabeleceram conexões bidirecionais, provavelmente por conta de múltiplas rodadas de compra e venda de arbitragistas e market-makers que permaneceram ativos durante os 7 dias. O resultado líquido foi uma SCC maior.

Khamenei produziu o oposto: com 57,6% de nós-IN (compradores unidirecionais), a SCC é diluída para 12,6% do total. A lógica é matemática — um nó só entra na SCC se tiver pelo menos uma rota de retorno. Compradores de varejo que chegam, enviam e saem nunca são incorporados à SCC. O evento Khamenei atraiu uma multidão de participantes que *usaram a rede como canal*, não como ecossistema.

### 3. Maduro-Sink no componente OUT — validação definitiva

`0xf977814e` aparece no componente **OUT** do grafo Maduro (in=4,36 trilhões, out=0). É o nó OUT com maior volume de in-flow de todos os grafos — recebe da SCC mas retorna zero. Sendo alcançável pela SCC (por isso está em OUT, não em OTHER), é um endpoint final de redistribuição: os hubs da SCC enviam para ele, mas ele não recicla para a rede. A combinação com k-core=1 (Alg.5) e auth_score alto (Alg.8) define o perfil completo: **vault ou cold wallet de custódia profissional** que serve como destino final de liquidação.

O fato de não aparecer no baseline (ou aparecer com volume muito menor) reforça que esse endereço foi *ativado pelo evento Maduro* — seja como destino de saques em escala de uma exchange, seja como acumulação estratégica de posição antes de liquidar.

### 4. OUT/IN equilibrado no Maduro — rede neutra em fluxo direcional

Maduro tem OUT/IN = 1,02 — quase exato equilíbrio. Isso é diferente do que os sub-grafos mostravam (variando de 0,67 a 1,01 ao longo dos dias): integrando os 7 dias, o Maduro praticamente equilibrou entradas e saídas. Houve muita movimentação, mas o capital líquido que saiu da SCC (SCC→OUT = 5,4%) foi comparável ao que entrou (IN→SCC = 3,4%).

O baseline, paradoxalmente, tem OUT/IN = 1,14 — ligeiramente acima de 1, indicando que em condições normais a rede PEPE tem pequeno excesso de distribuidores sobre compradores. O Maduro e o baseline são similares em fluxo direcional. O Khamenei é a exceção drástica (0,38).

### 5. A assimetria de componentes reflete a natureza dos choques

Olhando os dados conjuntamente, emerge uma hipótese sobre *por que* Maduro e Khamenei produziram estruturas bow-tie tão distintas:

O **sequestro de Maduro** foi um evento de incerteza prolongada — não havia clareza sobre o desfecho, o que motivou agentes profissionais (que permanecem na SCC por ficarem ativos ao longo de dias) a operar em ambas as direções. Daí a SCC maior e o equilíbrio IN/OUT.

O **assassinato de Khamenei** foi um choque abrupto e definitivo — gerou reação instantânea de massa (a onda de D-3), mas as condições se resolveram rapidamente. Os participantes que entraram não tinham estratégia de longo prazo — compraram, depositaram na CEX (componente OUT, possivelmente Binance como revelará o Alg.8) e encerraram a posição. Daí a SCC menor e a dominância IN.

---

## Síntese investigativa

A estrutura bow-tie dos grafos completos confirma e amplifica a narrativa que surgiu nos sub-grafos. Khamenei gerou o maior desequilíbrio IN vs OUT (0,38) e o maior percentual de compradores periféricos (57,6%) de todo o estudo. Maduro fortaleceu o núcleo (SCC de 25,2%) sem desequilíbrio direcional. São dois modelos opostos de como um choque geopolítico pode reorganizar a topologia de uma rede de ativos especulativos: o Maduro mostra que choques de incerteza sustentada podem *densificar* redes de trading; o Khamenei mostra que choques abruptos *inflamam temporariamente* a periferia da rede sem alterar seu núcleo.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_bowtie_gexf.csv` | Composição e razões por grafo |
| `results/whales_bowtie_gexf.csv` | Componente das whales por grafo |
| `results/report_bowtie_gexf.png` | Stacked bar composição + razão OUT/IN |
