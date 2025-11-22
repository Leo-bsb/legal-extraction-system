"""
🎯 Legal Extraction System - Enterprise Grade
Sistema Profissional de Extração Jurídica com LLM
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import time
import json
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from pdf_processor import PDFProcessor
from text_cleaner import TextCleaner
from llm_extractor import LLMExtractor
from validator import EntityValidator
from database import Database
from metrics import MetricsCalculator
from config import settings

# ═══════════════════════════════════════════════════════════════
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Legal Extraction System | Enterprise AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sistema de Extração Jurídica com IA - v1.0.0"
    }
)

# ═══════════════════════════════════════════════════════════════
# 💅 CSS PROFISSIONAL E MODERNO
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* ===== TEMA GERAL ===== */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* ===== HEADER PRINCIPAL ===== */
    .hero-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-weight: 600;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* ===== CARDS MODERNOS ===== */
    .premium-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }
    
    .feature-card {
        background: white;
        padding: 1.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-left-color: #764ba2;
        transform: translateX(5px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* ===== BADGES E STATUS ===== */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-success {
        background: #10b981;
        color: white;
    }
    
    .badge-warning {
        background: #f59e0b;
        color: white;
    }
    
    .badge-error {
        background: #ef4444;
        color: white;
    }
    
    .badge-info {
        background: #3b82f6;
        color: white;
    }
    
    /* ===== PROGRESS BAR ESTILIZADA ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* ===== BOTÕES PERSONALIZADOS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* ===== SIDEBAR PROFISSIONAL ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* ===== TABELAS ===== */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* ===== ANIMAÇÕES ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 🔧 INICIALIZAÇÃO DE COMPONENTES
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def init_components():
    """Inicializa componentes do sistema"""
    return {
        'pdf_processor': PDFProcessor(),
        'text_cleaner': TextCleaner(),
        'validator': EntityValidator(),
        'db': Database(),
        'metrics': MetricsCalculator()
    }

def get_llm_extractor():
    """Inicializa LLM Extractor"""
    try:
        return LLMExtractor()
    except Exception as e:
        st.error(f"🚨 **Erro de Configuração:** {e}")
        st.info("💡 **Solução:** Configure GEMINI_API_KEY no arquivo .env")
        with st.expander("📖 Como obter uma API Key"):
            st.markdown("""
            1. Acesse: [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Clique em "Create API Key"
            3. Copie a chave e adicione no arquivo `.env`
            4. Reinicie a aplicação
            """)
        return None

# ═══════════════════════════════════════════════════════════════
# 🏠 FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    """Função principal do app"""
    
    components = init_components()
    
    # ═══ SIDEBAR PROFISSIONAL ═══
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: white; font-size: 2rem; margin: 0;'>⚖️</h1>
            <h2 style='color: white; font-size: 1.3rem; margin: 0.5rem 0 0 0;'>Legal AI</h2>
            <p style='color: rgba(255,255,255,0.7); font-size: 0.8rem; margin: 0;'>Enterprise Edition</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menu de navegação estilizado
        page = st.radio(
            "**📍 NAVEGAÇÃO**",
            [
                "🏠 Dashboard Principal",
                "📄 Extração Individual", 
                "📁 Processamento em Lote",
                "📊 Análise & Métricas",
                "🗃️ Base de Dados",
                "ℹ️ Sobre o Sistema"
            ],
            label_visibility="visible"
        )
        
        st.markdown("---")
        
        # Métricas rápidas na sidebar
        st.markdown("**📈 ESTATÍSTICAS**")
        stats = components['db'].get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Casos", stats.get('total_cases', 0), delta=None)
        with col2:
            rate = stats.get('processing_success_rate', 0)
            st.metric("Taxa", f"{rate:.0%}", delta=None)
        
        st.markdown("---")
        
        # Info do sistema
        with st.expander("⚙️ Configuração"):
            st.caption(f"**Modelo:** {settings.MODEL_NAME}")
            st.caption(f"**Temperatura:** {settings.TEMPERATURE}")
            st.caption(f"**Max Tokens:** {settings.MAX_TOKENS}")
        
        st.markdown("---")
        st.caption("v1.0.0 | © 2024")
    
    # ═══ ROTEAMENTO DE PÁGINAS ═══
    if page == "🏠 Dashboard Principal":
        show_home_page(components)
    elif page == "📄 Extração Individual":
        show_extraction_page(components)
    elif page == "📁 Processamento em Lote":
        show_batch_page(components)
    elif page == "📊 Análise & Métricas":
        show_analytics_page(components)
    elif page == "🗃️ Base de Dados":
        show_database_page(components)
    elif page == "ℹ️ Sobre o Sistema":
        show_about_page()


# ═══════════════════════════════════════════════════════════════
# 📄 PÁGINAS DO SISTEMA
# ═══════════════════════════════════════════════════════════════

def show_home_page(components):
    """Dashboard Principal com Visão Executiva"""
    
    # Hero Header
    st.markdown("""
    <div class="hero-header fade-in">
        <h1 class="hero-title">⚖️ Legal Extraction System</h1>
        <p class="hero-subtitle">Transforme documentos jurídicos em dados estruturados com IA</p>
        <span class="hero-badge">🤖 Powered by Gemini 2.5</span>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs Principais
    stats = components['db'].get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Total de Documentos</div>
            <div class="metric-value">{stats.get('total_cases', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_comp = stats.get('avg_completeness', 0) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Completude Média</div>
            <div class="metric-value">{avg_comp:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        success = stats.get('processing_success_rate', 0) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🎯 Taxa de Sucesso</div>
            <div class="metric-value">{success:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        years = len(stats.get('cases_by_year', {}))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Anos Cobertos</div>
            <div class="metric-value">{years}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features do Sistema
    st.markdown("### 🎯 Capacidades do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 Extração Inteligente</h3>
            <p>Identifica automaticamente 8 entidades-chave de documentos jurídicos usando modelos avançados de IA.</p>
            <ul>
                <li>Autor e Réu</li>
                <li>Tipo e Resultado da Decisão</li>
                <li>Tribunal e Data</li>
                <li>Assunto e Resumo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>✅ Validação Rigorosa</h3>
            <p>Sistema de validação multicamadas garante qualidade e consistência dos dados extraídos.</p>
            <ul>
                <li>Validação de formato</li>
                <li>Verificação de completude</li>
                <li>Normalização automática</li>
                <li>Retry inteligente</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Métricas Avançadas</h3>
            <p>Acompanhe a performance do sistema com métricas detalhadas e visualizações interativas.</p>
            <ul>
                <li>Taxa de sucesso em tempo real</li>
                <li>Análise de completude</li>
                <li>Distribuição temporal</li>
                <li>Exportação para análise</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Tecnologias
    st.markdown("### 🛠️ Stack Tecnológica")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("**🤖 LLM**\nGemini 2.5 Flash")
    with col2:
        st.info("**📄 PDF**\nPyMuPDF")
    with col3:
        st.info("**🗄️ Database**\nSQLite")
    with col4:
        st.info("**🎨 Interface**\nStreamlit")


def show_extraction_page(components):
    """Página de Extração Individual - Design Profissional"""
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title" style="font-size: 2.5rem;">📄 Extração Individual</h1>
        <p class="hero-subtitle">Processe um documento jurídico e extraia informações estruturadas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("### 📤 Upload do Documento")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Selecione um arquivo PDF",
            type=['pdf'],
            help="Documentos jurídicos em Português ou Inglês",
            label_visibility="collapsed"
        )
    
    with col2:
        language = st.selectbox(
            "Idioma",
            options=['auto', 'pt', 'en'],
            format_func=lambda x: {
                'auto': '🤖 Detecção Automática',
                'pt': '🇧🇷 Português',
                'en': '🇺🇸 Inglês'
            }[x]
        )
    
    if uploaded_file:
        st.success(f"✅ Arquivo carregado: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            extract_btn = st.button("🚀 Processar Documento", type="primary", use_container_width=True)
        
        if extract_btn:
            extract_document(uploaded_file, language, components)
    else:
        st.info("👆 Faça upload de um documento PDF para começar")


def extract_document(uploaded_file, language, components):
    """Processa e extrai informações com UI profissional"""
    
    try:
        start_time = time.time()
        
        # Container para status
        status_container = st.container()
        
        with status_container:
            progress_bar = st.progress(0, text="Iniciando processamento...")
            
            # 1. Extração de texto
            with st.spinner("📖 Extraindo texto do PDF..."):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = Path(tmp_file.name)
                
                text = components['pdf_processor'].extract_text(tmp_path)
                
                if not text:
                    st.error("❌ Não foi possível extrair texto do PDF. Verifique se o arquivo não está protegido ou corrompido.")
                    return
                
                progress_bar.progress(20, text="✓ Texto extraído com sucesso")
                time.sleep(0.3)
            
            # 2. Limpeza
            with st.spinner("🧹 Processando e limpando texto..."):
                clean_text = components['text_cleaner'].clean(text)
                
                if language == 'auto':
                    language = components['pdf_processor'].detect_language(clean_text)
                    st.info(f"🌐 Idioma detectado: **{'Português 🇧🇷' if language == 'pt' else 'Inglês 🇺🇸'}**")
                
                truncated_text = components['text_cleaner'].truncate_for_llm(clean_text)
                progress_bar.progress(40, text="✓ Texto processado")
                time.sleep(0.3)
            
            # 3. Extração com LLM
            with st.spinner("🤖 Extraindo entidades com IA..."):
                extractor = get_llm_extractor()
                if not extractor:
                    return
                
                entities = extractor.extract_entities(truncated_text, language)
                
                if not entities:
                    st.error("❌ Falha na extração de entidades. Tente novamente.")
                    return
                
                progress_bar.progress(70, text="✓ Entidades extraídas")
                time.sleep(0.3)
            
            # 4. Validação
            with st.spinner("✅ Validando dados extraídos..."):
                is_valid, validated_entities, errors = components['validator'].validate(entities)
                completeness = components['validator'].calculate_completeness(validated_entities)
                progress_bar.progress(85, text="✓ Validação concluída")
                time.sleep(0.3)
            
            # 5. Salvamento
            with st.spinner("💾 Salvando no banco de dados..."):
                metadata = components['pdf_processor'].get_metadata(tmp_path)
                components['db'].insert_case(
                    filename=uploaded_file.name,
                    entities=validated_entities,
                    language=language,
                    year=metadata.year,
                    completeness_score=completeness,
                    validation_errors=errors
                )
                
                processing_time = time.time() - start_time
                
                components['db'].insert_metric(
                    filename=uploaded_file.name,
                    extraction_time=processing_time,
                    num_retries=1,
                    success=True
                )
                
                progress_bar.progress(100, text="✨ Processamento concluído!")
                time.sleep(0.5)
                
                tmp_path.unlink()
        
        # ═══ RESULTADOS ═══
        st.markdown("---")
        st.markdown("### 🎉 Extração Concluída com Sucesso!")
        
        # Métricas de performance
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⏱️ Tempo</div>
                <div class="metric-value">{processing_time:.1f}s</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📊 Completude</div>
                <div class="metric-value">{completeness*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status_color = "#10b981" if is_valid else "#f59e0b"
            status_text = "Válido" if is_valid else "Avisos"
            st.markdown(f"""
            <div class="metric-card" style="background: {status_color};">
                <div class="metric-label">🔍 Status</div>
                <div class="metric-value" style="font-size: 1.5rem;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📝 Campos</div>
                <div class="metric-value">{len([v for v in validated_entities.values() if v])}/8</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Entidades extraídas em cards
        st.markdown("### 📋 Dados Extraídos")
        
        for key, value in validated_entities.items():
            icon_map = {
                'autor': '👤', 'reu': '👥', 'assunto_principal': '📌',
                'tipo_decisao': '⚖️', 'resultado': '✅', 'resumo_5_linhas': '📝',
                'data_decisao': '📅', 'tribunal': '🏛️'
            }
            
            icon = icon_map.get(key, '📄')
            
            with st.expander(f"{icon} **{key.replace('_', ' ').title()}**", expanded=True):
                if value and str(value).lower() not in ['null', 'none', 'n/a', '']:
                    st.markdown(f"```\n{value}\n```")
                else:
                    st.warning("⚠️ Não extraído")
        
        # Avisos de validação
        if errors:
            with st.expander("⚠️ Avisos de Validação", expanded=False):
                for error in errors:
                    st.warning(error)
        
        # Download
        st.markdown("### 📥 Exportar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            df = pd.DataFrame([validated_entities])
            csv_str = df.to_csv(index=False)
            st.download_button(
                "📄 Baixar CSV",
                csv_str,
                file_name=f"{uploaded_file.name}_resultado.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_str = json.dumps(validated_entities, indent=2, ensure_ascii=False)
            st.download_button(
                "📋 Baixar JSON",
                json_str,
                file_name=f"{uploaded_file.name}_resultado.json",
                mime="application/json",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"❌ **Erro durante o processamento:** {str(e)}")
        import traceback
        with st.expander("🔍 Detalhes Técnicos"):
            st.code(traceback.format_exc())


def show_batch_page(components):
    """Página de Processamento em Lote"""
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title" style="font-size: 2.5rem;">📁 Processamento em Lote</h1>
        <p class="hero-subtitle">Processe múltiplos documentos simultaneamente</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📤 Upload de Múltiplos Arquivos")
    
    uploaded_files = st.file_uploader(
        "Selecione os PDFs (máximo: 20 arquivos)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Arraste e solte múltiplos arquivos ou clique para selecionar"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        if len(uploaded_files) > 20:
            st.warning("⚠️ Limite de 20 arquivos por lote. Processando apenas os primeiros 20...")
            uploaded_files = uploaded_files[:20]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            language = st.selectbox(
                "Idioma dos documentos",
                options=['auto', 'pt', 'en'],
                format_func=lambda x: {'auto': '🤖 Auto', 'pt': '🇧🇷 PT', 'en': '🇺🇸 EN'}[x]
            )
        
        with col2:
            st.metric("Total", len(uploaded_files))
        
        with col3:
            total_size = sum(f.size for f in uploaded_files) / (1024 * 1024)
            st.metric("Tamanho", f"{total_size:.1f} MB")
        
        if st.button("🚀 Processar Todos os Arquivos", type="primary", use_container_width=True):
            process_batch(uploaded_files, language, components)
    else:
        st.info("👆 Selecione múltiplos arquivos PDF para processamento em lote")


def process_batch(uploaded_files, language, components):
    """Processa múltiplos arquivos em lote"""
    
    st.markdown("### ⚙️ Processamento em Andamento")
    
    results = []
    progress = st.progress(0)
    status_text = st.empty()
    
    for idx, file in enumerate(uploaded_files):
        status_text.markdown(f"**📄 Processando ({idx+1}/{len(uploaded_files)}):** `{file.name}`")
        
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file.read())
                tmp_path = Path(tmp_file.name)
            
            text = components['pdf_processor'].extract_text(tmp_path)
            
            if not text:
                results.append({
                    'filename': file.name,
                    'status': '❌ Erro',
                    'completeness': 0,
                    'error': 'Extração falhou'
                })
                continue
            
            clean_text = components['text_cleaner'].clean(text)
            lang = language if language != 'auto' else components['pdf_processor'].detect_language(clean_text)
            truncated_text = components['text_cleaner'].truncate_for_llm(clean_text)
            
            extractor = get_llm_extractor()
            if not extractor:
                results.append({
                    'filename': file.name,
                    'status': '❌ Erro',
                    'completeness': 0,
                    'error': 'LLM não disponível'
                })
                continue
            
            entities = extractor.extract_entities(truncated_text, lang)
            
            if not entities:
                results.append({
                    'filename': file.name,
                    'status': '❌ Erro',
                    'completeness': 0,
                    'error': 'Entidades não extraídas'
                })
                continue
            
            is_valid, validated_entities, errors = components['validator'].validate(entities)
            completeness = components['validator'].calculate_completeness(validated_entities)
            
            metadata = components['pdf_processor'].get_metadata(tmp_path)
            components['db'].insert_case(
                filename=file.name,
                entities=validated_entities,
                language=lang,
                year=metadata.year,
                completeness_score=completeness,
                validation_errors=errors
            )
            
            results.append({
                'filename': file.name,
                'status': '✅ Sucesso',
                'completeness': f"{completeness*100:.0f}%",
                'avisos': len(errors)
            })
            
            tmp_path.unlink()
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            results.append({
                'filename': file.name,
                'status': '❌ Erro',
                'completeness': 0,
                'error': str(e)[:50]
            })
        
        progress.progress((idx + 1) / len(uploaded_files))
    
    status_text.empty()
    progress.empty()
    
    # ═══ RESUMO DOS RESULTADOS ═══
    st.markdown("---")
    st.markdown("### 🎉 Processamento Concluído!")
    
    success_count = sum(1 for r in results if '✅' in r['status'])
    error_count = len(results) - success_count
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: #10b981;">
            <div class="metric-label">✅ Sucesso</div>
            <div class="metric-value">{success_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: #ef4444;">
            <div class="metric-label">❌ Erros</div>
            <div class="metric-value">{error_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        rate = (success_count / len(results) * 100) if results else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Taxa</div>
            <div class="metric-value">{rate:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Total</div>
            <div class="metric-value">{len(results)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabela de resultados
    st.markdown("### 📋 Resultados Detalhados")
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download do relatório
    csv_str = df.to_csv(index=False)
    st.download_button(
        "📥 Baixar Relatório Completo (CSV)",
        csv_str,
        file_name=f"batch_results_{int(time.time())}.csv",
        mime="text/csv",
        use_container_width=True
    )


def show_analytics_page(components):
    """Página de Análise e Métricas Avançadas"""
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title" style="font-size: 2.5rem;">📊 Análise & Métricas</h1>
        <p class="hero-subtitle">Insights e visualizações dos dados processados</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = components['db'].get_statistics()
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📚 Documentos</div>
            <div class="metric-value">{stats.get('total_cases', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_comp = stats.get('avg_completeness', 0) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Completude</div>
            <div class="metric-value">{avg_comp:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        success = stats.get('processing_success_rate', 0) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Sucesso</div>
            <div class="metric-value">{success:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        years = len(stats.get('cases_by_year', {}))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 Anos</div>
            <div class="metric-value">{years}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Distribuição Temporal de Casos")
        cases_by_year = stats.get('cases_by_year', {})
        
        if cases_by_year:
            df_years = pd.DataFrame(
                list(cases_by_year.items()), 
                columns=['Ano', 'Quantidade']
            ).sort_values('Ano')
            
            fig = px.bar(
                df_years, 
                x='Ano', 
                y='Quantidade',
                color='Quantidade',
                color_continuous_scale='Purples',
                title="Casos Processados por Ano"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nenhum dado disponível")
    
    with col2:
        st.markdown("#### ⚖️ Distribuição de Resultados")
        result_dist = stats.get('result_distribution', {})
        
        if result_dist:
            df_results = pd.DataFrame(
                list(result_dist.items()), 
                columns=['Resultado', 'Quantidade']
            )
            
            fig = px.pie(
                df_results, 
                values='Quantidade', 
                names='Resultado',
                color_discrete_sequence=px.colors.sequential.RdBu,
                title="Tipos de Decisões"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Nenhum dado disponível")
    
    # Análise detalhada
    st.markdown("---")
    st.markdown("### 🔍 Análise Detalhada")
    
    cases = components['db'].get_all_cases()
    
    if cases:
        df = pd.DataFrame(cases)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Distribuição de Completude")
            
            # Cria bins de completude
            df['completude_categoria'] = pd.cut(
                df['completeness_score'], 
                bins=[0, 0.5, 0.7, 0.9, 1.0],
                labels=['Baixa (<50%)', 'Média (50-70%)', 'Alta (70-90%)', 'Excelente (>90%)']
            )
            
            completude_dist = df['completude_categoria'].value_counts()
            
            fig = go.Figure(data=[go.Bar(
                x=completude_dist.index,
                y=completude_dist.values,
                marker_color=['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
            )])
            fig.update_layout(
                title="Qualidade das Extrações",
                xaxis_title="Categoria",
                yaxis_title="Número de Casos",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🌍 Distribuição de Idiomas")
            
            if 'language' in df.columns:
                lang_dist = df['language'].value_counts()
                
                fig = px.pie(
                    values=lang_dist.values,
                    names=['🇧🇷 Português' if x == 'pt' else '🇺🇸 Inglês' for x in lang_dist.index],
                    color_discrete_sequence=['#667eea', '#764ba2']
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)


def show_database_page(components):
    """Página do Banco de Dados com UI Moderna"""
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title" style="font-size: 2.5rem;">🗃️ Base de Dados</h1>
        <p class="hero-subtitle">Consulte e exporte todos os casos processados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("📊 Limite de Resultados", min_value=10, max_value=1000, value=50, step=10)
    
    with col2:
        search_term = st.text_input("🔍 Buscar", placeholder="Digite o nome do arquivo...")
    
    with col3:
        st.write("")
        export_all = st.button("📥 Exportar Tudo (CSV)", use_container_width=True)
    
    # Busca casos
    cases = components['db'].get_all_cases(limit=limit)
    
    if search_term:
        cases = [c for c in cases if search_term.lower() in c['filename'].lower()]
    
    st.markdown(f"**📋 Mostrando {len(cases)} caso(s)**")
    
    if cases:
        df = pd.DataFrame(cases)
        
        # Seleciona colunas para exibição
        display_columns = ['filename', 'autor', 'reu', 'resultado', 
                          'completeness_score', 'year', 'language', 'created_at']
        
        df_display = df[[col for col in display_columns if col in df.columns]]
        
        # Formata completeness_score
        if 'completeness_score' in df_display.columns:
            df_display['completeness_score'] = df_display['completeness_score'].apply(
                lambda x: f"{x*100:.0f}%" if pd.notna(x) else "N/A"
            )
        
        # Exibe tabela
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400,
            column_config={
                "filename": st.column_config.TextColumn("📄 Arquivo", width="medium"),
                "autor": st.column_config.TextColumn("👤 Autor", width="medium"),
                "reu": st.column_config.TextColumn("👥 Réu", width="medium"),
                "resultado": st.column_config.TextColumn("⚖️ Resultado", width="small"),
                "completeness_score": st.column_config.TextColumn("📊 Completude", width="small"),
                "year": st.column_config.TextColumn("📅 Ano", width="small"),
                "language": st.column_config.TextColumn("🌐 Idioma", width="small"),
                "created_at": st.column_config.DatetimeColumn("🕐 Processado", width="medium")
            }
        )
        
        # Detalhes de caso
        st.markdown("---")
        st.markdown("### 🔍 Visualizar Detalhes de um Caso")
        
        selected_file = st.selectbox(
            "Selecione um documento",
            options=df['filename'].tolist(),
            label_visibility="collapsed"
        )
        
        if selected_file:
            case_details = components['db'].get_case(selected_file)
            
            if case_details:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📋 Informações Básicas")
                    st.markdown(f"""
                    <div class="feature-card">
                        <p><strong>📄 Arquivo:</strong> {case_details['filename']}</p>
                        <p><strong>📅 Ano:</strong> {case_details.get('year', 'N/A')}</p>
                        <p><strong>🌐 Idioma:</strong> {case_details.get('language', 'N/A').upper()}</p>
                        <p><strong>📊 Completude:</strong> {case_details.get('completeness_score', 0)*100:.1f}%</p>
                        <p><strong>🕐 Processado:</strong> {case_details.get('created_at', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 🎯 Entidades Extraídas")
                    
                    entities = {k: v for k, v in case_details.items() if k in settings.ENTITIES}
                    
                    for key, value in entities.items():
                        if value and str(value).lower() not in ['null', 'none', 'n/a', '']:
                            st.success(f"**{key}:** {value}")
                        else:
                            st.warning(f"**{key}:** Não extraído")
                
                # Download individual
                st.markdown("#### 📥 Exportar Este Caso")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    df_case = pd.DataFrame([entities])
                    csv_str = df_case.to_csv(index=False)
                    st.download_button(
                        "📄 Baixar CSV",
                        csv_str,
                        file_name=f"{selected_file}_detalhes.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    json_str = json.dumps(entities, indent=2, ensure_ascii=False)
                    st.download_button(
                        "📋 Baixar JSON",
                        json_str,
                        file_name=f"{selected_file}_detalhes.json",
                        mime="application/json",
                        use_container_width=True
                    )
    
    else:
        st.info("📭 Nenhum caso encontrado no banco de dados. Comece processando alguns documentos!")
    
    # Exportar tudo
    if export_all and cases:
        output_path = settings.RESULTS / f"export_completo_{int(time.time())}.csv"
        
        if components['db'].export_to_csv(output_path):
            st.success(f"✅ Exportação concluída: {output_path.name}")
            
            with open(output_path, 'rb') as f:
                st.download_button(
                    "📥 Download do Arquivo Exportado",
                    f,
                    file_name=output_path.name,
                    mime="text/csv",
                    use_container_width=True
                )


def show_about_page():
    """Página Sobre o Sistema"""
    
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title" style="font-size: 2.5rem;">ℹ️ Sobre o Sistema</h1>
        <p class="hero-subtitle">Tecnologia, funcionalidades e documentação</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visão Geral
    st.markdown("### 🎯 Visão Geral")
    
    st.markdown("""
    <div class="feature-card">
        <p>O <strong>Legal Extraction System</strong> é uma solução enterprise-grade para automatizar 
        a extração de informações de documentos jurídicos usando inteligência artificial.</p>
        
        Desenvolvido com as tecnologias mais modernas de LLM, o sistema é capaz de processar 
        documentos em <strong>Português</strong> e <strong>Inglês</strong>, extraindo automaticamente 
        entidades-chave com alta precisão.
    </div>
    """, unsafe_allow_html=True)
    
    # Stack Tecnológica
    st.markdown("### 🛠️ Stack Tecnológica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 Inteligência Artificial</h4>
            <ul>
                <li><strong>LLM:</strong> Google Gemini 2.5 Flash</li>
                <li><strong>Framework:</strong> LangChain</li>
                <li><strong>Validação:</strong> Pydantic</li>
                <li><strong>Métricas:</strong> Scikit-learn</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🗄️ Backend & Database</h4>
            <ul>
                <li><strong>API:</strong> FastAPI</li>
                <li><strong>Database:</strong> SQLite</li>
                <li><strong>PDF Processing:</strong> PyMuPDF</li>
                <li><strong>Data:</strong> Pandas, NumPy</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🎨 Frontend & Visualização</h4>
            <ul>
                <li><strong>Interface:</strong> Streamlit</li>
                <li><strong>Gráficos:</strong> Plotly</li>
                <li><strong>Styling:</strong> CSS3 Custom</li>
                <li><strong>UX:</strong> Responsive Design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 DevOps & Qualidade</h4>
            <ul>
                <li><strong>Logging:</strong> Python Logging</li>
                <li><strong>Testing:</strong> Pytest</li>
                <li><strong>Deploy:</strong> Hugging Face Spaces</li>
                <li><strong>Version Control:</strong> Git</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Entidades Extraídas
    st.markdown("### 📋 Entidades Extraídas")
    
    entities_info = {
        '👤 Autor': 'Nome da parte autora/requerente do processo',
        '👥 Réu': 'Nome da parte ré/requerida do processo',
        '📌 Assunto Principal': 'Tema central do caso jurídico',
        '⚖️ Tipo de Decisão': 'Classificação da decisão (sentença, acórdão, liminar, etc)',
        '✅ Resultado': 'Resultado da decisão (deferido, indeferido, procedente, etc)',
        '📝 Resumo': 'Resumo objetivo do caso em até 5 linhas',
        '📅 Data da Decisão': 'Data em que a decisão foi proferida',
        '🏛️ Tribunal': 'Nome do tribunal que proferiu a decisão'
    }
    
    for entity, description in entities_info.items():
        st.markdown(f"""
        <div class="feature-card">
            <h4>{entity}</h4>
            <p>{description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recursos
    st.markdown("### 🚀 Recursos e Funcionalidades")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("✅ **Extração Automática**\nProcessamento inteligente com IA")
    
    with col2:
        st.info("✅ **Multi-idioma**\nPortuguês e Inglês")
    
    with col3:
        st.info("✅ **Validação Rigorosa**\nQualidade garantida")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("✅ **Processamento em Lote**\nMúltiplos arquivos simultaneamente")
    
    with col2:
        st.info("✅ **Métricas Detalhadas**\nAnálise de performance")
    
    with col3:
        st.info("✅ **Exportação Flexível**\nCSV, JSON e mais")
    
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #64748b;">
        <p style="font-size: 1.2rem; font-weight: 600;">⚖️ Legal Extraction System</p>
        <p>Enterprise AI Solution | Version 1.0.0</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            Desenvolvido com ❤️ usando Python, Streamlit e Gemini AI
        </p>
        <p style="font-size: 0.8rem; color: #94a3b8;">
            © 2024 - MIT License
        </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 🚀 ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()