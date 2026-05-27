import requests
import json
import config
import websocket
import ssl
import time
import requests
import redis
import psutil

import os

token = config.TOKEN # railway の場合は os.getenv("TOKEN") 
ws_url = config.WS_URL # os.getenv("WS_URL")
base_url = config.BASE_URL # os.getenv("BASE_URL")
channel_id = config.CHANNEL_ID # os.getenv("CHANNEL_ID")
team_name = config.TEAM_NAME # os.getenv("TEAM_NAME")

#r = redis.Redis(host="localhost", port=6379, db=0)

print("REDIS CONNECT SETUP")
print("WS_URL:", ws_url)
print("BASE_URL:", base_url)
print("TOKEN exists:", bool(token))

redis_url = config.REDIS_PUBLIC_URL # os.getenv("REDIS_URL")  # or REDIS_TLS_URL / REDISS_URL

if not redis_url:
    print(" REDIS_URL not set")
    r = None
else:
    print(" REDIS_URL:", redis_url)
    r = redis.from_url(redis_url, decode_responses=True)




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



# reaction_added / reaction_removed イベントの処理
def handle_reaction(data):
    print("HANDLE REACTION")
    event = data.get("event")

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
    
    print("before incr")
    if event == "reaction_added":
        #カウント(同じ人OK）
        count = r.incr(key)
    else: #reaction_removed
        count = r.decr(key)
    print("after incr")

    print(f"COUNT: {count}")

    
    if event == "reaction_added":
        #10回以上で再投稿をまだしていない場合
        if count >= 10 and not r.exists(flag):
            # 再投稿してフラグ立てる
            r.set(flag, 1)
            repost(post_id)
    
def handle_posted(data):
    print("HANDLE POSTED")
    post_raw = data.get("data", {}).get("post")
    if not post_raw:
        return
    
    post = json.loads(post_raw)
    postid=post.get("id")
    print("post id:", postid)
    reply_count = post.get("reply_count")

    if reply_count == 5:
        print("返信数が5以上のスレッドです")
        root_id = post.get("root_id")
        repost(root_id)
    
    
def handle_thread_updated(data):
    print("HANDLE THREAD UPDATED")
    thread = data.get("data", {}).get("thread")
    if not thread:
        return

    root_id = thread.get("id")
    reply_count = thread.get("reply_count")

    print("THREAD:", root_id, reply_count)

def on_message(ws, message):
    print("RAW EVENT:", message[:300])
    try:
        data = json.loads(message)
    except:
        return
    
    event = data.get("event")

    # ① reaction イベント
    if event in ("reaction_added", "reaction_removed"):
        handle_reaction(data)
        return

    # ② posted イベント（root 投稿 or 返信）
    if event == "posted":
        handle_posted(data)
        return

    # ③ thread_updated イベント（返信数）
    if event == "thread_updated":
        handle_thread_updated(data)
        return

    # その他は無視
    return
    

    

def repost(post_id):
    print("REPOSTING:", post_id)
    # 投稿 URL を組み立てる
    post_url = f"{base_url}/{team_name}/pl/{post_id}"

    res = requests.post(
        f"{base_url}/api/v4/posts",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "channel_id": channel_id,
            "message": f"にぎわってるスレッド\n{post_url}",
        }
    )

    print("REPOST:", res.status_code)

def on_error(ws, error):
    print("ERROR:", error)

def on_close(ws, code, msg):
    print("CLOSED:", code, msg)

while True:
    print("CONNECTING...")
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