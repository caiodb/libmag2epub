#!/bin/bash
# Instala dependências necessárias para o scraper de Revista Liberta
echo "🔧 Instalando dependências para o scraper..."

# Verifica se BeautifulSoup4 está instalado
if ! python3 -c "import bs4" 2>/dev/null; then
    echo "⚠️ BeautifulSoup não encontrado. Tentando instalar via apt..."
    
    # Tenta pip primeiro (se possível)
    if [ -d "/home/devuser/myapps/newshit/venv/bin/pip" ]; then
        echo "  → Usando venv existente"
        source /home/devuser/myapps/newshit/venv/bin/activate || true
    fi
    
    # Tenta pip install
    if ! python3 -m pip --version 2>/dev/null; then
        echo "  → pip não encontrado, usando apt..."
        sudo apt-get update -qq && sudo apt-get install -y -qq python3-bs4 python3-requests > /dev/null 2>&1 && {
            echo "✅ BeautifulSoup instalado via apt!"
            exit 0
        }
    fi
    
    # Se pip estiver disponível, tenta instalar
    python3 -m pip install --quiet beautifulsoup4 requests 2>/dev/null && {
        echo "✅ BeautifulSoup instalado via pip!"
    } || {
        echo "❌ Falha ao instalar BeautifulSoup. Tente manualmente:"
        echo "   pip3 install beautifulsoup4"
        exit 1
    }
else
    echo "✅ BeautifulSoup já está instalado!"
fi

echo "========================================"
echo "Pronto para rodar o scraper!"
echo "Usage: python3 scraper_aprimorado.py [opcoes]"
echo "Exemplos:"
echo "  python3 scraper_aprimorado.py --paginas 5   # Captura 5 páginas de edições"
echo "  python3 scraper_aprimorado.py -u https://revistaliberta.com.br/digital/edicao/40/  # Captura edição específica"
