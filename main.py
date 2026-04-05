import requests
import json
import config
import websocket
import ssl
import time
import requests
import redis
import psutil



r = redis.Redis(host="localhost", port=6379, db=0)

def on_open(ws):
    print("CONNECTED")
    process = psutil.Process()
    print(process.memory_info().rss / 1024 / 1024, "MB")
# bot のwebsocket 認証
    ws.send(json.dumps({
        "seq": 1,
        "action": "authentication_challenge",
        "data": {"token": config.TOKEN}
    }))

def on_message(ws, message):
    try:
        data = json.loads(message)
    except:
        return

    if data.get("event") != "reaction_added":
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
    user_id = reaction.get("user_id")

    if not post_id:
        return

    #カウント(同じ人OK）
    key = f"count:{post_id}"
    count = r.incr(key)

    print(f"COUNT: {count}")

    #10回で再投稿
    flag = f"done:{post_id}"

    if count >= 10 and not r.exists(flag):
        r.set(flag, 1)
        repost(post_id)

def repost(post_id):
    # 元投稿取得
    res_post = requests.get(
        f"{config.BASE_URL}/api/v4/posts/{post_id}",
        headers={"Authorization": f"Bearer {config.TOKEN}"}
    )
    post = res_post.json()

    channel_id = post["channel_id"]
    message = post["message"]

    res = requests.post(
        f"{config.BASE_URL}/api/v4/posts",
        headers={
            "Authorization": f"Bearer {config.TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "channel_id": config.CHANNEL_ID,
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
            config.WS_URL,
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