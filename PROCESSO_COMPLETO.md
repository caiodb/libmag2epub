# Processo Completo: Pipeline Revista Liberta → EPUB

## Visão Geral
Este documento descreve o fluxo completo do processo que automatiza a raspagem, processamento e arquivamento das edições da **Revista Nois (Liberta)**, convertendo-as para formato EPUB.

---

## 1. Estrutura de Diretórios
```
myapps/newshit/
├── src/                    # Código principal do pipeline
│   ├── __init__.py         # Inicialização e imports
│   ├── main.py             # Orquestrador principal (ponto de entrada)
│   ├── scraper.py          # Módulo de raspagem web
│   ├── session.py          # Gerenciamento de autenticação/browser
│   └── sent_manager.py     # Arquivamento e envio para email
├── data/                   # Dados persistentes e estado
│   ├── auth.json           # Credenciais de login (usuário/senha)
│   └── sent_history.txt    # Histórico de edições já processadas
├── raw/                    # Edições baixadas temporariamente (deletado após uso)
│   └── edicao-XX/
├── ebook/                  # EPUBs finais arquivados (destino final)
│   ├── edicao-33.epub
│   ├── edicao-34.epub
│   └── ...
└── sent/                   # EPUBs intermediários durante processamento
    ├── edicao-33.epub
    └── ...
```

---

## 2. Fluxo Completo do Pipeline

### Passo 1: Autenticação Inicial (`get_authenticated_context()`)
**Objetivo:** Criar uma sessão persistente e autenticada com o site.

- **Como funciona:**
  - Abre um navegador headless (chromium) usando Playwright
  - Navega até `https://revistaliberta.com.br/digital-edicao`
  - Detecta se já está logado ou executa login automático com credenciais do `data/auth.json`
  - Retorna um **BrowserContext** autenticado que pode ser reutilizado por múltiplas operações
- **Persistência:**
  - Credenciais são salvas em `data/auth.json` (usuário/senha)
  - Sessão persiste entre execuções — se ainda estiver logada, não faz login novamente
- **Segurança:** O usuário é alertado ao atualizar credenciais

---

### Passo 2: Descoberta de Edições (`get_available_editions()` no `scraper.py`)
**Objetivo:** Identificar todas as edições disponíveis e quais ainda precisam ser processadas.

- **Como funciona:**
  - Navega até a página que lista todas as edições (URL dinâmica via JavaScript)
  - Extrai links das URLs no formato: `https://revistaliberta.com.br/digital/edicao/edicao-XX/`
  - Compara com o arquivo `data/sent_history.txt` para identificar edições **novas**
- **Deducação:**
  ```python
  # Pega lista de todas as edições do site
  all_editions = ['40', '39', '38', ...]
  # Pede lista processada anteriormente
  processed = [33, 34, 35, ...]  # De sent_history.txt
  # Filtra apenas as novas
  new_editions = set(all_editions) - set(processed)
  ```
- **Fallback:** Se a extração falhar, tenta URLs alternativas ou intercepta requisições de rede

---

### Passo 3: Raspagem e Download (`scrape()` no `scraper.py`)
**Objetivo:** Baixar o conteúdo completo de uma edição específica.

- **Como funciona (para cada nova edição):**
  1. Cria uma página dentro do contexto autenticado
  2. Navega até `https://revistaliberta.com.br/digital/edicao/[NÚMERO]/`
  3. Aguarda renderização completa (JavaScript + conteúdo)
  4. Extrai:
     - Conteúdo HTML principal (texto, imagens, layout)
     - URLs de capas e assets
     - Metadados (título, data, autores) se disponíveis
  5. Salva como arquivo `.html` na pasta `raw/`
- **Proteção contra falhas:**
  - Timeout configurável (60s por página)
  - Verificação de sucesso via tamanho do conteúdo (>10KB)
  - Retentativas automáticas em caso de erro

---

### Passo 4: Arquivamento (`_send_and_archive()` no `sent_manager.py`)
**Objetivo:** Convertar o HTML para EPUB e salvar na pasta final.

- **Como funciona:**
  - Usa bibliotecas Python (ex: `ebooklib`) para criar um arquivo `.epub`
  - Preserva:
    - Estrutura de capítulos e seções do HTML original
    - Imagens e seus caminhos relativos
    - Metadados básicos (título, autor = "Revista Nois")
  - Salva na pasta `ebook/` com nome: `edicao-[NÚMERO].epub`
- **Ordem CORRETA (CRÍTICA):**
  ```python
  # ✅ Correto:
  arquivar_epub()    # Grava o EPUB primeiro
  salvar_historico() # Atualiza sent_history.txt
  
  # ❌ Errado (bug corrigido):
  salvar_historico() # Tenta gravar antes de ter certeza que o arquivo existe
  arquivar_epub()
  ```
- **Arquivo histórico:** `data/sent_history.txt` — lista numérica das edições já processadas

---

### Passo 5: Limpeza e Finalização (`main()` no `main.py`)
**Objetivo:** Encerrar o processo de forma segura.

