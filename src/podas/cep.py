"""Análise poda -> queda com o CEP como unidade espacial (em desenvolvimento).

Nenhuma das tabelas mapeadas até agora (``chamado``, ``bairro``, ``logradouro``)
tem coluna de CEP; ``dados_mestres.numero_porta`` tem. O fluxo previsto é:

1. Montar ``pontos_cep`` (colunas ``cep``, ``lon``, ``lat`` e, de preferência,
   ``id_logradouro``) a partir de ``numero_porta`` ou de uma base externa.
2. Atribuir um CEP a cada chamado pelo vizinho mais próximo
   (``atribuir_cep``), com limite de distância.
3. Calcular, por chamado de poda, se houve queda na mesma unidade depois
   (``poda_para_queda``) e resumir por unidade (``resumo_por_unidade``).

Exemplo
-------
>>> from podas.bq import rodar
>>> poda = rodar(SQL_PODA); queda = rodar(SQL_QUEDA)
>>> poda["cep"], poda["dist_cep_m"] = atribuir_cep(poda, pontos_cep)
>>> queda["cep"], queda["dist_cep_m"] = atribuir_cep(queda, pontos_cep)
>>> res = poda_para_queda(poda, queda, chave="cep")
>>> tabela = resumo_por_unidade(res, chave="cep")

Sempre reporte junto a cobertura: a fração de podas e quedas com CEP atribuído.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SQL_PODA = """
SELECT id_chamado, data_inicio, id_bairro, id_logradouro,
       longitude AS lon, latitude AS lat
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE tipo = 'Manejo Arbóreo'
  AND subtipo IN ('Poda de árvore em logradouro',
                  'Poda de árvore em vias públicas',
                  'Árvore - Poda')
  AND data_inicio >= DATETIME '2021-01-01'
  AND data_inicio <  DATETIME '2026-01-01'
"""

SQL_QUEDA = """
SELECT id_chamado, data_inicio, id_bairro, id_logradouro,
       longitude AS lon, latitude AS lat
FROM `datario.adm_central_atendimento_1746.chamado`
WHERE tipo = 'Manejo Arbóreo'
  AND subtipo = 'Retirada de árvore caída'
  AND data_inicio >= DATETIME '2021-01-01'
"""

SQL_PONTOS_CEP = """
SELECT cep, longitude AS lon, latitude AS lat, id_logradouro
FROM `datario.dados_mestres.numero_porta`
WHERE cep IS NOT NULL
"""

SQL_ACHAR_CEP = """
SELECT table_name, column_name, data_type
FROM `datario.{dataset}.INFORMATION_SCHEMA.COLUMNS`
WHERE LOWER(column_name) LIKE '%cep%' OR LOWER(column_name) LIKE '%postal%'
"""


def padroniza_cep(s: pd.Series) -> pd.Series:
    """Mantém só dígitos e completa com zeros à esquerda até 8 posições."""
    return s.astype("string").str.replace(r"\D", "", regex=True).str.zfill(8)


def atribuir_cep(df: pd.DataFrame, pontos: pd.DataFrame, max_m: float = 150.0,
                 por_logradouro: bool = True) -> tuple[pd.Series, pd.Series]:
    """Devolve ``(cep, distancia_m)`` alinhados ao índice de ``df``.

    Sem coordenada, sem ponto de CEP no logradouro ou além de ``max_m`` -> NA.
    Com ``por_logradouro=True`` (e ``id_logradouro`` em ``pontos``), a busca do
    vizinho fica restrita ao mesmo logradouro, o que é mais seguro.
    """
    from sklearn.neighbors import BallTree

    R = 6_371_000.0
    cep = pd.Series(pd.NA, index=df.index, dtype="object")
    dist = pd.Series(np.nan, index=df.index, dtype="float64")
    d = df.dropna(subset=["lon", "lat"])

    def vizinho(sub_d, sub_p):
        tree = BallTree(np.radians(sub_p[["lat", "lon"]].to_numpy()), metric="haversine")
        dd, ii = tree.query(np.radians(sub_d[["lat", "lon"]].to_numpy()), k=1)
        return sub_p["cep"].to_numpy()[ii[:, 0]], dd[:, 0] * R

    if por_logradouro and "id_logradouro" in pontos.columns:
        grupos = {k: g for k, g in pontos.groupby("id_logradouro")}
        for k, sub_d in d.groupby("id_logradouro"):
            sub_p = grupos.get(k)
            if sub_p is None:
                continue
            c, dm = vizinho(sub_d, sub_p)
            cep.loc[sub_d.index] = c
            dist.loc[sub_d.index] = dm
    else:
        c, dm = vizinho(d, pontos)
        cep.loc[d.index] = c
        dist.loc[d.index] = dm

    cep[dist > max_m] = pd.NA
    return cep, dist


def poda_para_queda(poda: pd.DataFrame, queda: pd.DataFrame, chave: str = "cep",
                    janelas: tuple[int, ...] = (90, 365),
                    corte: str = "2026-09-20") -> pd.DataFrame:
    """Uma linha por chamado de poda.

    - ``dias_ate_queda``: dias até a PRIMEIRA queda estritamente depois da poda;
    - ``queda_{w}d``: houve queda em até ``w`` dias depois;
    - ``queda_antes_{w}d``: houve queda nos ``w`` dias ANTES da poda;
    - ``seg_completo_{w}d``: a janela de ``w`` dias cabe antes do corte dos dados.
    """
    corte = pd.Timestamp(corte)
    p = poda.dropna(subset=[chave])[["id_chamado", chave, "data_inicio"]]
    qd = (queda.dropna(subset=[chave])[[chave, "data_inicio"]]
          .rename(columns={"data_inicio": "data_queda"}))
    m = p.merge(qd, on=chave, how="left")
    m["dias"] = (m["data_queda"] - m["data_inicio"]).dt.total_seconds() / 86400

    res = p.set_index("id_chamado")
    res["dias_ate_queda"] = m[m["dias"] > 0].groupby("id_chamado")["dias"].min()
    for w in janelas:
        antes = m[(m["dias"] < 0) & (m["dias"] >= -w)]["id_chamado"].unique()
        res[f"queda_{w}d"] = res["dias_ate_queda"].le(w)
        res[f"queda_antes_{w}d"] = res.index.isin(antes)
        res[f"seg_completo_{w}d"] = (res["data_inicio"] + pd.Timedelta(days=w)) <= corte
    return res


def resumo_por_unidade(res: pd.DataFrame, chave: str = "cep",
                       janelas: tuple[int, ...] = (90, 365),
                       min_poda: int = 10) -> pd.DataFrame:
    """Taxas de queda depois (e antes) da poda por unidade espacial."""
    base = res.groupby(chave).size().rename("n_poda").to_frame()
    for w in janelas:
        g = res[res[f"seg_completo_{w}d"]].groupby(chave)
        base[f"n_seg_{w}d"] = g.size()
        base[f"queda_{w}d"] = g[f"queda_{w}d"].sum()
        base[f"taxa_{w}d"] = base[f"queda_{w}d"] / base[f"n_seg_{w}d"]
        base[f"taxa_antes_{w}d"] = res.groupby(chave)[f"queda_antes_{w}d"].mean()
    wmax = max(janelas)
    atraso = res[res["dias_ate_queda"] <= wmax].groupby(chave)["dias_ate_queda"]
    base[f"mediana_dias_ate_queda_{wmax}d"] = atraso.median()
    base = base[base["n_poda"] >= min_poda].sort_values("n_poda", ascending=False)
    return base.reset_index()
