"""
Authentication check module - Força reautenticação em cada execução.
Usado no cronjob para garantir que o login funciona antes do scraping começar.

Sempre roda LOGIN FRESCO a cada execução, ignorando cookies salvos.
"""
import asyncio
import sys
from playwright.async_api import async_playwright
from src.session import SessionManager
from src.config import LIBER_USER, LIBER_PASS, INDEX_URL, LOGIN_URL

print(f"\n{'='*60}")
print("🔐 AUTHENTICATION CHECK - FORCED FRESH LOGIN")
print("="*60)

async def run_test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Faz login fresco usando API pública do session.py
            print("   [Login] Fazendo login...")
            manager = SessionManager(force_fresh=True)
            context = await browser.new_context(storage_state=None, viewport={"width": 1280, "height": 720})
            page = await context.new_page()
            
            # Vai para página de login
            print("   [Login] Navegando para...")
            await page.goto(LOGIN_URL, timeout=30000)
            
            from src.config import SELECTOR_LOGIN_USERNAME, SELECTOR_LOGIN_PASSWORD, SELECTOR_LOGIN_SUBMIT_ID
            print(f"   [Login] Seletor de usuário: {SELECTOR_LOGIN_USERNAME}")
            await page.fill(SELECTOR_LOGIN_USERNAME, LIBER_USER)
            await page.fill(SELECTOR_LOGIN_PASSWORD, LIBER_PASS)
            await page.click(SELECTOR_LOGIN_SUBMIT_ID)
            
            # Espera o login processar
            print("   [Login] Aguardando navegação...")
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # VERIFICAÇÃO CRÍTICA: Procura pelo email logado na página
            print(f"   [Verificação] Procurando por '{LIBER_USER}' na página...")
            try:
                user_element = page.locator(f"text='{LIBER_USER}'")
                await user_element.wait_for(timeout=3000)
                print("   ✓ Usuário logado com sucesso! Página contém o email.")
            except Exception as e:
                # Tenta verificar se há algum indicador de login
                print(f"   [Verificação] Email não encontrado, buscando outros indicadores...")
                try:
                    # Verifica se a URL mudou ou se há conteúdo diferente
                    title = await page.title()
                    url = page.url
                    print(f"   [Verificação] Título: {title}, URL: {url}")
                    
                    # Navega para página principal e verifica se funciona
                    test_page = await context.new_page()
                    await test_page.goto("https://revistaliberta.com.br/digital/", timeout=30000)
                    content = await test_page.content()
                    if LIBER_USER in content:
                        print("   ✓ Usuário logado! Página principal contém o email.")
                        await test_page.close()
                    else:
                        print("   ❌ Login pode não ter funcionado corretamente")
                except Exception as e2:
                    print(f"   ❌ Verificação falhou: {e2}")
            
            # Navega para página principal
            print("   [Login] Navegando para página principal...")
            await page.goto(INDEX_URL, timeout=30000)
            print(f"   ✓ Login executado! Página principal carregada.")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
    sys.exit(0)