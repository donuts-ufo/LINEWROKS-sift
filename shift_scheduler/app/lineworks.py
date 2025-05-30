"""
LINE WORKS Bot 署名検証 & ユーザ API呼び出しユーティリティ
"""
import base64, hmac, hashlib, os, time, jwt, httpx
from typing import Any

API_ID = os.getenv("LW_API_ID")
CONSUMER_KEY = os.getenv("LW_SERVER_CONSUMER_KEY")
BOT_SECRET = os.getenv("LW_BOT_SECRET")
PRIVATE_KEY = os.getenv("LW_PRIVATE_KEY").replace("\\n", "\n")  # .env から読み込み

def verify_signature(body: bytes, signature: str | None) -> bool:
    if not (signature and BOT_SECRET):
        return False
    expected = hmac.new(BOT_SECRET.encode(), body, hashlib.sha256).digest()
    return hmac.compare_digest(base64.b64encode(expected).decode(), signature)

def _jwt_token() -> str:
    now = int(time.time())
    payload = {
        "iss": API_ID,
        "iat": now,
        "exp": now + 60 * 60,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

async def get_user_profile(user_id: str) -> dict[str, Any]:
    url = f"https://www.worksapis.com/v1.0/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {_jwt_token()}",
        "consumerKey": CONSUMER_KEY,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()
