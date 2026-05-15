from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

LISTINGS_API = "https://portal-market.com/api/nfts/search"
OFFERS_API = "https://portal-market.com/api/collection-offers/{collection_id}/all"

HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0"
}

def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():

    result = []

    try:

        r = requests.get(
            LISTINGS_API,
            headers=HEADERS,
            params={
                "offset": 0,
                "limit": 15
            },
            timeout=20
        )

        listings = r.json().get("results", [])

        for nft in listings:

            try:

                name = nft.get("name", "Unknown")

                collection = nft.get("collection", {})

                floor = safe_float(
                    collection.get("floor_price")
                )

                collection_id = nft.get("collection_id")

                if not collection_id:
                    continue

                offers_r = requests.get(
                    OFFERS_API.format(
                        collection_id=collection_id
                    ),
                    headers=HEADERS,
                    timeout=20
                )

                data = offers_r.json()
                
                print(data)
                
                offers = data.get("offers") or data.get("data") or []
                )

                prices = []

                for o in offers:

                    amount = safe_float(
                        o.get("amount")
                    )

                    if amount > 0:
                        prices.append(amount)
                        
                print("OFFERS:", prices)
                
                if not prices:
                    continue

                offer = max(prices)

                profit = round(
                    floor - offer,
                    4
                )

                roi = round(
                    (profit / offer) * 100,
                    2
                )

                result.append({
                    "name": name,
                    "offer": offer,
                    "floor": floor,
                    "profit": profit,
                    "roi": roi
                })

            except:
                pass

        result.sort(
            key=lambda x: x["profit"],
            reverse=True
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
