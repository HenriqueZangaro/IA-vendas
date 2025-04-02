# Dockerfile dentro de /backend

# Usando uma imagem base
FROM python:3.9

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando os arquivos
COPY . /app

# Instalando dependências
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .env

# Expondo a porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]