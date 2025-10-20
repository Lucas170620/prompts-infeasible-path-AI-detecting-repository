import concurrent.futures
import logging
import os
from random import random
import re
import time
from typing import List, Any

from ia_prompt_integration import IAIntegration

ia_integration = IAIntegration()
OUTPUT_BASE = 'output'
# será atualizado em main para output/<code_name>
OUTPUT_DIR = OUTPUT_BASE

def load_markdown_file(caminho_arquivo: str) -> str:
    print(f"Iniciando: load_markdown_file -> {caminho_arquivo}")
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo_markdown = arquivo.read()
            print(f"Finalizado: load_markdown_file -> {caminho_arquivo}")
            return conteudo_markdown
    except FileNotFoundError:
        print(f"Arquivo não encontrado!: {caminho_arquivo}")
        print(f"Finalizado (com erro): load_markdown_file -> {caminho_arquivo}")
        return ""
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        print(f"Finalizado (com erro): load_markdown_file -> {caminho_arquivo}")
        return ""

def process_code(path: str) -> str:
    print(f"Iniciando: process_code -> {path}")
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except Exception as e:
        print(f"Erro em process_code ao abrir arquivo: {e}")
        print(f"Finalizado (com erro): process_code -> {path}")
        raise
    encodings_to_try = [
        'utf-8',
        'utf-8-sig',
        'utf-16',
        'utf-16-le',
        'utf-16-be',
        'cp1252',
        'latin-1',
    ]
    text = None
    for enc in encodings_to_try:
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue

    if text is None:
        text = raw.decode('utf-8', errors='replace')

    if '\x00' in text:
        text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.rstrip() for ln in text.split('\n')]
    text = '\n'.join(lines)
    text = text.strip('\n') + ('\n' if text.endswith('\n') else '')
    MAX_CHARS = 500_000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    print(f"Finalizado: process_code -> {path}")
    return text


