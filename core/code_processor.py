import logging
import os
from typing import Dict

from utils.file_utils import FileUtils
from ai.ia_client import IAClient
from utils.models import FunctionResult
from core.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class CodeProcessor:
    """Processa um arquivo de código: leitura, geração de CDFGs e detecção de caminhos inviáveis."""

    def __init__(self, ia_client: IAClient, output_base: str = "output"):
        self.file_utils = FileUtils()
        self.ia_client = ia_client
        self.output_base = output_base

    def process_code(self, path: str) -> str:
        logger.info("Iniciando: process_code -> %s", path)
        try:
            text = self.file_utils.safe_read_text(path)
            logger.info("Finalizado: process_code -> %s", path)
            return text
        except Exception as e:
            logger.exception("Erro em process_code ao abrir arquivo %s: %s", path, e)
            logger.info("Finalizado (com erro): process_code -> %s", path)
            raise

    def process_code_file(self, code: str) -> None:
        logger.info("Iniciando: process_code_file -> %s", code)

        path = os.path.join("codes", code)
        code_name = os.path.splitext(os.path.basename(path))[0]

        output_dir = os.path.join(self.output_base, code_name)
        prompt_builder = PromptBuilder(self.ia_client, output_dir, self.file_utils)
        prompt_builder._ensure_dirs()

        code_text = self.process_code(path)
        try:
            self.file_utils.write_text_file(os.path.join(output_dir, "original_code.txt"), code_text)
        except Exception as e:
            logger.exception("Failed to save original_code.txt: %s", e)

        result_per_function: Dict[str, FunctionResult] = {}

        try:
            functions = prompt_builder.fetch_all_functions(code_text)
        except Exception as e:
            logger.exception("Failed to fetch functions (serial): %s", e)
            functions = []

        if functions is None:
            functions = []
        logger.info("Functions found: %s", functions)
        for func in functions:
            logger.info("Processing function: %s", func)
            try:
                cdfg = prompt_builder.generate_cdfg(func, code_text)
                infeasible_paths = prompt_builder.detecting_infeasible_paths_in_function(cdfg, func, code_text)
                result_per_function[func] = FunctionResult(cdfg=cdfg, infeasible_paths=infeasible_paths)
            except Exception as e:
                logger.exception("CDFG generation failed for function %s (serial): %s", func, e)
                result_per_function[func] = FunctionResult(cdfg=None, infeasible_paths=None)

        logger.debug("Result per function: %s", result_per_function)
        try:
            _ = prompt_builder.detecting_all_infeasible_paths(result_per_function, code_text)
        except Exception as e:
            logger.exception("Infeasible path detection failed: %s", e)

        logger.info("Finalizado: process_code_file -> %s", code_name)
