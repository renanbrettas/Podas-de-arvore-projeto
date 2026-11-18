-- Em que tipos de evento do COR a Light é acionada.
-- ocorrencias_orgaos_responsaveis: uma linha por órgão acionado em cada evento.
SELECT
  o.id_pop,
  p.pop_titulo,
  COUNT(DISTINCT o.id_evento) AS eventos
FROM `datario.adm_cor_comando.ocorrencias_orgaos_responsaveis` g
JOIN `datario.adm_cor_comando.ocorrencias` o USING (id_evento)
LEFT JOIN `datario.adm_cor_comando.procedimento_operacional_padrao` p USING (id_pop)
WHERE LOWER(TRIM(g.sigla)) = 'light'
GROUP BY 1, 2
ORDER BY eventos DESC;