def prompt_fetch_all_functions(code: str) -> list:
    caminho_prompt = "fetch_all_functions.md"
    print("Iniciando: prompt_fetch_all_functions")
    conteudo_markdown = load_markdown_file(caminho_prompt)

    # clearer separation for LLM: wrap code block and prompt body with '---' separators
    prompt = "[code]\n" + code + "\n---\n" + conteudo_markdown
    path_save = os.path.join(OUTPUT_DIR, 'functions_list.txt')
    path_reasoning = os.path.join(OUTPUT_DIR, 'reasoning_fetch_all_functions.txt')
    path_prompt = os.path.join(OUTPUT_DIR, 'prompt_fetch_all_functions.txt')
    reasoning, response = ia_integration.fetch_response(prompt)
    try:
        functions = [func.strip() for func in response.split('\n') if func.strip()]
    except Exception as e:
        print(f"Erro ao parsear lista de funções: {e}")
        print("Finalizado (com erro): prompt_fetch_all_functions")
        raise
    with open(path_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
    with open(path_save, 'w', encoding='utf-8') as f:
        for func in functions:
            f.write(func + '\n')
    with open(path_reasoning, 'w', encoding='utf-8') as f:
        f.write(reasoning if reasoning else "No reasoning provided")
    print("Finalizado: prompt_fetch_all_functions -> {} funções encontradas".format(len(functions)))
    return functions
    
def prompt_generate_cdfg(function: str, code: str) -> str:
    caminho_prompt = "generate_cdfg.md"
    path_save = os.path.join(OUTPUT_DIR, 'cdfg_' + function + '.txt')
    path_reasoning = os.path.join(OUTPUT_DIR, 'reasoning_cdfg_' + function + '.txt')
    path_prompt = os.path.join(OUTPUT_DIR, 'prompt_cdfg_' + function + '.txt')
    print(f"Iniciando: prompt_generate_cdfg -> {function}")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    # clearer separation for LLM: wrap code block and prompt body with '---' separators
    prompt = "[code]\n" + code + "\n---\n" + conteudo_markdown.replace("{substitua aqui o nome da funcao}", function)
    resoning, response = ia_integration.fetch_response(prompt)
    try:
        with open(path_save, 'w', encoding='utf-8') as f:
            f.write(response)
        with open(path_prompt, 'w', encoding='utf-8') as f:
            f.write(prompt)
        with open(path_reasoning, 'w', encoding='utf-8') as f:
            f.write(resoning if resoning else "No reasoning provided")
    except Exception as e:
        print(f"Erro ao salvar cdfg_{function}.txt: {e}")
    print(f"Finalizado: prompt_generate_cdfg -> {function}")
    return response

def extrair_todos_os_digraphs(conteudo: str) -> list:
    print("Iniciando: extrair_todos_os_digraphs")
    digraphs_encontrados = []
    offset = 0

    while True:
        try:
            start_keyword_idx = conteudo.find('digraph', offset)
            if start_keyword_idx == -1:
                break

            open_brace_idx = conteudo.find('{', start_keyword_idx)
            if open_brace_idx == -1:
                offset = start_keyword_idx + len('digraph')
                continue

            header = conteudo[start_keyword_idx:open_brace_idx]
            match = re.search(r'digraph\s+([a-zA-Z0-9_]+)', header)
            if not match:
                offset = open_brace_idx + 1
                continue

            digraph_name = match.group(1)

            brace_count = 1
            search_idx = open_brace_idx + 1
            while search_idx < len(conteudo) and brace_count > 0:
                if conteudo[search_idx] == '{':
                    brace_count += 1
                elif conteudo[search_idx] == '}':
                    brace_count -= 1
                search_idx += 1

            if brace_count == 0:
                bloco_conteudo = conteudo[start_keyword_idx:search_idx]
                digraphs_encontrados.append({'nome': digraph_name, 'conteudo': bloco_conteudo})
                offset = search_idx
            else:
                offset = open_brace_idx + 1

        except Exception:
            break

    print("Finalizado: extrair_todos_os_digraphs -> {} digraphs encontrados".format(len(digraphs_encontrados)))
    return digraphs_encontrados

def save_cdfg_output(code_name: str, func_name: str, conteudo: str) -> None:
    print(f"Iniciando: save_cdfg_output -> {code_name} / {func_name}")
    out_dir = os.path.join(OUTPUT_BASE, code_name)
    os.makedirs(out_dir, exist_ok=True)

    lista = extrair_todos_os_digraphs(conteudo)
    if lista:
        for dig in lista:
            nome_dot = f"{dig['nome']}.dot"
            caminho = os.path.join(out_dir, nome_dot)
            try:
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(dig['conteudo'])
            except Exception as e:
                logging.getLogger(__name__).exception("Failed to write dot file %s: %s", caminho, e)
    else:
        nome_dot = f"{func_name}.dot"
        caminho = os.path.join(out_dir, nome_dot)
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to write dot file %s: %s", caminho, e)
    print(f"Finalizado: save_cdfg_output -> {code_name} / {func_name}")

def prompt_detecting_all_infeasible_paths(result_per_function: dict, code_cleaned: str) -> str:
    caminho_prompt = "detecting_all_infeasible_paths.md"
    print("Iniciando: prompt_detecting_all_infeasible_paths")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    functions = list(result_per_function.keys())
    # clearer separation for LLM: wrap each major section with '---' separators
    prompt = "[code]\n" + code_cleaned + "\n---\n"
    for func in functions:
        cdfg_content = result_per_function[func]['cdfg'] if result_per_function[func]['cdfg'] else ""
        infeasible_content = result_per_function[func]['infeasible_paths'] if result_per_function[func]['infeasible_paths'] else ""
        prompt += "\n---\n[cdfg " + func + "]\n" + cdfg_content + "\n---\n"
        prompt += "\n---\n[analise infeasible_paths " + func + "]\n" + infeasible_content + "\n---\n"
    
    prompt += "\n---\n" + conteudo_markdown + "\n---\n"
    reasoning, resposta = ia_integration.fetch_response(prompt)
    path_save = os.path.join(OUTPUT_DIR, 'infeasible_paths_all_functions.txt')
    path_reasoning = os.path.join(OUTPUT_DIR, 'reasoning_infeasible_paths_all_functions.txt')
    path_prompt_final = os.path.join(OUTPUT_DIR, 'final_prompt_infeasible_paths_all_functions.txt')
    try:
        with open(path_save, 'w', encoding='utf-8') as f:
            f.write(resposta)
        with open(path_reasoning, 'w', encoding='utf-8') as f:
            f.write(reasoning if reasoning else "No reasoning provided")
        with open(path_prompt_final, 'w', encoding='utf-8') as f:
            f.write(prompt)
    except Exception as e:
        print(f"Erro ao salvar infeasible_paths_all_functions.txt: {e}")
    print("Finalizado: prompt_detecting_all_infeasible_paths")
    return resposta

def prompt_detecting_infeasible_paths_in_function(cdfg: str, function: str, code_cleaned: str) -> str:
    caminho_prompt = "detecting_all_infeasible_paths_in_function.md"
    print(f"Iniciando: prompt_detecting_infeasible_paths_in_function -> {function}")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    # clearer separation for LLM: delimit code and cdfg sections with '---'
    prompt =  "[code]\n" + code_cleaned + "\n---\n[cdfg]\n" + cdfg + "\n---\n" + conteudo_markdown.replace("INSIRA AQUI A FUNÇÃO", function)
    reasoning, out = ia_integration.fetch_response(prompt)


    path_save = os.path.join(OUTPUT_DIR, 'infeasible_paths_' + function + '.txt')
    path_reasoning = os.path.join(OUTPUT_DIR, 'reasoning_infeasible_paths_' + function + '.txt')
    path_prompt = os.path.join(OUTPUT_DIR, 'prompt_infeasible_paths_' + function + '.txt')
    try:
        with open(path_prompt, 'w', encoding='utf-8') as f:
            f.write(prompt)
        with open(path_save, 'w', encoding='utf-8') as f:
            f.write(out)
        with open(path_reasoning, 'w', encoding='utf-8') as f:
            f.write(reasoning if reasoning else "No reasoning provided")
    except Exception as e:
        print(f"Erro ao salvar infeasible_paths_{function}.txt: {e}")
    print(f"Finalizado: prompt_detecting_infeasible_paths_in_function -> {function}")
    return out if out else "No infeasible paths detected"

def process_code_file(code: str):

    print(f"Iniciando: process_code_file -> {code}")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    path = os.path.join('codes', code)
    code_name = os.path.splitext(os.path.basename(path))[0]
    # configurar diretório de saída para este código: output/<code_name>
    global OUTPUT_DIR
    OUTPUT_DIR = os.path.join(OUTPUT_BASE, code_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    code = process_code(path)
    try:
        with open(os.path.join(OUTPUT_DIR, 'original_code.txt'), 'w', encoding='utf-8') as f:
            f.write(code)
    except Exception as e:
        logger.exception("Failed to save original_code.txt: %s", e)

    result_per_function : dict = {}

    # dicionario para cada funcao -> cdfg e infeasible paths

    try:
        functions = prompt_fetch_all_functions(code)
    except Exception as e:
        logger.exception("Failed to fetch functions (serial): %s", e)
        functions = []

    if functions is None:
        functions = []
    print(f"Functions found: {functions}")
    for func in functions:
        print(f"Processing function: {func}")
        try:
            cdfg = prompt_generate_cdfg(func, code)
            infeasible_paths = prompt_detecting_infeasible_paths_in_function(cdfg, func, code)
            result_per_function[func] = {'cdfg': cdfg, 'infeasible_paths': infeasible_paths}
        except Exception as e:
            logger.exception("CDFG generation failed for function %s (serial): %s", func, e)
            result_per_function[func] = {'cdfg': None, 'infeasible_paths': None}
    print(result_per_function)

    # salvar saídas dos CDFGs (ambos os modos)
    try:
        for func_name, cdfg_content in zip(functions, [result_per_function[f]['cdfg'] for f in functions]):
            if cdfg_content:
                save_cdfg_output(code_name, func_name, cdfg_content)
            else:
                logger.info("No CDFG content for function %s, skipping save", func_name)
    except Exception as e:
        logger.exception("Failed while saving CDFG outputs: %s", e)

    try:
        infeasible_paths = prompt_detecting_all_infeasible_paths(result_per_function, code)
    except Exception as e:
        logger.exception("Infeasible path detection failed: %s", e)
        infeasible_paths = None

    print(f"Finalizado: process_code_file -> {code}")

def main():
    """Varre o diretório 'codes' e executa o processamento para cada arquivo regular encontrado."""
    print("Iniciando: main - scanning 'codes' directory")
    codes_dir = 'codes'
    if not os.path.isdir(codes_dir):
        print(f"Diretório não encontrado: {codes_dir}")
        return

    entries = sorted(os.listdir(codes_dir))
    files = [e for e in entries if os.path.isfile(os.path.join(codes_dir, e))]

    if not files:
        print("Nenhum arquivo encontrado em 'codes/'.")
        return

    for fname in files:
        print(f"==== Iniciando processamento do arquivo: {fname} ====")
        try:
            process_code_file(fname)
        except Exception as e:
            logging.getLogger(__name__).exception("Erro ao processar %s: %s", fname, e)
        print(f"==== Finalizado processamento do arquivo: {fname} ====")

    print("Finalizado: main - todos os códigos processados")

if __name__ == "__main__":
    main()
