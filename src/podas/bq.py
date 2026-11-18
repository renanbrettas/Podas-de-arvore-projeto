"""Conexão com o BigQuery e execução de consultas com estimativa de custo.

O ID do projeto de faturamento vem da variável de ambiente ``GCP_PROJECT_ID``
(veja ``.env.example``). As tabelas consultadas são públicas, no projeto
``datario``; o seu projeto só é usado para cobrar a leitura.
"""

from __future__ import annotations

import os

from google.cloud import bigquery

_client: bigquery.Client | None = None


def _autenticar_colab() -> None:
    """No Google Colab, abre o fluxo de autenticação do usuário."""
    try:
        from google.colab import auth  # type: ignore
    except ImportError:
        return
    auth.authenticate_user()


def get_client(project_id: str | None = None) -> bigquery.Client:
    """Devolve (e guarda) um cliente do BigQuery."""
    global _client
    if _client is not None and project_id is None:
        return _client

    project_id = project_id or os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError(
            "Defina a variável de ambiente GCP_PROJECT_ID com o ID do seu "
            "projeto no Google Cloud (ex.: export GCP_PROJECT_ID=meu-projeto)."
        )
    _autenticar_colab()
    _client = bigquery.Client(project=project_id)
    return _client


def estimar_gb(sql: str, params: list | None = None) -> float:
    """Estima os GB que a consulta vai processar (dry run, não consome cota)."""
    cfg = bigquery.QueryJobConfig(
        dry_run=True, use_query_cache=False, query_parameters=params or []
    )
    return get_client().query(sql, job_config=cfg).total_bytes_processed / 1e9


def rodar(sql: str, params: list | None = None, limite_gb: float = 20):
    """Imprime o custo estimado e executa a consulta com teto de bytes faturados.

    Parâmetros
    ----------
    sql : consulta em SQL padrão do BigQuery.
    params : lista de ``bigquery.ScalarQueryParameter`` / ``ArrayQueryParameter``.
    limite_gb : a consulta falha se for processar mais do que isso.
    """
    params = params or []
    print(f"custo estimado: {estimar_gb(sql, params):.3f} GB")
    cfg = bigquery.QueryJobConfig(
        query_parameters=params, maximum_bytes_billed=int(limite_gb * 10**9)
    )
    return get_client().query(sql, job_config=cfg).to_dataframe()
