# Conclusões — Algoritmo 8: HITS (Hubs & Authorities)

## Metodologia

Algoritmo HITS (Kleinberg, 1999) aplicado aos três grafos completos. Hubs = endereços que enviam para muitas authorities (distribuidores); Authorities = endereços que recebem de muitos hubs (acumuladores). O Gini dos scores captura a concentração de cada papel. Overlap = endereços no top-20 de ambos simultaneamente.

---

## Resultados

| Grafo | Gini Hub | Gini Auth | Overlap top-20 | Top-1 Hub | Top-1 Auth |
|---|---|---|---|---|---|
| Baseline | 0,975 | 0,829 | **0** | `0xdfd52…` | `0xa21c0…` |
| Maduro | **0,9999** | 0,768 | **2** | `0x301d9…` (score=1,0) | `0x663a5…` |
| Khamenei | **0,222** | **0,9997** | **0** | `0x06fd4…` | `0x28c6c…` (score=1,0) |

### HITS das whales

| Whale | Grafo | Rank Hub | Rank Auth | Papel |
|---|---|---|---|---|
| Maduro-Hub | Maduro | 469 | 22.082 | Hub |
| Maduro-Sink | Maduro | 11.265 | 4.410 | Auth |
| Khamenei-Antecipador | Maduro | **16** | 2.611 | Hub |
| Khamenei-Antecipador | Khamenei | 18.456 | 18.169 | — |
| Khamenei-Hub | Khamenei | 17.701 | 14.518 | — |

---

## Achados principais

### 1. O grafo Khamenei inverte completamente os papéis Hub/Authority

O resultado mais estruturalmente incomum do projeto: no grafo Khamenei, o **Gini Hub = 0,222** (muito baixo) e o **Gini Auth = 0,9997** (máximo). Isso é o inverso de todos os outros grafos, onde Gini Hub é sempre maior que Gini Auth.

O que isso significa? Em todos os outros contextos, a influência de *envio* (hub) está mais concentrada que a de *recebimento* (authority): um ou poucos endereços dominam os envios. No Khamenei isso se inverte: a *recepção* é ultra-concentrada (uma authority domina tudo com score=1,0), enquanto os *envios* são feitos por uma multidão de endereços com scores semelhantes (daí o baixo Gini).

A interpretação é direta: os 10.641 nós IN do grafo Khamenei (57,6% — Alg.3) são todos "hubs" de tamanho similar, pois cada um enviou um volume semelhante para a mesma authority. Uma massa de compradores, todos apontando para o mesmo destino. Isso cria uma estrutura de hub ultra-distribuída e uma authority ultra-concentrada — exatamente o oposto do baseline e do Maduro.

### 2. `0x28c6c06298d514db089934071355e5743bf21d60` — authority com score=1,0 no Khamenei

Esse endereço captura o score de authority máximo (1,0 normalizado) no grafo Khamenei. Em termos práticos: é o destino que maximiza a recepção de todas as outras authorities — o "ponto focal" para onde flui o maior peso de transações vindas de hubs. Na literatura de redes Ethereum, esse endereço (`0x28c6c062…`) é amplamente documentado como a **hot wallet da Binance** — o endereço de entrada principal da maior exchange centralizada do mundo.

Se essa identificação for correta, ela tem implicação direta para a interpretação do evento Khamenei: a onda de compra de D-3 (10.818 nós em um único dia — Alg.4) foi, em grande medida, uma onda de **depósitos na Binance**. Endereços individuais compraram PEPE em DEXs ou retiraram de outras fontes e depositaram na Binance. Isso explica:
- Por que o componente IN é tão grande (todos depositando)
- Por que a authority é ultra-concentrada (um único endereço de destino)
- Por que a transitivity é quase zero (clientes da Binance não transacionam entre si diretamente)

A questão que permanece aberta: esses depósitos eram para *vender* (o que geraria pressão vendedora) ou para *comprar mais* (especulação de alta)? Sem dados de preço do período exato, ambas as hipóteses são compatíveis com a estrutura observada.

### 3. `0x301d9bc22d66f7bc49329a9d9eb16d3ecc4a12b4` — hub com score=1,0 no Maduro

Esse endereço domina absolutamente o score de hub no grafo Maduro, presente como top-1 hub com score=1,0. Um hub de score=1,0 significa que maximiza o somatório de authorities que recebe — é o endereço que conecta sistematicamente para os maiores acumuladores da rede.

