# Mattermost Reaction Repost Bot

Mattermost の投稿に付いたリアクション数を監視し、  
**一定数（例：10個）以上リアクションが付いた投稿を自動で再投稿する Bot** 

WebSocket を用いて Mattermost に常時接続し、  
状態管理には Redis を使用します。  
常駐実行環境として Railway を利用しています。
---

## 機能概要
- Mattermost WebSocket API を使用してイベントを監視
- 投稿にリアクションが付くたびにカウント
- リアクション数が指定数以上になったら Bot が再投稿
- Redis によりカウント・再投稿済みフラグを管理
- Railway 上で常時稼働
---

## 使用技術
- Python
- Mattermost WebSocket API
- Redis
- Railway
- GitHub
---

## 構成図（論理構成）
Mattermost
   │ WebSocket
   ▼
Reaction Bot (Python / Railway)
   │
   ▼
Redis (Railway Plugin)
---
## 動作要件
- Mattermost Bot 作成・権限付与済みであること
- Railway アカウント
- GitHub アカウント



