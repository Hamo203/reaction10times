# Mattermost Reaction Repost Bot

Mattermost の投稿に付いたリアクション数を監視し、  
一定数（例：10個）以上リアクションが付いた投稿を自動で再投稿する Bot

WebSocket を用いて Mattermost に常時接続し、  状態管理には Redis を使用します。  

本botはDocker コンテナとして動作する想定です。
---

## 機能概要
- Mattermost WebSocket API を使用してイベントを監視
- 投稿にリアクションが付くたびにカウント
- リアクション数が指定数以上になったら Bot が再投稿
- Redis によりカウント・再投稿済みフラグを管理
- 常時接続型としてバックグラウンドで動作
---

## 使用技術
- Python
- Mattermost WebSocket API
- Redis
- Docker
---
## 動作要件
- Mattermost Bot 作成・権限付与済みであること
- Docker がインストールされている環境

##　設定
config.py に以下を設定してください：
- TOKEN
- WS_URL
- BASE_URL
- CHANNEL_ID
- TEAM_NAME
- REDIS_URL
---
## 起動手順(ローカル)

### Redisの起動

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis
```
### Botのビルド
```bash
docker build -t mm-bot .
```
### Botの停止・再起動
```bash
# 停止
docker stop mm-bot
docker stop redis
# 再起動
docker start redis
docker start mm-bot
```



