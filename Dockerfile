# ベースイメージの指定
FROM python:3.11-slim
# 作業ディレクトリを設定
WORKDIR /app
# アプリケーションのソースコードをコピー
COPY . .
# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt
# コンテナ起動時に実行
CMD ["python", "main.py"]