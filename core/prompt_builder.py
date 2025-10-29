import logging
import os
from typing import Dict, List, Optional

from utils.file_utils import FileUtils
from ai.ia_client import IAClient
from utils.models import FunctionResult

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Constrói prompts e orquestra chamadas à IA, gravando arquivos de saída."""

    def __init__(self, ia_client: IAClient, output_dir: str, file_utils: FileUtils):
        self.ia = ia_client
        self.output_dir = output_dir
        self.file_utils = file_utils

    def _ensure_dirs(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "prompts"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "reasonings"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "cdfgs"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "output_llm"), exist_ok=True)

    def fetch_all_functions(self, code: str) -> List[str]:
        caminho_prompt = "prompts/fetch_all_functions.md"
        logger.info("Iniciando: prompt_fetch_all_functions")
        template = self.file_utils.load_markdown_file(caminho_prompt)

        prompt = "[code]\n" + code + "\n---\n" + template

        path_save = os.path.join(self.output_dir, "output_llm", "functions_list.txt")
        path_reasoning = os.path.join(self.output_dir, "reasonings", "reasoning_fetch_all_functions.txt")
        path_prompt = os.path.join(self.output_dir, "prompts", "prompt_fetch_all_functions.txt")

        reasoning, response = self.ia.call(prompt)
        response = response or ""

        try:
            functions = [func.strip() for func in response.split("\n") if func.strip()]
        except Exception as e:
            logger.exception("Erro ao parsear lista de funções: %s", e)
            logger.info("Finalizado (com erro): prompt_fetch_all_functions")
            raise

        self.file_utils.write_text_file(path_prompt, prompt)
        self.file_utils.write_text_file(path_save, "\n".join(functions) + ("\n" if functions else ""))
        self.file_utils.write_text_file(path_reasoning, reasoning if reasoning else "No reasoning provided")

        logger.info("Finalizado: prompt_fetch_all_functions -> %d funções encontradas", len(functions))
        return functions

    def generate_cdfg(self, function: str, code: str) -> Optional[str]:
        caminho_prompt = "prompts/generate_cdfg.md"
        logger.info("Iniciando: prompt_generate_cdfg -> %s", function)
        template = self.file_utils.load_markdown_file(caminho_prompt)

        prompt = "[code]\n" + code + "\n---\n" + template.replace("{replace with function name here}", function)

        path_save = os.path.join(self.output_dir, "cdfgs", f"cdfg_{function}.txt")
        path_reasoning = os.path.join(self.output_dir, "reasonings", f"reasoning_cdfg_{function}.txt")
        path_prompt = os.path.join(self.output_dir, "prompts", f"prompt_cdfg_{function}.txt")

        reasoning, response = self.ia.call(prompt)
        self.file_utils.write_text_file(path_save, response or "")
        self.file_utils.write_text_file(path_prompt, prompt)
        self.file_utils.write_text_file(path_reasoning, reasoning if reasoning else "No reasoning provided")

        logger.info("Finalizado: prompt_generate_cdfg -> %s", function)
        return response

    def detecting_infeasible_paths_in_function(self, cdfg: Optional[str], function: str, code_cleaned: str) -> str:
        caminho_prompt = "prompts/detecting_all_infeasible_paths_in_function.md"
        logger.info("Iniciando: prompt_detecting_infeasible_paths_in_function -> %s", function)
        template = self.file_utils.load_markdown_file(caminho_prompt)
        cdfg_text = cdfg or ""

        prompt = "[code]\n" + code_cleaned + "\n---\n" + template.replace("<INSERT FUNCTION HERE>", function).replace("<INSERT CDFG HERE>", cdfg_text)

        reasoning, out = self.ia.call(prompt)

        path_save = os.path.join(self.output_dir, "output_llm", f"infeasible_paths_{function}.txt")
        path_reasoning = os.path.join(self.output_dir, "reasonings", f"reasoning_infeasible_paths_{function}.txt")
        path_prompt = os.path.join(self.output_dir, "prompts", f"prompt_infeasible_paths_{function}.txt")

        self.file_utils.write_text_file(path_prompt, prompt)
        self.file_utils.write_text_file(path_save, out or "")
        self.file_utils.write_text_file(path_reasoning, reasoning if reasoning else "No reasoning provided")

        logger.info("Finalizado: prompt_detecting_infeasible_paths_in_function -> %s", function)
        return out if out else "No infeasible paths detected"

    def detecting_all_infeasible_paths(self, result_per_function: Dict[str, FunctionResult], code_cleaned: str) -> str:
        caminho_prompt = "prompts/detecting_all_infeasible_paths.md"
        logger.info("Iniciando: prompt_detecting_all_infeasible_paths")
        template = self.file_utils.load_markdown_file(caminho_prompt)

        prompt = "[code]\n" + code_cleaned + "\n---\n"
        for func, entry in result_per_function.items():
            cdfg_content = entry.cdfg or ""
            infeasible_content = entry.infeasible_paths or ""
            prompt += f"\n---\n[cdfg {func}]\n{cdfg_content}\n---\n"
            prompt += f"\n---\n[analise infeasible_paths {func}]\n{infeasible_content}\n---\n"

        prompt += "\n---\n" + template + "\n---\n"

        reasoning, resposta = self.ia.call(prompt)

        path_save = os.path.join(self.output_dir, "output_llm", "infeasible_paths_all_functions.txt")
        path_reasoning = os.path.join(self.output_dir, "reasonings", "reasoning_infeasible_paths_all_functions.txt")
        path_prompt_final = os.path.join(self.output_dir, "prompts", "final_prompt_infeasible_paths_all_functions.txt")

        self.file_utils.write_text_file(path_save, resposta or "")
        self.file_utils.write_text_file(path_reasoning, reasoning if reasoning else "No reasoning provided")
        self.file_utils.write_text_file(path_prompt_final, prompt)

        logger.info("Finalizado: prompt_detecting_all_infeasible_paths")
        return resposta
