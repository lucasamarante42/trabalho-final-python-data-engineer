"""
Configuration of all relevant parameters to use in the project
"""

from pathlib import Path
from typing import List
from pydantic import BaseModel
from strictyaml import load

# Paths
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
ASSETS_PATH = PACKAGE_ROOT / "assets"
CONFIG_FILE_PATH = ASSETS_PATH / "config.yml"


# =========================
# CONFIG MODELS
# =========================

class DataConfig(BaseModel):
    """
    Configuração da ingestão e validação
    """
    input_api: str
    results: int
    required_columns: List[str]


class DatabaseConfig(BaseModel):
    """
    Configuração do banco
    """
    db_path: str
    table_name: str


class Config(BaseModel):
    """
    Configuração geral
    """
    data: DataConfig
    database: DatabaseConfig


# =========================
# LOAD + VALIDATION
# =========================

def create_and_validate_config(cfg_path=CONFIG_FILE_PATH) -> Config:
    """
    Carrega e valida o config.yml
    """

    try:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read()).data
    except Exception:
        raise OSError(f"Config não encontrado em: {cfg_path}")

    config = Config(
        data=DataConfig(**parsed_config["data"]),
        database=DatabaseConfig(**parsed_config["database"]),
    )

    return config


# Objeto global (igual aula 04)
configs = create_and_validate_config()


if __name__ == '__main__':
    print(configs)