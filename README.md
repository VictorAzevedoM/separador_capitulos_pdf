# 📚 Separador de Capítulos de PDF

Ferramenta de linha de comando em Python que pega livros em PDF e gera PDFs menores separados por capítulos, utilizando os **bookmarks** (sumário/índice) embutidos no próprio PDF para identificar automaticamente os capítulos.

## ✨ Funcionalidades

- **Separação automática** de capítulos usando os bookmarks do PDF
- **Níveis configuráveis** de profundidade (partes, capítulos, seções)
- **Modo listar** para visualizar a estrutura antes de separar
- **Nomes organizados** com prefixo numérico sequencial
- **Sanitização** de caracteres especiais nos nomes de arquivo

## 📋 Pré-requisitos

- Python 3.10+
- Biblioteca `PyPDF2`

## 🚀 Instalação

```bash
git clone https://github.com/VictorAzevedoM/separador_capitulos_pdf.git
cd separador_capitulos_pdf
pip install -r requirements.txt
```

## 🔧 Uso

### Separar por capítulos (padrão)

```bash
python separador.py livro.pdf
```

### Separar por partes principais (nível 0)

```bash
python separador.py livro.pdf --nivel 0
```

### Separar por seções detalhadas (nível 2)

```bash
python separador.py livro.pdf --nivel 2
```

### Apenas listar a estrutura do PDF

```bash
python separador.py livro.pdf --listar
```

### Definir pasta de saída personalizada

```bash
python separador.py livro.pdf --saida ./meus_capitulos
```

### Sem prefixo numérico nos nomes

```bash
python separador.py livro.pdf --sem-prefixo
```

## 📂 Estrutura de saída

Por padrão, os PDFs são gerados em uma pasta `<nome_do_pdf>_capitulos/`:

```
livro_capitulos/
├── 01 - Capítulo 1 Introdução.pdf
├── 02 - Capítulo 2 Fundamentos.pdf
├── 03 - Capítulo 3 Aplicações.pdf
└── ...
```

## ⚙️ Argumentos da CLI

| Argumento       | Curto | Descrição                                               | Padrão             |
| --------------- | ----- | ------------------------------------------------------- | ------------------ |
| `pdf`           | —     | Caminho do arquivo PDF (obrigatório)                    | —                  |
| `--nivel`       | `-n`  | Nível de profundidade (0=partes, 1=capítulos, 2=seções) | `1`                |
| `--saida`       | `-s`  | Pasta de saída para os PDFs gerados                     | `<pdf>_capitulos/` |
| `--listar`      | `-l`  | Apenas listar estrutura sem gerar PDFs                  | `false`            |
| `--sem-prefixo` | —     | Não adicionar prefixo numérico nos nomes                | `false`            |

## 🏗️ Arquitetura do código

O script `separador.py` é composto por módulos funcionais:

| Função                    | Descrição                                                           |
| ------------------------- | ------------------------------------------------------------------- |
| `extrair_bookmarks()`     | Lê os bookmarks do PDF e monta uma árvore hierárquica de `Bookmark` |
| `achatar_bookmarks()`     | Converte a árvore em lista plana, filtrando por nível máximo        |
| `identificar_capitulos()` | Identifica início/fim de cada capítulo a partir dos bookmarks       |
| `sanitizar_nome()`        | Remove caracteres inválidos para nomes de arquivo                   |
| `gerar_pdfs()`            | Cria os PDFs separados usando `PdfWriter`                           |
| `listar_estrutura()`      | Imprime a árvore de bookmarks no terminal                           |

### Dataclass principal

```python
@dataclass
class Bookmark:
    titulo: str       # Título do bookmark
    pagina: int       # Página (0-indexed)
    nivel: int        # Profundidade na hierarquia (0=raiz)
    filhos: list      # Sub-bookmarks
```

## ⚠️ Limitações

- O PDF **precisa ter bookmarks** embutidos. PDFs sem sumário/índice interno não podem ser processados automaticamente.
- A separação é feita com base nos bookmarks — se eles estiverem incorretos no PDF original, a separação também será.

## 📄 Licença

MIT
