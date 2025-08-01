# YouTube Shorts Scraper

![Python Version](https://img.shields.io/badge/Python-3.10-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Development-orange.svg)

A Python-based scraping tool designed to collect data from YouTube Shorts videos. This project is a foundational component of a larger initiative, **Lhana AI**, which aims to analyze viral patterns and content trends across short-form video platforms.

## Project Goals

The primary objectives of `youtube-shorts-scraper` are to:
- Collect raw data (such as views, likes, comments, remix counts, captions, hashtags, sound usage) from YouTube Shorts videos.
- Facilitate the analysis of viral trends and the behavior of YouTube Shorts' recommendation algorithm.
- Provide clean and structured datasets for the future development of virality prediction models (as part of Lhana AI Phase 1).

## Next Project
The tool is finally complete. There will be no more major updates, only necessary fixes and adjustments to the HTML structure of YouTube if it changes.

The next phase is data cleansing, which I'll be doing in Google Colab and sharing here. The third and final phase is data analysis. I will not be sharing this part, as it involves a proprietary formula. This is where I'll be pulling YouTube Shorts videos for analysis. I'll be using Google Vision AI to extract the content and OpenAI Whisper to transcribe the audio for keyword searching. Afterward, a final analysis will be conducted using my proprietary XYZ formula.

## Features

-   **Automated Data Collection:** Utilizes Selenium to simulate user interactions and gather data from YouTube Shorts feeds.
-   **Dummy Account Support:** Designed to work with multiple dummy accounts to capture a variety of algorithmic recommendations.
-   **Key Metric Extraction:** Retrieves essential metrics like view count, likes count, comments count, and remix count.
-   **CSV Storage:** Raw data is stored in CSV format for easy further analysis.
-   **Encoding Handling:** Addresses character encoding issues (mojibake) to ensure accurate text data.

## Installation

### Prerequisites

Before you begin, ensure you have:
-   Python 3.10 installed.
-   Google Chrome installed.
-   A ChromeDriver compatible with your Google Chrome version. Download it from the [official ChromeDriver website](https://chromedriver.chromium.org/downloads). Make sure `chromedriver.exe` (or the equivalent executable for your OS) is in your system's PATH or in the same directory as your Python script.

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/LhanaAI/youtube-shorts-scraper.git
    cd youtube-shorts-scraper
    ```

2.  **Create and Activate a Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Configure Dummy Accounts:**
    -   Create a `config.py` (or `config.json`) file in the root directory.
    -   Add your dummy account profile path to this file. **IMPORTANT: Do not hardcode credentials directly into the main script.**
    -   Example `config.py`:
        ```python
        # config.py
        DUMMY_ACCOUNTS = [
            {"id": "dummy_1", "profile_path": Your chrome profile path, example: "C:/Users/user/AppData/Local/Google/Chrome/User Data/Profile 1"},
            # Add more accounts as needed
        ]
        RAW_DATA_CSV = 'lhana_shorts_raw_data.csv'
        ```
        
2. **Install Chromedriver**
     - Download chromedriver.exe in https://googlechromelabs.github.io/chrome-for-testing/
     - Extract file
     - Paste chromedriver.exe to your clone repository folder/chromedriver_custom  

3.  **Run the Scraper:**
    ```bash
    python youtube-shorts-scraper.py # Or the name of your main scraping script file
    ```
    The script will launch browsers (in headless mode by default), log into dummy accounts, and begin collecting data.

    **NOTE**
    After browser opened, please log in your YouTube account for better collecting data.

**OPTIONAL**
**Setting Up Your VPN Extension (Urban VPN)**
To effectively use the VPN with your dummy accounts, please follow these installation steps carefully:

1. Initial Setup for One Dummy Account: It's highly recommended to run the script with only one dummy account enabled during this setup phase. Temporarily comment out the other dummy accounts in your configuration (config.py) to avoid launching multiple browsers simultaneously.
2. Navigate to the Chrome Web Store: Once the browser for your single dummy account is open, go to the Chrome Web Store.
3. Search for Urban VPN: In the search bar, type "Urban VPN" and press Enter.
4. Add to Chrome: Locate the "Urban VPN" extension and click "Add to Chrome." Follow any on-screen prompts to confirm the addition.
5. Wait for Installation: Allow the extension to complete its installation process.
6. Open the Urban VPN Extension: After installation, click on the Urban VPN icon in your browser's toolbar to open its popup.
7. Agree to Terms: Once the extension's popup appears, click the "Agree" button to accept its terms.
8. Close the Browser: Close the browser window. The extension's settings and your agreement should now be saved to this dummy account's profile.
9. Enable VPN in Configuration: To activate the VPN for your scraping session, change the ENABLE_VPN value to True in your config.py file.
10. Relaunch the Python Script: Execute your Python script again. The VPN should now be active for this dummy account, and you can then enable other dummy accounts as needed.

## Data Structure (CSV Headers)

The collected data will be saved in a CSV file with the following headers:
'timestamp_scan', 'dummy_account_id', 'video_id', 'caption', 'hashtags_on_caption', 'hashtags_on_description', 'description', 'channel_name', 'raw_views_count', 'likes_count', 'comments_count', 'remix_count', 'upload_date', 'extracted_keywords', 'sound_id', 'sound_name', 'sound_artist', 'sound_usage', 'video_url_full', 'watch_duration_sec'

## Contributing

We welcome contributions from the community! If you'd like to help improve this project, here are some areas where you can contribute:

-   **Scraper Robustness:** Making the scraper more resilient to YouTube UI changes or bot detection.
-   **Additional Data Extraction:** Adding new relevant data extraction (e.g., audience demographics, more accurate video duration).
-   **Improved Error Handling:** Implementing more sophisticated error handling.
-   **Performance Optimization:** Speeding up the scraping process.
-   **Automated Content Classification:** Developing modules for automated `video_category` classification using NLP or basic Computer Vision techniques.
-   **Documentation:** Writing more detailed documentation.

### How to Contribute

1.  **Fork** this repository.
2.  Create a new **branch** (`git checkout -b feature/your-feature-name`).
3.  Make your changes and **commit** them (`git commit -m 'Add feature X'`).
4.  **Push** to your branch (`git push origin feature/your-feature-name`).
5.  Create a **Pull Request** to the main repository.

Please adhere to any existing coding guidelines and ensure your commit messages are clear.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