- **O que acontece:**
  1. Fecha todas as páginas e navegadores criados (se houver erro)
 2. Destrói o contexto do Playwright
 3. Imprime resumo final:
     ```
     >>> PIPELINE COMPLETED SUCCESSFULLY <<<
     Processed: N edições
     New EPUBs: M arquivos
     Failed: X edições
     ```
- **Recuperação:** Se o processo for interrompido (Ctrl+C, erro), pode ser retomado da próxima edição — o histórico previne duplicação

---

## 3. Variáveis de Ambiente e Configuração

| Variável | Valor padrão | Função |
|----------|-------------|--------|
| `LIBER_USER` | `...@revistaliberta.com.br` | Email do usuário da conta |
| `LIBER_PASS` | `xxxxx` | Senha da conta |
| `LIBER_FRESH_LOGIN=true` | (não definido) | Força login fresco a cada execução (útil para debug) |

**Como usar:**
```bash
# Login fresco (apenas para testes)
LIBER_FRESH_LOGIN=true python -m main

# Login com sessão persistente (modo normal)
python -m main
```

---

## 4. Pontos de Falha e Tratamento de Erros

| Problema | Causa provável | Solução implementada |
|----------|---------------|----------------------|
| "Permission denied" ao deletar arquivos | Permissões do `auth.json` incorretas | `sudo chown devuser:devuser data/auth.json` |
| "Target page, context or browser has been closed" | Gerenciamento de recursos Playwright mal feito | Separar limpeza de erro vs sucesso; usar `async with` corretamente |
| Autenticação expirada | Sessão do site venceu | Re-autenticação automática com fallback para login fresco |
| Edições não encontradas | Site mudou a estrutura da página | Fallback para extração via interceptação de rede |
| Arquivo EPUB corrompido | HTML muito grande ou mal formatado | Validação pós-criação do arquivo |

---

## 5. Cronograma e Execução Automática (Futuro)

**Execução manual atual:**
```bash
cd /home/devuser/myapps/newshit
LIBER_FRESH_LOGIN=true python -m main  # Debug
python -m main                          # Normal
```

**Execução automática planejada:**
- **Cron:** Rodar semanalmente (ex: domingo às 03:00)
- **Condições de execução:**
  - Se `data/auth.json` existir e estiver válido → login automático
  - Se não, forçar login fresco com alerta via email/SMS
  - Enviar relatório de progresso por email após conclusão

---

## 6. Monitoramento e Logs

**Logs de execução:** Cada rodadas cria um arquivo `run_*.log` na raiz do projeto.

**Monitoramento manual:**
```bash
# Ver últimas edições processadas
cat data/sent_history.txt

# Listar EPUBs disponíveis
ls -lh ebook/*.epub

# Verificar falhas recentes
tail -f run_pipeline.log 2>&1 | grep -i error
```

**Logs automáticos:** O pipeline registra:
- Edições processadas nesta rodada
- Tempo de execução por edição
- Erros individuais (com stack trace) e totais
- Status final de sucesso/falha

---

## 7. Fluxo em Diagrama

```
[INÍCIO]
    │
    ▼
┌─────────────────────┐
│  Autenticação       │ ← Usa SessionManager + Playwright
│ (get_authenticated) │   Credenciais: data/auth.json
└──────────┬──────────┘
           │ Contexto ativo?
     ┌─────▼─────┐
     │ Não → Login│
     └─────┬─────┘
           ▼
    [Contexto autenticado]
           │
    ┌──────┴──────┐
    │ Lista edições│ ← Extrai links do site
    └──────┬──────┘
           │
    ┌──────┴────────┐
    │ Filtra novas? │ ← Comparar com sent_history.txt
    └──────┬────────┘
     Não  │ Sim
     ▼    ▼
[FINAL] [Processar uma edição]
         │
         ▼
   ┌─────────────┐
   │ Raspagem    │ ← Navega para /digital/edicao/[N]/
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │ Arquivar EPUB│ ← Converte HTML → .epub
   └──────┬──────┘
          ▼
     [Atualizar histórico]
    (data/sent_history.txt)
          │
          ▼
         [PRÓXIMA EDIÇÃO?]
            /      \
           Sim      Não
           │        │
         ▼          ▼
       ┌─────┐  ┌───────────┐
       │Repetir│ │ Limpeza e │
       └─────┘  │ Finalização│
                └───────┬─────┘
                        │
                        ▼
                   [SAÍDA]
```

---

## 8. Resumo das Dependências Externas

| Nome | Versão | Uso |
|------|--------|-----|
| Playwright | ^1.40+ | Automação de navegador (headless Chromium) |
| Python | 3.11 | Linguagem principal |
| `ebooklib` | ≥0.18 | Criação de arquivos EPUB |
| `requests` / `beautifulsoup4` | — | Fallback para scraping estático se Playwright falhar |

---

## 9. Histórico de Mudanças Relevantes (Comentário)

- **2026-06-21:** Correção crítica no arquivamento: agora salva o EPUB antes do histórico — evita inconsistências entre arquivo e código.
- **Anteriormente:** Problemas com gerenciamento de sessão do Playwright (contextos fechados prematuramente) — ainda em investigação.

---

**Arquivo criado:** `/home/devuser/myapps/newshit/PROCESSO_COMPLETO.md`
