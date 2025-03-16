from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
import re

FILE_DIR = Path(__file__).parent

# Configure Selenium WebDriver
firefox_options = Options()
# Replace with the correct path to Firefox binary
firefox_options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"  
# firefox_options.add_argument("--headless")  # Run in headless mode (no UI)
# firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--window-size=1920x1080")

service = Service(
    # Replace with your GeckoDriver path
    "driver/geckodriver-v0.35.0-win32/geckodriver.exe"
)
driver = webdriver.Firefox(service=service, options=firefox_options)


def sanitize_filename(filename):
    """Remove invalid characters from the filename."""
    return re.sub(r'[\\/*?"<>|]\'', "_", filename)


def log_download_error(url):
    with open(FILE_DIR.joinpath("download-error.log"), "+a") as f:
        f.write(f"{url}\n")


def remove_path(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def download_file(url: str, save_path: Path):
    try:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the file using urllib
        urllib.request.urlretrieve(url, save_path)

        print(f"File downloaded: {save_path}")
    except Exception as e:
        log_download_error(save_path)
        print(f"Error downloading file: {e}")


def download_track(url):
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        artist = sanitize_filename(
            soup.find("p", id="band-name-location")
            .find(class_="title")
            .text.strip()
            .strip("\n")
        )
        # print(artist.strip())
        album = sanitize_filename(
            soup.find("span", class_="fromAlbum").text.strip().strip("\n")
        )
        if album == "":
            album = "_"
        # print(album.strip())
        title = sanitize_filename(
            soup.find("h2", class_="trackTitle").text.strip().strip("\n")
        )
        # print(title)

        # Toggle play button on and off.
        driver.find_element(By.CLASS_NAME, "playbutton").click()
        time.sleep(3)
        driver.find_element(By.CLASS_NAME, "playbutton").click()

        audio = driver.find_element(By.TAG_NAME, "audio")
        audio_src = audio.get_attribute("src")
        # print(audio_src)

        download_file(
            audio_src,
            Path(FILE_DIR)
            .joinpath("music")
            .joinpath(artist)
            .joinpath(album)
            .joinpath(title + ".mp3"),
        )
    except Exception as e:
        log_download_error(url)
        print(f"Error occurred: {e}")


def download_album(url):
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        tracks = [
            remove_path(url) + x.find("a").get("href")
            for x in soup.find("table", id="track_table").find_all(class_="title")
        ]
        # print(tracks)
        for track_url in tracks:
            download_track(track_url)
    except Exception as e:
        log_download_error(url)
        print(f"Error occurred: {e}")


def download_artist(url):
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        albums = [
            remove_path(url) + x.get("href")
            for x in soup.find("ol", id="music-grid").find_all("a")
        ]
        # print(albums)
        for album_url in albums:
            download_album(album_url)
    except Exception as e:
        log_download_error(url)
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    driver.get("https://bandcamp.com")
    input("Press enter once after preparing browser. E.g. By-pass privacy page blocker")
    # download_track("https://father2006.bandcamp.com/track/reflection")
    download_album("https://father2006.bandcamp.com/album/reflection")
    # download_artist("https://father2006.bandcamp.com/")
