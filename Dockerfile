FROM python:3.14-alpine

WORKDIR /app

COPY pyproject.toml README.md .

COPY keyring ./keyring

RUN pip install --no-cache-dir .

COPY sample_project ./sample_project

EXPOSE 8000

CMD ["python", "sample_project/manage.py", "runserver", "0.0.0.0:8000"]
