# Sistema Distribuído de Sincronização de Arquivos (Python RMI) 🔄🖧

> **Projeto acadêmico desenvolvido para a disciplina de Sistemas Distribuídos do curso de Bacharelado em Ciência da Computação — UNESP.**

---

## 📚 Contexto Acadêmico e Objetivo

Este projeto implementa um sistema distribuído cliente-servidor de **sincronização automática de arquivos (arquitetura Master/Slave)** utilizando o paradigma de **Invocação de Método Remoto (RMI / RPC)** exclusivamente com a biblioteca padrão do Python.

### Conceitos de Sistemas Distribuídos Trabalhados:
* **Comunicação Cliente-Servidor e Stubs Remotos (`client/stub.py`, `interface/remote_interface.py`):** Abstração de chamadas de rede como invocações locais.
* **Autenticação e Controle de Sessão (`common/auth.py`):** Validação de credenciais antes da sincronização de estado.
* **Consistência e Monitoramento Contínuo (`client/sync_monitor.py`):** Verificação periódica de integridade via *checksum/hash* e replicação automática de atualizações do arquivo *Master* para os nós *Slaves*.

---

## Pré-requisitos

* Python 3.12.x

## Configuração (Setup)

1.  **Clonar/Baixar:** Obtenha os arquivos do projeto para o seu sistema.
2.  **Configurar Usuários (Opcional):** Edite `server/users.json` para adicionar/modificar nomes de usuário e senhas autorizados. O padrão é `{"admin": "password123", "client1": "syncpass"}`.
3.  **Arquivo Master Inicial (Opcional):** Você pode modificar o conteúdo inicial de `server/master.txt`. Se ele não existir, o servidor o criará com conteúdo padrão.

## Executando o Sistema

1.  **Iniciar o Servidor:**
    Abra um terminal, navegue até o diretório `sync_rmi_project` e execute:
    ```bash
    python -m server.server_main
    ```
    O servidor começará a escutar na porta 8000 por padrão. Os logs aparecerão no console e serão escritos em `server/sync.log`.

2.  **Iniciar o Cliente:**
    Abra outro terminal, navegue até o diretório `sync_rmi_project` e execute:
    ```bash
    python -m client.client_main
    ```
    O cliente solicitará a você:
    * Endereço do servidor (ex: `localhost:8000`)
    * Nome de usuário (deve corresponder a uma chave em `users.json`)
    * Senha (deve corresponder à senha para o nome de usuário em `users.json`)
    * Modo de comunicação (R, RR ou RRA - o padrão é RR se deixado em branco).

    Uma vez iniciado, o cliente executará um monitor de sincronização automático em segundo plano, verificando periodicamente o servidor por mudanças no `master.txt` com base no modo de comunicação escolhido. A verificação inicial provavelmente acionará uma sincronização se `slave.txt` não existir ou diferir.

## Testando

1.  **Sincronização Inicial:** Execute o cliente. Ele deve realizar uma verificação inicial e potencialmente baixar o conteúdo de `master.txt` para `client/slave.txt`. Verifique o conteúdo de `slave.txt`.
2.  **Modificar Master:** Enquanto o cliente e o servidor estiverem rodando, edite e salve alterações em `server/master.txt`.
3.  **Atualização Automática:** Aguarde o próximo intervalo de sincronização do cliente (padrão de 15 segundos). Observe a saída do console do cliente – ele deve detectar a mudança e atualizar `client/slave.txt`. Verifique o conteúdo de `slave.txt` novamente.
4.  **Autenticação:** Tente executar o cliente com credenciais incorretas. Os logs do servidor (`sync.log`) devem mostrar falhas de autenticação, e o cliente deve reportar erros.
5.  **Modos de Comunicação:** Execute o cliente várias vezes, especificando modos diferentes (R, RR, RRA) na inicialização. Observe a saída do console (cliente e servidor) e os logs do servidor (`sync.log`) para ver evidências do modo escolhido (ex: mensagens de ACK para RR/RRA).
6.  **Concorrência:** Inicie múltiplas instâncias do cliente simultaneamente (conectando com credenciais válidas). O servidor deve lidar com elas concorrentemente graças ao uso de threads. Modifique `master.txt` e veja se todos os clientes eventualmente sincronizam.
7.  **Logs:** Examine `server/sync.log` para registros detalhados de tentativas de conexão, resultados de autenticação, chamadas de método, sucessos/falhas de sincronização e confirmações (acknowledgments).

## Como os Conceitos são Implementados (Comentários no Código)

* **Interface Remota (IDL):** Definida conceitualmente em `interface/remote_interface.py`.
* **Proxy/Stub:** Implementado em `client/stub.py` (classe `RemoteFileStub`).
* **Skeleton/Dispatcher:** Implementado em `server/dispatcher.py` (classe `RMIDispatcherHandler`).
* **Esqueletos Dinâmicos:** Usado dentro de `RMIDispatcherHandler.do_POST` via `getattr(service_object, method_name)`.
* **Ativação Dinâmica:** Instância de `FileHandler` criada dentro de `RMIDispatcherHandler` quando necessário (poderia ser otimizado para reutilizar a instância).
* **Threads no Servidor:** Realizado usando `socketserver.ThreadingMixIn` em `server/server_main.py`.
* **Persistência Simples:** Tratada pela leitura/escrita de `master.txt` (`FileHandler`) e `slave.txt` (`SyncMonitor`), e carregamento de `users.json`.
* **Binder com Autenticação Simples:** Implementado dentro de `RMIDispatcherHandler.do_POST` chamando `common.auth.authenticate`.
* **Estilos de Protocolo (R, RR, RRA):** Lógica implementada em `client/stub.py` (enviando requisições/ACKs) e `server/dispatcher.py` (tratando requisições, registrando ACKs). Modo indicado no console/logs.
* **Registro de Logs:** Gerenciado pela configuração do módulo `logging` em `server/dispatcher.py`, escrevendo para `server/sync.log`.
* **Detecção Automática de Alterações:** Implementada em `client/sync_monitor.py` chamando periodicamente `stub.check_master_version` (que obtém o hash do arquivo) e comparando com a versão local.