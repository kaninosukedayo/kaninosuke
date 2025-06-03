import streamlit as st
import json
import os

USER_FILE = "users.json"
REQUEST_FILE = "sellback_requests.json"
DEFAULT_STOCK_PRICE = 120

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def load_requests():
    if not os.path.exists(REQUEST_FILE):
        with open(REQUEST_FILE, "w") as f:
            json.dump([], f)
    with open(REQUEST_FILE, "r") as f:
        return json.load(f)

def save_requests(requests):
    with open(REQUEST_FILE, "w") as f:
        json.dump(requests, f)

users = load_users()
requests = load_requests()

def login():
    st.title("投資ゲーム ログイン")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        if username in users and users[username]["password"] == password:
            st.session_state["username"] = username
            st.success("ログイン成功！")
            st.experimental_rerun()
        else:
            st.error("ユーザー名またはパスワードが間違っています")

    if st.button("新規登録"):
        if username in users:
            st.error("このユーザー名は既に存在します")
        else:
            users[username] = {
                "password": password,
                "ebi": 5000,
                "stock": 0,
                "listed_stock": 0,
                "comment": "",
                "banned": False,
                "stock_price": DEFAULT_STOCK_PRICE,
                "owned_from": {}  # key: seller, value: number of stocks bought from them
            }
            save_users(users)
            st.success("登録完了！ログインしてください")

def home():
    st.title("🦐 投資ゲーム ホーム")
    username = st.session_state["username"]
    user = users[username]

    if user.get("banned"):
        st.error("あなたのアカウントは凍結されています。")
        return

    st.write(f"### ようこそ、{username}さん")
    st.metric("🦐 エビ", user["ebi"])
    st.metric("📈 保有株数", user["stock"])
    st.metric("💹 あなたの株価", user["stock_price"])
    st.metric("🧺 売りに出している株数", user.get("listed_stock", 0))

    st.subheader("🛒 売りに出す株数の設定")
    new_listed = st.number_input("売りに出す株数", min_value=0, step=1, value=user.get("listed_stock", 0))
    if st.button("売り出し株数を更新"):
        user["listed_stock"] = new_listed
        save_users(users)
        st.success(f"{new_listed} 株を市場に出しました")

    st.subheader("株の売買")
    available_targets = [u for u in users if u != username and not users[u]["banned"] and users[u].get("listed_stock", 0) > 0]
    if available_targets:
        target_user = st.selectbox("購入対象プレイヤー", available_targets)
        target_data = users[target_user]
        target_price = target_data["stock_price"]
        target_listed = target_data.get("listed_stock", 0)
        st.write(f"{target_user} の株価: {target_price} エビ（残り {target_listed} 株）")

        buy_amount = st.number_input("購入株数", min_value=1, max_value=target_listed, step=1, key="buy_amount")
        if st.button("株を購入"):
            total_cost = buy_amount * target_price
            if user["ebi"] >= total_cost:
                user["ebi"] -= total_cost
                user["stock"] += buy_amount
                user["owned_from"][target_user] = user["owned_from"].get(target_user, 0) + buy_amount
                target_data["ebi"] += total_cost
                target_data["listed_stock"] -= buy_amount
                save_users(users)
                st.success(f"{target_user} の株を {buy_amount} 株購入しました！")
            else:
                st.error("エビが足りません")
    else:
        st.info("現在、購入可能な株がありません。")

        st.subheader("🤝 他社株の売却（売り返し）")
    owned_from = user.get("owned_from", {})
    others = [u for u in users if u != username and not users[u].get("banned")]

    if not others:
        st.info("売却可能な相手がいません")
    else:
        for seller in others:
            owned_amount = owned_from.get(seller, 0)
            st.markdown(f"#### {seller} への売却提案")
            st.write(f"保有株数（{seller} から購入）: {owned_amount} 株")
            
            sell_back_count = st.number_input(
                f"{seller} への売却株数", min_value=0, max_value=owned_amount,
                step=1, key=f"sell_back_count_{seller}"
            )
            propose_price = st.number_input(
                f"1株あたりの提案価格（エビ）", min_value=1,
                key=f"sell_back_price_{seller}"
            )

            if sell_back_count == 0:
                st.warning("売却株数が 0 のため、売却できません")
                st.button("売却提案（無効）", disabled=True, key=f"disabled_button_{seller}")
            elif st.button(f"{seller} に売却提案", key=f"sell_propose_button_{seller}"):
                if "sell_backs" not in users[seller]:
                    users[seller]["sell_backs"] = []
                users[seller]["sell_backs"].append({
                    "from": username,
                    "amount": sell_back_count,
                    "price_per_stock": propose_price
                })
                save_users(users)
                st.success(f"{seller} に {sell_back_count} 株（@{propose_price}）の売却提案を送りました！")
