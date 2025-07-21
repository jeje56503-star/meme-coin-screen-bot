
import requests
from telegram import Bot
import time

bot = Bot(token="YOUR_BOT_TOKEN")
channel_id = -1001234567890  # Ganti dengan chat_id grup kamu

def get_new_tokens():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    res = requests.get(url)
    return res.json() if res.ok else []

def get_token_data(chain, address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
    res = requests.get(url)
    return res.json() if res.ok else {}

def is_token_promising(token):
    chain = token["chainId"]
    address = token["tokenAddress"]
    data = get_token_data(chain, address)

    if "pair" not in data:
        return False, None

    pair = data["pair"]
    try:
        fdv = float(pair["fdvUsd"] or 0)
        liquidity = float(pair["liquidity"]["usd"] or 0)
        volume = float(pair["volume"]["h24"] or 0)
        price_change = float(pair["priceChange"]["m5"] or 0)

        if fdv < 1000000 and liquidity > 10000 and volume > 5000 and price_change > 30:
            return True, pair
    except:
        return False, None

    return False, None

def send_alert(pair):
    name = pair["baseToken"]["name"]
    symbol = pair["baseToken"]["symbol"]
    price = pair["priceUsd"]
    change = pair["priceChange"]["m5"]
    link = pair["url"]

    msg = f"🚀 *Token Potensial Terdeteksi!*

" \          f"*{name}* ({symbol})
" \          f"Harga: ${price}
" \          f"Naik 5 Menit: {change}%
" \          f"[Lihat di DexScreener]({link})"

    bot.send_message(chat_id=channel_id, text=msg, parse_mode="Markdown")

# === MAIN LOOP ===
while True:
    try:
        tokens = get_new_tokens()
        for token in tokens[:20]:
            is_good, pair_data = is_token_promising(token)
            if is_good:
                send_alert(pair_data)
                time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(300)  # Cek tiap 5 menit
