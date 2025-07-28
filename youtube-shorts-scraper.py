import pandas as pd
import time
import random
import threading
import csv
import os
import traceback
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import tkinter as tk
import sys

# Import configurations from config.py
from config import (
    RAW_DATA_CSV, CSV_HEADERS, DUMMY_ACCOUNTS, YOUTUBE_API_KEY,
    MAX_SHORTS_TO_SCRAPE_PER_ACCOUNT, THREAD_START_DELAY_MIN, THREAD_START_DELAY_MAX,
    MIN_BROWSER_WINDOW_SIZE, HORIZONTAL_PADDING, VERTICAL_PADDING, TASKBAR_HEIGHT_ASSUMPTION,
    ENABLE_VPN, VPN_EXTENSION_ID, VPN_EXTENSION_VERSION, VPN_EXTENSIONS_BASE_PATH,
    CUSTOM_CHROMEDRIVER_DIR
)

# --- Dynamic Window Sizing and Positioning Calculation ---
SCREEN_WIDTH, SCREEN_HEIGHT = 0, 0 # Will be updated by get_screen_resolution
BROWSER_WINDOW_WIDTH, BROWSER_WINDOW_HEIGHT = 0, 0
WINDOW_POSITIONS = []

def get_screen_resolution():
    """
    Retrieves the primary screen resolution using Tkinter.
    Falls back to a default resolution if Tkinter encounters an error.
    """
    try:
        root = tk.Tk()
        root.withdraw() # Hide the main Tkinter window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    except Exception as e:
        print(f"Error getting screen resolution with tkinter: {e}")
        print("Falling back to default resolution (1920x1080).")
        return 1920, 1080 # Fallback if tkinter has issues