=f"

    st.subheader("💬 受け取った売り返し提案")
    my_requests = [r for r in requests if r["to"] == username]
    for req in my_requests:
        st.info(f"{req['from']} から {req['amount']} 株を {req['price']} エビで買い戻して欲しいという提案")
        if st.button("承諾", key=f"accept_{req['from']}"):
            buyer = users[req["from"]]
            total_cost = req["amount"] * req["price"]
            if user["ebi"] >= total_cost:
                user["ebi"] -= total_cost
                user["stock"] += req["amount"]
                buyer["ebi"] += total_cost
                buyer["stock"] -= req["amount"]
                buyer["owned_from"][username] -= req["amount"]
                requests.remove(req)
                save_users(users)
                save_requests(requests)
                st.success("売り返しを承諾しました")
            else:
                st.error("エビが足りません（あなた）")
        if st.button("拒否", key=f"reject_{req['from']}"):
            requests.remove(req)
            save_requests(requests)
            st.info("売り返しを拒否しました")

    st.subheader("説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

    st.subheader("他のプレイヤーにエビを送る")
    to_user = st.selectbox("送信先", [u for u in users if u != username and not users[u]["banned"]], key="send_user")
    ebi_amount = st.number_input("送るエビ数", min_value=1, step=1, key="send_amount")
    if st.button("送信"):
        if user["ebi"] >= ebi_amount:
            user["ebi"] -= ebi_amount
            users[to_user]["ebi"] += ebi_amount
            save_users(users)
            st.success(f"{to_user} に {ebi_amount} エビを送信しました！")
        else:
            st.error("エビが足りません")

    st.subheader("プレイヤー一覧")
    for name, data in users.items():
        if not data.get("banned"):
            st.write(f"🧑‍💼 **{name}** ｜🦐 {data['ebi']} ｜📈 {data['stock']} 株 ｜💹 株価: {data['stock_price']} ｜🧺 出品株数: {data.get('listed_stock', 0)}")
            st.caption(data.get("comment", ""))

    if username == "admin":
        st.subheader("👮 管理者パネル")

        ban_user = st.selectbox("BANするユーザー", [u for u in users if u != "admin"])
        if st.button("BAN実行"):
            users[ban_user]["banned"] = True
            save_users(users)
            st.success(f"{ban_user} をBANしました")

        st.subheader("🦐 エビ量の調整")
        target_user = st.selectbox("対象ユーザー", [u for u in users if u != "admin"], key="ebi_target")
        ebi_change = st.number_input("増減させるエビ量（マイナスも可）", value=0, step=100, key="ebi_change")
        if st.button("エビを調整する"):
            users[target_user]["ebi"] += ebi_change
            if users[target_user]["ebi"] < 0:
                users[target_user]["ebi"] = 0
            save_users(users)
            st.success(f"{target_user} のエビを {'増加' if ebi_change >= 0 else '減少'} させました")

        st.subheader("💹 株価自動計算")
        calc_user = st.selectbox("株価を計算するユーザー", [u for u in users if u != "admin"], key="stock_calc_user")
        base = 100
        city = st.number_input("都市数", min_value=0, step=1)
        army = st.number_input("軍の数", min_value=0.0, step=0.5)
        kill_rate = st.number_input("キルレ (K/D)", min_value=0.0, step=0.1)
        expect = st.number_input("私の期待値", min_value=0.0, step=1.0)

        if st.button("株価を計算して反映"):
            price = int(base + city * 2 + army * 0.5 + kill_rate * 10 + expect * 1)
            users[calc_user]["stock_price"] = price
            save_users(users)
            st.success(f"{calc_user} の株価を {price} に設定しました")

if "username" not in st.session_state:
    login()
else:
    home()



