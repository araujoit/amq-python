# Processamento de Eventos RPC  

  
Desenvolvidos bots com o intuito de efetuar testes de processamento RPC
  
## Bots
- bot_eventos_test.py  
    Efetua a ingestão continua de eventos randômicos;  
- bot_pipeline.py  
    Controla o pipeline RPC;  
- bot_buscador_regras.py  
    Busca e popula as regras relacionadas;  
  
  
## Configuração
- Script de criação: mysql_script.sql  
- Script inicial de configuração: mysql_init_config.sql  
  

## Diagramas

### Bot Eventos Test
```mermaid
sequenceDiagram

bot_eventos_test.py ->> RabbitMQ: POST evento na fila fila_eventos_a_processar
Note right of bot_eventos_test.py: propriedades com valores randômicos
```

### Bot Pipeline
```mermaid
sequenceDiagram

bot_pipeline.py ->> RabbitMQ: consome evento na fila_eventos_a_processar
bot_pipeline.py ->> Database: persiste evento na tb_evento
bot_pipeline.py ->> RabbitMQ: cria fila para callback, com nome randômico
bot_pipeline.py ->> RabbitMQ: insere na fila_eventos_a_buscar_regras + propriedade de callback
RabbitMQ ->> bot_pipeline.py: devolve evento com regras encontradas
bot_pipeline.py ->> Database: persiste regras callback na tb_evento_regra 
```
  
### Bot Buscador Regras
```mermaid
sequenceDiagram

bot_buscador_regras.py ->> RabbitMQ: consome evento na fila_eventos_a_buscar_regras
bot_buscador_regras.py ->> Database: seleciona regras configuradas na tb_regra_campos
bot_buscador_regras.py ->> RabbitMQ: publica evento com regras encontradas na fila_callback
```

### Fluxo Completo
```mermaid
graph LR
BET[Bot Eventos Test] -. POST evento .-> R>RabbitMQ]
R -- consome evento --> BP[Bot Pipeline]
BP -. cria fila com nome randômico .-> R
BP -. insere evento .-> D
BP -. publica evento para busca de regras .-> R
BP -. insere regras encontradas .-> D
BBR -. insere evento com regras encontradas .-> R
R -- consome evento --> BBR[Bot Buscador Regras]
BBR -. busca regras configuradas .-> D(Database)
```
  
## Releases Futuros  
- Refatoração em classes; 
- Utilização de pattern;  


> Escrito com [StackEdit](https://stackedit.io/).