FROM python:3.12

WORKDIR /cat-clicker

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "cat-clicker.py"]
