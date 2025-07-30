
# App da Federação Brasileira de Krav Maga e Kapap - Leão do Norte

![Logo da Federação](assets/icon.jpg)

## Visão Geral do Projeto

O App da Federação Leão do Norte é uma plataforma digital exclusiva para alunos e instrutores, projetada para centralizar o acesso a materiais de treinamento, facilitar a análise de performance e acompanhar a evolução técnica dos praticantes de Krav Maga e Kapap.

A aplicação utiliza uma interface moderna e responsiva construída com [Flet](https://flet.dev/), permitindo seu uso em desktops e dispositivos móveis.

**Versão Atual:** 0.2.0

---

## Roadmap de Desenvolvimento

Este roadmap destaca o progresso do projeto e os próximos passos planejados, oferecendo uma visão clara da evolução do produto.

### ✔️ **Fase 1: Fundação e MVP (Concluído)**
-   [x] **Estrutura do Projeto:** Arquitetura modular com separação de responsabilidades (`src`, `assets`, `tests`).
-   [x] **Interface Inicial:** Criação das telas de Login e Dashboard com Flet.
-   [x] **Autenticação Real:** Implementação de um sistema de login seguro que valida usuários a partir de uma planilha do Google Sheets.
-   [x] **UI/UX Refinada:** Design responsivo, com foco em acessibilidade e legibilidade para todos os públicos.

### ⏳ **Fase 2: Liberação de Conteúdo e Ferramentas (Em Andamento)**
-   [ ] **Controle de Acesso por Graduação:** Implementar a lógica para exibir conteúdo (PDFs e Vídeos) com base na faixa do aluno (faixa atual + próxima).
-   [ ] **Visualizador de PDF:** Criar a tela "Programa Técnico" que exibe os PDFs das faixas liberadas.
-   [ ] **Player de Vídeo:** Criar a tela "Vídeos de Movimentos" que exibe os vídeos das técnicas liberadas.
-   [ ] **Integração do Analisador:** Migrar e adaptar o "Analisador de Movimentos" (Projeto 1) para dentro do App da Federação.

### 🚀 **Fase 3: Expansão e Ecossistema (Futuro)**
-   [ ] **Módulo de Cursos:** Desenvolver a funcionalidade de cursos para assinantes.
-   [ ] **Gamificação:** Introduzir elementos de gamificação para acompanhar o progresso e engajar os alunos.
-   [ ] **Área do Instrutor:** Criar um painel para instrutores gerenciarem seus alunos e turmas.
-   [ ] **Migração para Banco de Dados:** Substituir a planilha por um banco de dados robusto (ex: Firebase, Supabase) para escalar a aplicação.

---

## Tecnologias Utilizadas

-   **Python 3.11**
-   **Flet:** Para a construção da interface gráfica multiplataforma.
-   **Pandas:** Para leitura e manipulação de dados da planilha de alunos.
-   **OpenCV:** Para processamento de vídeo no módulo de análise.
-   **MediaPipe:** Para a detecção de pose e extração de landmarks corporais.
-   **Matplotlib:** Para a renderização do esqueleto em 3D.
-   **FPDF2:** Para a geração de relatórios de análise em PDF.

---

## Como Instalar e Rodar o Projeto

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/atnzpe/app_fbkmkln.git](https://github.com/atnzpe/app_fbkmkln.git)
    cd app_fbkmkln
    ```

2.  **Crie e Ative um Ambiente Virtual:**
    * No Windows:
        ```powershell
        py -3.11 -m venv .venv
        .\.venv\Scripts\activate
        ```
    * No macOS/Linux:
        ```bash
        python3.11 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a Aplicação:**
    Certifique-se de que a pasta `assets` com o `icon.jpg` está na raiz do projeto.
    ```bash
    flet run main.py
    ```
---

## Estrutura do Projeto


app_fbkmkln/
|-- assets/
|   |-- icon.png
|   |-- videos_tecnicas/
|   `-- programa_tecnico/
|
|-- src/
|   |-- __init__.py               <-- (Boa prática adicionar este arquivo)
|   |-- auth.py
|   |-- motion_comparator.py
|   |-- pose_estimator.py
|   |-- renderer_3d.py
|   |-- report_generator.py
|   |-- utils.py
|   `-- video_analyzer.py
|
|-- tests/
|
|-- main.py                       <-- MOVIDO PARA A RAIZ
|-- README.md
|-- requirements.txt
`-- flet.yml


## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues, propor melhorias ou enviar pull requests.



## Licença

Este projeto está licenciado sob a [Apache](LICENSE.md).