def calculate_window_layout():
    """
    Calculates optimal browser window sizes and positions based on screen resolution
    and the number of dummy accounts, to arrange them in a grid.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, BROWSER_WINDOW_WIDTH, BROWSER_WINDOW_HEIGHT, WINDOW_POSITIONS

    SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_resolution()
    TOTAL_DUMMY_ACCOUNTS = len(DUMMY_ACCOUNTS)

    # Calculate optimal number of columns and rows for a grid layout
    num_cols = int(TOTAL_DUMMY_ACCOUNTS**0.5) # Square root for width approximation
    if num_cols == 0: num_cols = 1 # Ensure not zero
    num_rows = (TOTAL_DUMMY_ACCOUNTS + num_cols - 1) // num_cols # Round up

    # Calculate browser window size per account
    BROWSER_WINDOW_WIDTH = (SCREEN_WIDTH - (num_cols + 1) * HORIZONTAL_PADDING) // num_cols
    BROWSER_WINDOW_HEIGHT = (SCREEN_HEIGHT - TASKBAR_HEIGHT_ASSUMPTION - (num_rows + 1) * VERTICAL_PADDING) // num_rows

    # Ensure minimum reasonable size
    if BROWSER_WINDOW_WIDTH < MIN_BROWSER_WINDOW_SIZE:
        BROWSER_WINDOW_WIDTH = MIN_BROWSER_WINDOW_SIZE
        print(f"Warning: Browser width set to minimum {MIN_BROWSER_WINDOW_SIZE}px due to too many dummy accounts.")
    if BROWSER_WINDOW_HEIGHT < MIN_BROWSER_WINDOW_SIZE:
        BROWSER_WINDOW_HEIGHT = MIN_BROWSER_WINDOW_SIZE
        print(f"Warning: Browser height set to minimum {MIN_BROWSER_WINDOW_SIZE}px due to too many dummy accounts.")

    # Generate window positions
    WINDOW_POSITIONS = []
    for i in range(TOTAL_DUMMY_ACCOUNTS):
        row = i // num_cols
        col = i % num_cols
        
        x = col * (BROWSER_WINDOW_WIDTH + HORIZONTAL_PADDING) + HORIZONTAL_PADDING
        y = row * (BROWSER_WINDOW_HEIGHT + VERTICAL_PADDING) + VERTICAL_PADDING
        
        WINDOW_POSITIONS.append((x, y))

    print(f"Detected Screen Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"Total Dummy Accounts: {TOTAL_DUMMY_ACCOUNTS}")
    print(f"Browser Window Size Per Account: {BROWSER_WINDOW_WIDTH}x{BROWSER_WINDOW_HEIGHT}")
    print(f"Layout: {num_rows} rows x {num_cols} columns")
    print(f"Calculated Window Positions: {WINDOW_POSITIONS}")


# --- Anti-Bot Utility Functions ---

def human_like_delay(min_sec=2, max_sec=5):
    """Introduces a random human-like delay."""
    time.sleep(random.uniform(min_sec, max_sec))

def simulate_watch_video(video_url, min_duration=5, max_duration=15):
    """
    Simulates watching a video by returning a random watch duration.
    (Does not actually open the video URL in the browser).
    """
    watch_duration = random.randint(min_duration, max_duration)
    print(f"Simulating watch of {video_url} for {watch_duration} seconds.")
    return watch_duration

# --- WebDriver Initialization Function (using undetected_chromedriver) ---
def init_undetected_driver(profile_path=None, headless=False, position_index=None):
    """
    Initializes and configures an undetected_chromedriver instance.
    Includes options for user profiles, window positioning, and VPN extension loading.
    """
    options = uc.ChromeOptions()
    # Assuming Chrome binary location, adjust if necessary
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"

    # Load VPN extension if enabled
    if ENABLE_VPN:
        vpn_ext_path = os.path.join(VPN_EXTENSIONS_BASE_PATH, VPN_EXTENSION_ID, VPN_EXTENSION_VERSION)
        if os.path.exists(vpn_ext_path):
            options.add_argument(f"--load-extension={vpn_ext_path}")
            print(f"Loading VPN extension from: {vpn_ext_path}")
        else:
            print(f"Warning: VPN extension not found at {vpn_ext_path}. Proceeding without VPN.")

    # Set window size and position regardless of headless mode
    options.add_argument(f"--window-size={BROWSER_WINDOW_WIDTH},{BROWSER_WINDOW_HEIGHT}")
    if position_index is not None and position_index < len(WINDOW_POSITIONS):
        x, y = WINDOW_POSITIONS[position_index]
        options.add_argument(f"--window-position={x},{y}")
    else:
        print(f"Warning: Window position for index {position_index} not found or invalid. Browser might appear at default position.")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--mute-audio")
    else:
        # Mute audio even if not headless to avoid noise
        options.add_argument("--mute-audio")
    
    # Use user-data-dir to load pre-logged-in profiles
    if profile_path:
        base_user_data_dir = os.path.dirname(profile_path)
        profile_dir_name = os.path.basename(profile_path)

        if not os.path.exists(profile_path):
            print(f"Warning: Profile path not found, undetected_chromedriver will create a new one: {profile_path}")

        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument(f"--profile-directory={profile_dir_name}")
        print(f"Using User Data Dir: {base_user_data_dir}, Profile: {profile_dir_name}")
    else:
        print("Warning: No profile_path provided, a temporary profile will be used.")

    # Set random User-Agent (important for anti-bot measures)
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Set driver executable path if a custom directory is specified
    driver_executable_path = None
    if CUSTOM_CHROMEDRIVER_DIR:
        os.makedirs(CUSTOM_CHROMEDRIVER_DIR, exist_ok=True)
        driver_executable_path = os.path.join(CUSTOM_CHROMEDRIVER_DIR, 'chromedriver.exe')
        if not os.path.exists(driver_executable_path):
            print(f"Error: Chromedriver not found at {driver_executable_path}. Please place it there or set CUSTOM_CHROMEDRIVER_DIR to None.")
            sys.exit(1) # Exit if driver not found in custom path

    driver = uc.Chrome(options=options, driver_executable_path=driver_executable_path)
    # Evade webdriver detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Force window size and position after launch
    try:
        driver.set_window_size(BROWSER_WINDOW_WIDTH, BROWSER_WINDOW_HEIGHT)
        print(f"[{profile_path}] Successfully set window size to {BROWSER_WINDOW_WIDTH}x{BROWSER_WINDOW_HEIGHT}")
    except WebDriverException as e:
        print(f"[{profile_path}] Failed to set window size via WebDriver: {e}")

    try:
        if position_index is not None and position_index < len(WINDOW_POSITIONS):
            x, y = WINDOW_POSITIONS[position_index]
            driver.set_window_position(x, y)
            print(f"[{profile_path}] Successfully set window position to {x},{y}")
    except WebDriverException as e:
        print(f"[{profile_path}] Failed to set window position via WebDriver: {e}")

    # --- Logic to activate VPN (automation is challenging) ---
    # This part often requires specific UI interaction with the extension's popup.
    # The example below is illustrative and highly dependent on the VPN extension's UI.
    if ENABLE_VPN:
        try:
            status_text_selector = (By.CLASS_NAME, "connection-state__status-text") 
            driver.get(f"chrome-extension://{VPN_EXTENSION_ID}/popup/index.html")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "play-button")))
            driver.find_element(By.CLASS_NAME, "play-button").click()
            print(f"[{profile_path}] Attempting to activate VPN via extension.")
            human_like_delay(3, 5)
            WebDriverWait(driver, 30).until(
                EC.text_to_be_present_in_element(status_text_selector, "Connected")
            )
            print(f"[{profile_path}] VPN successfully connected! Status: Connected.")
            human_like_delay(1, 2)
            # Optional: Close extension tab if not needed
            # driver.close() 
            # driver.switch_to.window(driver.window_handles[0])
        except TimeoutException:
            print(f"[{profile_path}] Timeout: VPN failed to connect within the specified time.")
        except NoSuchElementException:
            print(f"[{profile_path}] VPN UI element (button or status) not found. Check selectors.")
        except Exception as e:
            print(f"[{profile_path}] Unexpected error while managing VPN: {e}")
            traceback.print_exc()

    return driver

# --- Function to Extract Data from YouTube Shorts Page ---
def extract_shorts_data(driver, dummy_id, scraped_video_ids):
    """
    Extracts relevant data from the currently displayed YouTube Shorts video.
    Includes logic to handle encoding issues and extract various metrics.
    """
    scraped_data = []
    
    try:
        # Wait until the main shorts video element is loaded.
        # On youtube.com/shorts, videos are loaded within 'ytd-reel-video-renderer'.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "ytd-reel-video-renderer"))
        )
        print(f"Dummy account {dummy_id}: Shorts element detected on page.")

        # Get HTML and parse with BeautifulSoup, applying encoding fix for mojibake
        # This is the crucial fix for the 'â˜ ï¸ðŸ‘€' issue.
        try:
            clean_page_source = driver.page_source.encode('latin1').decode('utf-8')
        except UnicodeEncodeError:
            clean_page_source = driver.page_source
            print(f"Warning: Encoding fix failed for {dummy_id}, using original page_source.")
            
        soup = BeautifulSoup(clean_page_source, 'html.parser')
        
        # Find the active shorts video element (usually one in full view)
        shorts_element = soup.find("ytd-reel-video-renderer")
        
        if not shorts_element:
            print(f"Dummy account {dummy_id}: No 'ytd-reel-video-renderer' element found by BeautifulSoup in current view.")
            return scraped_data

        try:
            # Extract Video ID from the current URL
            current_url = driver.current_url
            video_id = None
            if "/shorts/" in current_url:
                video_id = current_url.split("/shorts/")[1].split("?")[0].split("&")[0]
            elif "/watch?v=" in current_url:
                video_id = current_url.split("/watch?v=")[1].split("&")[0]
            
            if not video_id or video_id in scraped_video_ids:
                return [] # Return empty list if ID not found or already scraped

            full_video_url = f"https://www.youtube.com/shorts/{video_id}" if video_id else "NaN" # Placeholder URL

            # Locate relevant elements within the shorts panel
            shorts_panel_elems = soup.find("div", id="shorts-panel-container").find("div", id="anchored-panel").find_all("ytd-engagement-panel-section-list-renderer")

            # Check if it's a valid video and not an ad or other panel
            if len(shorts_panel_elems) > 1: # Assuming second panel is usually details
                shorts_panel = shorts_panel_elems[1].find("div", id="content").find("ytd-structured-description-content-renderer")

                # Shorts description related elements
                short_description_elem = soup.find("ytd-video-description-header-renderer")
                short_description_expander_elem = soup.find("ytd-expandable-video-description-body-renderer")

                # Metapanel for main video info
                metapanel_elem = soup.find("div", id="metapanel").find("yt-reel-metapanel-view-model")

                # Extract Caption
                caption_elem = metapanel_elem.find("yt-shorts-video-title-view-model").find("h2").find("span")
                caption = caption_elem.get_text(strip=True, separator=' ') if caption_elem else "Caption not found"

                # Extract Hashtags
                hashtags = {
                    'hashtag_on_caption': [],
                    'hashtag_on_description': []
                }
                hashtags_on_caption_elem = caption_elem.find_all("a", class_="yt-core-attributed-string__link")
                for hashtag in hashtags_on_caption_elem:
                    hashtags['hashtag_on_caption'].append(hashtag.get_text(strip=True))

                # Extract Description (requires clicking to expand)
                is_expanded_button_clicked = False
                try:
                    # Attempt to find and click the description expand button
                    expanded_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div#expanded"))
                    )
                    if expanded_button:
                        expanded_button.click()
                        print(f"Dummy account {dummy_id}: Clicking description expand button.")
                        human_like_delay(random.uniform(2, 5))
                        is_expanded_button_clicked = True
                except (TimeoutException, NoSuchElementException):
                    print(f"Dummy account {dummy_id}: Description expand button not found or clickable.")
                    pass

                description_elem = None
                if is_expanded_button_clicked and short_description_expander_elem:
                    description_elem = short_description_expander_elem.find("div", id="expanded").find("yt-formatted-string")
                elif short_description_expander_elem: # Fallback if button not clicked/found
                    description_elem = short_description_expander_elem.find("div", id="snippet").find("span", id="snippet-text")

                description = description_elem.get_text(strip=True, separator=' ') if description_elem else "Description not found"

                if description_elem:
                    hashtags_on_description = description_elem.find_all("a")
                    for hashtag2 in hashtags_on_description:
                        hashtags['hashtag_on_description'].append(hashtag2.get_text(strip=True))

                # Extract Channel Name
                channel_name_elem = shorts_element.find("yt-reel-channel-bar-view-model").find("span").find("a")
                channel_name = channel_name_elem.get_text(strip=True) if channel_name_elem else "Channel not found"
                channel_id = "NaN" # Requires further scraping or YouTube Data API

                # Extract Views Count (can be tricky due to dynamic loading and abbreviations)
                views_count_elem = short_description_elem.find("view-count-factoid-renderer")
                raw_views_count = views_count_elem.find("span", class_="ytwFactoidRendererValue").find("span").get_text(strip=True) if views_count_elem else "0"

                # Extract Likes Count (often from aria-label)
                likes_count_elem = short_description_elem.find_all("factoid-renderer")[0]
                likes_count = likes_count_elem['aria-label'] if likes_count_elem and 'aria-label' in likes_count_elem.attrs else "0"

                # Extract Comments Count (often from aria-label of button)
                comments_button_elem = shorts_element.find("div", id="comments-button")
                comments_count = comments_button_elem.find("button")['aria-label'] if comments_button_elem and 'aria-label' in comments_button_elem.find("button").attrs else "0"

                # Extract Remix Count
                remix_button_elem = shorts_element.find("div", id="remix-button")
                remix_count = remix_button_elem.find("button")['aria-label'] if remix_button_elem and 'aria-label' in remix_button_elem.find("button").attrs else "0"
                
                # Extract Upload Date (tricky from Shorts feed, better with API)
                upload_date_elem = short_description_elem.find_all("factoid-renderer")[2]
                upload_date = upload_date_elem['aria-label'] if upload_date_elem and 'aria-label' in upload_date_elem.attrs else "NaN"

                # Simulate video watch duration
                watch_duration = simulate_watch_video(full_video_url)

                # Extract Keywords
                keywords_model = metapanel_elem.find("yt-shorts-suggested-action-view-model")
                extracted_keywords_elem = keywords_model.find("div", class_="ytShortsSuggestedActionViewModelStaticHostPrimaryText").find("span") if keywords_model else None
                keywords = extracted_keywords_elem.get_text(strip=True, separator=' ') if extracted_keywords_elem else "NaN"

                # Extract Sound Usage
                marquee_sound_elem = metapanel_elem.find("div", class_="ytReelSoundMetadataViewModelMarqueeContainer")
                sound_elem = marquee_sound_elem.find("span").find("span").find("span") if marquee_sound_elem else None
                sound_use = sound_elem.get_text(strip=True) if sound_elem else "NaN"
                sound_id = "NaN" # Requires further scraping or YouTube Data API
                sound_name = sound_use # Use sound_use as name for now
                sound_artist = "NaN" # Requires further scraping or YouTube Data API
                video_category = "NaN" # Requires further analysis/classification

                scraped_data.append({
                    'timestamp_scan': datetime.now().isoformat(),
                    'dummy_account_id': dummy_id,
                    'video_id': video_id,
                    'caption': caption,
                    'hashtags': hashtags, # Storing as dict, consider flattening for CSV
                    'description': description,
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'raw_views_count': raw_views_count,
                    'likes_count': likes_count,
                    'comments_count': comments_count,
                    'remix_count': remix_count, 
                    'upload_date': upload_date,
                    'extracted_keywords': keywords,
                    'sound_id': sound_id,
                    'sound_name': sound_name,
                    'sound_artist': sound_artist,
                    'video_url_full': full_video_url,
                    'watch_duration_sec': watch_duration,
                    'video_category': video_category
                })
                scraped_video_ids.add(video_id) # Add ID to the set of scraped videos
            else:
                print(f"Dummy account {dummy_id}: Detected shorts element appears to be an ad or unparseable.")
                return []

        except Exception as inner_exception:
            print(f"Error processing the current video element for {dummy_id}: {inner_exception}")
            print("--- Traceback Detail ---")
            traceback.print_exc()
            print("------------------------")
            return []
    except TimeoutException:
        print(f"Timeout: Could not find 'ytd-reel-video-renderer' element after waiting.")
    except Exception as outer_exception:
        print(f"Error extracting shorts data from page for {dummy_id}: {outer_exception}")
    
    return scraped_data

# --- Function to Write Data to CSV (with safe file handling) ---
def write_to_csv(data, filename, headers):
    """
    Appends a list of dictionaries (data rows) to a CSV file.
    Writes headers only if the file is new or empty.
    """
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

# --- Main Task Function for Each Dummy Account ---
def dummy_account_task(dummy_info):
    """
    Main task runner for a single dummy account.
    Handles browser initialization, navigation, data scraping, and error handling.
    """
    dummy_id = dummy_info['id']
    profile_path = dummy_info['profile_path']
    position_index = dummy_info.get('position_index')
    print(f"Starting task for dummy account: {dummy_id}")
    driver = None
    scraped_video_ids = set() # Set to track video IDs scraped per session
    try:
        # Pass headless=True if you want the browser to run in the background without UI
        driver = init_undetected_driver(profile_path=profile_path, headless=False, position_index=position_index) 
        
        # Navigate to YouTube Shorts
        driver.get("https://www.youtube.com/shorts")
        human_like_delay(5, 10) # Initial delay to load the page

        all_scraped_data_for_account = []
        scraped_count = 0

        while scraped_count < MAX_SHORTS_TO_SCRAPE_PER_ACCOUNT:
            print(f"Dummy account {dummy_id}: Scraping attempt {scraped_count + 1}/{MAX_SHORTS_TO_SCRAPE_PER_ACCOUNT}")
            
            # Extract data from the currently active short
            # We need to get page_source again each time as content changes without full page reload
            new_data = extract_shorts_data(driver, dummy_id, scraped_video_ids)
            
            if new_data:
                all_scraped_data_for_account.extend(new_data)
                scraped_count += len(new_data)
                print(f"Dummy account {dummy_id}: Found {len(new_data)} new videos. Total: {scraped_count}")
                
                # Simulate watching (if new videos were found)
                valid_urls = [d['video_url_full'] for d in new_data if d['video_url_full'] != "NaN"]
                if valid_urls and random.random() < 0.3: # 30% chance to simulate watch
                    random_video_url = random.choice(valid_urls)
                    simulate_watch_video(random_video_url, 10, 30)
                    human_like_delay(random.uniform(5, 10))

            # --- Navigate to the Next Short ---
            navigated = False
            try:
                # Attempt to click the "Next video" button (common selector)
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        "button.yt-spec-button-shape-next[aria-label='Video berikutnya'], " # Indonesian label
                        "button.yt-spec-button-shape-next[aria-label='Next video']" # English label
                    )) 
                )
                if next_button:
                    next_button.click()
                    print(f"Dummy account {dummy_id}: Clicking 'Next video' button.")
                    human_like_delay(random.uniform(2, 5))
                    navigated = True
            except (TimeoutException, NoSuchElementException):
                print(f"Dummy account {dummy_id}: 'Next video' button not found or clickable.")
                pass

            # If "Next" button not found, try sending Keys.ARROW_DOWN
            if not navigated:
                print(f"Dummy account {dummy_id}: Attempting to scroll Shorts player with ARROW_DOWN...")
                try:
                    # Sending Keys.ARROW_DOWN to the body scrolls the Shorts player
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ARROW_DOWN)
                    human_like_delay(random.uniform(2, 5))
                    navigated = True
                except Exception as scroll_exception:
                    print(f"Dummy account {dummy_id}: Failed to scroll Shorts player with ARROW_DOWN: {scroll_exception}")

            if not navigated:
                print(f"Dummy account {dummy_id}: Could not navigate to the next video. Stopping scraping.")
                break # Stop if unable to navigate

            # Add a longer delay after several interactions to avoid detection
            if (scraped_count + 1) % 10 == 0: # Every 10 videos
                print(f"Dummy account {dummy_id}: Longer delay to avoid detection...")
                human_like_delay(15, 30) 

        if all_scraped_data_for_account:
            # Remove final duplicates before saving to CSV
            unique_scraped_data = []
            seen_ids = set()
            for item in all_scraped_data_for_account:
                if item['video_id'] not in seen_ids:
                    unique_scraped_data.append(item)
                    seen_ids.add(item['video_id'])

            write_to_csv(unique_scraped_data, RAW_DATA_CSV, CSV_HEADERS)
            print(f"Dummy account {dummy_id} scraped {len(unique_scraped_data)} unique videos and saved to CSV.")
        else:
            print(f"Dummy account {dummy_id} found no data.")

    except Exception as main_exception:
        print(f"An error occurred for dummy account {dummy_id}: {main_exception}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit() # Close the browser
        return

# --- Main Execution ---
if __name__ == "__main__":
    # Calculate window layout once at the start
    calculate_window_layout()

    # Initialize CSV file if it doesn't exist (write header only)
    if not os.path.exists(RAW_DATA_CSV) or os.path.getsize(RAW_DATA_CSV) == 0:
        with open(RAW_DATA_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()

    threads = []
    for i, account_info in enumerate(DUMMY_ACCOUNTS):
        account_info['position_index'] = i 
        thread = threading.Thread(target=dummy_account_task, args=(account_info,))
        threads.append(thread)
        thread.start()
        human_like_delay(random.uniform(THREAD_START_DELAY_MIN, THREAD_START_DELAY_MAX)) # Delay between starting threads

    for thread in threads:
        thread.join() # Wait for all threads to complete

    print("\nAll dummy account tasks completed. Raw data saved to:", RAW_DATA_CSV)
    print("Next step: Use your data analysis skills to clean, analyze, and build your dashboard from this CSV!")