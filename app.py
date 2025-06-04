import streamlit as st
import json
import os

USER_FILE = "users.json"
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

users = load_users()

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
                "owned_from": {},
                "sell_backs": []
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

    st.subheader("株の購入")
    targets = [u for u in users if u != username and not users[u]["banned"] and users[u].get("listed_stock", 0) > 0]
    if targets:
        target_user = st.selectbox("購入対象プレイヤー", targets)
        target_data = users[target_user]
        price = target_data["stock_price"]
        listed = target_data.get("listed_stock", 0)
        st.write(f"{target_user} の株価: {price} エビ、出品数: {listed} 株")

        buy_num = st.number_input("購入株数", min_value=1, max_value=listed, step=1)
        if st.button("株を購入"):
            total = buy_num * price
            if user["ebi"] >= total:
                user["ebi"] -= total
                user["stock"] += buy_num
                user["owned_from"][target_user] = user["owned_from"].get(target_user, 0) + buy_num
                target_data["ebi"] += total
                target_data["listed_stock"] -= buy_num
                save_users(users)
                st.success(f"{target_user} の株を {buy_num} 株購入しました！")
            else:
                st.error("エビが足りません")
    else:
        st.info("現在、購入可能な株がありません")

    st.subheader("📤 他社株の売却提案")
    owned_from = user.get("owned_from", {})
    for seller, amount in owned_from.items():
        if amount > 0:
            st.write(f"{seller} から {amount} 株保有中")
            sell_back_amount = st.number_input(f"{seller} に売り返す株数", min_value=1, max_value=amount, step=1, key=f"sell_{seller}")
            price_back = st.number_input(f"{seller} に売り返す株価（1株あたり）", min_value=1, step=1, key=f"price_{seller}")
            if st.button(f"{seller} に売却提案"):
                proposal = {"from": username, "amount": sell_back_amount, "price_per_stock": price_back}
                users[seller].setdefault("sell_backs", []).append(proposal)
                save_users(users)
                st.success(f"{seller} に売却提案を送りました")

    st.subheader("📬 受けた売却提案")
    for i, proposal in enumerate(user.get("sell_backs", [])):
        from_user = proposal["from"]
        amount = proposal["amount"]
        price = proposal["price_per_stock"]
        total = amount * price
        st.write(f"{from_user} が {amount} 株を {price} エビ/株 で売却提案（計 {total} エビ）")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"承諾（{i}）"):
                if user["ebi"] >= total:
                    user["ebi"] -= total
                    users[from_user]["ebi"] += total
                    users[from_user]["stock"] -= amount
                    users[from_user]["owned_from"][username] -= amount
                    user["stock"] += amount
                    user["sell_backs"].pop(i)
                    save_users(users)
                    st.success(f"{from_user} からの売却を承諾しました")
                else:
                    st.error("エビが足りません")
        with col2:
            if st.button(f"キャンセル（{i}）"):
                user["sell_backs"].pop(i)
                save_users(users)
                st.info("売却提案をキャンセルしました")

    st.subheader("説明コメントの更新")
    comment = st.text_area("説明", value=user["comment"])
    if st.button("説明を更新"):
        user["comment"] = comment
        save_users(users)
        st.success("説明を更新しました")

if "username" not in st.session_state:
    login()
else:
    home()
