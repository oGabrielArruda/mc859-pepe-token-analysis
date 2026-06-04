# Conclusões — Algoritmo 2: Distribuição de Grau (Lei de Potência)

## Metodologia

Lei de potência P(k) ~ k^{-α} ajustada ao in-degree e out-degree (contagem de contrapartes únicas) e ao volume ponderado para os três grafos completos. O parâmetro α e o xmin são estimados por máxima verossimilhança. O valor R (razão de log-verossimilhança) compara lei de potência contra log-normal: R > 0 favorece lei de potência; R < 0 favorece log-normal.

---

## Resultados

| Grafo | α in-deg | α out-deg | α in-vol | R_in (PL vs LN) | R_out |
|---|---|---|---|---|---|
| Baseline | **1,976** | 1,833 | 1,433 | −0,02 ≈ 0 | −0,39 |
| Maduro | 2,719 | **2,943** | 1,402 | **+3,68** | −193,4 |
| Khamenei | 2,399 | 1,972 | 1,352 | −10,25 | −6,63 |

---

## Achados principais

### 1. Baseline é o único grafo genuinamente scale-free — e com o expoente teórico clássico

O in-degree do grafo baseline tem α = **1,976** e R ≈ 0 (lei de potência e log-normal são estatisticamente indistinguíveis). Esse valor é notavelmente próximo de α = 2,0, o expoente previsto pelo modelo de Barabási-Albert para redes de crescimento preferencial — a teoria que explica por que a internet, redes sociais e redes financeiras convergem para estruturas scale-free. A rede PEPE em equilíbrio se comporta exatamente como a teoria prediz: um processo de "os ricos ficam mais ricos" onde endereços com mais conexões atraem desproporcionalmente mais transações.

Isso também tem implicação prática: o baseline é a *distribuição nula* contra a qual devemos comparar os eventos. Um grafo genuinamente scale-free tem propriedades bem conhecidas — vulnerabilidade a ataques direcionados a hubs, robustez a falhas aleatórias, e small-world behavior. Os desvios observados nos eventos são desvios em relação a esse estado "natural" da rede.

### 2. Maduro: in-degree segue lei de potência melhor que log-normal (R = +3,68)

No grafo Maduro, o R de in-degree é **positivo (+3,68)** — o único caso em todo o estudo onde a lei de potência é *preferida* sobre a log-normal. Isso é contraintuitivo à primeira vista: por que um evento de choque tornaria a distribuição *mais* compatível com lei de potência?

A explicação provável é a **amplificação de hubs existentes**. Durante o Maduro, os endereços já proeminentes (exchanges, DEXs, grandes traders) receberam volume ainda mais desproporcional — exatamente o mecanismo de ligação preferencial que gera lei de potência. A cauda longa ficou *mais pesada*, não mais dispersa. Os novos participantes continuaram chegando por "ligação preferencial" — enviando para os mesmos grandes hubs — o que reforça a estrutura de lei de potência em vez de diluí-la.

### 3. Maduro: out-degree com α = 2,943 e R = −193 — uma distribuição fundamentalmente diferente

O resultado mais extremo do algoritmo: no grafo Maduro, o out-degree tem R = **−193,4** (log-normal é overwhelmingly melhor que lei de potência) e α = 2,943 (cauda leve). Isso cria uma assimetria interna dramática no mesmo grafo: in-degree scale-free (lei de potência com α < 2), out-degree fundamentalmente não-scale-free.

O que isso significa? Quem *recebe* segue lei de potência — há hubs de recepção ultra-dominantes (o Maduro-Sink com rank_in=6 e 4,36 trilhões de tokens). Mas quem *envia* segue distribuição muito mais homogênea — muitos endereços enviando quantidades parecidas. Maduro foi um evento de **consolidação assimétrica**: capital disperso sendo canalizado para poucos acumuladores, mas sem um único "super-distribuidor" equivalente no lado de saída.

### 4. Khamenei: log-normal domina em ambas as dimensões — rede estruturalmente diferente

No grafo Khamenei, R_in = −10,25 e R_out = −6,63 (log-normal muito melhor em ambos). Isso indica que o Khamenei gerou uma distribuição de grau *nem scale-free nem concentrada no out-degree* — mais próxima do que um modelo de rede aleatória produziria. Por quê?

A hipótese mais coerente com os demais algoritmos: os 10.641 nós IN do grafo Khamenei (57,6% de todos os nós — ver Alg.3) eram participantes esporádicos com distribuição de grau muito homogênea — cada um transacionou com 1–3 contrapartes. Essa massa de nós periféricos "normaliza" a distribuição global, diluindo a cauda longa que os hubs criam. Quando 81,9% dos nós têm k-core = 1 (Alg.5), o grau médio da distribuição é puxado para baixo e a cauda pesada é abafada estatisticamente pela massa periférica.

### 5. O expoente de volume (α in-vol ≈ 1,35–1,43) é estável e mais baixo que o de grau

Em todos os três grafos, o α do in-volume (número de contrapartes ponderado por volume) é sistematicamente mais baixo que o α do in-degree (número de contrapartes). Isso confirma que a cauda do volume é *mais pesada* que a cauda de conectividade: concentrar capital é mais extremo que concentrar conexões. Independentemente do evento, a rede PEPE sempre distribui o volume de forma mais desigual do que as conexões.

Esse resultado tem uma interpretação financeira direta: é mais fácil "aparecer como hub de conectividade" (transacionar com muitos) do que "aparecer como hub de volume" (mover muito dinheiro). Os grandes agentes financeiros não são necessariamente os mais conectados — mas quando ambos coincidem (como as whales identificadas no Alg.1), a assimetria entre os dois perfis sinaliza comportamento estratégico.

---

## Síntese investigativa

A análise de distribuição de grau com grafos completos revela que os três períodos têm *regimes estatísticos distintos*, não apenas parâmetros diferentes. O baseline é scale-free clássico (α≈2, R≈0). O Maduro produz uma assimetria interna única: in-degree scale-free reforçado, out-degree colapsado para log-normal. O Khamenei produz normalização geral da distribuição — a inundação de compradores periféricos apaga a estrutura de cauda pesada.

Esses três regimes diferentes sugerem que o tipo de choque importa tanto quanto sua magnitude: choques que amplificam hubs existentes (Maduro) mantêm ou reforçam a lei de potência; choques que atraem massa de novos participantes periféricos (Khamenei) a destroem.

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/resumo_distribuicao_gexf.csv` | α, xmin e R por grafo (in/out grau e volume) |
| `results/whales_distribuicao_gexf.csv` | Rank de volume e in-degree das whales |
| `results/report_distribuicao_gexf.png` | Log-log in/out degree com ajuste para os 3 grafos |
