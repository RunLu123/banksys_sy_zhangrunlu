ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

# ARG 必须在 FROM 之后重新声明，才能在构建阶段内使用
ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i ${PIP_INDEX_URL} -r requirements.txt

# 复制项目代码与数据
COPY data/ ./data/
COPY src/ ./src/
COPY models/ ./models/

# 离线训练模型（构建时完成）
RUN python src/train.py

# Streamlit 默认端口 8501，映射到 8888
EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8888/_stcore/health || exit 1

CMD ["streamlit", "run", "src/app.py", "--server.port=8888", "--server.address=0.0.0.0"]
