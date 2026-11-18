-- Chamados de Manejo Arbóreo (todos os subtipos) e de poda por logradouro.
-- Parâmetros: @ini, @fim (DATETIME; início inclusivo, fim exclusivo).
SELECT
  id_logradouro,
  COUNT(*) AS n_manejo,
  COUNTIF(subtipo IN ('Poda de árvore em logradouro',
                      'Poda de árvore em vias públicas',
                      'Árvore - Poda')) AS n_poda
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE tipo = 'Manejo Arbóreo'
  AND data_inicio >= @ini AND data_inicio < @fim
  AND id_logradouro IS NOT NULL
  AND TRIM(id_logradouro) NOT IN ('', '0')
GROUP BY id_logradouro
ORDER BY n_manejo DESC, id_logradouro;
