from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import yt_dlp
import time

options = webdriver.FirefoxOptions()
# options.add_argument("-headless")
options.page_load_strategy = "none"
options.set_preference("permissions.default.image", 2)
options.set_preference("media.volume_scale", "0.0")
# options.set_preference("javascript.enabled", False)
# options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

driver = webdriver.Firefox(options=options)


###
##subclass olarak olusturulacak
def wait_element(by, element, default_wait_delay=10):
    attempt = 0
    try:
        while attempt < 3:
            WebDriverWait(driver, default_wait_delay).until(
                EC.presence_of_element_located((by, element))
            )
            break
    except (
        selenium.common.exceptions.StaleElementReferenceException,
        selenium.common.exceptions.ElementNotInteractableException,
        selenium.common.exceptions.NoSuchElementException,
    ):
        attempt = +1
        print(attempt)
        pass


def wait_element_clickable(by, element, default_wait_delay=10):
    attempt = 0
    try:
        while attempt < 3:
            WebDriverWait(driver, default_wait_delay).until(
                EC.element_to_be_clickable((by, element))
            )
            break
    except (
        selenium.common.exceptions.StaleElementReferenceException,
        selenium.common.exceptions.ElementNotInteractableException,
        selenium.common.exceptions.NoSuchElementException,
    ):
        attempt = +1
        print(attempt)
        pass


###

# CLi'de search fonk
search = "Mushoku Tensei: Isekai Ittara Honki Dasu"


driver.get("https://diziwatch.net/")

wait_element(By.CSS_SELECTOR, "#searchInput")
search_input = driver.find_element(By.CSS_SELECTOR, "#searchInput")
search_input.clear()
search_input.send_keys(search + Keys.ENTER)


try:
    wait_element(By.XPATH, rf"//div[@id='search-name' and text()='{search}']", 1)
    wait_element_clickable(
        By.XPATH, rf"//div[@id='search-name' and text()='{search}']", 1
    )
except (
    selenium.common.exceptions.TimeoutException,
    selenium.common.exceptions.NoSuchElementException,
):
    search_input.send_keys(Keys.ENTER)

wait_element(By.XPATH, rf"//div[@id='search-name' and text()='{search}']")
target_series = driver.find_element(
    By.XPATH, rf"//div[@id='search-name' and text()='{search}']"
)
target_series.click()

season_list  = {}

wait_element(By.ID, "myBtnContainer")
season_check = driver.find_element(By.ID, "myBtnContainer")
buttons = season_check.find_elements(By.TAG_NAME, "button")
print(season_check)
for button in buttons:
    season = button.get_attribute("search-text").strip()
    season_list.update({season : button})
print(season_list)
print(season_list["2. Sezon"])
kururin = input("S: ")
season_list[kururin].click()

wait_element(
    By.XPATH, "//div[contains(@class, 'bolumust') and contains(@class, 'show')]"
)
target_series_episodes = driver.find_elements(
    By.XPATH, "//div[contains(@class, 'bolumust') and contains(@class, 'show')]"
)

target_series_episode_links = []

for episode in target_series_episodes:
    href_element = episode.find_element(By.XPATH, ".//a[@href]")
    href = href_element.get_attribute("href")
    target_series_episode_links.append(href)


anime_name = driver.find_element(By.XPATH, "//h1[@class='title-border']").text


current_resolution = None

for site in target_series_episode_links:
    driver.get(site)
    time.sleep(0.2)

    wait_element(By.CSS_SELECTOR, "h1.title-border")

    file_name = driver.find_element(By.CSS_SELECTOR, "h1.title-border").text
    print(file_name)

    wait_element_clickable(By.CSS_SELECTOR, "#player")
    jwp = driver.find_element(By.CSS_SELECTOR, "#player")
    jwp.click()

    wait_element_clickable(By.CSS_SELECTOR, "div.jw-icon:nth-child(15)")
    setting_button = driver.find_element(By.CSS_SELECTOR, "div.jw-icon:nth-child(15)")
    setting_button.click()

    wait_element_clickable(
        By.CSS_SELECTOR, "#jw-player-settings-submenu-quality > div:nth-child(1)"
    )
    video_quality_info_element = driver.find_element(
        By.CSS_SELECTOR, "#jw-player-settings-submenu-quality > div:nth-child(1)"
    )
    ###

    wait_element(
        By.XPATH,
        "//div[@id='jw-player-settings-submenu-quality']/div/button[contains(@class, 'jw-reset-text') and contains(@class, 'jw-settings-content-item') and contains(@class, 'jw-settings-item-active')]",
    )
    active_res = driver.find_element(
        By.XPATH,
        "//div[@id='jw-player-settings-submenu-quality']/div/button[contains(@class, 'jw-reset-text') and contains(@class, 'jw-settings-content-item') and contains(@class, 'jw-settings-item-active')]",
    ).get_attribute("aria-label")
    print(active_res)

    if current_resolution:
        if current_resolution == active_res:
            print("aciveres==currentres")
            continue
        else:
            print("else-1")
            child_resolutions_elements = video_quality_info_element.find_elements(
                By.XPATH, "*"
            )
            resolutions = {}
            for child_resolutions_element in child_resolutions_elements:
                resolution = child_resolutions_element.get_attribute("aria-label")
                resolutions.update({resolution: child_resolutions_element})
            keys = resolutions.keys()
            print(list(keys))
            select_res = input("resolution: ")
            res = resolutions[f"{select_res}"]
            res.click()
            current_resolution = select_res
    else:
        print("else2")
        child_resolutions_elements = video_quality_info_element.find_elements(
            By.XPATH, "*"
        )
        resolutions = {}
        for child_resolutions_element in child_resolutions_elements:
            resolution = child_resolutions_element.get_attribute("aria-label")
            resolutions.update({resolution: child_resolutions_element})
        keys = resolutions.keys()
        print(list(keys))
        select_res = input("resolution: ")
        res = resolutions[f"{select_res}"]
        res.click()
        current_resolution = select_res
