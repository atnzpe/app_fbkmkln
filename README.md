# App da Federação Brasileira de Krav Maga e Kapap - Leão do Norte

![Logo da Federação](assets/icon.jpg)

## Visão Geral do Projeto

O App da Federação Leão do Norte é uma plataforma digital exclusiva para alunos e instrutores, projetada para centralizar o acesso a materiais de treinamento, facilitar a análise de performance e acompanhar a evolução técnica dos praticantes de Krav Maga e Kapap.

A aplicação utiliza uma interface moderna e responsiva construída com [Flet](https://flet.dev/), permitindo seu uso em desktops e dispositivos móveis.

**Versão Atual:** 0.1.0

---

## Funcionalidades Planejadas

-   **Login Seguro:** Autenticação de usuários (alunos e instrutores) via CPF e Senha.
-   **Acesso por Graduação:** Liberação de conteúdo (vídeos e documentos) de acordo com a faixa do aluno, permitindo o acesso à sua graduação atual e à próxima.
-   **Biblioteca de Vídeos:** Acesso a uma videoteca completa com todas as técnicas do programa, organizadas por faixa.
-   **Programa Técnico Digital:** Visualização do programa técnico oficial em PDF diretamente no aplicativo.
-   **Analisador de Movimentos:** Uma ferramenta integrada (Projeto 1) que utiliza Visão Computacional para comparar a execução de um movimento pelo aluno com um vídeo de referência do mestre.
-   **Plataforma de Cursos (Futuro):** Módulo para acesso a cursos e conteúdos exclusivos para assinantes.
-   **Mídias Sociais:** Acesso rápido às redes sociais oficiais da Federação.

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

