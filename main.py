import requests
import json
#import config
import websocket
import ssl
import time
import requests
import redis
import psutil

import os

token = os.getenv("TOKEN") #config.TOKEN
ws_url = os.getenv("WS_URL") #config.WS_URL
base_url = os.getenv("BASE_URL") #config.BASE_URL
channel_id = os.getenv("CHANNEL_ID") #config.CHANNEL_ID


#r = redis.Redis(host="localhost", port=6379, db=0)

print("REDIS CONNECT SETUP")

redis_url = os.getenv("REDIS_URL")  # or REDIS_TLS_URL / REDISS_URL

r = redis.from_url( #host,port,password打つ場合→redis.Redis
    #host=os.getenv("REDISHOST"),
    #port=int(os.getenv("REDISPORT", 6379)),
    #password=os.getenv("REDISPASSWORD"),
    redis_url,
    decode_responses=True,
)


def on_open(ws):
    print("CONNECTED")
    process = psutil.Process()
    print(process.memory_info().rss / 1024 / 1024, "MB")
# bot のwebsocket 認証
    ws.send(json.dumps({
        "seq": 1,
        "action": "authentication_challenge",
        "data": {"token": token}
    }))

def on_message(ws, message):
    print("RAW EVENT:", message[:300])
    try:
        data = json.loads(message)
    except:
        return
    
    event = data.get("event")
    
    post_raw = data.get("data", {}).get("post")
    post = json.loads(post_raw)

    print("POST KEYS:", post.keys())
    print("ROOT_ID:", post.get("root_id"))
    
    # reaction_added もしくは reaction_removed イベント以外は無視
    if event not in ("reaction_added", "reaction_removed"):
        return

    reaction_data = data.get("data", {}).get("reaction")
    if not reaction_data:
        return

    # 文字列 or dict対応
    if isinstance(reaction_data, str):
        reaction = json.loads(reaction_data)
    else:
        reaction = reaction_data

    post_id = reaction.get("post_id")
    if not post_id:
        return

    key = f"count:{post_id}"
    #10回で再投稿
    flag = f"done:{post_id}"
    
    if event == "reaction_added":
        #カウント(同じ人OK）
        count = r.incr(key)
    else: #reaction_removed
        count = r.decr(key)

    print(f"COUNT: {count}")

    
    if event == "reaction_added":
        if count >= 10 and not r.exists(flag):
            r.set(flag, 1)
            repost(post_id)
    
    

def repost(post_id):
    # 元投稿取得
    res_post = requests.get(
        f"{base_url}/api/v4/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    post = res_post.json()

    channel_id = post["channel_id"]
    message = post["message"]

    res = requests.post(
        f"{base_url}/api/v4/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "channel_id": channel_id,
            "message": f"再投稿\n{message}",
        }
    )

    print("REPOST:", res.status_code)

def on_error(ws, error):
    print("ERROR:", error)

def on_close(ws, code, msg):
    print("CLOSED:", code, msg)

while True:
    try:
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        ws.run_forever(
            sslopt={
                "cert_reqs": ssl.CERT_NONE,
                "check_hostname": False
            }
        )

    except Exception as e:
        print("Reconnect...", e)
        time.sleep(5)