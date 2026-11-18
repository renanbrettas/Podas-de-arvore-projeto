"""Constantes do projeto: tabelas, recortes, caminhos e limites geográficos."""

from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Caminhos (relativos à raiz do repositório)
# --------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[2]
DATA_DIR = RAIZ / "data"        # extrações locais (não versionadas)
FIG_DIR = RAIZ / "figures"      # figuras exportadas
OUT_DIR = RAIZ / "outputs"      # planilhas e tabelas geradas (não versionadas)

ARQ_PODA = DATA_DIR / "poda_2021_2025.parquet"

# --------------------------------------------------------------------------
# Tabelas públicas do Data.Rio no BigQuery
# --------------------------------------------------------------------------
T_CHAMADO = "`datario.adm_central_atendimento_1746.chamado`"
T_COR_OCORRENCIAS = "`datario.adm_cor_comando.ocorrencias`"
T_COR_ORGAOS = "`datario.adm_cor_comando.ocorrencias_orgaos_responsaveis`"
T_COR_POP = "`datario.adm_cor_comando.procedimento_operacional_padrao`"
T_BAIRRO = "`datario.dados_mestres.bairro`"
T_LOGRADOURO = "`datario.dados_mestres.logradouro`"

# --------------------------------------------------------------------------
# Recorte analítico
# --------------------------------------------------------------------------
# Subtipos do 1746 tratados como "poda" (definidos no notebook 01).
ALVO = [
    "Poda de árvore em logradouro",
    "Poda de árvore em vias públicas",
    "Árvore - Poda",
]
# Subtipo misto (poda + remoção): usado só em análises de sensibilidade.
SENSIBILIDADE = ["Poda e remoção de árvore"]

# Desfecho usado na análise poda -> queda (notebook 05).
SUBTIPOS_QUEDA = ["Retirada de árvore caída"]

# Período principal (início inclusivo, fim exclusivo).
DATA_INI = datetime(2021, 1, 1)
DATA_FIM = datetime(2026, 1, 1)

# Caixa aproximada do município do Rio de Janeiro (lon/lat, EPSG:4326),
# usada para descartar coordenadas inválidas.
LAT_MIN, LAT_MAX = -23.08, -22.74
LON_MIN, LON_MAX = -43.80, -43.09

# CRS métrico para áreas e distâncias (SIRGAS 2000 / UTM 23S).
CRS_METRICO = "EPSG:31983"
