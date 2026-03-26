import requests
import sqlite3
import re
from typing import Any
import pandas as pd
from core import Config
import urllib3

def ingestion(configs: Config) -> pd.DataFrame:
    """
    Função de ingestão dos dados.
    Consome dados da api: https://randomuser.me, 10 resultados por página pelo menos.

    Args:
        configs (dict): Dicionário com configurações (ex: quantidade de registros).

    Returns:
        pd.DataFrame: DataFrame contendo os dados ingeridos da API.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = configs.data.input_api
    results = configs.data.results

    response = requests.get(url, params={"results": results}, verify=True)

    if response.status_code != 200:
        raise Exception(f"Erro na requisição: {response.status_code}")

    data = response.json()["results"]

    # Normalizando JSON para DataFrame
    df = pd.json_normalize(data)

    return df


def validation_inputs(df: pd.DataFrame, configs: Config) -> bool:
    """
    Valida se os dados estão no padrão esperado.

    Args:
        df (pd.DataFrame): DataFrame de entrada
        configs (Config): Configurações do projeto

    Raises:
        ValueError: Caso dados inválidos
    """

    required_columns = configs.data.required_columns

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        with open("assets/log.txt", "a") as f:
            f.write(f"Erro: colunas faltantes {missing}\n")
        raise ValueError(f"Colunas faltantes: {missing}")

    if df.empty:
        with open("assets/log.txt", "a") as f:
            f.write("Erro: DataFrame vazio\n")
        raise ValueError("DataFrame vazio")

    with open("assets/log.txt", "a") as f:
        f.write("Dados corretos\n")

    return True


def preparation(df: pd.DataFrame, configs: Config) -> pd.DataFrame:
    """
    Função de preparação dos dados:
        - Renomeia colunas
        - Ajusta tipo dos dados
        - Remove caracter especial

    Outputs:
        Salva dados tratados em base sqlite no diretorio assets
    """

    # =========================
    # Validação
    # =========================
    validation_inputs(df, configs)

    df = df.copy()

    # =========================
    # 1. Renomear colunas
    # =========================
    rename_map = {
        "name.first": "first_name",
        "name.last": "last_name",
        "email": "email",
        "dob.age": "age",
        "phone": "phone"
    }

    df = df.rename(columns=rename_map)

    # Selecionar só as colunas desejadas
    df = df[["first_name", "last_name", "email", "age", "phone"]]

    # =========================
    # 2. Ajustar tipos
    # =========================
    if "age" in df.columns:
        df["age"] = df["age"].astype(int)

    # =========================
    # 3. Remover caracteres especiais
    # =========================
    def clean_text(value: Any) -> Any:
        """
        Remove caracteres especiais de valores string.

        Args:
            value (Any): Valor de entrada

        Returns:
            Any: Valor limpo se for string, caso contrário retorna o mesmo valor
        """
        if isinstance(value, str):
            return re.sub(r"[^a-zA-Z0-9@. ]", "", value)
        return value

    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # =========================
    # 5. Salvar no SQLite
    # =========================
    db_path = configs.database.db_path
    table_name = configs.database.table_name

    conn = sqlite3.connect(db_path)

    df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.close()

    return df

