# Instruções para o GitHub Copilot / Agente AI
# =============================================
#
# Este arquivo serve como contexto para qualquer agente AI (Copilot, etc.)
# que venha a trabalhar neste projeto.

## Sobre o Projeto

Este é o **Separador de Capítulos de PDF** — uma ferramenta CLI em Python que:

1. Recebe um livro em PDF como entrada
2. Lê os **bookmarks** (outline/sumário embutido) do PDF
3. Identifica os capítulos com base na hierarquia dos bookmarks
4. Gera PDFs menores, um para cada capítulo

## Stack Técnica

- **Linguagem:** Python 3.10+
- **Biblioteca principal:** PyPDF2 (leitura/escrita de PDF)
- **Paradigma:** Funcional com dataclasses, script CLI com argparse
- **Arquivo principal:** `separador.py` (arquivo único, ~230 linhas)

## Arquitetura e Fluxo

```
PDF de entrada
    │
    ▼
extrair_bookmarks(reader)     → Árvore de Bookmark (hierárquica)
    │
    ▼
identificar_capitulos(...)    → Lista de {titulo, pagina_inicio, pagina_fim}
    │                            Filtra por nível de profundidade
    ▼
gerar_pdfs(...)               → PDFs individuais salvos em pasta de saída
```

### Modelo de dados central

```python
@dataclass
class Bookmark:
    titulo: str       # Título do bookmark no PDF
    pagina: int       # Número da página (0-indexed)
    nivel: int        # Profundidade hierárquica (0=raiz, 1=capítulo, 2=seção...)
    filhos: list      # Lista de Bookmark filhos
```

### Conceito de "nível"

Os bookmarks do PDF formam uma árvore. O "nível" determina a granularidade da separação:
- **Nível 0:** Partes principais do livro (ex: "PARTE I", "PARTE II")
- **Nível 1:** Capítulos individuais (ex: "Capítulo 1", "Capítulo 2") — **padrão**
- **Nível 2:** Seções dentro dos capítulos (ex: "1.1 Introdução", "1.2 Fundamentos")

### Cálculo do intervalo de páginas

Para cada bookmark de nível N, o **início** é sua própria página e o **fim** é
a página anterior ao próximo bookmark do mesmo nível (ou a última página do PDF
para o último bookmark).

## Convenções de Código

- Nomes de funções e variáveis em **português** (snake_case)
- Docstrings em português
- Emojis no output do terminal para UX amigável (✅ ❌ 📖 📂 🔍 🎉)
- Type hints em todas as funções
- Sem dependências além de PyPDF2

## Como Estender

### Adicionar novo formato de saída
Modifique `gerar_pdfs()` ou crie uma função paralela.

### Suportar PDFs sem bookmarks
Implementar detecção de capítulos por análise de texto (regex em títulos como
"Capítulo X", "CAPÍTULO X") usando `pdfplumber` (já no requirements.txt).

### Adicionar interface web
Considerar Flask/FastAPI + upload de arquivo + download ZIP dos capítulos.

## Testes

Ainda não há testes automatizados. Para testar manualmente:
```bash
# Listar estrutura
python separador.py livro.pdf --listar

# Separar por capítulos
python separador.py livro.pdf --nivel 1

# Verificar saída
ls -la livro_capitulos/
```

## Arquivos do Projeto

```
separador_capitulos_pdf/
├── separador.py          # Script principal (único arquivo de código)
├── requirements.txt      # Dependências Python
├── README.md             # Documentação do projeto
├── .github/
│   └── copilot-instructions.md  # ← ESTE ARQUIVO (contexto para AI)
└── .gitignore            # Ignora PDFs e pastas de saída
```
