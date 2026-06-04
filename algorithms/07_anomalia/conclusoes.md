# Conclusões — Algoritmo 7: Detecção de Anomalia Estatística Formal

## Metodologia

As 8 métricas diárias do Algoritmo 4 foram usadas para construir uma distribuição de referência com os dias do baseline (n=8 observações por métrica). Para cada dia de cada evento, calculou-se o z-score: z = (valor − média_baseline) / std_baseline. Um dia é **formalmente anômalo** em uma métrica quando |z| > 2. O **anomaly score** de um dia é a soma dos |z-scores| de todas as métricas — quanto maior, mais desviante do comportamento normal em termos combinados.

---

## Resultados

### Baseline (referência)
| Métrica | Média | Desvio |
|---|---|---|
| Nós ativos | 2.602,5 | 553,3 |
| SCC% | 14,6% | 2,3 p.p. |
| Razão OUT/IN | 1,062 | 0,261 |
| Volume IN→SCC | 11,96% | 2,10 p.p. |
| Gini do volume | 0,9428 | 0,0078 |
| Top-20 PageRank share | 28,5% | 3,2 p.p. |

### Z-scores — Maduro

| Dia | Nós | SCC% | OUT/IN | Vol IN→SCC | Gini | PR top-20 | Score | Anomalias |
|---|---|---|---|---|---|---|---|---|
| D-3 | 0,3 | −0,5 | −0,5 | −2,0 | **2,6** | −0,1 | 6,0 | 1 |
| D-2 | 0,7 | −0,3 | −1,3 | −1,6 | **2,9** | **2,5** | 9,4 | 2 |
| D-1 | **6,5** | 1,0 | −0,5 | **−2,5** | **3,0** | 0,8 | 14,4 | 3 |
| D   | **4,2** | 0,9 | −0,8 | **−3,6** | **3,5** | 2,0 | 15,0 | 3 |
| D+1 | **7,0** | −0,1 | −1,2 | **−3,1** | **3,7** | 1,6 | **16,7** | 3 |
| D+2 | **5,6** | 0,9 | −1,5 | **−3,3** | **3,9** | −0,2 | 15,3 | 3 |
| D+3 | **3,9** | 1,1 | −1,2 | **−2,8** | **3,8** | 0,9 | 13,8 | 3 |

### Z-scores — Khamenei

| Dia | Nós | SCC% | OUT/IN | Vol IN→SCC | Gini | PR top-20 | Score | Anomalias |
|---|---|---|---|---|---|---|---|---|
| **D-3** | **14,8** | **−4,4** | **−3,7** | 1,7 | 0,9 | **7,1** | **32,8** | **4** |
| D-2 | −0,2 | 1,6 | **2,0** | **−3,9** | −0,7 | 0,7 | 9,1 | 2 |
| D-1 | −0,9 | 1,3 | **3,8** | −0,9 | −0,1 | −1,5 | 8,5 | 1 |
| D   | −0,7 | 1,4 | **2,3** | **2,9** | **−3,1** | −1,9 | 12,3 | 3 |
| D+1 | −1,0 | **2,1** | **3,1** | −1,8 | −1,4 | −0,2 | 9,6 | 2 |
| D+2 | −1,4 | **3,5** | 0,7 | 0,5 | −1,5 | 1,0 | 8,5 | 1 |
| D+3 | −1,6 | 1,5 | 1,1 | −1,3 | −1,9 | 0,3 | 7,5 | **0** |

---

## Achados principais

### 1. D-3 Khamenei é o dia mais anômalo de todo o estudo — por ampla margem

Com anomaly score = **32,8**, o D-3 de Khamenei (25 de fevereiro) é mais do que o dobro do segundo dia mais anômalo (D+1 Maduro = 16,7). Quatro métricas cruzam o limiar de |z| > 2 simultaneamente:
- Nós ativos: z = **14,8** (10.818 nós vs média baseline de 2.602 — +4,2 desvios-padrão em valor, mas o z é 14 porque o desvio do baseline é 553)
- SCC%: z = **−4,4** (SCC de 4,3% vs média 14,6%)
- Razão OUT/IN: z = **−3,7** (0,09 vs média 1,06)
- Top-20 PR share: z = **7,1** (51,1% vs média 28,5%)

É a anomalia mais clara e quantificável de todos os 14 dias de evento analisados. Formalmente, se considerarmos o baseline como a distribuição normal, a probabilidade de observar z=14,8 em nós ativos por acaso é astronomicamente baixa. Isso não é variação natural — é ruptura estrutural concentrada em um único dia, 3 dias antes do assassinato.

### 2. O Gini começa a subir no Maduro 3 dias antes — primeiro sinal formal

