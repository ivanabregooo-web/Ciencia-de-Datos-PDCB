FROM python:3.12-slim AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
COPY requirements-dev.lock .
RUN pip install --no-cache-dir -r requirements-dev.lock
RUN find /opt/venv -type d -name "pycache" -exec rm -rf {} + \
    && find /opt/venv -type f -name "*.py[co]" -delete

FROM python:3.12-slim
RUN useradd -m clinlab && \
    mkdir /app && chown clinlab:clinlab /app
USER clinlab
WORKDIR /app
COPY --from=builder --chown=clinlab:clinlab /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
COPY --chown=clinlab:clinlab . .

RUN pip install --no-deps .
CMD ["pytest"]