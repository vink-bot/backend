FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
# EXPOSE 8000

# RUN apk add postgresql-client build-base postgresql-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# RUN adduser --disabled-password user

# USER user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "vink.wsgi"]