FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN useradd --create-home appuser
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . /code/
USER appuser
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]