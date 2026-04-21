**MC859 \- Projeto em Teoria da Computação**  
Gabriel Alves de Arruda \- RA: 248132  
Guilherme Brentan de Oliveira \- RA: 252764

**Proposta de Projeto**

**Tema:** Análise de Redes Complexas na Blockchain: Comportamento de Ativos Altamente Especulativos Diante de Cenários de Impacto Global — O Token $TRUMP na Ethereum.

**Introdução**  
Redes blockchain são, fundamentalmente, grafos direcionados de larga escala, onde as carteiras digitais representam os vértices e as transações financeiras representam as arestas. Tokens especulativos com forte carga simbólica e política, como o $TRUMP, são especialmente sensíveis a choques externos, tornando-se laboratórios naturais para o estudo de como eventos de impacto global alteram a estrutura topológica de redes financeiras descentralizadas.

Este projeto analisa o grafo de transações do token ERC-20 $TRUMP na rede Ethereum, comparando três janelas temporais: uma janela de controle sem eventos relevantes (baseline) e duas janelas associadas a eventos geopolíticos de alta volatilidade — o sequestro de Nicolás Maduro e o assassinato de Ali Khamenei. Os dados foram extraídos do dataset público da Ethereum no Google BigQuery. O objetivo central é aplicar a teoria dos grafos para investigar se e como esses eventos alteram a estrutura da rede: detectando comunidades, revelando atuação coordenada de carteiras (cartéis de "baleias") e identificando topologias anômalas geradas por robôs de alta frequência (MEV bots).

**Objetivo Geral**  
Este projeto tem por objetivo modelar a rede de transações do token $TRUMP na blockchain Ethereum como um grafo direcionado de grande escala e comparar suas propriedades topológicas em diferentes janelas temporais — uma de controle e duas associadas a eventos geopolíticos extremos —, com ênfase na detecção de comunidades e na identificação de padrões de comportamento anômalo no fluxo de ativos especulativos.

**Objetivos Específicos**

* Extrair um dataset massivo: Obter um conjunto de dados reais de transações (arestas) e carteiras (vértices) únicas interagindo com o contrato inteligente ERC-20 do token na rede Ethereum, cobrindo três janelas temporais distintas.

* Identificar e isolar subgrafos e comunidades: Aplicar algoritmos de detecção de comunidades para agrupar vértices fortemente conectados. A partir das comunidades topológicas detectadas, realizamos uma análise detalhada secundária (avaliando timestamps das transações, volume financeiro e direcionamento de fluxo) para investigar se há evidências de que esses nós atuam como grupos coordenados (exchanges, MEV bots transacionando entre si)

* Mapear topologias de ataque/manipulação: Identificar padrões estruturais conhecidos em grafos financeiros, como "estrelas" (indicando distribuição centralizada ou ataques Sybil) e "cliques/ciclos" (indicando wash trading ou lavagem de dinheiro).  
* Análise de Centralidade: Classificar os nós de maior influência na rede utilizando métricas de centralidade (grau e intermediação/betweenness).

**Metodologia**

**Fase 1: Coleta de Dados**  
Os dados reais foram extraídos diretamente do dataset público da Ethereum no Google BigQuery (`bigquery-public-data.crypto_ethereum.token_transfers`). Utilizamos consultas SQL filtrando pelo endereço do contrato ERC-20 do token $TRUMP e por três janelas temporais: (1) **Baseline** — 16 a 23 de outubro de 2025, sem eventos relevantes; (2) **Maduro** — 31 de dezembro de 2025 a 6 de janeiro de 2026, sequestro de Nicolás Maduro; (3) **Khamenei** — 28 de fevereiro a 3 de março de 2026, assassinato de Ali Khamenei. Os dados exportados contêm: endereço de origem, endereço de destino, valor transferido, timestamp, número do bloco, gas utilizado e status da transação.

**Fase 2: Criação dos Grafos**  
O ambiente de desenvolvimento é o Google Colab com a linguagem Python. Para cada uma das três janelas temporais, o conjunto de dados será convertido em um Grafo Direcionado Ponderado (Directed Weighted Graph) utilizando a biblioteca NetworkX. Os nós são os endereços criptográficos e as arestas representam as transferências, tendo o volume financeiro como peso. Transferências duplicadas (mesmo `tx_hash`) e transações com falha são removidas no pré-processamento.

**Fase 3: Implementação dos Algoritmos**  
Para a divisão da rede, será implementado o Algoritmo de Louvain (focado na otimização de modularidade), ideal para grafos com milhares de nós. Paralelamente, calcularemos métricas intrínsecas do grafo, como Grau de Entrada/Saída (In-Degree / Out-Degree) e Centralidade de Intermediação (Betweenness Centrality) para encontrar os "nós-ponte" que conectam diferentes comunidades.

**Fase 4: Análise dos Resultados**  
As comunidades detectadas serão analisadas estatisticamente e comparadas entre as três janelas temporais. O objetivo central é identificar se eventos geopolíticos extremos provocam mudanças mensuráveis na topologia da rede do ativo especulativo: variações na densidade, tamanho do componente gigante (SCC), distribuição de grau e concentração de hubs. O cruzamento entre agrupamentos topológicos e comportamentos econômicos reais (corretoras descentralizadas como hubs, robôs isolados em clusters periféricos) complementará a análise. Uma sub-amostra visualmente tratada dos grafos será gerada para a apresentação final com o auxílio da ferramenta Gephi.

**Planejamento de Execução**  
O projeto será desenvolvido em 5 etapas principais:

**Entrega Parcial:**

* **Etapa 1**  **(conclusão prevista 10/04)**: Configuração do ambiente (Google Cloud / Colab), elaboração das queries em SQL e extração do dataset completo com validação de escopo (\> 50 mil arestas).  
* **Etapa 2 (conclusão prevista 23/04)**: Tratamento dos dados (limpeza), instanciação do grafo via NetworkX e extração das métricas básicas iniciais (densidade, diâmetro, nós de maior grau).

**Entrega Final:**

* **Etapa 3 (conclusão prevista 08/05)**: Execução do algoritmo de Louvain, particionamento da rede e identificação dos padrões estruturais (estrelas, cliques, hubs).  
* **Etapa 4 (conclusão prevista 22/05)**: Interpretação analítica das comunidades formadas e cruzamento do comportamento topológico do grafo com as características teóricas abordadas na disciplina.  
* **Etapa 5** **(conclusão prevista 05/06)**: Elaboração da apresentação visual do grafo, compilação dos dados descobertos e fechamento do relatório final.