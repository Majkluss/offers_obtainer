FROM python:3.10
COPY . .
RUN pip install --upgrade pip
RUN pip install -U -r requirements.txt
CMD python app.py
