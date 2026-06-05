# Mattermost Reaction Repost Bot

Mattermost の投稿に付いたリアクション数を監視し、  一定数（例：10個）以上リアクションが付いた投稿を自動で再投稿する Bot

## 概要
コミュニケーションツール(Mattermost)において、有益な投稿や活発な議論が日々の業務連絡に埋もれてしまう課題がありました。そこで、リアクションが多く付いた投稿を自動的に検知し、専用チャンネルへ再共有するBotを開発しました。重要な情報を見逃しにくくし、コミュニケーション活性化につなげることを目的としています。

## 担当した役割
企画・設計・実装・運用を一人で担当しました

## 直面した課題と解決方法
リアクション数の増加に伴い同じ投稿が複数回共有される問題がありました。そのため投稿状態を管理し、再共有済みフラグを保持することで重複投稿を防止しました。
本botはDocker コンテナとして動作する想定です。今後はAWS(EC2)上の常時起動できるサーバーに配置することでBotをいつでも稼働できる状態にする想定です．

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



