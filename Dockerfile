FROM python:3.11

RUN mkdir /fastapi_chat_app

WORKDIR /fastapi_chat_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh
