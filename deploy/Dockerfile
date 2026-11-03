FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENTRYPOINT ["deep-ad-slot"]
CMD ["weekly"]
