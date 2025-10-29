import os
import sys
import logging

logger = logging.getLogger(__name__)

def limpar_arquivos_gerados(diretorio_raiz):
    """
    Percorre um diretório e suas subpastas para excluir todos os arquivos
    com as extensões .dot e .svg.

    Args:
        diretorio_raiz (str): O caminho para a pasta principal a ser limpa.
    """
    # Verifica se o diretório fornecido realmente existe
    if not os.path.isdir(diretorio_raiz):
        logger.error("Erro: O diretório '%s' não foi encontrado.", diretorio_raiz)
        return

    # Pega o caminho absoluto para mostrar ao usuário de forma clara
    caminho_abs = os.path.abspath(diretorio_raiz)

    logger.warning("========================= AVISO =========================")
    logger.warning("Este script irá excluir PERMANENTEMENTE todos os arquivos com as extensões *.dot e *.svg dentro da pasta: %s", caminho_abs)
    logger.warning("Esta ação não pode ser desfeita.")
    logger.warning("=========================================================")

    # Etapa de confirmação para segurança
    try:
        confirmacao = input("Você tem certeza absoluta de que deseja continuar? (Digite 's' para sim): ")
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário.")
        return

    if confirmacao.lower() != 's':
        logger.info("Operação cancelada. Nenhum arquivo foi excluído.")
        return

    logger.info("Iniciando a exclusão dos arquivos .dot e .svg...")
    
    arquivos_excluidos = 0
    # os.walk percorre a árvore de diretórios
    for dirpath, _, filenames in os.walk(diretorio_raiz):
        for filename in filenames:
            # CONDIÇÃO ATUALIZADA: Verifica se o arquivo termina com .dot OU .svg
            # O método endswith() aceita uma tupla de strings.
            if filename.endswith(('.dot', '.svg')):
                caminho_completo = os.path.join(dirpath, filename)
                try:
                    # Tenta excluir o arquivo
                    os.remove(caminho_completo)
                    logger.info("Excluído: %s", caminho_completo)
                    arquivos_excluidos += 1
                except OSError as e:
                    # Captura erros caso não consiga excluir (ex: falta de permissão)
                    logger.exception("Erro ao tentar excluir %s: %s", caminho_completo, e)

    logger.info("\n--------------------------------------------------")
    logger.info("Processo concluído.")
    if arquivos_excluidos == 0:
        logger.info("Nenhum arquivo .dot ou .svg foi encontrado para excluir.")
    else:
        logger.info("Total de arquivos (.dot e .svg) excluídos: %d", arquivos_excluidos)
    logger.info("--------------------------------------------------")


# --- INÍCIO DA CONFIGURAÇÃO ---
# IMPORTANTE: Altere esta variável para o caminho da pasta raiz do seu projeto.
# Usar "." significa que o script vai rodar no diretório atual.
DIRETORIO_PROJETO = "." 
# --- FIM DA CONFIGURAÇÃO ---


if __name__ == "__main__":
    # Permite passar o diretório como argumento na linha de comando
    if len(sys.argv) > 1:
        DIRETORIO_PROJETO = sys.argv[1]
    
    limpar_arquivos_gerados(DIRETORIO_PROJETO)