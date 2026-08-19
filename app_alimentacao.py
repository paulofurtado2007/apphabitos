import datetime
import threading
import customtkinter as ctk
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

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class DailyTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Diário: Alimentação, Treino & Hábitos")
        self.geometry("490x550")
        self.resizable(False, False)

        self.worksheet = None
        self.data_hoje = datetime.date.today().strftime("%d/%m/%Y")

        # --- Cabeçalho ---
        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Diário de Progresso Diário", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_titulo.pack(pady=(15, 2))

        self.label_data = ctk.CTkLabel(
            self, 
            text=f"Hoje: {self.data_hoje}", 
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color="gray"
        )
        self.label_data.pack(pady=(0, 10))

        # --- Seção 1: Alimentação ---
        self.label_sec_comida = ctk.CTkLabel(
            self, 
            text="Registrar Refeição:", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.label_sec_comida.pack(anchor="w", padx=45, pady=(4, 2))

        self.entry_alimento = ctk.CTkEntry(
            self, 
            placeholder_text="Ex: Arroz, feijão e ovos...", 
            width=400,
            height=35
        )
        self.entry_alimento.pack(pady=2)
        self.entry_alimento.bind("<Return>", lambda event: self.iniciar_envio_texto("comida"))

        self.btn_refeicao = ctk.CTkButton(
            self, 
            text="Adicionar Refeição", 
            command=lambda: self.iniciar_envio_texto("comida"),
            width=400,
            height=32,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        self.btn_refeicao.pack(pady=(3, 12))

        # --- Seção 2: Treino ---
        self.label_sec_treino = ctk.CTkLabel(
            self, 
            text="Treino", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.label_sec_treino.pack(anchor="w", padx=45, pady=(0, 2))

        self.entry_treino = ctk.CTkEntry(
            self, 
            placeholder_text="Descreva a atividade realizada", 
            width=400,
            height=35
        )
        self.entry_treino.pack(pady=2)
        self.entry_treino.bind("<Return>", lambda event: self.iniciar_envio_texto("treino"))

        self.btn_treino = ctk.CTkButton(
            self, 
            text="Registrar Treino", 
            command=lambda: self.iniciar_envio_texto("treino"),
            width=400,
            height=32,
            fg_color="#E65100",
            hover_color="#BF360C"
        )
        self.btn_treino.pack(pady=(3, 15))

        # --- Seção 3: Disciplina / Vício (Sim / Não na Coluna E) ---
        self.label_sec_habito = ctk.CTkLabel(
            self, 
            text="dia livre?", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.label_sec_habito.pack(anchor="w", padx=45, pady=(0, 4))

        self.frame_botoes_habito = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes_habito.pack(pady=2)

        self.btn_sim = ctk.CTkButton(
            self.frame_botoes_habito, 
            text="✅ Sim", 
            command=lambda: self.iniciar_envio_habito("Sim"),
            width=195,
            height=36,
            fg_color="#1565C0",
            hover_color="#0D47A1"
        )
        self.btn_sim.pack(side="left", padx=5)

        self.btn_nao = ctk.CTkButton(
            self.frame_botoes_habito, 
            text="❌ Não", 
            command=lambda: self.iniciar_envio_habito("Não"),
            width=195,
            height=36,
            fg_color="#C62828",
            hover_color="#8E0000"
        )
        self.btn_nao.pack(side="left", padx=5)

        # --- Status ---
        self.label_status = ctk.CTkLabel(
            self, 
            text="Conectando à planilha...", 
            font=ctk.CTkFont(size=12)
        )
        self.label_status.pack(pady=12)

        self.entry_alimento.focus_set()

        # Conectar em segundo plano
        threading.Thread(target=self.conectar_google_sheets, daemon=True).start()

    def conectar_google_sheets(self):
        """Autentica na API do Google Sheets."""
        try:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            try:
                self.worksheet = spreadsheet.worksheet(SHEET_NAME)
            except gspread.WorksheetNotFound:
                self.worksheet = spreadsheet.get_worksheet(0)

            self.atualizar_status("✅ Conectado com sucesso!", "green")
        except Exception as e:
            self.atualizar_status(f"❌ Erro de conexão: {str(e)}", "red")

    def obter_ou_criar_linha_hoje(self):
        """Garante que a data de hoje existe na Coluna A e retorna o número da linha."""
        coluna_datas = self.worksheet.col_values(1)
        if self.data_hoje in coluna_datas:
            return coluna_datas.index(self.data_hoje) + 1
        else:
            todas_linhas = self.worksheet.get_all_values()
            nova_linha = len(todas_linhas) + 1
            self.worksheet.update_cell(nova_linha, 1, self.data_hoje)
            return nova_linha

    def travar_botoes(self, travar=True):
        estado = "disabled" if travar else "normal"
        self.btn_refeicao.configure(state=estado)
        self.btn_treino.configure(state=estado)
        self.btn_sim.configure(state=estado)
        self.btn_nao.configure(state=estado)

    # --- Gravação de Refeição e Treino ---
    def iniciar_envio_texto(self, tipo):
        if not self.worksheet:
            self.atualizar_status("⚠️ Aguarde a conexão com a planilha...", "orange")
            return

        if tipo == "comida":
            texto = self.entry_alimento.get().strip()
            if not texto:
                self.atualizar_status("⚠️ Digite o alimento consumido.", "orange")
                return
            entry_alvo = self.entry_alimento
        else:
            texto = self.entry_treino.get().strip()
            if not texto:
                self.atualizar_status("⚠️ Digite a descrição do treino.", "orange")
                return
            entry_alvo = self.entry_treino

        self.travar_botoes(True)
        self.atualizar_status("Salvando...", "gray")
        threading.Thread(target=self.salvar_texto, args=(tipo, texto, entry_alvo), daemon=True).start()

    def salvar_texto(self, tipo, texto, entry_alvo):
        try:
            linha_data = self.obter_ou_criar_linha_hoje()

            if tipo == "comida":
                num_linha = linha_data
                linha_valores = self.worksheet.row_values(num_linha)
                num_coluna = len(linha_valores) + 1
                if num_coluna < 2:
                    num_coluna = 2

                self.worksheet.update_cell(num_linha, num_coluna, texto)
                msg = f"✅ Refeição salva na linha {num_linha} (Col {num_coluna})!"
            else:
                # Linha do treino (linha de baixo)
                num_linha = linha_data + 1
                linha_valores = self.worksheet.row_values(num_linha)
                num_coluna = len(linha_valores) + 1
                if num_coluna < 2:
                    num_coluna = 2

                self.worksheet.update_cell(num_linha, num_coluna, texto)
                msg = f"✅ Treino salvo na linha {num_linha} (Col {num_coluna})!"

            entry_alvo.delete(0, "end")
            self.atualizar_status(msg, "green")
        except Exception as e:
            self.atualizar_status(f"❌ Erro ao salvar: {str(e)}", "red")
        finally:
            self.travar_botoes(False)

    # --- Gravação do Hábito (Sim / Não na Coluna E) ---
    def iniciar_envio_habito(self, valor):
        if not self.worksheet:
            self.atualizar_status("⚠️ Aguarde a conexão com a planilha...", "orange")
            return

        self.travar_botoes(True)
        self.atualizar_status(f"Registrando '{valor}' na Coluna E...", "gray")
        threading.Thread(target=self.salvar_habito, args=(valor,), daemon=True).start()

    def salvar_habito(self, valor):
        try:
            linha_data = self.obter_ou_criar_linha_hoje()
            linha_treino = linha_data + 1
            coluna_e = 5  # Coluna E

            # Atualiza diretamente a Coluna E da linha de treino
            self.worksheet.update_cell(linha_treino, coluna_e, valor)
            
            emoji = "💪" if valor == "Sim" else "⚠️"
            self.atualizar_status(f"{emoji} Registrado '{valor}' na Coluna E (Linha {linha_treino})!", "green")
        except Exception as e:
            self.atualizar_status(f"❌ Erro ao registrar hábito: {str(e)}", "red")
        finally:
            self.travar_botoes(False)

    def atualizar_status(self, texto, cor):
        self.label_status.configure(text=texto, text_color=cor)


if __name__ == "__main__":
    app = DailyTrackerApp()
    app.mainloop()