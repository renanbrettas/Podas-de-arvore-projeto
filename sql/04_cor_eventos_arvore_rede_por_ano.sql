-- Eventos de queda de árvore (11), queda de poste (12), falta de luz (17) e
-- queda de árvore sobre fiação (40) por ano, com Light / Concessionária acionadas.
WITH acion AS (
  SELECT
    id_evento,
    LOGICAL_OR(LOWER(TRIM(sigla)) = 'light') AS light,
    LOGICAL_OR(LOWER(TRIM(sigla)) IN ('concessionária', 'concessionaria')) AS concess
  FROM `datario.adm_cor_comando.ocorrencias_orgaos_responsaveis`
  GROUP BY id_evento
)
SELECT
  o.id_pop,
  p.pop_titulo,
  EXTRACT(YEAR FROM o.data_inicio) AS ano,
  COUNT(DISTINCT o.id_evento) AS eventos,
  COUNT(DISTINCT IF(a.light,   o.id_evento, NULL)) AS com_light,
  COUNT(DISTINCT IF(a.concess, o.id_evento, NULL)) AS com_concess
FROM `datario.adm_cor_comando.ocorrencias` o
LEFT JOIN acion a USING (id_evento)
LEFT JOIN `datario.adm_cor_comando.procedimento_operacional_padrao` p USING (id_pop)
WHERE o.id_pop IN ('11', '12', '17', '40')
  AND o.data_inicio >= TIMESTAMP '2015-01-01'
GROUP BY 1, 2, 3
ORDER BY id_pop, ano;
