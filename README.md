# Análise de Redes Complexas: O Token $PEPE em Cenários de Impacto Global

Este repositório contém os dados, scripts de processamento e grafos gerados para o projeto da disciplina **MC859 - Projeto em Teoria da Computação (Unicamp)**. O estudo foca na modelagem da rede de transações do token **$PEPE** na blockchain Ethereum, analisando sua resiliência e mudanças topológicas diante de choques geopolíticos externos.

## 📋 Sobre o Projeto
Redes blockchain são grafos direcionados de larga escala, onde as carteiras representam os vértices e as transações as arestas. Tokens de alta volatilidade e forte apelo comunitário, como o **$PEPE**, funcionam como sensores sensíveis a eventos globais. Este projeto investiga como a estrutura da rede (comunidades, centralidade e padrões de comportamento) se reconfigura em três janelas temporais distintas:

1.  **Baseline:** Período de controle sem eventos significativos (16 a 23 de outubro de 2025).
2.  **Choque 1 (Caso Maduro):** Janela associada ao sequestro de Nicolás Maduro (31 de dezembro de 2025 a 6 de janeiro de 2026).
3.  **Choque 2 (Caso Khamenei):** Janela associada ao assassinato de Ali Khamenei (28 de fevereiro a 3 de março de 2026).

## 📂 Estrutura do Repositório
* `**/data**`: Conjuntos de dados extraídos via Google BigQuery (`token_transfers`).
* `**/result**`: Exportações dos grafos nos formatos `.gephi` e visualizações estáticas.

## 🛠️ Metodologia
O projeto utiliza uma stack de Ciência de Dados e Teoria dos Grafos para processar grandes volumes de transações *on-chain*:

* **Extração:** Consultas SQL no dataset público `bigquery-public-data.crypto_ethereum`.
* **Processamento:** Python em ambiente Google Colab, utilizando as bibliotecas **Pandas** e **NetworkX**.
* **Detecção de Comunidades:** Aplicação do **Algoritmo de Louvain** para otimização de modularidade e identificação de clusters especulativos.
* **Visualização:** Utilização do **Gephi** para mapear o componente gigante, hubs de baleias e pontes entre comunidades.

## 👥 Autores
* **Gabriel Alves de Arruda** - RA: 248132
* **Guilherme Brentan de Oliveira** - RA: 252764

---
*Projeto desenvolvido para a disciplina MC859 - Unicamp.*
