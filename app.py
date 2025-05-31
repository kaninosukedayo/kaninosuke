import streamlit as st
import json
import os

USER_DATA_FILE = "users.json"

# 初期ユーザーデータ作成（存在しない場合）
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as f:
        json.dump({}, f)

# ユーザーデータをロード
def load_users():
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

# ユーザーデータを保存
def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ログイン処理
def login():
    st.title("ログイン")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        users = load_users()
        if username in users and users[username]["password"] == password:
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが間違っています")

# ホーム画面（ログイン後）
def home():
    users = load_users()
    username = st.session_state["username"]
    user = users[username]

    st.title(f"ようこそ、{username}さん！")

    # 現在の状態
    st.subheader("あなたのステータス")
    st.write(f"エビ：{user['eb']}")
    st.write(f"保有株：{user['stock']}")
    st.write(f"株価：{user['stock_price']}")

    # 売りに出す株数の調節
    st.subheader("売りに出す株数を設定")
    max_sellable = user["stock"]
    current_for_sale = user.get("stock_for_sale", 0)
    new_for_sale = st.slider("売りに出す株数", 0, max_sellable, current_for_sale, 1)
    if st.button("売りに出す数を更新"):
        user["stock_for_sale"] = new_for_sale
        save_users(users)
        st.success(f"{new_for_sale} 株を売りに出しました")
        st.rerun()

    # 他のユーザーの株を購入
    st.subheader("株を購入する")
    for target_name, target_data in users.items():
        if target_name == username:
            continue

        stock_for_sale = target_data.get("stock_for_sale", 0)
        stock_price = target_data["stock_price"]

        st.markdown(f"### {target_name}")
        st.write(f"株価：{stock_price}")
        st.write(f"売りに出されている株数：{stock_for_sale}")

        if stock_for_sale > 0:
            buy_amount = st.number_input(
                f"{target_name}から購入する株数",
                min_value=1,
                max_value=stock_for_sale,
                step=1,
                key=f"buy_{target_name}"
            )

            if st.button(f"{target_name}の株を{buy_amount}株購入", key=f"buy_button_{target_name}"):
                total_price = buy_amount * stock_price
                if user["eb"] < total_price:
                    st.error("エビが足りません。")
                else:
                    # 購入処理
                    user["eb"] -= total_price
                    user["stock"] += buy_amount

                    target_data["stock"] -= buy_amount
                    target_data["stock_for_sale"] -= buy_amount
                    target_data["eb"] += total_price

                    save_users(users)
                    st.success(f"{target_name}の株を{buy_amount}株購入しました")
                    st.rerun()

# 新規登録
def register():
    st.title("新規登録")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("登録"):
        users = load_users()
        if username in users:
            st.error("このユーザー名はすでに使われています")
        else:
            users[username] = {
                "password": password,
                "eb": 5000,
                "stock": 10,
                "stock_price": 100,
                "stock_for_sale": 0
            }
            save_users(users)
            st.success("登録が完了しました。ログインしてください。")

# アプリのメイン関数
def main():
    if "username" not in st.session_state:
        menu = st.sidebar.selectbox("メニュー", ["ログイン", "新規登録"])
        if menu == "ログイン":
            login()
        else:
            register()
    else:
        if st.sidebar.button("ログアウト"):
            del st.session_state["username"]
            st.rerun()
        home()

if __name__ == "__main__":
    main()







