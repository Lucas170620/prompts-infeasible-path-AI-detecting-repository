import os
import unicodedata
import subprocess
import shutil
import logging

# Logger do módulo
logger = logging.getLogger(__name__)


def remover_acentos(texto: str) -> str:
    """
    Remove acentos de uma string, convertendo para o caractere base.
    
    Args:
        texto (str): A string de entrada que pode conter acentos.

    Returns:
        str: A string resultante sem acentos.
    
    Exemplo: 'olá, mundo!' se torna 'ola, mundo!'.
    """
    # Normaliza a string para a forma NFKD (Normalization Form Compatibility Decomposition)
    # Isso separa os caracteres base de seus acentos (marcas de combinação).
    nfkd_form = unicodedata.normalize('NFKD', texto)
    # Filtra e remove todas as marcas de combinação (acentos).
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def processar_arquivos_dot():
    """
    Varre o diretório atual e seus subdiretórios em busca de arquivos .dot.
    Para cada arquivo encontrado, remove os acentos de seu conteúdo e, em seguida,
    utiliza o Graphviz para gerar um arquivo SVG correspondente.
    """
    # 1. Verifica se o comando 'dot' do Graphviz está instalado e acessível no PATH.
    if not shutil.which("dot"):
        logger.warning("Graphviz 'dot' not found in PATH. SVG generation will be skipped.")
        logger.warning("Download: https://graphviz.org/download/")
        gerar_svg = False
    else:
        gerar_svg = True

    diretorio_atual = '.'
    arquivos_processados = 0

    # 2. Percorre todos os diretórios e arquivos a partir do local atual.
    for raiz, _, arquivos in os.walk(diretorio_atual):
        for nome_arquivo in arquivos:
            # 3. Verifica se o arquivo tem a extensão .dot.
            if nome_arquivo.endswith('.dot'):
                caminho_arquivo_dot = os.path.join(raiz, nome_arquivo)
                nome_base = os.path.splitext(nome_arquivo)[0]
                caminho_arquivo_svg = os.path.join(raiz, f"{nome_base}.svg")

                logger.info("Processing DOT file: %s", caminho_arquivo_dot)
                
                try:
                    # Bloco de tratamento de erros para cada arquivo.
                    
                    # 4. Lê o conteúdo do arquivo, remove os acentos e salva no mesmo arquivo.
                    with open(caminho_arquivo_dot, 'r', encoding='utf-8') as f:
                        conteudo = f.read()

                    conteudo_sem_acentos = remover_acentos(conteudo)

                    with open(caminho_arquivo_dot, 'w', encoding='utf-8') as f:
                        f.write(conteudo_sem_acentos)
                    
                    logger.info("Acentos removidos de: %s", nome_arquivo)

                    # 5. Se o Graphviz estiver disponível, gera o arquivo SVG.
                    if gerar_svg:
                        comando = [
                            "dot",
                            "-Tsvg",
                            caminho_arquivo_dot,
                            "-o",
                            caminho_arquivo_svg
                        ]
                        
                        # Executa o comando 'dot' e verifica se há erros.
                        resultado = subprocess.run(comando, check=True, capture_output=True, text=True, encoding='utf-8')
                        logger.info("SVG gerado com sucesso em: %s", caminho_arquivo_svg)
                    
                    arquivos_processados += 1

                except FileNotFoundError:
                    logger.error("Arquivo não encontrado: %s", caminho_arquivo_dot)
                except subprocess.CalledProcessError as e:
                    # Captura erros específicos da execução do comando 'dot'.
                    logger.exception("ERRO ao gerar SVG para %s; cmd=%s; stderr=%s", nome_arquivo, ' '.join(e.cmd), (e.stderr or '').strip())
                except Exception as e:
                    # Captura qualquer outro erro inesperado.
                    logger.exception("ERRO inesperado ao processar o arquivo %s: %s", caminho_arquivo_dot, e)

    if arquivos_processados > 0:
        logger.info("Processo concluído. %d arquivo(s) .dot foram processados.", arquivos_processados)
    else:
        logger.info("Processo concluído. Nenhum arquivo .dot foi encontrado para processar.")


if __name__ == "__main__":
    processar_arquivos_dot()
