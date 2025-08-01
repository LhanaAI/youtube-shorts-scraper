# config.py

import os

# --- General Configuration ---
# Path to the CSV file where raw data will be saved.
RAW_DATA_CSV = 'lhana_shorts_raw_data.csv'

# CSV Headers: Defines the order and names of columns in the output CSV.
CSV_HEADERS = [
    'timestamp_scan', 'dummy_account_id', 'video_id', 'caption', 'hashtags_on_caption',
    'hashtags_on_description', 'description', 'channel_name', 'raw_views_count',
    'likes_count', 'comments_count', 'remix_count', 'upload_date', 'extracted_keywords',
    'sound_id', 'sound_name', 'sound_artist', 'sound_usage', 'video_url_full',
    'watch_duration_sec'
]

# YouTube Data API Key (optional): Used for more accurate data if integrated.
# It's highly recommended to set this as an environment variable for security.
# Example: export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_FALLBACK_API_KEY_IF_NEEDED") # Replace YOUR_FALLBACK_API_KEY_IF_NEEDED with a valid key if you don't use env var

# --- Scraping Behavior Configuration ---
# Target number of unique shorts to scrape per dummy account.
MAX_SHORTS_TO_SCRAPE_PER_ACCOUNT = 15 
# Initial delay between starting each dummy account thread (in seconds).
THREAD_START_DELAY_MIN = 5
THREAD_START_DELAY_MAX = 15

# --- Browser Window & Layout Configuration ---
# Minimum reasonable size for a browser window (in pixels).
MIN_BROWSER_WINDOW_SIZE = 300
# Padding between browser windows and screen edges (in pixels).
HORIZONTAL_PADDING = 10
VERTICAL_PADDING = 10
# Assumed height of the taskbar/dock (in pixels) to avoid overlapping.
TASKBAR_HEIGHT_ASSUMPTION = 50

# --- Dummy Account Profiles ---
# IMPORTANT: Replace these paths with your actual Chrome user profile paths.
# Ensure these profiles are already logged into YouTube.
# Example: C:/Users/YourUser/AppData/Local/Google/Chrome/User Data/Profile 1
DUMMY_ACCOUNTS = [
    {"id": "dummy_1", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 1"},
    {"id": "dummy_2", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 2"},
    {"id": "dummy_3", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 3"},
    {"id": "dummy_4", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 4"},
    {"id": "dummy_5", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 5"},
    {"id": "dummy_6", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 6"},
    # {"id": "dummy_7", "profile_path": "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 7"},
    # Add more dummy accounts as needed
]

# --- VPN Extension Configuration (if applicable) ---
# Set to True to attempt loading and activating VPN extension.
ENABLE_VPN = False
# Extension ID and Version for the VPN. Find this in Chrome extensions management.
VPN_EXTENSION_ID = "eppiocemhmnlbhjplcgkofciiegomcon" # ID Urban VPN Chrome Extension
VPN_EXTENSION_VERSION = "5.6.0_0" # Example version
# Base path to your VPN extension folder.
# This should point to the directory containing the specific extension ID folder.
# Example: "D:/MY_PROJECT/Mini_Project/LhanaAI/backend/tools/plugins/scrape/extensions"
VPN_EXTENSIONS_BASE_PATH = os.path.join(os.getcwd(), 'extensions') # os.path.join(os.getcwd(), 'extensions') if you want a custom path

# --- Chrome Driver Configuration ---
# Custom directory for Chromedriver (optional, if you encounter path issues).
# If None, undetected_chromedriver will manage its own driver.
CUSTOM_CHROMEDRIVER_DIR = os.path.join(os.getcwd(), 'chromedriver_custom') # os.path.join(os.getcwd(), 'chromedriver_custom') if you want a custom path

# OUTPUT MODE
FORMAT_EXT = 'csv'  # Options: 'csv', 'json'