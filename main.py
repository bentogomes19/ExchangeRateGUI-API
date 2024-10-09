import os
import sys
import json
import requests
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from MainWindow import Ui_MainWindow
from datetime import datetime
from fileos import resource_path
# IMPORTAÇÃO DOS MÓDULOS 
# sys -> Fornece acesso a variáveis e funções específicas do sistema (operações no sistema operacional).
# json -> Modulo para acessar ou manipular dados no formato JSON.
# requests -> Módulo que permite fazer requisições HTTP (Utilizado para integrar API No sistema).
# PyQt6 -> Biblioteca para criar Interfaces Gráficas de Usuário (GUI).
# MainWindow -> Importa a classe Ui_MainWindow que foi criada no QtDesigner, ou seja a construção do desgin é feita por este aplicativo

# Project 02 - ExchangeRate - Conversor de moedas em Python utilizando PyQt6
# O programa irá fazer as conversões das moedas que temos disponíveis no sistema

# API UTILIZADA
#  https://www.exchangerate-api.com/
# UTILIZAÇÃO POR 30 DIAS E COM NO 1500 REQUISIÇÕES POSSÍVEIS


# Criação da Classe MyApp() que herda de QMainWindow. -> Representa aplicação principal
# Todo as funcionalidades e operações do sistema deve ficar dentro da classe
class MyApp(QtWidgets.QMainWindow):
    def __init__(self): # MÉTODO CONSTRUTOR DA CLASSE E OS ATRIBUTOS QUE INICIALIZARÁ COM A OBJETO
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) # Método que pega todos as informações da classe Ui_MainWindow para configura a interface gráfica
        
        # VALIDANDO SOMENTE VALORES NUMÉRICOS NAS ENTRADAS DO USUÁRIO
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        validator.setDecimals(3) # quantas casas decimais
        self.ui.coin1_Edit.setValidator(validator)
        self.ui.coin2_Edit.setValidator(validator)
        
        # ATUALIZAR A HORA 
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updatetime)
        self.timer.start(1000)
        
        
        self.updatetime()
    
        
        # CARREGANDO DADOS DO JSON COM AS MOEDAS
        self.load_currency_data() # Carrega os dados das moedas com o Nome da moeda, Código e a bandeira do país
        # Assim que o programa é inicializado ele é chamado para o carregamento de todos dados das medas
        
        
        ## FAZENDO A CONEXÃO COM OS COMPONENTES
        # Conectar todos os eventos de alteraçẽos de texto e seleções nas caixas de combinação (combo_box)
        # com métodos que vão lidar com essas mudanças
        # QLineEdit -> textChanged
        # textChanged -> Sempre que o texto mudar, a função convert_currency será chamada para atualizar a conversão
        self.ui.coin1_Edit.textChanged.connect(self.convert_currency)
        self.ui.coin2_Edit.textChanged.connect(self.convert_currency)
        # QComboBox -> currentIndexChanged
        # Quando o indice da caixa de seleção mudar chama o método update_combo_box que irá atualizar as bandeiras e atualiza o valor convertido
        self.ui.combo_top.currentIndexChanged.connect(self.update_combo_box)
        self.ui.combo_top.currentIndexChanged.connect(self.convert_currency)
        self.ui.combo_bottom.currentIndexChanged.connect(self.update_combo_box)
        self.ui.combo_bottom.currentIndexChanged.connect(self.convert_currency)

        
        self.update_combo_box()

    def updatetime(self):
        now = datetime.now()
        formatted_time = now.strftime("%b %d %H:%M")
        
        self.ui.clock_label.setText(formatted_time)
        
    def load_currency_data(self):
        currency_data_path = resource_path('currency.json')
        with open(currency_data_path, 'r') as f: # ABERTURA DO ARQUIVO JSON 
            data = json.load(f) 
            # Armazena os dados em currency_data => um dicionaŕio que associa o nome da moeda à sua informação completa
            self.currency_data = {currency["name"]: currency for currency in data["currencies"]}
        
            self.currency_names = list(self.currency_data.keys())
            
            # Adicionando os dados do json na COMBO BOX
            self.ui.combo_bottom.addItems(self.currency_names)
            self.ui.combo_top.addItems(self.currency_names)
            
            # Definindo os valores padrões ao inicializar o programa
            self.ui.combo_top.setCurrentText("United States Dollar")
            self.ui.combo_bottom.setCurrentText("Euro")
            
            self.ui.coin1_Edit.setText("1")
            
            
            # Atualiza as caixas de seleção do programa com as moedas e a conversão
            self.update_combo_box()
            self.convert_currency()
            
            
    # Atualiza a caixa de seleção
    def update_combo_box(self):
        # Aqui ao selecionar o texto atual da caixa de texto ele atualiza as bandeira ao lado 
        selected_combo_top = self.ui.combo_top.currentText()
        selected_combo_bottom = self.ui.combo_bottom.currentText()
        
        self.update_flag(selected_combo_top, self.ui.flag_top)
        self.update_flag(selected_combo_bottom, self.ui.flag_bottom)


    # Atualiza a bandeira
    def update_flag(self, currency_name, label):
        # Coleta o nome da moeda
        currency_info = self.currency_data.get(currency_name)
        
        if currency_info: # 
            flag_path = resource_path(currency_info.get("flag")) # Tenta obter o valor associado a chave flag
            if flag_path: # Verifica se há um caminho válido
                pixmap = QtGui.QPixmap(flag_path)
                label.setPixmap(pixmap.scaled(80, 65, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
            else:
                print("Não foi possível encontrar a imagem")



    def convert_currency(self): # CONVERSÃO DA MOEDA
        from_currency = self.ui.combo_bottom.currentText() # Pegando os codigos das moedas selecionadas
        to_currency = self.ui.combo_top.currentText()
        
        
        # Pega os codigos das moedas
        from_currency_code = self.currency_data[from_currency]["code"]
        to_currency_code = self.currency_data[to_currency]["code"]
        
        
        # Amount = quantia a ser convertida
        amount = float(self.ui.coin1_Edit.text() or 0)
        
        # Pegar a taxa de cambio do dia
        
        exchange_rate = self.get_exchange_rate(from_currency_code, to_currency_code)
        
        # Converter a quantia
        
        converterd_amount = amount * exchange_rate
        
        self.ui.coin2_Edit.setText(f"{converterd_amount:.2f}")


    
    # INTEGRAÇÃO COM A API ExchangeRate
    # Utiliza uma chave API e a moeda de origem e faz a requisição
    # Retorna a taxa de câmbio somente (O calculo é realizado pela função convert_currency)
    def get_exchange_rate(self, from_currency, to_currency):
        api_key = '2dfff8b6d8963b49dda081a3'
        url = f'https://v6.exchangerate-api.com/v6/2dfff8b6d8963b49dda081a3/latest/{from_currency}'
        
        try: 
            response = requests.get(url)
            print(response.json())
            data = response.json()
            return data['conversion_rates'][to_currency]
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return 0.0



# Abrindo o programa
# Execução da aplicação
app = QtWidgets.QApplication(sys.argv)

window = MyApp() # intancia da classe
window.show() # Mostra a janela
sys.exit(app.exec()) # System break
        