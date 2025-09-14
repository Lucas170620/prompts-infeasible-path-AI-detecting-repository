import os
import sys
import re

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
                print(f"  -> Aviso: Encontrado um digraph sem nome ou malformado. Ignorando.")
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
            print(f"  -> Ocorreu um erro inesperado durante a análise do conteúdo: {e}")
            break # Encerra em caso de erro grave

    return digraphs_encontrados

def processar_arquivos_out(diretorio_raiz):
    """
    Percorre um diretório, encontra arquivos .out, extrai todos os digraphs nomeados
    e cria os arquivos .dot correspondentes.
    """
    if not os.path.isdir(diretorio_raiz):
        print(f"Erro: O diretório '{diretorio_raiz}' não foi encontrado.")
        return

    print(f"Iniciando a busca por arquivos *.out em '{diretorio_raiz}'...\n")
    
    arquivos_out_encontrados = 0
    total_dots_criados = 0

    for dirpath, _, filenames in os.walk(diretorio_raiz):
        for filename in filenames:
            if filename.endswith('.out'):
                arquivos_out_encontrados += 1
                caminho_arquivo_out = os.path.join(dirpath, filename)
                print(f"Processando arquivo: {caminho_arquivo_out}")

                try:
                    with open(caminho_arquivo_out, 'r', encoding='utf-8', errors='ignore') as f:
                        conteudo = f.read()
                    
                    lista_de_digraphs = extrair_todos_os_digraphs(conteudo)

                    if not lista_de_digraphs:
                        print("  -> Nenhum digraph nomeado foi encontrado neste arquivo.\n")
                        continue

                    for digraph_info in lista_de_digraphs:
                        nome_dot = f"{digraph_info['nome']}.dot"
                        conteudo_dot = digraph_info['conteudo']
                        caminho_arquivo_dot = os.path.join(dirpath, nome_dot)

                        with open(caminho_arquivo_dot, 'w', encoding='utf-8') as f_out:
                            f_out.write(conteudo_dot)
                        
                        print(f"  -> Digraph '{digraph_info['nome']}' extraído. Arquivo criado: {caminho_arquivo_dot}")
                        total_dots_criados += 1
                    
                    print("") # Adiciona uma linha em branco para separar os arquivos

                except Exception as e:
                    print(f"  -> Erro ao processar o arquivo {caminho_arquivo_out}: {e}\n")

    print("--------------------------------------------------")
    print("Processo concluído.")
    print(f"Total de arquivos .out encontrados: {arquivos_out_encontrados}")
    print(f"Total de arquivos .dot criados: {total_dots_criados}")
    print("--------------------------------------------------")

# --- INÍCIO DA CONFIGURAÇÃO ---
# IMPORTANTE: Altere esta variável para o caminho da pasta raiz do seu projeto.
DIRETORIO_PROJETO = "." 
# --- FIM DA CONFIGURAÇÃO ---

if __name__ == "__main__":
    if len(sys.argv) > 1:
        DIRETORIO_PROJETO = sys.argv[1]
    
    processar_arquivos_out(DIRETORIO_PROJETO)