O perfil (alto hub, baixo authority, aparece exclusivamente nos períodos Maduro) é consistente com um **aggregador de liquidez ou roteador de DEX** — um smart contract intermediário que direciona tokens de entrada para múltiplos destinos (liquidity pools, vaults, outros contratos). Sua ausência no baseline e no Khamenei sugere que foi *especificamente ativado* pelo padrão de trading do evento Maduro.

Por que esse roteador é mais ativo no Maduro e não no Khamenei? Uma hipótese: durante o Maduro, havia mais atividade bidirecional e arbitragem (confirmada pelos 5.601 triângulos e 1.865 tríades 030T do Alg.6), o que aciona roteadores de liquidez. No Khamenei, dominado por compra unidirecional simples, o roteamento sofisticado é desnecessário.

### 4. Overlap top-20 = 0 no baseline e Khamenei, mas 2 no Maduro

A separação funcional entre distribuidores e acumuladores é quase absoluta: no baseline e no Khamenei, nenhum endereço aparece simultaneamente no top-20 de hubs E authorities. No Maduro, **2 endereços** quebram essa regra — são "generalistas" que exercem ambos os papéis com significância.

Esses 2 generalistas do Maduro são endereços que recebem de hubs (authority) E enviam para authorities (hub) — ou seja, intermediários puros, que compram e vendem de forma suficientemente simétrica para aparecer nos dois rankings. O equivalente de um market-maker: compra de um lado, vende para o outro. O fato de aparecerem apenas no Maduro (e não no baseline ou Khamenei) reforça que o evento Maduro ativou comportamento de market-making que normalmente não está tão visível na cadeia.

### 5. Khamenei-Antecipador: rank_hub=16 no Maduro, rank 18.456 no Khamenei

`0xb334a61a` tem rank de hub extremamente baixo (=16, top-20) no grafo Maduro, mas não aparece entre os principais hubs no grafo Khamenei — onde seria esperado ser proeminente. Esse resultado é aparentemente contra-intuitivo: o endereço que identificamos como "antecipador do Khamenei" não domina como hub no próprio grafo Khamenei?

A explicação está no mecanismo do HITS: no grafo Khamenei, os hubs são os 10.641 compradores periféricos de score similar — o HITS distribui o score de hub entre eles de forma homogênea (daí Gini_hub=0,222). Um único endereço com alto volume mas que também *recebe* muito (como `0xb334a61a` com rank_in=5) tende a ter score de authority mais alto que de hub. Com score de authority alto mas não top-20, e score de hub mediano, o endereço "desaparece" dos extremos.

No Maduro, por outro lado, o mecanismo é diferente: os hubs são mais heterogêneos (Gini_hub=0,9999), e `0xb334a61a` como endereço ativo no período aparece entre os 16 maiores distribuidores. Isso sugere que no Maduro ele operou mais como distribuidor (hub), enquanto no Khamenei operou mais como receptor intermediário — consistente com o perfil de exchange que redistribui liquidez conforme o contexto.

---

## Síntese investigativa

O HITS com grafos completos revelou a inversão mais dramaticamente clara do projeto: Khamenei inverte os papéis fundamentais de hub e authority em relação a todos os outros grafos. A ultra-concentração de authority no Khamenei (score=1,0 para o provável endereço da Binance) e a distribuição homogênea de hubs (Gini=0,222) são a assinatura funcional de um evento de *massa comprando via CEX* — muitos distribuidores iguais, um acumulador dominante.

O Maduro mostra o polo oposto: um único hub absoluto (score=1,0) com authorities mais distribuídas (Gini=0,768). É a assinatura de um *roteador profissional de liquidez* centralizando a distribuição para vários destinos — um padrão de mercado sofisticado, não de varejo.

Esses dois perfis HITS opostos são a síntese funcional de tudo que os algoritmos anteriores revelaram sobre os dois eventos: Maduro foi dominado por agentes sofisticados e bidirecionais; Khamenei foi dominado por compradores de varejo unidirecionais.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_hits_gexf.csv` | Gini hub/auth e overlap por grafo |
| `results/whales_hits_gexf.csv` | Rank e papel das whales em cada grafo |
| `results/exclusivos_hits_gexf.csv` | Tops exclusivos de eventos vs baseline |
| `results/top_hubs_*_gexf.csv` | Top-20 hubs por grafo |
| `results/top_auths_*_gexf.csv` | Top-20 authorities por grafo |
| `results/report_hits_gexf.png` | Gini hub vs auth + scatter whales |