O primeiro sinal anômalo do Maduro aparece em **D-3** (31 de dezembro), com Gini z=2,638. Não são os nós ativos (z=0,26 — normal) nem o fluxo (z≈-2,0 — limítrofe). É especificamente a **concentração de volume** que começa a crescer antes do evento tornar-se público. A sequência é: Gini sobe (D-3) → PR top-20 e nós sobem (D-2) → atividade explode (D-1 em diante). O Gini é o indicador mais precoce de choque neste evento.

### 3. Maduro tem anomalias persistentes nos 7 dias — Khamenei normaliza em D+3

Todos os dias da janela Maduro têm ao menos 1 métrica anômala (anomaly_count ≥ 1). O efeito não decai dentro da janela observada. Khamenei, por contraste, tem **zero anomalias em D+3** — o impacto do evento se dissipa em 5 dias. Os dois eventos têm "meia-vida" de anomalia muito diferentes: Maduro é persistente, Khamenei é agudo e transitório.

### 4. Volume IN→SCC negativo no Maduro — paradoxo formal confirmado

O z-score de Vol IN→SCC é **negativo e fortemente anômalo** durante o Maduro (z=-3,6 no dia D). Isso significa que, apesar da rede estar muito mais ativa, a *fração* do volume fluindo de IN para a SCC está abaixo do baseline. Como reconciliar com o Alg.3 (que mostrou IN crescente)? Muitos compradores entraram na rede (IN grande), mas cada um movimentou volumes menores individualmente, diluindo a fração do fluxo total que vai de IN→SCC. O *valor absoluto* de IN→SCC sobe, mas a *proporção* cai porque o volume total explodiu.

### 5. Gini Khamenei no dia D tem z = −3,1 — democratização formal

No dia do assassinato, o Gini do volume fica **abaixo** da média do baseline (z=−3,1) — única ocorrência de Gini negativo em qualquer dia de evento. Isso formaliza a descoberta do Alg.2 e Alg.4: no dia D, a especulação foi mais pulverizada, distribuída entre mais participantes com volumes menores por transação. O volume IN→SCC de 18% naquele dia (Alg.3) veio de muitos participantes pequenos, não das whales.

### 6. SCC% em D+2 Khamenei tem z=+3,5 — recuperação anômala do núcleo

O processo de consolidação pós-Khamenei (SCC% sobe para 22,8% em D+2) é formalmente anômalo: z=3,5. A rede não retorna ao normal — ela "supercorrige" em SCC%, ultrapassando o baseline por mais de 3 desvios-padrão. Isso acontece porque os ~10.000 compradores de D-3 saíram, deixando apenas os participantes mais interconectados — e esses formam uma SCC muito maior proporcionalmente ao total de nós restantes.

### 7. Razão OUT/IN do Khamenei é positivamente anômala de D-1 a D+1

A razão OUT/IN em Khamenei é negativa em D-3 (z=−3,7, onda compradora) e positiva depois (z=+3,8 em D-1, z=+2,3 em D, z=+3,1 em D+1). A inversão formal da razão — de anomalia de compra para anomalia de distribuição — ocorre entre D-3 e D-2. A detecção automática confirma a narrativa: a mudança de regime é abrupta, não gradual.

---

## Síntese narrativa (fio para o relatório)

A detecção de anomalia formal converte as observações qualitativas dos algoritmos anteriores em evidências quantificadas. O D-3 de Khamenei com score=32,8 é o dia formalmente mais rupturista de todo o estudo — não o dia D. O Maduro tem um sinal precoce no Gini (D-3) e um efeito persistente que não se dissipa na janela observada. O Khamenei é agudo: entra com força (32,8) e normaliza completamente em D+3. Esses perfis de anomalia diferentes refletem naturezas diferentes dos eventos: o sequestro de Maduro foi um evento de incerteza prolongada; o assassinato de Khamenei foi um choque pontual com resolução rápida.

---

## Hipóteses verificadas

| Hipótese (algoritmos.md) | Resultado |
|---|---|
| Cada evento tem ao menos um dia com z > 3 em múltiplas métricas | **Confirmada**: Maduro tem 5 dias com score > 13; Khamenei tem D-3 com score 32,8 |
| D-3 Khamenei é o dia mais anômalo | **Confirmada** e quantificada: score 32,8 vs. segundo lugar 16,7 |
| Gini é o sinal mais precoce no Maduro | **Confirmada**: primeiro z > 2 aparece em D-3, exclusivamente no Gini |

---

## Arquivos de resultado

| Arquivo | Conteúdo |
|---|---|
| `results/zscores_diarios.csv` | Z-scores e anomaly score por dia e dataset |
| `results/heatmap_zscores.png` | Heatmap de z-scores (vermelho = acima, azul = abaixo do baseline) |
| `results/anomaly_score_por_dia.png` | Score combinado por dia para ambos os eventos |
| `results/zscore_por_metrica.png` | Evolução temporal do z-score por métrica |
