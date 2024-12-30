from flask import Flask, send_file
import subprocess
import threading
import os

# Inicializar o app Flask
app = Flask(__name__)

# Caminho para o arquivo principal do Streamlit
STREAMLIT_APP = "Dataviz.py"  # Atualize com o nome correto do arquivo Streamlit principal

def run_streamlit():
    """Executa o Streamlit como subprocesso."""
    os.system(f"streamlit run {STREAMLIT_APP}")

# Endpoint principal do Flask
@app.route('/')
def index():
    # Redireciona para a interface do Streamlit
    return """
    <h1>Aplicativo BI Crome</h1>
    <p>Seu aplicativo Streamlit está rodando. <a href="/streamlit">Acesse aqui.</a></p>
    """

# Endpoint para redirecionar para Streamlit
@app.route('/streamlit')
def streamlit_app():
    return send_file('http://127.0.0.1:8501/')  # Porta padrão do Streamlit

if __name__ == "__main__":
    # Rodar o Streamlit em uma thread separada
    threading.Thread(target=run_streamlit).start()
    # Iniciar o servidor Flask
    app.run(port=5000)
