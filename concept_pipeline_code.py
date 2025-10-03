import concurrent.futures
import logging
import os
from random import random
import re
import time
from typing import List, Any

from ia_prompt_integration import IAIntegration

ia_integration = IAIntegration()

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

def prompt_code_cleaning(code: str) -> str:
    caminho_prompt = "quinta/clean_code.md"
    print("Iniciando: prompt_code_cleaning")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    prompt = conteudo_markdown + "\n[code]\n" + code
    out = ia_integration.fetch_response(prompt)
    with open('code_clean.txt', 'w', encoding='utf-8') as f:
        f.write(out)
    print("Finalizado: prompt_code_cleaning")
    return out

def prompt_fetch_all_functions(code: str) -> list:
    caminho_prompt = "quinta/fetch_all_functions.md"
    print("Iniciando: prompt_fetch_all_functions")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    prompt = conteudo_markdown + "\n[code]\n" + code
    out = ia_integration.fetch_response(prompt)
    try:
        functions = [func.strip() for func in out.split('\n') if func.strip()]
    except Exception as e:
        print(f"Erro ao parsear lista de funções: {e}")
        print("Finalizado (com erro): prompt_fetch_all_functions")
        raise
    with open('functions_list.txt', 'w', encoding='utf-8') as f:
        for func in functions:
            f.write(func + '\n')
    print("Finalizado: prompt_fetch_all_functions -> {} funções encontradas".format(len(functions)))
    return functions

def prompt_generate_entrypoint(code: str) -> str:
    caminho_prompt = "quinta/fetch_input_code.md"
    print("Iniciando: prompt_generate_entrypoint")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    prompt = conteudo_markdown + "\n[code]\n" + code
    out = ia_integration.fetch_response(prompt)
    with open('entrypoint.txt', 'w', encoding='utf-8') as f:
        f.write(out)
    print("Finalizado: prompt_generate_entrypoint")
    return out

def prompt_generate_cdfg(function: str, code: str) -> str:
    caminho_prompt = "quinta/generate_cdfg.md"
    print(f"Iniciando: prompt_generate_cdfg -> {function}")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    prompt = conteudo_markdown.replace("{substitua aqui o nome da funcao}", function) + "\n[code]\n" + code
    out = ia_integration.fetch_response(prompt)
    try:
        with open(f'cdfg_{function}.txt', 'w', encoding='utf-8') as f:
            f.write(out)
    except Exception as e:
        print(f"Erro ao salvar cdfg_{function}.txt: {e}")
    print(f"Finalizado: prompt_generate_cdfg -> {function}")
    return out

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
    out_dir = os.path.join('quinta', code_name)
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

def prompt_detecting_all_infeasible_paths(cdfg: list, entrypoint: str, code_cleaned: str) -> str:
    caminho_prompt = "quinta/detecting_all_infeasible_paths.md"
    print("Iniciando: prompt_detecting_all_infeasible_paths")
    conteudo_markdown = load_markdown_file(caminho_prompt)
    prompt = conteudo_markdown + "\n[code]\n" + code_cleaned + "\n[entrypoint]\n" + entrypoint + "\n[cdfg]\n" + '\n'.join([c for c in cdfg if c])
    out = ia_integration.fetch_response(prompt)
    with open('infeasible_paths_output.txt', 'w', encoding='utf-8') as f:
        f.write(out)
    print("Finalizado: prompt_detecting_all_infeasible_paths")
    return out if out else "No infeasible paths detected"

def main():
    import argparse

    print("Iniciando: main")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Executa pipeline (parallel ou serial)")
    parser.add_argument('--mode', '-m', choices=['parallel', 'serial'], default='parallel',
                        help='Modo de execução: "parallel" (padrão) usa ThreadPool; "serial" executa em série')
    args = parser.parse_args()

    path = os.path.join('codes', 'fibcall.c')
    processed = process_code(path)
    cleaned = prompt_code_cleaning(processed)
    code_name = os.path.splitext(os.path.basename(path))[0]

    mode = args.mode
    logger.info("Execution mode: %s", mode)

    cdfgs: List[Any] = []

    if mode == 'parallel':
        # comportamento anterior: paraleliza a busca de funções, entrypoint e geração de CDFGs
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_functions = executor.submit(prompt_fetch_all_functions, cleaned)
            future_entry = executor.submit(prompt_generate_entrypoint, cleaned)

            try:
                functions = future_functions.result()
            except Exception as e:
                logger.exception("Failed to fetch functions: %s", e)
                functions = []

            if functions is None:
                functions = []

            cdfg_futures: List[concurrent.futures.Future] = []
            for func in functions:
                cdfg_futures.append(executor.submit(prompt_generate_cdfg, func, cleaned))

            waitables = list(cdfg_futures) + [future_entry]
            if waitables:
                concurrent.futures.wait(waitables, return_when=concurrent.futures.ALL_COMPLETED)

            for f in cdfg_futures:
                try:
                    cdfgs.append(f.result())
                except Exception as e:
                    logger.exception("CDFG generation failed for a function: %s", e)
                    cdfgs.append(None)

            try:
                entry = future_entry.result()
            except Exception as e:
                logger.exception("Entry generation failed: %s", e)
                entry = None

    else:  # serial
        # executar tudo de forma sequencial (sem threads)
        try:
            functions = prompt_fetch_all_functions(cleaned)
        except Exception as e:
            logger.exception("Failed to fetch functions (serial): %s", e)
            functions = []

        if functions is None:
            functions = []

        for func in functions:
            try:
                result = prompt_generate_cdfg(func, cleaned)
                cdfgs.append(result)
            except Exception as e:
                logger.exception("CDFG generation failed for function %s (serial): %s", func, e)
                cdfgs.append(None)

        try:
            entry = prompt_generate_entrypoint(cleaned)
        except Exception as e:
            logger.exception("Entry generation failed (serial): %s", e)
            entry = None

    # salvar saídas dos CDFGs (ambos os modos)
    try:
        for func_name, cdfg_content in zip(functions, cdfgs):
            if cdfg_content:
                save_cdfg_output(code_name, func_name, cdfg_content)
            else:
                logger.info("No CDFG content for function %s, skipping save", func_name)
    except Exception as e:
        logger.exception("Failed while saving CDFG outputs: %s", e)

    try:
        infeasible_paths = prompt_detecting_all_infeasible_paths(cdfgs, entry, cleaned)
    except Exception as e:
        logger.exception("Infeasible path detection failed: %s", e)
        infeasible_paths = None

    print("Finalizado: main")
        
if __name__ == "__main__":
    main()
