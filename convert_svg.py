import os
import unicodedata
import subprocess
import shutil

def remover_acentos(texto):
    """
    Remove acentos de uma string, convertendo para o caractere base.
    Exemplo: 'olá, mundo!' se torna 'ola, mundo!'.
    """
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def processar_arquivos_dot():
    """
    Varre o diretório atual e subdiretórios em busca de arquivos .dot,
    remove os acentos do conteúdo e gera um SVG para cada um.
    """
    # Verifica se o comando 'dot' do Graphviz está disponível
    if not shutil.which("dot"):
        print("---------------------------------------------------------------")
        print(" ATENÇÃO: O comando 'dot' do Graphviz não foi encontrado.")
        print(" Por favor, instale o Graphviz e adicione-o ao PATH do seu sistema.")
        print(" Download: https://graphviz.org/download/")
        print(" O script continuará apenas removendo os acentos.")
        print("---------------------------------------------------------------")
        gerar_svg = False
    else:
        gerar_svg = True

    diretorio_atual = '.'
    for raiz, _, arquivos in os.walk(diretorio_atual):
        for nome_arquivo in arquivos:
            if nome_arquivo.endswith('.dot'):
                caminho_arquivo_dot = os.path.join(raiz, nome_arquivo)
                nome_base = os.path.splitext(nome_arquivo)[0]
                caminho_arquivo_svg = os.path.join(raiz, f"{nome_base}.svg")

                print(f"\nProcessando arquivo: {caminho_arquivo_dot}")
                
                try:
                    # 1. Remove acentos do arquivo .dot
                    with open(caminho_arquivo_dot, 'r', encoding='utf-8') as f:
                        conteudo = f.read()

                    conteudo_sem_acentos = remover_acentos(conteudo)

                    with open(caminho_arquivo_dot, 'w', encoding='utf-8') as f:
                        f.write(conteudo_sem_acentos)
                    
                    print(f"-> Acentos removidos de: {nome_arquivo}")

                    # 2. Gera o arquivo SVG usando Graphviz, se disponível
                    if gerar_svg:
                        comando = [
                            "dot",
                            "-Tsvg",
                            caminho_arquivo_dot,
                            "-o",
                            caminho_arquivo_svg
                        ]
                        
                        subprocess.run(comando, check=True, capture_output=True, text=True)
                        print(f"-> SVG gerado em: {caminho_arquivo_svg}")

                except FileNotFoundError:
                    print(f"ERRO: Arquivo não encontrado: {caminho_arquivo_dot}")
                except subprocess.CalledProcessError as e:
                    print(f"ERRO ao gerar SVG para {nome_arquivo}:")
                    print(f"   Comando: {' '.join(e.cmd)}")
                    print(f"   Erro: {e.stderr}")
                except Exception as e:
                    print(f"Ocorreu um erro inesperado ao processar o arquivo {caminho_arquivo_dot}: {e}")

if __name__ == "__main__":
    processar_arquivos_dot()
    print("\nProcesso concluído.")