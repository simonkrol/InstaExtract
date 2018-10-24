import time
import environ
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# The account you want to check
account = environ.toCheck

# Chrome executable
chrome_binary = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # Add your path here


def login(driver):
    username = environ.username   # Your username
    password = environ.password   # Your password

    # Load page
    driver.get("https://www.instagram.com/accounts/login/")

    # Login
    driver.find_element_by_xpath("//div/input[@name='username']").send_keys(username)
    driver.find_element_by_xpath("//div/input[@name='password']").send_keys(password)
    driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/article/div/div[1]/div/form/div[3]/button").click()

    # Wait for the login page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "See All")))


def scrape_followers(driver, account):
    # Load account page
    driver.get("https://www.instagram.com/{0}/".format(account))

    # Click the 'Follower(s)' link
    driver.find_element_by_partial_link_text("follower").click()

    # Wait for the followers modal to load
    xpath = "/html/body/div[3]/div/div/div[2]/ul/div"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = .4  # Pause to allow loading of content
    oldFollowers = 0
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element_by_xpath("/html/body/div[3]/div/div/div[2]"))
    actions.click()
    # We need to scroll the followers modal to ensure that all followers are loaded
    while True:
        try:
            actions.send_keys(Keys.SPACE).perform()
            time.sleep(0.15)
            actions.send_keys(Keys.SPACE).perform()
        except:
            pass
        
        newFollowers=len(driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[2]/ul/div/li"))

        # Wait for page to load
        time.sleep(SCROLL_PAUSE)
        # Calculate new scrollHeight and compare with the previous
        if newFollowers == oldFollowers:
            break
        oldFollowers = newFollowers

    # Finally, scrape the followers
    xpath = "/html/body/div[3]/div/div/div[2]/ul/div/li"

    followers_elems = driver.find_elements_by_xpath(xpath)

    followers_temp = [e.text for e in followers_elems]  # List of followers (username, full name, follow text)
    followers = []  # List of followers (usernames only)

    # Go through each entry in the list, append the username to the followers list
    for i in followers_temp:
        username, sep, name = i.partition('\n')
        followers.append(username)

    return followers

def scrape_following(driver, account):
    # Load account page
    driver.get("https://www.instagram.com/{0}/".format(account))

    # Click the 'Following' link
    driver.find_element_by_partial_link_text("following").click()

    # Wait for the following modal to load
    xpath = "/html/body/div[3]/div/div/div[2]/ul[1]/div"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath)))

    SCROLL_PAUSE = .4  # Pause to allow loading of content
    oldFollowing = 0
    # We need to scroll the following modal to ensure that all following are loaded
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element_by_xpath("/html/body/div[3]/div/div/div[2]"))
    actions.click()
    while True:
        try:
            actions.send_keys(Keys.SPACE).perform()
            time.sleep(0.15)
            actions.send_keys(Keys.SPACE).perform()
        except:
            pass
        newFollowing=len(driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[2]/ul/div/li"))
        time.sleep(SCROLL_PAUSE)

        # Calculate new scrollHeight and compare with the previous
        if newFollowing == oldFollowing:
            break
        oldFollowing = newFollowing

    # Finally, scrape the following
    xpath = "/html/body/div[3]/div/div/div[2]/ul/div/li"
    following_elems = driver.find_elements_by_xpath(xpath)

    following_temp = [e.text for e in following_elems]  # List of following (username, full name, follow text)
    following = []  # List of following (usernames only)

    # Go through each entry in the list, append the username to the following list
    for i in following_temp:
        username, sep, name = i.partition('\n')
        following.append(username)
    return following


if __name__ == "__main__":
    options = wd.ChromeOptions()
    options.binary_location = chrome_binary # chrome.exe
    driver_binary = r"/Users/simonkrol/Desktop/PathSoftware/chromedriver"

    driver = wd.Chrome(driver_binary, chrome_options=options)
    try:
        login(driver)
        followers = scrape_followers(driver, account)
        print(followers)
        following = scrape_following(driver, account)
        print(following)
        input()
        print((set(following)-set(followers)))
    finally:
        driver.quit()