import streamlit as st
import requests
import os
import time

# --- Configuration / 配置 ---
REPO_OWNER = "sharpvision1980"
REPO_NAME = "CSI300"  # Updated / 已更新
REPO_PATH = f"{REPO_OWNER}/{REPO_NAME}"
API_URL = f"https://api.github.com/repos/{REPO_PATH}"

st.set_page_config(page_title="Repo Visibility Guard", page_icon="🔐")

# --- Authentication Logic / 身份验证逻辑 ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["ACCESS_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Enter Password to Proceed", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Enter Password to Proceed", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- GitHub Logic / GitHub 逻辑 ---
def get_repo_status(token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            st.error(f"Repository `{REPO_PATH}` not found. Check the name or token permissions.")
            return None
        return None
    except:
        return None

def update_visibility(token, new_visibility):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    data = {"visibility": new_visibility}
    return requests.patch(API_URL, headers=headers, json=data)

# --- Main App Execution / 主程序执行 ---

if check_password():
    # --- Authorized Area / 已授权区域 ---
    st.title("🛡️ Repo Visibility Control")
    st.subheader(f"Target: `{REPO_NAME}`")
    
    # Load GitHub Token
    try:
        TOKEN = st.secrets["GITHUB_TOKEN"]
    except Exception:
        TOKEN = os.getenv("GITHUB_TOKEN")

    if not TOKEN:
        st.error("Missing GITHUB_TOKEN in secrets.")
        st.stop()

    repo_data = get_repo_status(TOKEN)

    if repo_data:
        is_private = repo_data.get("private")
        current_vis = "private" if is_private else "public"
        
        st.markdown(f"[🔗 View `{REPO_NAME}` on GitHub](https://github.com/{REPO_PATH})")
        
        col1, col2 = st.columns(2)
        status_emoji = "🔴" if is_private else "🟢"
        col1.metric("Current Status", f"{status_emoji} {current_vis.upper()}")
        col2.metric("Owner", REPO_OWNER)
        
        target_vis = "public" if is_private else "private"
        
        st.divider()
        if target_vis == "public":
            st.warning("⚠️ **Warning**: Making this repo PUBLIC will expose the code to everyone.")

        if st.button(f"🚀 Switch to {target_vis.upper()}", type="primary", use_container_width=True):
            with st.spinner(f"Updating GitHub to {target_vis}..."):
                res = update_visibility(TOKEN, target_vis)
                if res.status_code == 200:
                    st.success(f"✅ Success! `{REPO_NAME}` is now **{target_vis}**.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(f"Update Failed: {res.status_code}")
                    st.json(res.json())
    
    # Logout button in sidebar
    if st.sidebar.button("Logout / 退出登录"):
        st.session_state["password_correct"] = False
        st.rerun()
