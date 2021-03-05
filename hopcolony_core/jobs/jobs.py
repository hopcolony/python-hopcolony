import logging, requests, re
from itertools import cycle
from urllib.parse import urlparse
from parsel import Selector
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxProfile, DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium import common
from webdriver_manager.firefox import GeckoDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

class Job:
    entrypoint = None
    selenium = False
    def __init__(self, *args, **kwargs):
        # Set the input args as attributes to the job
        self.__dict__.update(kwargs)

        printger = logging.getLogger(self.name)
        logging.basicConfig(level=logging.INFO, format='%(message)s')

class Engine:
    last_get = None
    proxies = cycle(["3.239.28.97:8080", "3.238.35.140:8080", "174.129.147.226:8080"])
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}

    def __init__(self, job, pipelines):
        self.job = job
        self.pipelines = pipelines
        assert job.entrypoint, "Please provide an entrypoint"

    def do_captcha(self, driver):
        try:
            wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath("/html/body/iframe")))
            wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath("//*[@id='captcha-submit']/div/div/iframe")))

            captcha = driver.find_element_by_xpath("//*[@id='recaptcha-anchor']")
            ActionChains(driver).move_to_element(captcha).click().perform()
        except common.exceptions.NoSuchElementException as e:
            print(e)
            pass
        return False
    
    def get(self, url, callback = None):
        if isinstance(url, str):
            assert self.last_get != url, f"You're trying to follow an url you have just visited: {url}"
            self.last_get = url

        parse_callback = self.job.parse
        if callback:
            parse_callback = callback

        try:
            if not self.job.selenium:
                data = requests.get(url, headers = self.headers, proxies = {"http": self.proxy})
                response = RESTJobResponse(self, data)
            else:
                if isinstance(url, str):
                    self.browser.get(url)
                else:
                    ActionChains(self.browser).click(url).perform()
                response = SeleniumJobResponse(self)
                # Check captcha
                if self.do_captcha(self.browser):
                    return
        except requests.exceptions.ConnectionError:
            self.job.logger.error(f"Could not get a connection with \"{url}\"")
            return
        except common.exceptions.WebDriverException as e:
            print(e)
            self.browser.close()
            return

        # Rotate proxy
        self.proxy = next(self.proxies)

        try:
            for item in parse_callback(response):
                # Send to pipelines
                for pipeline in self.pipelines:
                    item = pipeline.process_item(item, self.job)
        except TypeError as e:
            # Probably returning nothing from parse method
            pass
    
    headless = False
    options = None
    profile = None
    capabilities = None

    def setUpProfile(self):
        self.profile = FirefoxProfile()
        self.profile._install_extension("buster_captcha_solver_for_humans-1.1.0-an+fx.xpi", unpack=False)
        self.profile.set_preference("security.fileuri.strict_origin_policy", False)
        self.profile.update_preferences()

    def setUpOptions(self):
        self.options = FirefoxOptions()
        # self.options.headless = self.headless
    
    def setUpCapabilities(self):
        self.capabilities = DesiredCapabilities.FIREFOX
        self.capabilities['marionette'] = True
    
    def setUpProxy(self):
        self.proxy = next(self.proxies)
        self.capabilities['proxy'] = { "proxyType": "MANUAL", "httpProxy": self.proxy, "ftpProxy": self.proxy, "sslProxy": self.proxy }
        
    def start(self):
        if self.job.selenium:
            self.setUpProfile()
            self.setUpOptions()
            self.setUpCapabilities()
            # self.setUpProxy()

            self.browser = Firefox(options=self.options, capabilities=self.capabilities, 
                    firefox_profile=self.profile, executable_path=GeckoDriverManager().install())

        self.get(self.job.entrypoint)

class RESTJobResponse:
    def __init__(self, engine, response):
        self.engine = engine
        self.url = response.url
        self.response = response
        parsed_uri = urlparse(self.url)
        self.base = f"{parsed_uri.scheme}://{parsed_uri.netloc}/"
        self.status = response.status_code
        self.raw = response.text
        self.selector = Selector(text=self.raw)
        
    def css(self, query):
        return self.selector.css(query)

    def xpath(self, query):
        return self.selector.xpath(query)
        
    def follow(self, endpoint, callback):
        url = self.base + endpoint
        if re.match(r"http.*", endpoint):
            url = endpoint
        self.engine.get(url, callback)

class SeleniumJobResponse:
    def __init__(self, engine):
        self.engine = engine
        self.url = engine.browser.current_url
        parsed_uri = urlparse(self.url)
        self.base = f"{parsed_uri.scheme}://{parsed_uri.netloc}/"
        self.raw = engine.browser.page_source

    def xpath(self, query):
        return self.engine.browser.find_elements_by_xpath(query)

    def click(self, element, callback = None):
        self.engine.get(element, callback)

    def follow(self, endpoint, callback = None):
        url = self.base + endpoint
        if re.match(r"http.*", endpoint):
            url = endpoint
        self.engine.get(url, callback)
    
    def close(self):
        self.engine.browser.close()