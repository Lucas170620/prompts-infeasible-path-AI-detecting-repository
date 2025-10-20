Você é um especialista em análise estática de código e engenharia de software. Sua tarefa é processar o código fornecido para remover todos os elementos desnecessários para análise de fluxo de dados em testes estruturais (como cobertura de código). Realize as seguintes ações:

1. **Remova comentários** (linhas únicas e blocos).  
2. **Remova espaços em branco redundantes** e linhas vazias excessivas (mantenha no máximo 1 linha vazia entre blocos lógicos).  
3. **Preserve intacta** a estrutura do código, incluindo:  
   - Declarações de variáveis/funções.  
   - Estruturas de controle (if/for/while/etc.).  
   - Expressões e atribuições.  
   - Chamadas de função.  
4. **Mantenha a indentação** original para garantir legibilidade.  

**Saída Esperada:**  
Forneça **apenas o código limpo** em formato de texto, sem explicações adicionais.  

**Exemplo de Entrada (para referência):**  
```python
# Calcula a média
def avg(x, y):
    # Soma os valores
    s = x + y
    return s / 2  # Retorna a média
```

**Saída Correspondente:**  
```python
def avg(x, y):
    s = x + y
    return s / 2
```