import streamlit as st
import requests
import os
import time  # <--- This was missing / 之前缺少这一行

# --- Configuration / 配置 ---
REPO_PATH = "sharpvision1980/CSI300"
API_URL = f"https://api.github.com/repos/{REPO_PATH}"

st.set_page_config(page_title="GitHub Visibility Toggler", page_icon="🔒")

# --- Robust Token Loading / 鲁棒的令牌加载 ---
# This checks secrets.toml first, then environment variables
# 优先检查 secrets.toml，然后检查环境变量
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
except Exception:
    TOKEN = os.getenv("GITHUB_TOKEN")

# --- Functions / 功能函数 ---

def get_repo_status():
    """Fetches current visibility status from GitHub API."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"GitHub API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def update_visibility(new_visibility):
    """Updates the repository visibility (public or private)."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    # GitHub API uses 'visibility': 'private' or 'public'
    data = {"visibility": new_visibility}
    response = requests.patch(API_URL, headers=headers, json=data)
    return response

# --- UI Layout / 界面布局 ---
st.title("🛡️ GitHub Repo Visibility Control")
st.write(f"**Target Repository:** `{REPO_PATH}`")

if not TOKEN:
    st.error("❌ **GITHUB_TOKEN not found!**")
    st.info("Please create `.streamlit/secrets.toml` in your project folder with the following content:")
    st.code('GITHUB_TOKEN = "your_token_here"', language="toml")
    st.stop() 

# 1. Fetch current status
repo_data = get_repo_status()

if repo_data:
    # GitHub returns 'private': True/False
    is_private = repo_data.get("private")
    current_visibility = "private" if is_private else "public"
    
    # 2. Display Status Metrics
    col1, col2 = st.columns(2)
    status_color = "🔴" if is_private else "🟢"
    col1.metric("Current Status", f"{status_color} {current_visibility.upper()}")
    
    # 3. Toggle Logic
    target_visibility = "public" if is_private else "private"
    btn_label = f"Switch to {target_visibility.upper()}"
    
    st.divider()
    st.write(f"Click the button below to change visibility to **{target_visibility}**.")
    
    # Use a unique key for the button to prevent state issues
    if st.button(btn_label, type="primary", use_container_width=True):
        with st.spinner(f"Setting repository to {target_visibility}..."):
            res = update_visibility(target_visibility)
            
            if res.status_code == 200:
                st.success(f"✅ Success! Repository is now **{target_visibility}**.")
                time.sleep(1.5) # Wait a moment so user can see the success message
                st.rerun() # Refresh the UI to show new status
            else:
                st.error(f"Update Failed: {res.status_code}")
                st.json(res.json()) # Show detailed error from GitHub

# Footer info
st.sidebar.info(f"Connected as: {repo_data.get('owner', {}).get('login') if repo_data else 'Unknown'}")
