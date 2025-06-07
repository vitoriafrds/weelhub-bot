FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates fonts-liberation \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxss1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm-dev libasound2 \
    libpangocairo-1.0-0 libgtk-3-0 libdrm2 libu2f-udev libgl1-mesa-glx \
    libdbus-glib-1-2 xdg-utils --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Instala o Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Instala o ChromeDriver versão 137.0.7151.68 (compatível com Chrome 137)
RUN wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.68/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# Variáveis de ambiente
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH=/usr/local/bin:$PATH
ENV WELLHUB_USERNAME=contato@jogamiga.com.br
ENV WELLHUB_PWD=GymPass@J0G4M1G4#2025!
ENV WELLHUB_URL=https://partners.gympass.com/

# Diretório da aplicação
WORKDIR /app

# Copia os arquivos da aplicação
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando de execução
ENTRYPOINT ["python", "checkin-wellhub.py"]