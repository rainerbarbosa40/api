from flask import Flask, render_template, request
import requests
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import os

app = Flask(__name__)

# Função para consultar a API de endereço pelo CEP
def consulta_endereco(cep):
    url = f"https://cep.awesomeapi.com.br/json/{cep}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Função para consultar as cotações
def consulta_cotacoes():
    url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Função para carregar as taxas SELIC
def CarregaSELIC(data_inicial, data_final):
    url_bcb = f"http://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    serie_SELIC = pd.read_csv(url_bcb, sep=";")
    return serie_SELIC

# Função para obter a taxa SELIC atual
def taxa_selic_atual():
    url_bcb = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados?formato=json"
    response = requests.get(url_bcb)
    if response.status_code == 200:
        data_atual = response.json()[-1]  # Pega a última entrada da série
        return float(data_atual['valor']), data_atual['data']
    return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    endereco = None
    erro = None
    cotacoes = consulta_cotacoes()  # Buscar cotações ao acessar a página

    if request.method == "POST":
        cep = request.form.get("cep")
        endereco = consulta_endereco(cep)
        
        if not endereco:
            erro = "CEP não encontrado."

    # Carregar os dados SELIC e gerar o gráfico
    serie = CarregaSELIC("01/01/2023", "24/09/2024")
    serie1 = serie.replace({',': '.'}, regex=True)
    serie1['valor'] = serie1['valor'].astype(float)

    # Gerar o gráfico e salvá-lo como arquivo
    plt.figure()
    serie1.plot.line(x="data", y="valor", title="SELIC taxas ao ano", legend=False)
    plt.savefig('static/selic_taxas.png')  # Salvar o gráfico na pasta 'static'
    plt.close()  # Fechar a figura

    # Obter a taxa SELIC atual
    taxa_atual, data_atual = taxa_selic_atual()

    return render_template(
        "index.html", 
        endereco=endereco, 
        erro=erro, 
        cotacoes=cotacoes, 
        selic_image='selic_taxas.png', 
        taxa_atual=taxa_atual, 
        data_atual=data_atual
    )

if __name__ == "__main__":
    app.run(debug=True)
