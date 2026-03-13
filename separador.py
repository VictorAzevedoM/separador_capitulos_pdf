#!/usr/bin/env python3
"""
Separador de Capítulos de PDF
==============================
Sistema que lê um livro em PDF e gera PDFs menores separados por capítulos,
utilizando os bookmarks (sumário) do próprio PDF para identificar os capítulos.

Uso:
    python separador.py livro.pdf
    python separador.py livro.pdf --nivel 1
    python separador.py livro.pdf --nivel 2 --saida pasta_destino
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field

from PyPDF2 import PdfReader, PdfWriter


# ──────────────────────────────────────────────
# Modelos de dados
# ──────────────────────────────────────────────


@dataclass
class Bookmark:
    """Representa um bookmark (marcador) do PDF."""

    titulo: str
    pagina: int  # 0-indexed
    nivel: int  # profundidade na hierarquia (0 = raiz)
    filhos: list = field(default_factory=list)


# ──────────────────────────────────────────────
# Extração de bookmarks
# ──────────────────────────────────────────────


def extrair_bookmarks(reader: PdfReader) -> list[Bookmark]:
    """Extrai todos os bookmarks do PDF mantendo a hierarquia."""

    def _parse(items, nivel=0) -> list[Bookmark]:
        resultado = []
        for item in items:
            if isinstance(item, list):
                # Sub-lista → filhos do último bookmark adicionado
                if resultado:
                    resultado[-1].filhos = _parse(item, nivel + 1)
            else:
                pagina = reader.get_destination_page_number(item)
                bm = Bookmark(
                    titulo=item.title.strip(),
                    pagina=pagina,
                    nivel=nivel,
                )
                resultado.append(bm)
        return resultado

    outline = reader.outline
    if not outline:
        return []
    return _parse(outline)


def achatar_bookmarks(
    bookmarks: list[Bookmark], nivel_max: int | None = None
) -> list[Bookmark]:
    """
    Achata a árvore de bookmarks em uma lista plana, filtrando por nível máximo.
    Útil para iterar sequencialmente sobre os capítulos.
    """
    resultado = []
    for bm in bookmarks:
        if nivel_max is None or bm.nivel <= nivel_max:
            resultado.append(bm)
        resultado.extend(achatar_bookmarks(bm.filhos, nivel_max))
    return resultado


# ──────────────────────────────────────────────
# Identificação dos capítulos
# ──────────────────────────────────────────────


def identificar_capitulos(
    bookmarks: list[Bookmark],
    total_paginas: int,
    nivel: int = 1,
) -> list[dict]:
    """
    Identifica os capítulos a partir dos bookmarks.

    Args:
        bookmarks: lista hierárquica de bookmarks
        total_paginas: número total de páginas do PDF
        nivel: nível de profundidade para separação
               0 = partes principais (ex: I – Fonética, II – Morfologia)
               1 = capítulos (ex: Capítulo 1, Capítulo 2)
               2 = seções dentro dos capítulos

    Returns:
        lista de dicts com {titulo, pagina_inicio, pagina_fim}
    """
    # Achata tudo e filtra pelo nível desejado
    todos = achatar_bookmarks(bookmarks)
    capitulos_bm = [bm for bm in todos if bm.nivel == nivel]

    if not capitulos_bm:
        print(f"⚠  Nenhum bookmark encontrado no nível {nivel}.")
        print("   Níveis disponíveis:")
        niveis = sorted(set(bm.nivel for bm in todos))
        for n in niveis:
            exemplos = [bm.titulo for bm in todos if bm.nivel == n][:3]
            print(f"   Nível {n}: {', '.join(exemplos)}...")
        return []

    # Ordena por página
    capitulos_bm.sort(key=lambda b: b.pagina)

    # Calcula início e fim de cada capítulo
    capitulos = []
    for i, bm in enumerate(capitulos_bm):
        inicio = bm.pagina
        if i + 1 < len(capitulos_bm):
            fim = capitulos_bm[i + 1].pagina - 1
        else:
            fim = total_paginas - 1

        capitulos.append(
            {
                "titulo": bm.titulo,
                "pagina_inicio": inicio,
                "pagina_fim": fim,
            }
        )

    return capitulos


# ──────────────────────────────────────────────
# Sanitização de nomes de arquivo
# ──────────────────────────────────────────────


def sanitizar_nome(nome: str) -> str:
    """Remove caracteres inválidos e ajusta o nome para uso como arquivo."""
    # Remove/substitui caracteres problemáticos
    nome = nome.replace("/", "-").replace("\\", "-")
    nome = re.sub(r'[<>:"|?*]', "", nome)
    # Reduz espaços múltiplos
    nome = re.sub(r"\s+", " ", nome).strip()
    # Limita comprimento
    if len(nome) > 120:
        nome = nome[:120].strip()
    return nome


# ──────────────────────────────────────────────
# Geração dos PDFs separados
# ──────────────────────────────────────────────


def gerar_pdfs(
    caminho_pdf: str,
    capitulos: list[dict],
    pasta_saida: str,
    prefixo_numerico: bool = True,
) -> list[str]:
    """
    Gera um PDF separado para cada capítulo.

    Returns:
        lista com os caminhos dos PDFs gerados
    """
    reader = PdfReader(caminho_pdf)
    os.makedirs(pasta_saida, exist_ok=True)
    arquivos_gerados = []

    for idx, cap in enumerate(capitulos, start=1):
        writer = PdfWriter()

        for pag in range(cap["pagina_inicio"], cap["pagina_fim"] + 1):
            writer.add_page(reader.pages[pag])

        # Monta nome do arquivo
        titulo_limpo = sanitizar_nome(cap["titulo"])
        if prefixo_numerico:
            nome_arquivo = f"{idx:02d} - {titulo_limpo}.pdf"
        else:
            nome_arquivo = f"{titulo_limpo}.pdf"

        caminho_saida = os.path.join(pasta_saida, nome_arquivo)

        with open(caminho_saida, "wb") as f:
            writer.write(f)

        n_paginas = cap["pagina_fim"] - cap["pagina_inicio"] + 1
        print(f"  ✅ {nome_arquivo}  ({n_paginas} páginas)")
        arquivos_gerados.append(caminho_saida)

    return arquivos_gerados


# ──────────────────────────────────────────────
# Listar estrutura do PDF
# ──────────────────────────────────────────────


def listar_estrutura(bookmarks: list[Bookmark], indent: int = 0):
    """Imprime a estrutura de bookmarks do PDF de forma visual."""
    for bm in bookmarks:
        marcador = "📁" if bm.filhos else "📄"
        print(
            f"{'  ' * indent}{marcador} [Nível {bm.nivel}] [Pág {bm.pagina + 1}] {bm.titulo}"
        )
        if bm.filhos:
            listar_estrutura(bm.filhos, indent + 1)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="📚 Separador de Capítulos de PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s livro.pdf                      Separa por capítulos (nível 1)
  %(prog)s livro.pdf --nivel 0            Separa por partes principais
  %(prog)s livro.pdf --nivel 2            Separa por seções
  %(prog)s livro.pdf --listar             Mostra a estrutura sem separar
  %(prog)s livro.pdf -s ./meus_capitulos  Define pasta de saída
        """,
    )
    parser.add_argument("pdf", help="Caminho do arquivo PDF")
    parser.add_argument(
        "--nivel",
        "-n",
        type=int,
        default=1,
        help="Nível de profundidade para separação (0=partes, 1=capítulos, 2=seções). Padrão: 1",
    )
    parser.add_argument(
        "--saida",
        "-s",
        type=str,
        default=None,
        help="Pasta de saída para os PDFs gerados. Padrão: <nome_do_pdf>_capitulos/",
    )
    parser.add_argument(
        "--listar",
        "-l",
        action="store_true",
        help="Apenas listar a estrutura de bookmarks sem gerar PDFs",
    )
    parser.add_argument(
        "--sem-prefixo",
        action="store_true",
        help="Não adicionar prefixo numérico nos nomes dos arquivos",
    )

    args = parser.parse_args()

    # Validações
    if not os.path.isfile(args.pdf):
        print(f"❌ Arquivo não encontrado: {args.pdf}")
        sys.exit(1)

    print(f"\n📖 Abrindo: {args.pdf}")
    reader = PdfReader(args.pdf)
    total_paginas = len(reader.pages)
    print(f"   Total de páginas: {total_paginas}")

    # Extrai bookmarks
    bookmarks = extrair_bookmarks(reader)
    if not bookmarks:
        print("❌ Este PDF não possui bookmarks/sumário embutido.")
        print("   Não é possível identificar os capítulos automaticamente.")
        sys.exit(1)

    total_bm = len(achatar_bookmarks(bookmarks))
    print(f"   Bookmarks encontrados: {total_bm}")

    # Modo listar
    if args.listar:
        print("\n📋 Estrutura do PDF:\n")
        listar_estrutura(bookmarks)
        return

    # Identifica capítulos
    print(f"\n🔍 Identificando capítulos no nível {args.nivel}...\n")
    capitulos = identificar_capitulos(bookmarks, total_paginas, nivel=args.nivel)

    if not capitulos:
        sys.exit(1)

    print(f"   {len(capitulos)} capítulo(s) identificado(s)\n")

    # Define pasta de saída
    if args.saida:
        pasta_saida = args.saida
    else:
        nome_base = os.path.splitext(os.path.basename(args.pdf))[0]
        pasta_saida = os.path.join(
            os.path.dirname(args.pdf) or ".", f"{nome_base}_capitulos"
        )

    print(f"📂 Gerando PDFs em: {pasta_saida}\n")

    # Gera os PDFs
    arquivos = gerar_pdfs(
        args.pdf,
        capitulos,
        pasta_saida,
        prefixo_numerico=not args.sem_prefixo,
    )

    print(f"\n🎉 Concluído! {len(arquivos)} arquivo(s) gerado(s) em: {pasta_saida}\n")


if __name__ == "__main__":
    main()
