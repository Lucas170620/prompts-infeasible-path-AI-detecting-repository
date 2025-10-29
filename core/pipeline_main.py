"""Controlador do pipeline: varre o diretório 'codes' e processa cada arquivo."""

import logging
import os

from ai.ia_client import IAClient
from core.code_processor import CodeProcessor
from ai.ia_prompt_integration import IAIntegration

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, codes_dir: str = "codes", output_base: str = "output"):
        self.codes_dir = codes_dir
        self.output_base = output_base
        self.ia_client = IAClient(IAIntegration())
        self.processor = CodeProcessor(self.ia_client, output_base=self.output_base)

    def run(self) -> None:
        logger.info("Iniciando: main - scanning 'codes' directory")
        if not os.path.isdir(self.codes_dir):
            logger.error("Diretório não encontrado: %s", self.codes_dir)
            return

        entries = sorted(os.listdir(self.codes_dir))
        files = [e for e in entries if os.path.isfile(os.path.join(self.codes_dir, e))]

        if not files:
            logger.warning("Nenhum arquivo encontrado em 'codes/'.")
            return

        for fname in files:
            logger.info("==== Iniciando processamento do arquivo: %s ====", fname)
            try:
                self.processor.process_code_file(fname)
            except Exception as e:
                logger.exception("Erro ao processar %s: %s", fname, e)
            logger.info("==== Finalizado processamento do arquivo: %s ====", fname)

        logger.info("Finalizado: main - todos os códigos processados")
