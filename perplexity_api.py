import os
import time
import re
import urllib

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc
import markdownify
from bs4 import BeautifulSoup

FOCUS = {"internet": 1, "academic":2, "writing":3, "wolfram":4, "youtube":5, "reddit":6, "wikipedia":7}

def debug(*args):
    if "DEBUG" in os.environ:
        print(*args)

def slow_type(element, text: str, delay: float=0.1):
    """Send a text to an element one character at a time with a delay."""
    for character in text:
        element.send_keys(character)
        time.sleep(delay)

class PerplexityAPI:
    def __init__(
        self,
        headless=True,
        user_agent=None,
        stealth=True,
        incognito=False,
        user_data_dir=None,
        proxy=None,
        timeout=15.0,
        response_timeout=60.0
    ):
        """PerplexityAPI
        Args:
            headless (bool): whether to run in headless mode or not
            user_agent (Optional, str): user agent to use
            stealth (bool): disable blink features
            incognito (bool): run in incognito
            user_data_dir (Optional, str): path to chrome user data
            proxy (Optional, str): proxy to use, in format of {ip_address}:{port}
            timeout (float): time to wait for a response
            response_timeout (float): time to wait for response to generate
        """
        options = Options()
        if headless:
            options.add_argument("--headless")
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        if stealth:
            options.add_argument('--disable-blink-features')
            options.add_argument('--disable-blink-features=AutomationControlled')
        if incognito:
            options.add_argument('--incognito')
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')

        # set-up proxy
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        self.driver = uc.Chrome(options=options)
        self.timeout = timeout
        self.response_timeout = response_timeout
        #print("User-Agent:", self.driver.execute_script("return navigator.userAgent"))

    def query(self, prompt, follow_up=False, focus="internet"):
        """Send a query to Perplexity AI
        Args:
            prompt (str): the prompt to send
            follow_up (bool): whether it's a follow-up or not
            focus (str): which focus to use, note only "internet" works logged out, logged in can use "academic", "writing", "wolfram", "youtube", "reddit", "wikipedia", see user_data_dir of PerplexityAPI
        """
        if focus not in FOCUS:
            raise ValueError("unknown focus,", focus)
        if not follow_up: # self.driver.current_url == "data:,"
            #self.driver.delete_all_cookies()
            self.driver.get(f"https://www.perplexity.ai")
            time.sleep(0.2)
            WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))).click()
            
            if focus != "internet":
                for i in range(2):
                    # click Focus
                    WebDriverWait(self.driver, self.timeout).until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "button")) >= 3)
                    self.driver.find_elements(By.CSS_SELECTOR, "button")[2].click()
                    # XXX login screen
                    if len(self.driver.find_elements(By.CSS_SELECTOR, ".top-sm button")):
                        time.sleep(0.25)
                        self.driver.find_elements(By.CSS_SELECTOR, ".top-sm button")[0].click()
                        time.sleep(0.25)
                        continue
                    time.sleep(0.25)
                    # click focus setting
                    WebDriverWait(self.driver, self.timeout).until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".cursor-pointer")) >= FOCUS[focus]+1)
                    self.driver.find_elements(By.CSS_SELECTOR, ".cursor-pointer")[FOCUS[focus]].click()
                    # XXX login screen
                    if len(self.driver.find_elements(By.CSS_SELECTOR, ".top-sm button")):
                        time.sleep(0.25)
                        self.driver.find_elements(By.CSS_SELECTOR, ".top-sm button")[0].click()
                        time.sleep(0.25)
                        continue
                    break

        count = len(self.driver.find_elements(By.CSS_SELECTOR, ".prose")) + 1
        WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea")))
        textarea = self.driver.find_elements(By.CSS_SELECTOR, "textarea")[0]

        for line in prompt.split('\n'): # type the message with new lines using shift+enter
            actions = ActionChains(self.driver)
            actions.send_keys(line.replace("\t", ""))
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
            actions.perform()

        textarea.send_keys(Keys.ENTER)
        #time.sleep(0.4)
        #WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text-white"))).click()
        #textarea = self.driver.find_elements(By.CSS_SELECTOR, "textarea")[0]

        try:
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".prose")) == count)
        except TimeoutException:
            success = False
            #self.driver.delete_all_cookies() #XXX
            for i in range(3):
                if "/search" not in self.driver.current_url:
                    raise TimeoutException("Query timeout")
                    return "[Error]"
                self.driver.refresh()
                time.sleep(1)
                try:
                    WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
                    wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".prose")) == count)
                    success = True
                    break
                except TimeoutException:
                    continue
            if not success:
                raise TimeoutException("Query timeout")
                return "[Error]"

        try:
            wait = WebDriverWait(self.driver, self.response_timeout)
            wait.until(
                (lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".mb-md .-ml-sm")) == count and
                EC.visibility_of(driver.find_elements(By.CSS_SELECTOR, ".mb-md .-ml-sm")[count-1]))
            )
            time.sleep(0.25)
            element = self.driver.find_elements(By.CSS_SELECTOR, ".pb-md")[-1]
            #query = element.find_elements(By.CSS_SELECTOR, ".text-xl")[0].get_attribute("innerText") # nn
            WebDriverWait(self.driver, self.timeout).until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".prose")) == count)
        except TimeoutException:
            raise TimeoutException("Response timeout")
            return "[Error]"

        text = self.driver.find_elements(By.CSS_SELECTOR, ".prose")[-1]
        html = text.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        for el in soup.select("span.text-\\[0\\.60rem\\]") + soup.select("a"):
            el.decompose()

        for el in soup.select(".text-textMainDark"):
            el.replace_with(el.text + "\n")

        for el in soup.select(".codeWrapper"):
            el.name = "tt"
            #el.insert_before(soup.new_tag("br"))
            el.replace_with(el.text)

        debug("==DEBUG==\n", soup.decode())
        response = markdownify.markdownify(soup.decode(), strip=["a", "img", "code", "span"]).strip()

        # clean up pre code blocks
        response = re.sub(r"```\n(?=[^\n])", "```", response)
        response = re.sub(r"(?<=[^:])\n\n```", "\n```", response)
        response = response.replace("\n\n\n```\n", "```")
        response = response.replace("\n\n```", "\n```")
        response = response.replace("\n\n```", "\n```")
        response = response.replace("```\n\n", "```\n")

        debug("==RESPONSE==\n", response)

        # clean up line breaks
        response = re.sub("\n\n\n+", "\n\n", response)

        return response

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    ppl = PerplexityAPI()
    queries = [
        "lifu huang, a researcher on computer science, tell me his home page",
        "and in c++",
    ]
    for i, query in enumerate(queries):
        if i > 0:
            print("***")
        print(query)
        print("***")
        result = ppl.query(query, follow_up=True)
        print(result)
    ppl.quit()