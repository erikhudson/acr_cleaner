# Usando a imagem base oficial do Python 3.10
FROM python:3.12.3-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos para dentro do contêiner
COPY . /app

# Instalando as dependências necessárias, incluindo Python e o driver ODBC
RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalando as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que será usada pela aplicação
EXPOSE 8501

# Comando para rodar a aplicação Streamlit
CMD ["streamlit", "run", "acr_cleaner.py.py", "--server.port=8501", "--server.address=0.0.0.0"]
