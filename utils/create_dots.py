import os
import sys
import re
import logging

logger = logging.getLogger(__name__)

def extrair_todos_os_digraphs(conteudo):
    """
    Extrai todos os blocos 'digraph <nome> {...}' de uma string.
    Esta função lida corretamente com chaves aninhadas e extrai o nome de cada digraph.

    Args:
        conteudo (str): O conteúdo do arquivo para pesquisar.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário contém o 'nome'
              e o 'conteúdo' de um digraph encontrado. Ex: [{'nome': 'ex1', 'conteudo': '...'}, ...]
    """
    digraphs_encontrados = []
    offset = 0 # Posição inicial para a busca no texto

    while True:
        try:
            # Procura a próxima ocorrência de "digraph" a partir do offset atual
            start_keyword_idx = conteudo.find('digraph', offset)
            if start_keyword_idx == -1:
                break # Se não encontrar mais, encerra o loop

            # Encontra a primeira chave de abertura após a palavra "digraph"
            open_brace_idx = conteudo.find('{', start_keyword_idx)
            if open_brace_idx == -1:
                # Se não encontrar a chave, avança o offset para evitar loop infinito
                offset = start_keyword_idx + len('digraph')
                continue

            # --- Extração do Nome do Digraph ---
            header = conteudo[start_keyword_idx:open_brace_idx]
            # Usa uma expressão regular para encontrar o nome (primeira palavra após 'digraph')
            match = re.search(r'digraph\s+([a-zA-Z0-9_]+)', header)
            if not match:
                # Digraph anônimo ou malformado, pula para o próximo
                offset = open_brace_idx + 1
                logger.warning("Aviso: Encontrado um digraph sem nome ou malformado. Ignorando.")
                continue
            
            digraph_name = match.group(1)

            # --- Encontrar a Chave de Fechamento Correspondente ---
            brace_count = 1
            search_idx = open_brace_idx + 1
            
            while search_idx < len(conteudo) and brace_count > 0:
                if conteudo[search_idx] == '{':
                    brace_count += 1
                elif conteudo[search_idx] == '}':
                    brace_count -= 1
                search_idx += 1

            if brace_count == 0:
                # Bloco completo encontrado
                bloco_conteudo = conteudo[start_keyword_idx : search_idx]
                digraphs_encontrados.append({
                    'nome': digraph_name,
                    'conteudo': bloco_conteudo
                })
                # Atualiza o offset para continuar a busca APÓS o bloco encontrado
                offset = search_idx
            else:
                # Bloco malformado (não fechou chaves), avança para não ficar preso
                offset = open_brace_idx + 1

        except Exception as e:
            logger.exception("Ocorreu um erro inesperado durante a análise do conteúdo: %s", e)
            break # Encerra em caso de erro grave

    return digraphs_encontrados

def processar_arquivos_out(diretorio_raiz):
    """
    Percorre um diretório, encontra arquivos .out, extrai todos os digraphs nomeados
    e cria os arquivos .dot correspondentes.
    """
    if not os.path.isdir(diretorio_raiz):
        logger.error("Erro: O diretório '%s' não foi encontrado.", diretorio_raiz)
        return
    logger.info("Iniciando a busca por arquivos *.out em '%s'...", diretorio_raiz)
    
    arquivos_out_encontrados = 0
    total_dots_criados = 0

    for dirpath, _, filenames in os.walk(diretorio_raiz):
        for filename in filenames:
            if filename.endswith('.out'):
                arquivos_out_encontrados += 1
                caminho_arquivo_out = os.path.join(dirpath, filename)
                logger.info("Processando arquivo: %s", caminho_arquivo_out)

                try:
                    with open(caminho_arquivo_out, 'r', encoding='utf-8', errors='ignore') as f:
                        conteudo = f.read()
                    
                    lista_de_digraphs = extrair_todos_os_digraphs(conteudo)

                    if not lista_de_digraphs:
                        logger.info("Nenhum digraph nomeado foi encontrado em: %s", caminho_arquivo_out)
                        continue

                    for digraph_info in lista_de_digraphs:
                        nome_dot = f"{digraph_info['nome']}.dot"
                        conteudo_dot = digraph_info['conteudo']
                        caminho_arquivo_dot = os.path.join(dirpath, nome_dot)

                        with open(caminho_arquivo_dot, 'w', encoding='utf-8') as f_out:
                            f_out.write(conteudo_dot)
                        
                        logger.info("Digraph '%s' extraído. Arquivo criado: %s", digraph_info['nome'], caminho_arquivo_dot)
                        total_dots_criados += 1
                    
                    logger.debug("") # separador visual (debug)

                except Exception as e:
                    logger.exception("Erro ao processar o arquivo %s: %s", caminho_arquivo_out, e)

    logger.info("--------------------------------------------------")
    logger.info("Processo concluído.")
    logger.info("Total de arquivos .out encontrados: %d", arquivos_out_encontrados)
    logger.info("Total de arquivos .dot criados: %d", total_dots_criados)
    logger.info("--------------------------------------------------")

# --- INÍCIO DA CONFIGURAÇÃO ---
# IMPORTANTE: Altere esta variável para o caminho da pasta raiz do seu projeto.
DIRETORIO_PROJETO = "." 
# --- FIM DA CONFIGURAÇÃO ---

if __name__ == "__main__":
    if len(sys.argv) > 1:
        DIRETORIO_PROJETO = sys.argv[1]
    
    processar_arquivos_out(DIRETORIO_PROJETO)