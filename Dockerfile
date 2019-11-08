FROM python:3.7

ENV INSTALL_PATH /app

RUN mkdir -p $INSTALL_PATH
RUN chmod -R 777 $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY . $INSTALL_PATH

RUN pip install -r requirements.txt

VOLUME ["/tv", "/movies", "$INSTALL_PATH/logs"]

RUN adduser --disabled-password --gecos "" --shell /bin/sh app
USER app

ENTRYPOINT [ "python", "./main.py" ]
