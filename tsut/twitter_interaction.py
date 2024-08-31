import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import logging

HEX_TEMPLATE = "(?:[0-9a-f]{{2}}){{{length}}}"

VALID_COOKIES = {
    "auth_token": re.compile(HEX_TEMPLATE.format(length=20)),
    "ct0": re.compile(HEX_TEMPLATE.format(length=80)),
}

COOKIES_PATTERN = re.compile(
    r"\s+({keys})\s+({values})$".format(
        keys="|".join(VALID_COOKIES.keys()), values=HEX_TEMPLATE.format(length="20,80")
    ),
    re.MULTILINE,
)


def load_cookies(path: str) -> dict[str, str]:
    """Load cookies from the specified path in Netscape format."""
    try:
        with open(path, encoding="utf-8") as f:
            return dict(COOKIES_PATTERN.findall(f.read()))
    except OSError as e:
        raise RuntimeError(f"Cannot load cookies from file: {e.filename}") from e


def validate_cookies(cookies: dict[str, str]) -> None:
    """Validate the specified cookies."""
    if missing := VALID_COOKIES.keys() - cookies.keys():
        raise TypeError(f"Missing required cookies: {', '.join(missing)}")
    if extra := cookies.keys() - VALID_COOKIES.keys():
        raise TypeError(f"Extra cookies: {', '.join(extra)}")
    if invalid := {
        key
        for key, value in cookies.items()
        if not VALID_COOKIES[key].fullmatch(str(value))
    }:
        raise ValueError(f"Invalid cookies: {', '.join(invalid)}")


def add_cookies_to_driver(driver, cookies: dict[str, str]) -> None:
    """Adds validated cookies to the WebDriver session."""
    driver.get("https://x.com")
    for key, value in cookies.items():
        driver.add_cookie({"name": key, "value": value})
    driver.refresh()


def interact_with_tweet(link: str, cookie_file_path: str):
    cookies = load_cookies(cookie_file_path)
    validate_cookies(cookies)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    s = Service("c:/chrome/chromedriver.exe")
    driver = webdriver.Chrome(service=s, options=options)

    add_cookies_to_driver(driver, cookies)

    driver.get(link)

    try:
        wait = WebDriverWait(driver, 10)
        play_recording = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'css-146c3p1') and .//span[contains(text(), 'Play recording')]]")))
        play_recording.click()
        wait2 = WebDriverWait(driver, 10)
        share_button = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div[1]/div/div/div[1]/div[1]/div/button[2]")))
        share_button.click()
        copy_link = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/div[3]/div/div/div/div[2]/div/div[3]/div/div/div/div[3]/div[2]/div/span")))
        copy_link.click()

        time.sleep(1)
        copied_link = driver.execute_script("""
        return navigator.clipboard.readText().then(function(text) { return text; });
        """)

        logging.info(f"Copied link: {copied_link}")
        return copied_link

        driver.close()
    except Exception as e:
        logging.error(f"Error interacting with the tweet: {e}")
