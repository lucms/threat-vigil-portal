FROM python:3.12.0

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PORT=

COPY . .

CMD streamlit run app.py --server.port=${PORT} --browser.serverAddress="0.0.0.0" --client.toolbarMode=minimal
