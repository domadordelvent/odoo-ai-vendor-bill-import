FROM odoo:18

USER root

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --break-system-packages --ignore-installed -r /tmp/requirements.txt

USER odoo