from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# =====================================
# API
# =====================================

LISTINGS_API = "https://portal-market.com/api/nfts/search"
OFFERS_API = "https://portal-market.com/api/collection-offers/{collection_id}/all"

# =====================================
# HEADERS
# =====================================

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://portal-market.com/",
    "origin": "https://portal-market.com",
    "user-agent": "Mozilla/5.0"
}

# =====================================
# HELPERS
# =====================================

def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0

# =====================================
# HOME
# =====================================

@app.route("/")
def home():
    return render_template("index.html")

# =====================================
# DATA API
# =====================================

@app.route("/data")
def data():

    result = []

    try:

        # =========================
        # GET NFT LISTINGS
        # =========================

        r = requests.get(
            LISTINGS_API,
            headers=HEADERS,
            params={
                "offset": 0,
                "limit": 15,
                "premarket_status": "all",
                "exclude_bundled": "true"
            },
            timeout=20
        )

        listings_data = r.json()

        print("LISTINGS RESPONSE:", listings_data)

        listings = listings_data.get("results", [])

        print("NFT FOUND:", len(listings))

        # =========================
        # LOOP NFT
        # =========================

        for nft in listings:

            try:

                name = nft.get("name", "Unknown")

                collection = nft.get("collection", {})

                floor = safe_float(
                    collection.get("floor_price")
                )

                collection_id = nft.get("collection_id")

                print("NFT:", name)

                if not collection_id:
                    print("NO COLLECTION ID")
                    continue

                # =========================
                # GET OFFERS
                # =========================

                offers_r = requests.get(
                    OFFERS_API.format(
                        collection_id=collection_id
                    ),
                    headers=HEADERS,
                    timeout=20
                )

                offers_data = offers_r.json()

                print("OFFERS RESPONSE:", offers_data)

                offers = (
                    offers_data.get("offers")
                    or offers_data.get("data")
                    or []
                )

                prices = []

                # =========================
                # PARSE OFFERS
                # =========================

                for o in offers:

                    amount = o.get("amount")

                    if isinstance(amount, dict):
                        amount = (
                            amount.get("value")
                            or amount.get("amount")
                        )

                    amount = safe_float(amount)

                    if amount > 0:
                        prices.append(amount)

                print("OFFERS:", prices)

                if not prices:
                    continue

                # =========================
                # CALCULATIONS
                # =========================

                best_offer = max(prices)

                profit = round(
                    floor - best_offer,
                    4
                )

                roi = round(
                    (profit / best_offer) * 100,
                    2
                )

                print(
                    f"{name} | "
                    f"BUY {best_offer} | "
                    f"SELL {floor} | "
                    f"PROFIT {profit} | "
                    f"ROI {roi}%"
                )

                # =========================
                # SAVE RESULT
                # =========================

                result.append({
                    "name": name,
                    "offer": best_offer,
                    "floor": floor,
                    "profit": profit,
                    "roi": roi
                })

            except Exception as nft_error:

                print("NFT ERROR:", nft_error)

        # =========================
        # SORT
        # =========================

        result.sort(
            key=lambda x: x["profit"],
            reverse=True
        )

        return jsonify(result)

    except Exception as e:

        print("MAIN ERROR:", e)

        return jsonify({
            "error": str(e)
        })

# =====================================
# START
# =====================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
        )
