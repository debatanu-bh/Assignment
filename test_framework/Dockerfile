FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Allure results will be written here
VOLUME /app/allure-results

ENTRYPOINT ["pytest"]
CMD ["tests/", "-v", "--alluredir=allure-results"]
