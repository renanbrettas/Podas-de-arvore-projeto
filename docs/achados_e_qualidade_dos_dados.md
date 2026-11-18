# Achados detalhados, decisões e qualidade dos dados

Registro das decisões tomadas e dos problemas de dados encontrados. Os números vêm das saídas
originais dos notebooks.

## 1. Recorte de "poda" no 1746 (notebook 01)

- A tabela `chamado` tem **20.263.796** chamados e **5.545** combinações tipo/subtipo.
- Classificação das combinações por palavras-chave, com a partição conferida por `assert`:

  | Classe | Combinações | Chamados |
  |---|---:|---:|
  | alvo | 3 | 376.293 |
  | sensibilidade | 1 | 13.690 |
  | revisar | 92 | 588.115 |
  | fora | 5.449 | 19.285.698 |

- **Alvo:** `Poda de árvore em logradouro`, `Poda de árvore em vias públicas`, `Árvore - Poda`.
- **Sensibilidade:** `Poda e remoção de árvore` (mistura poda e remoção).
- **Excluído:** `Árvore-Poda e Remoção` (46.326 chamados, nenhum em 2021–2025).
- **Atenção para 2026:** `Poda de árvore em vias públicas` salta de 9.143 (2021–2025) para 21.780 só em
  2026. O 1746 parece estar migrando a poda para esse subtipo.
- **Desfecho escolhido para quedas:** `Retirada de árvore caída` (7.890 em 2021–2025; existe desde 2019).

## 2. Light e unidades responsáveis (notebook 02)

- Poda é atendida pela **COMLURB (unidade 118)** e pela **Ouvidoria COMLURB (247)**. A hipótese inicial
  de que 118 fosse a Rio Luz estava errada.
- A única unidade com nome ligado a energia é a **RIOLUZ (8)**, que atende os subtipos de galho sobre a
  rede ou luminária (35 chamados) e de poda por obstrução da iluminação (3).
- **Nenhuma** justificativa de chamado de poda cita Light, fiação ou rede elétrica.
- Uma tentativa de marcar "chamados dependentes da Light" por texto foi descartada: a extração não tem
  coluna de descrição, e a marcação resultou em 100% dos registros.

## 3. COR (notebook 02)

- A Light aparece em `ocorrencias_orgaos_responsaveis` com **5.407 acionamentos em 2.940 eventos**.
  As ações mais comuns são desligar energia (1.911), restabelecer fornecimento (1.881), retirar poste
  (810) e verificar fiação (797).
- Eventos em que a Light é acionada: queda de árvore (1.103), queda de poste (345), incêndio no entorno
  de vias (317), acidente sem vítima (315)...
- **Problemas da fonte:**
  - `id_evento` não é único em `ocorrencias` (91.406 linhas, 87.620 IDs) e é **reaproveitado entre anos**;
  - 1.060 acionamentos com data zerada (1970);
  - `bairro` vazio até 2018;
  - a tabela **termina em 02/04/2024**;
  - a participação da Light nas quedas de árvore cai de 188 eventos (2021) para 11 (2023) e 5 (2024),
    e o procedimento "Queda de árvore sobre fiação" (`id_pop` 40) só existe desde 2021: mudança de
    registro, não necessariamente do fenômeno.

## 4. Qualidade da localização no 1746 (notebook 03)

| Ano | Chamados de poda | Bairro/logradouro ok | Coordenada válida | Justificativa preenchida |
|---|---:|---:|---:|---:|
| 2021 | 23.906 | 98,1% | 94,7% | 7,8% |
| 2022 | 25.223 | 99,1% | 86,5% | 8,7% |
| 2023 | 31.176 | 99,7% | 65,5% | 17,0% |
| 2024 | 27.518 | 97,6% | 59,8% | 23,0% |
| 2025 | 25.892 | 98,4% | 59,2% | 24,5% |

- Os 1.841 chamados sem bairro são exatamente os mesmos sem logradouro.
- O campo `reclamacoes` é zero em ~97% dos chamados.
- Consequência: o **logradouro** foi usado como unidade espacial principal, porque a coordenada perde
  cobertura justamente nos anos recentes.

## 5. Geometrias e análise espacial (notebook 04)

- `dados_mestres.bairro` retorna 167 polígonos; **23 inválidos** ("hole lies outside shell") foram
  corrigidos com `make_valid`, sem variação de área.
- Join espacial dos eventos de árvore do COR (2021–2023): 1.233 de 1.235 caem dentro de um bairro.
  O bairro digitado concorda com o polígono em **83,8%** dos casos.
- Manejo arbóreo 2021–2025: 212.501 chamados, 6.507 sem bairro; mediana de 749 chamados por bairro
  (máx. 17.048); 2 bairros sem chamado.
- Logradouros: 14.089 com chamado; mediana de **4 podas** por logradouro; 2.932 com uma só. O topo do
  ranking é dominado por vias extensas (Av. Brasil: 1.108 trechos em 31 bairros), então comparações
  precisam de normalização por extensão ou de outra unidade.
- 176 `id_logradouro` dos chamados (466 podas) não existem no cadastro de logradouros.

## 6. Poda → queda (notebook 05)

- 131.874 podas com logradouro válido; 10.585 quedas (`Retirada de árvore caída`) desde 2021; dados
  até 20/09/2026.
- Linha de base: Poisson por logradouro, P(≥1 queda em H dias) = 1 − exp(−λ·H), com λ = quedas do
  logradouro ÷ duração do período.

| Horizonte | Obs. depois | Esperado | Razão depois | Razão antes |
|---|---:|---:|---:|---:|
| 7 d | 1,18% | 1,03% | 1,15 | 1,39 |
| 30 d | 3,24% | 4,07% | 0,80 | 0,88 |
| 90 d | 7,67% | 10,35% | 0,74 | 0,78 |
| 180 d | 13,03% | 17,28% | 0,75 | 0,78 |
| 365 d | 22,74% | 26,79% | 0,85 | 0,80 |

- **Leitura:** não há excesso de quedas depois da poda a partir de 30 dias. O excesso em 7 dias é
  simétrico (até maior antes da poda), o que é compatível com abertura conjunta de chamados num
  mesmo episódio (temporal), e não com antecipação.
- **Limitações:** a taxa de base é constante no tempo (sem sazonalidade ou chuva); a unidade
  logradouro mistura vias muito longas; o atendimento da poda não é observado; e a razão abaixo de 1
  pode refletir que λ, calculado sobre o período inteiro, superestima o risco em janelas curtas para
  logradouros com quedas concentradas.
