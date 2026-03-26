import logging
import utils as utils
from core import configs

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == '__main__':

    logging.info("Iniciando processo de ingestão")

    try:
        df = utils.ingestion(configs)
        logging.info("Ingestão realizada com sucesso")
    except Exception as e:
        logging.error(f"Erro de ingestão de dados: {e}")
        raise

    try:
        utils.preparation(df, configs)
        logging.info("Fim do processo com sucesso")
    except Exception as e:
        logging.error(f"Erro de preparação: {e}")
        raise