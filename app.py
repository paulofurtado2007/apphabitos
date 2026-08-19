import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# CONFIGURAÇÕES
# ==========================================
SPREADSHEET_ID = "1L0EkG6Hyxq4GtigGTz1AyD6OSWUs4KV_iJoqZIgE_dE"
SHEET_NAME = "Alimentação"
CREDENTIALS_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Configuração da página para mobile
st.set_page_config(
    page_title="Diário de Hábitos",
    page_icon="🎯",
    layout="centered"
)

# Conexão com cache para carregamento rápido
@st.cache_resource
def get_worksheet():
    # Suporta credenciais via arquivo local ou Secrets do Streamlit Cloud
    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=SCOPES
        )
    else:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=SCOPES
        )
        
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        return spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        return spreadsheet.get_worksheet(0)

worksheet = get_worksheet()
data_hoje = datetime.date.today().strftime("%d/%m/%Y")

def obter_ou_criar_linha_hoje():
    coluna_datas = worksheet.col_values(1)
    if data_hoje in coluna_datas:
        return coluna_datas.index(data_hoje) + 1
    else:
        todas_linhas = worksheet.get_all_values()
        nova_linha = len(todas_linhas) + 1
        worksheet.update_cell(nova_linha, 1, data_hoje)
        return nova_linha

# --- Interface Web ---
st.title("🎯 Diário de Progresso")
st.caption(f"📅 Data de hoje: **{data_hoje}**")

st.divider()

# --- Seção 1: Alimentação ---
st.subheader("🥗 Alimentação")
with st.form("form_comida", clear_on_submit=True):
    alimento = st.text_input("O que você comeu?", placeholder="Ex: Arroz, feijão e ovos mexidos...")
    btn_comida = st.form_submit_button("Adicionar Refeição", use_container_width=True)

    if btn_comida and alimento.strip():
        with st.spinner("Salvando refeição..."):
            linha_data = obter_ou_criar_linha_hoje()
            valores = worksheet.row_values(linha_data)
            num_coluna = max(len(valores) + 1, 2)
            worksheet.update_cell(linha_data, num_coluna, alimento.strip())
            st.success(f"Refeição salva com sucesso!")

# --- Seção 2: Treino ---
st.subheader("🏋️ Treino & Atividade Física")
with st.form("form_treino", clear_on_submit=True):
    treino = st.text_input("Qual foi a atividade?", placeholder="Ex: Cardio 30 min, 10 km...")
    btn_treino = st.form_submit_button("Registrar Treino", use_container_width=True)

    if btn_treino and treino.strip():
        with st.spinner("Salvando treino..."):
            linha_data = obter_ou_criar_linha_hoje()
            linha_treino = linha_data + 1
            valores = worksheet.row_values(linha_treino)
            num_coluna = max(len(valores) + 1, 2)
            worksheet.update_cell(linha_treino, num_coluna, treino.strip())
            st.success(f"Treino salvo com sucesso!")

st.divider()

# --- Seção 3: Disciplina (Coluna E) ---
st.subheader("🛡️ Venceu o dia sem recaída?")
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ SIM (Firme)", use_container_width=True):
        with st.spinner("Registrando..."):
            linha_data = obter_ou_criar_linha_hoje()
            worksheet.update_cell(linha_data + 1, 5, "Sim")
            st.success("💪 Vitória registrada!")

with col2:
    if st.button("❌ NÃO (Recaída)", use_container_width=True):
        with st.spinner("Registrando..."):
            linha_data = obter_ou_criar_linha_hoje()
            worksheet.update_cell(linha_data + 1, 5, "Não")
            st.warning("⚠️ Registrado. Foco no próximo dia!")