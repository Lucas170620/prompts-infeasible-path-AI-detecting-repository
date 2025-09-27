Criar um prompt que peça para ele criar explciitamente o grafo no formato https://graphviz.org/doc/info/lang.html

- Explicar o que é o CFG (control flow graph) e DFG (Data flow graph)
- Mostrar modelo de grafos no graphviz

- Experiemntar montar um grafo por arquivo ou um grafo por função

Anotacao 16-09
- juntar os grafos DFG e CFG em um
- declaração , definição , re-definição , uso -> explicar os conceitos
- considerar prompt para cada função/método um grafo


Anotacoes :
- Na terceira e segunda rodada nota algumas respostas que nao houve a construcao de nenhum grafo , outros incompletos
- primeira rodada ele tentou fazer um grafo só para todo o código
- para codigos muitos grandes ou com muitos métodos ele lista um como exemplo

Fazer um teste em um prompt com pipeline na quinta tentatca
-> ideia de pipeline:

- Lista métodos e funções : usar um prompt para identificar os métodos e função
- Identificação do ponto de entrada geral do código , se houver
- para cada uma das funções usar um prompt especifico para aquela função para gerar dos CDFG identificando quais infeasible paths
- salvar esses grafos
- Fazer uma analise completa de todos os grafos apartir do ponto de entada

- Para a rodada 4 como ele indicava aonde estava os infeasible paths , decidi não fazer os que CONTA a quantida , isto é prompt 2 , 4 ,6 