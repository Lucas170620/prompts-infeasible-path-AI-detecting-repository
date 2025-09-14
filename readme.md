# Prompts - Infeasible Paths Detection

Este repositório reúne prompts de inteligência artificial e utilitários para analisar a ocorrência de "infeasible paths" em testes estruturais de código. O objetivo principal é armazenar, processar e visualizar representações gráficas (Graphviz) extraídas de saídas de ferramentas de análise, facilitando a inspeção e investigação de caminhos impossíveis ou não cobertos nos testes.

## Estrutura do repositório

- `primeira/`, `segunda/`, `terceira/`: pastas com prompts organizados por etapa e exemplos.
- `codes/`: exemplos de códigos em C usados como referência para geração de saídas.
- Scripts utilitários (documentados abaixo):
  - `create_dots.py`  — extrai blocos `digraph` de arquivos `.out` e gera `.dot` separados.
  - `convert_svg.py`  — remove acentos de arquivos `.dot` e (opcionalmente) gera `.svg` usando Graphviz.
  - `exclude_dots_svg.py` — exclui arquivos gerados `.dot` e `.svg` em massa.

## Requisitos

- Python 3.6+ (recomendado 3.8+)
- (Opcional) Graphviz instalado e disponível no PATH para gerar SVGs a partir de `.dot` (usado por `convert_svg.py`).

No Windows, instale Graphviz a partir de: https://graphviz.org/download/ e adicione o diretório bin (`dot.exe`) ao PATH.

## Scripts utilitários

Cada script abaixo é documentado com o que faz, argumentos e exemplos de uso.

### 1) `create_dots.py`

O que faz
- Percorre uma pasta (recursivamente) procurando arquivos com extensão `.out`.
- Em cada `.out`, procura blocos `digraph <nome> { ... }`, mesmo que contenham chaves aninhadas, e cria um arquivo `<nome>.dot` para cada digraph nomeado encontrado.

Como usar

1. Coloque o script no diretório raiz do projeto (ou aponte o diretório desejado como argumento).
2. Execute:

```powershell
python create_dots.py
```

Exemplo

```powershell
python create_dots.py
```

Notas
- O script ignora digraphs anônimos ou malformados (exibe um aviso) e grava os arquivos `.dot` no mesmo diretório onde o `.out` foi encontrado.

### 2) `convert_svg.py`

O que faz
- Procura por arquivos `.dot` no diretório atual e subdiretórios.
- Remove acentos do conteúdo dos arquivos `.dot` (substitui caracteres acentuados por suas formas básicas).
- Se o utilitário `dot` do Graphviz estiver disponível no PATH, converte cada `.dot` em `.svg` (gera `<nome>.svg`). Caso contrário, avisa e apenas remove os acentos.

Como usar

```powershell
python convert_svg.py
```

Notas importantes
- Para que a conversão para SVG funcione, instale o Graphviz e verifique se o comando `dot` está acessível no PATH do sistema. O script detecta automaticamente a presença do comando e continua mesmo se estiver ausente (apenas removerá acentos).

### 3) `exclude_dots_svg.py`

O que faz
- Percorre um diretório e suas subpastas e exclui permanentemente todos os arquivos com extensão `.dot` e `.svg`.
- Antes de excluir, pede confirmação explícita (digite `s` para confirmar).

Como usar

```powershell
python exclude_dots_svg.py
```

Exemplo

```powershell
python exclude_dots_svg.py
```

Cuidados
- Esta ação é irreversível: os arquivos são removidos do disco. Verifique o caminho exibido pelo script antes de confirmar.

## Fluxo de uso sugerido

1. Execute ferramentas/analyses que gerem arquivos `.out` (fora deste repositório).
2. Rode `create_dots.py` apontando para a pasta com os `.out` para extrair os `digraphs` em arquivos `.dot` individuais.
3. Rode `convert_svg.py` para limpar acentos e gerar visualizações `.svg` (se tiver Graphviz instalado).
4. Se quiser limpar os arquivos gerados, execute `exclude_dots_svg.py` e confirme a exclusão.