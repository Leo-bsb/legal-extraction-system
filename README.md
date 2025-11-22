# ⚖️ Legal Extraction System

> Sistema de Extração Automática de Informações Jurídicas usando LLM (Gemini 2.0)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

## 📋 Índice

- [Sobre](#sobre)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Métricas](#métricas)
- [Deploy](#deploy)
- [Contribuindo](#contribuindo)

## 🎯 Sobre

Este projeto implementa um **pipeline completo e robusto** para extração automática de informações jurídicas de documentos PDF usando modelos de linguagem avançados (LLM). 

O sistema foi desenvolvido para processar o dataset **SC Judgment Indian** do Kaggle, mas suporta qualquer documento jurídico em **Português** ou **Inglês**.

### Problema Resolvido

Transformar documentos jurídicos desestruturados (PDFs) em dados estruturados e utilizáveis, extraindo:

- 📝 **Partes Envolvidas** (Autor e Réu)
- ⚖️ **Tipo de Decisão**
- 📅 **Data da Decisão**
- ✅ **Resultado**
- 📄 **Resumo da Decisão**
- 🏛️ **Tribunal**
- 📌 **Assunto Principal**

## ✨ Características

### 🔥 Principais Funcionalidades

- ✅ **Extração com LLM**: Utiliza Gemini 2.0 Flash (gratuito) para extração inteligente
- ✅ **Multi-idioma**: Suporta Português e Inglês com detecção automática
- ✅ **Validação Rigorosa**: Sistema de validação de entidades com retry automático
- ✅ **Pipeline Completo**: Do PDF até o banco de dados estruturado
- ✅ **Métricas Detalhadas**: Avaliação quantitativa da qualidade das extrações
- ✅ **Interface Web**: Dashboard Streamlit para visualização e teste
- ✅ **API REST**: FastAPI para integração com outros sistemas
- ✅ **Processamento em Lote**: Suporte para processar centenas de documentos

### 🛠️ Stack Tecnológica

- **LLM**: Google Gemini 2.0 Flash Lite
- **Framework**: LangChain (text splitting e chains)
- **PDF Processing**: PyMuPDF (fitz)
- **API**: FastAPI
- **Interface**: Streamlit
- **Database**: SQLite
- **Validação**: Pydantic
- **Métricas**: Scikit-learn, ROUGE

## 🏗️ Arquitetura

```
┌─────────────────┐
│   PDF Input     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Extraction │ ← PyMuPDF
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text Cleaning   │ ← Regex + Normalização
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Extraction │ ← Gemini 2.0 + Prompt Engineering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │ ← Regras de validação
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLite DB     │ ← Persistência
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Streamlit UI │ FastAPI │ CLI   │
└─────────────────────────────────┘
```

## 📦 Instalação

### Pré-requisitos

- Python 3.9+
- API Key do Google Gemini (gratuita)

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/legal-extraction.git
cd legal-extraction

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

### Obter API Key do Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave e adicione no `.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
```

## 🚀 Uso

### 1. Interface Streamlit (Recomendado para Demo)

```bash
streamlit run app/streamlit_app.py
```

Acesse: `http://localhost:8501`

**Recursos da Interface:**
- 📄 Upload de PDF individual
- 📁 Processamento em lote
- 📊 Dashboard com métricas
- 🗃️ Visualização do banco de dados
- 📥 Exportação para CSV

### 2. API REST

```bash
# Inicia o servidor
uvicorn api.main:app --reload

# Acesse a documentação
# http://localhost:8000/docs
```

**Endpoints principais:**

```bash
# Extrair de um PDF
POST /api/extract
Content-Type: multipart/form-data
file: arquivo.pdf

# Processar lote
POST /api/batch

# Ver casos
GET /api/cases?limit=50

# Estatísticas
GET /api/statistics

# Exportar CSV
GET /api/export/csv
```

### 3. CLI (Command Line Interface)

```bash
# Processar um PDF
python main.py --input data/raw/documento.pdf --language pt

# Processar diretório
python main.py --input data/raw/ --language auto --max-files 10

# Processar recursivamente
python main.py --input supreme_court_judgments/ --recursive --export-csv results.csv

# Dataset do Kaggle
python main.py --input supreme_court_judgments/ --recursive --language en
```

## 📊 Métricas

O sistema calcula automaticamente:

### Métricas de Qualidade

- **Taxa de Sucesso**: % de extrações bem-sucedidas
- **Completude Média**: % de campos preenchidos por documento
- **Taxa por Campo**: Sucesso na extração de cada entidade
- **Tipos de Erro**: Distribuição dos erros de validação

### Métricas de Performance

- **Tempo Médio de Extração**: Segundos por documento
- **Throughput**: Documentos por minuto
- **Taxa de Retry**: Quantas vezes foi necessário retentar

### Exemplo de Relatório

```
╔══════════════════════════════════════════════════════════╗
║           RELATÓRIO DE MÉTRICAS DE EXTRAÇÃO             ║
╚══════════════════════════════════════════════════════════╝

📊 RESUMO GERAL
  • Total de Documentos: 100
  • Extrações Bem-sucedidas: 94
  • Extrações Falhadas: 6
  • Taxa de Sucesso: 94.0%

📈 QUALIDADE DA EXTRAÇÃO
  • Completude Média: 87.3%
  • Tempo Médio de Processamento: 3.45s

🎯 TAXA DE EXTRAÇÃO POR CAMPO
  • resultado            [████████████████████████████░░] 95.7%
  • autor                [███████████████████████████░░░] 92.6%
  • reu                  [███████████████████████████░░░] 91.5%
  • resumo_5_linhas      [██████████████████████████░░░░] 89.4%
  • tipo_decisao         [█████████████████████████░░░░░] 85.1%
  • data_decisao         [████████████████████████░░░░░░] 82.3%
  • tribunal             [███████████████████████░░░░░░░] 78.7%
  • assunto_principal    [██████████████████████░░░░░░░░] 76.6%
```

## 🌐 Deploy

### Hugging Face Spaces (Recomendado)

O projeto está otimizado para deploy em **Hugging Face Spaces** (somente CPU):

```bash
# 1. Crie um novo Space no Hugging Face
# 2. Clone o repositório do Space
# 3. Copie os arquivos do projeto
# 4. Crie um arquivo app.py:

from app.streamlit_app import main
if __name__ == "__main__":
    main()

# 5. Configure secrets no Space:
# GEMINI_API_KEY = sua_chave

# 6. Push para o repositório
git add .
git commit -m "Initial deployment"
git push
```

### Docker (Opcional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501 8000

CMD ["streamlit", "run", "app/streamlit_app.py"]
```

## 📁 Estrutura do Projeto

```
legal-extractor/
│
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências
├── .env.example                 # Template de configuração
├── main.py                      # Script principal CLI
│
├── data/
│   ├── raw/                     # PDFs originais
│   ├── processed/               # Textos extraídos
│   ├── results/                 # Resultados JSON/CSV
│   └── logs/                    # Logs de processamento
│
├── src/
│   ├── config.py                # Configurações globais
│   ├── pdf_processor.py         # Extração de PDFs
│   ├── text_cleaner.py          # Limpeza de texto
│   ├── llm_extractor.py         # Extração com LLM
│   ├── validator.py             # Validação de entidades
│   ├── database.py              # Persistência SQLite
│   └── metrics.py               # Cálculo de métricas
│
├── api/
│   └── main.py                  # FastAPI backend
│
└── app/
    └── streamlit_app.py         # Interface Streamlit
```

## 🎓 Para Recrutadores

### Por que este projeto impressiona?

✅ **Arquitetura Profissional**: Código modular, limpo e bem documentado  
✅ **Engenharia de Prompt**: Demonstra domínio avançado de LLMs  
✅ **Validação Rigorosa**: Sistema robusto de validação e tratamento de erros  
✅ **Métricas Quantitativas**: Avaliação científica da qualidade  
✅ **Full Stack**: Backend (FastAPI) + Frontend (Streamlit)  
✅ **Production-Ready**: Logs, métricas, testes e documentação  
✅ **Deploy Real**: Rodando em Hugging Face Spaces  

### Conceitos Demonstrados

- LLMs e Prompt Engineering
- Data Engineering (ETL Pipeline)
- API REST Design
- Validação de Dados
- Processamento de Documentos
- Metrics & Observability
- Clean Architecture
- DevOps (Deploy)

## 🔧 Desenvolvimento

### Melhorias Futuras

- [ ] Suporte a mais idiomas (Espanhol, Francês)
- [ ] Fine-tuning de modelo específico
- [ ] OCR para PDFs escaneados
- [ ] Cache de resultados
- [ ] Processamento assíncrono com Celery
- [ ] Interface multi-usuário com autenticação
- [ ] Exportação para múltiplos formatos (JSON, XML, Excel)
- [ ] Integração com sistemas jurídicos

### Testes

```bash
# Instale dependências de teste
pip install pytest pytest-cov

# Execute testes
pytest tests/ -v --cov=src
```

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👤 Autor

Desenvolvido como projeto portfolio para demonstrar habilidades em:
- Machine Learning / LLMs
- Engenharia de Software
- Data Engineering
- Full Stack Development

---

⭐ **Se este projeto foi útil, deixe uma estrela!**

📧 **Contato**: [leonardoborges6947@gmail.com]  
🔗 **LinkedIn**: [https://www.linkedin.com/in/leonardo-borges1/]  