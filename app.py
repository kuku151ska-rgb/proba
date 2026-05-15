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
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",

    "authorization": """tma query_id=AAHLyjg0AwAAAMvKODTmT1fK&user=%7B%22id%22%3A7318588107%2C%22first_name%22%3A%22%D0%A2%D1%96%D0%B3%D0%B5%D1%80%E2%96%AA%EF%B8%8F%F0%9F%90%BE%F0%9F%90%8D%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22uk%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FWUTJgWh0IosbFoZ-P1KF_3SUYqoHWsWpNGDyW4KNTvxnX7OzRAINrc7tvBsEzKto.svg%22%7D&auth_date=1778761182&signature=xawUfPxf8QedI4bh7PY5M_bbQ1xcqVXv7vbsYrQrWFZK8I9_90Y3OZaltlL_DRquRHs97qMw0KySySKQkzNQBg&hash=95927c15db9e989d7483bc5787c56fbf518bb3da72163370c659d7d7d2c42381""",

    "cookie": """cf_clearance=PVVjFU7jhAvNhUSCppKNQXLYEH7F4Y2PPmyh5zsx8qI-1778761186-1.2.1.1-QC3S.g52anLaZEQLbbeXF7vpLGm1Von8DJRCX1pP9MJ7QCc.4Pfkmc4tLMyjSQdwbu_g8trZ4rXicfIWH7SHFi63eOYRbk7ngikIKKPwESjh4JT3yF.dDd2QcJdZgyZ1RO_huxXjMqTtYhJ87EMYFQpXivOXk3DzltOm4zXFn986d2WOEukgM49d5xdsiOROeeJYOSr4AVrRpAj_7Tw5zbuQYDjVVkowcYQqGVoU8OTnng3h5MiSf9s3aE05H7dEnPuU6at_yWVcMBkJ0lRXi_S.zv677N0eGmsSseVwCrRb5IMjCK5COr1XpP18gEq7CRzk29Jrjvnd9Xo7lMGoUQ""",

    "referer": "https://portal-market.com/quick-sale-offers",
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
