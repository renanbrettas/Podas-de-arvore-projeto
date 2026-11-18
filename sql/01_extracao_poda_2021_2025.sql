-- Extração base: chamados de poda de árvore no 1746, 2021–2025.
-- Gera o arquivo data/poda_2021_2025.parquet (133.715 linhas na extração original).
-- Parâmetro: @alvo = ['Poda de árvore em logradouro',
--                      'Poda de árvore em vias públicas',
--                      'Árvore - Poda']
SELECT
  id_chamado,
  id_bairro,
  id_logradouro,
  numero_logradouro,
  data_inicio,
  id_unidade_organizacional,
  reclamacoes,
  latitude,
  longitude
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE subtipo IN UNNEST(@alvo)
  AND data_inicio >= DATETIME '2021-01-01'
  AND data_inicio <  DATETIME '2026-01-01';
