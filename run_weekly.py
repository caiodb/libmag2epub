#!/usr/bin/env python3
"""
Newshit Weekly Runner - Pega APENAS a edição mais recente da Revista Liberta.

Rodar semanalmente (ex: toda segunda-feira) para baixar o lançamento da semana
e enviar automaticamente ao Kindle.

Uso:
    python run_weekly.py [última_edição_processada]

Exemplos:
    python run_weekly.py                # Processa a mais recente (nenhuma edição anterior)
    python run_weekly.py 40             # Processa desde da edição 41 em diante
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import RAW_DIR, EBOOK_DIR, PROJECT_ROOT
from src.scraper import IndexScraper
from src.orchestrator import PipelineOrchestrator


def get_latest_edition_number(last_processed: int | None) -> int:
    """
    Descobre qual é o número da edição mais recente no site.
    
    Args:
        last_processed: Número da última edição processada (None = começar do zero)
    
    Returns:
        Número da edição mais recente disponível
    """
    scraper = IndexScraper()
    editions = asyncio.run(scraper.get_available_editions())
    
    if not editions:
        print("❌ Nenhuma edição encontrada no site.")
        return 0
    
    # Extrair números das edições (ex: "edicao-42" → 42)
    edition_nums = []
    for slug in editions:
        try:
            num = int(slug.replace("edicao-", ""))
            edition_nums.append(num)
        except ValueError:
            continue
    
    if not edition_nums:
        print(f"❌ Não consegui extrair números das edições: {editions}")
        return 0
    
    latest = max(edition_nums)
    
    # Se last_processed for None, começar do zero
    start_num = last_processed if last_processed else 0
    
    print(f"\n{'='*60}")
    print(f"EDIÇÕES ENCONTRADAS NO SITE: {sorted(edition_nums)}")
    print(f"ÚLTIMA PROCESSADA ANTERIORMENTE: {last_processed}")
    print(f"EDIÇÃO MAIS RECENTE: #{latest}")
    
    if start_num >= latest:
        print(f"\n✅ Nenhuma nova edição desde a # {start_num}!")
        return 0
    
    next_edition = start_num + 1
    print(f"\n📦 PRÓXIMA EDIÇÃO PARA PROCESSAR: #{next_edition}")
    print(f"{'='*60}\n")
    
    return latest


async def main(last_processed: int | None = None) -> int:
    """
    Main entry point.
    
    Args:
        last_processed: Número da última edição processada (None = começar do zero)
    
    Returns:
        0 = Sucesso, 1 = Erro
    """
    # Descobrir qual é a próxima edição
    latest_num = get_latest_edition_number(last_processed)
    
    if latest_num == 0:
        return 1
    
    next_issue = str(latest_num).zfill(2)  # Ex: "41"
    print(f"\n🚀 INICIANDO PROCESSAMENTO DA EDIÇÃO #{latest_num}")
    print(f"   Slug: edicao-{next_issue}")
    
    try:
        orchestrator = PipelineOrchestrator()
        success = await orchestrator._process_magazine(f"edicao-{next_issue}")
        
        if success:
            print(f"\n{'='*60}")
            print(f"✅ EDIÇÃO #{latest_num} PROCESSADA COM SUCESSO!")
            print(f"   Próxima execução: rodar novamente com --last={latest_num}")
            print(f"{'='*60}\n")
            return 0
        else:
            # O _process_magazine retorna False se já foi processado
            print(f"\n⚠️ EDIÇÃO #{latest_num} parece ter sido processada antes!")
            return 0
    
    except Exception as e:
        print(f"\n❌ ERRO ao processar a edição #{latest_num}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    last_processed = None
    
    # Checar se há um argumento passado
    if len(sys.argv) > 1:
        try:
            last_processed = int(sys.argv[1])
            print(f"\n🔧 Último processado informado: #{last_processed}")
        except ValueError:
            print(f"❌ Argumento inválido: {sys.argv[1]}. Deve ser um número inteiro.")
            sys.exit(1)
    
    exit_code = asyncio.run(main(last_processed))
    sys.exit(exit_code)
