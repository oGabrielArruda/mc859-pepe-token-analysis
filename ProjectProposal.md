**MC859 \- Projeto em Teoria da Computação**  
Gabriel Alves de Arruda \- RA: 248132  
Guilherme Brentan de Oliveira \- RA: 252764

**Proposta de Projeto**

**Tema:** Análise de Redes Complexas na Blockchain: Detecção de Comunidades e Padrões de Comportamento no Token Político $TRUMP.

**Introdução**  
Redes blockchain são, fundamentalmente, grafos direcionados de larga escala, onde as carteiras digitais representam os vértices e as transações financeiras representam as arestas. Com o recente surgimento do setor "PolitiFi" (Finanças Políticas) no ecossistema de criptomoedas, tokens temáticos ligados a figuras públicas tornaram-se alvos de intensa especulação e volatilidade.

Este projeto propõe a extração e análise do grafo de transações do token SPL $TRUMP na rede Solana. O foco será analisar uma janela de tempo associada a um evento de alta volatilidade no noticiário político, como o assassinato do líder político Ali Khamenei, ou o sequestro de Nicolás Maduro. O objetivo central é ir além do pseudo anonimato da rede, aplicando a teoria dos grafos para detectar comunidades ocultas, descobrir a atuação coordenada de carteiras (cartéis de "baleias") e identificar topologias anômalas geradas por robôs de alta frequência (MEV bots). O projeto utilizará um grande volume de dados reais, para extrair conhecimento sobre a dinâmica comportamental em redes descentralizadas.

**Objetivo Geral**  
Este projeto tem por objetivo modelar a rede de transações do token $TRUMP na blockchain Solana como um grafo direcionado de grande escala para identificar e analisar suas propriedades topológicas, com ênfase na detecção de comunidades, revelando padrões de centralização velada e comportamentos anômalos no fluxo de ativos.

**Objetivos Específicos**

* Extrair um dataset massivo: Obter um conjunto de dados reais de transações (arestas) e carteiras (vértices) únicas interagindo com o contrato inteligente do token.

* Identificar e isolar subgrafos e comunidades: Aplicar algoritmos de detecção de comunidades para agrupar vértices fortemente conectados. A partir das comunidades topológicas detectadas, realizamos uma análise detalhada secundária (avaliando timestamps das transações, volume financeiro e direcionamento de fluxo) para investigar se há evidências de que esses nós atuam como grupos coordenados (exchanges, MEV bots transacionando entre si)

* Mapear topologias de ataque/manipulação: Identificar padrões estruturais conhecidos em grafos financeiros, como "estrelas" (indicando distribuição centralizada ou ataques Sybil) e "cliques/ciclos" (indicando wash trading ou lavagem de dinheiro).  
* Análise de Centralidade: Classificar os nós de maior influência na rede utilizando métricas de centralidade (grau e intermediação/betweenness).

**Metodologia**

**Fase 1: Coleta de Dados**  
Os dados reais serão extraídos diretamente do banco de dados público da blockchain espelhado no Google BigQuery (bigquery-public-data.crypto\_solana.token\_transfers). Utilizaremos consultas SQL filtrando pelo endereço de contrato inteligente do token $TRUMP e por uma janela temporal específica de alta volatilidade. Os dados serão exportados estruturados contendo: endereço de origem, endereço de destino, valor transferido e timestamp.

**Fase 2: Criação dos Grafos**  
O ambiente de desenvolvimento será o Google Colab com a linguagem Python. O conjunto de dados será convertido em um Grafo Direcionado Ponderado (Directed Weighted Graph) utilizando a biblioteca NetworkX. Os nós serão os endereços criptográficos e as arestas representam as transferências, tendo o volume financeiro como peso.

**Fase 3: Implementação dos Algoritmos**  
Para a divisão da rede, será implementado o Algoritmo de Louvain (focado na otimização de modularidade), ideal para grafos com milhares de nós. Paralelamente, calcularemos métricas intrínsecas do grafo, como Grau de Entrada/Saída (In-Degree / Out-Degree) e Centralidade de Intermediação (Betweenness Centrality) para encontrar os "nós-ponte" que conectam diferentes comunidades.

**Fase 4: Análise dos Resultados**  
As comunidades detectadas serão analisadas estatisticamente. O objetivo será correlacionar os agrupamentos topológicos com comportamentos econômicos reais (ex: corretoras descentralizadas atuando como hubs, robôs isolados em clusters periféricos). Uma sub-amostra visualmente tratada do grafo será gerada para a apresentação final, possivelmente com o auxílio da ferramenta Gephi ou bibliotecas visuais do Python.

**Planejamento de Execução**  
O projeto será desenvolvido em 5 etapas principais:

**Entrega Parcial:**

* **Etapa 1**  **(conclusão prevista 10/04)**: Configuração do ambiente (Google Cloud / Colab), elaboração das queries em SQL e extração do dataset completo com validação de escopo (\> 50 mil arestas).  
* **Etapa 2 (conclusão prevista 23/04)**: Tratamento dos dados (limpeza), instanciação do grafo via NetworkX e extração das métricas básicas iniciais (densidade, diâmetro, nós de maior grau).

**Entrega Final:**

* **Etapa 3 (conclusão prevista 08/05)**: Execução do algoritmo de Louvain, particionamento da rede e identificação dos padrões estruturais (estrelas, cliques, hubs).  
* **Etapa 4 (conclusão prevista 22/05)**: Interpretação analítica das comunidades formadas e cruzamento do comportamento topológico do grafo com as características teóricas abordadas na disciplina.  
* **Etapa 5** **(conclusão prevista 05/06)**: Elaboração da apresentação visual do grafo, compilação dos dados descobertos e fechamento do relatório final.