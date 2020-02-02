from urllib2 import URLError

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import Proxy, ProxyType

from scrapy.selector import Selector
from scrapy.http import Request

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from xvfbwrapper import Xvfb

from PIL import Image
from functools import wraps

import os.path
import time
import socket
import errno
import sys
from traceback import format_exc

from Queue import Empty

def uses_selenium(func):
    """
    Decorator used in callbacks that will use Selenium. This allows
    to reduce the count after the callback has finished and keep the limit
    in place.
    """
    @wraps(func)
    def inner(spider, response, *args, **kwargs):
        if '_been_in_decorator' in response.meta:
            for item in func(spider, response, *args, **kwargs):
                yield item
        else:
            response.meta['_been_in_decorator'] = True
            try:
                for item in func(spider, response, *args, **kwargs):
                    yield item
            except Exception as e:
                spider._logger.critical("Uncaught Exception %s.\n%s" %
                    (str(e), format_exc()))
                raise e
            finally:
                spider.active_sel_requests-=1
                if spider.active_sel_requests<spider.max_sel_requests:
                    try:
                        request = spider.request_queue.get_nowait()
                        yield request
                    except Empty:
                        pass
    return inner


def get_award_image_screenshot(spider, response, xpath, source_id, file_identifier):
    '''
    screenshot an award image at the xpath specified if it is not available at local file system
    :param spider: the spider that requested the award image
    :param response: Scrapy response object (https://doc.scrapy.org/en/latest/topics/request-response.html)
    :param xpath: the xpath of the award image
    :param source_id: the ID of review source
    :param file_identifier: the identifler of award image file
    :return: the hosted image file address in URL format
    '''
    file_name = "%d_%s.png" % (source_id, file_identifier)
    file_path = '/var/www/html/' + file_name

    if os.path.isfile(file_path):
        return SeleniumBrowser.get_hosted_file_address(file_name)
    else:
        with SeleniumBrowser(spider, response, no_images=False, no_css=False) as browser:
            browser.get(response.url)
            # Save the image of the award from the page and return us the hosted address of the image
            return browser.screenshot_element(xpath, source_id, file_identifier)


class SeleniumBrowser(object):

    WIDTH = 2048
    HEIGHT = 6000

    def __init__(self, spider, original_response,
                 no_images=False,
                 no_css=False):
        self.spider = spider
        self.original_response = original_response
        self.no_images=no_images
        self.no_css=no_css

    def __enter__(self):
        project_conf = self.spider.project_conf
        self.graphic_browser = project_conf.getboolean("RUN", "graphic_browser")
        self.max_wait = 5
        self.wait_timeout = 10
        self.scrolled = 0
        self.browser = None
        self.exited = False
        self.spider.active_browsers+=1

        try:
            if not self.graphic_browser:
                self.vdisplay = Xvfb(width=self.WIDTH, height=self.HEIGHT) #huge screen to take screenshots properly
                self.vdisplay.start()

            self.browser = self._chrome_driver()
            #self.browser = self._firefox_driver()
        except OSError, e:
            if e.errno==errno.ENOMEM:
                new_request = self.original_response.request.replace(
                    dont_filter=True)
                self.spider.request_queue.put(new_request)
            raise e
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()

    def quit(self):
        if not self.exited:
            del self.original_response
            if self.browser:
                self.browser.quit()
            if not self.graphic_browser:
                self.vdisplay.stop()
            self.exited=True
            self.spider.active_browsers-=1

    def __del__(self):
        self.quit()
        
    def _chrome_driver(self):
        selenium_useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/46.0.2490 Chrome/46.0.2490 Safari/537.36'
            
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--user-agent={}".format(selenium_useragent))
        chrome_options.add_argument("--proxy-server={}".format(self.spider.default_proxy))
        chrome_options.add_argument("--proxy-bypass-list={}".format(self.spider.no_proxy))
        
        if self.no_images:
            prefs = {"profile.managed_default_content_settings.images":2}
            chrome_options.add_experimental_option("prefs", prefs)
            
        # Currently there is no way to disable CSS on ChromeDriver    
        #if self.no_css:
        #    pass
            
        capabilities = chrome_options.to_capabilities()
        capabilities['nativeEvents'] = True
        capabilities['overlappingCheckDisabled'] = True
    
        browser = webdriver.Chrome(desired_capabilities=capabilities)
        browser.set_window_size(self.WIDTH, self.HEIGHT)
        return browser
    
    # Not used
    def _firefox_driver(self):
        selenium_useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        
        # TODO: this way of setting proxy does not work in Firefox with version >= 48,
        # find an alternative way if need to use Firefox in the future
        proxy = Proxy({
            'autodetect': False,
            'proxyType': ProxyType.MANUAL,
            'httpProxy': self.spider.http_proxy[0],
            'sslProxy': self.spider.https_proxy[0],
            'noProxy': self.spider.no_proxy})

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", selenium_useragent)
        profile.set_preference("privacy.trackingprotection.enabled", True)
        
        if self.no_css:
            profile.set_preference("permissions.default.stylesheet", 2)
            
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities['nativeEvents'] = True
        capabilities['overlappingCheckDisabled'] = True
        
        browser = webdriver.Firefox(profile, proxy=proxy)
        #browser.maximize_window()
        browser.set_window_size(self.WIDTH, self.HEIGHT)
        
        if self.no_images:
            self.firefox_disable_images()
        
        return browser

    def firefox_disable_images(self):
        ac = ActionChains(self.browser)
        # SHIFT+F2 opens dev toolbar
        ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
        # command to disable images
        ac.send_keys('pref set permissions.default.image 2').perform()
        ac.send_keys(Keys.ENTER).perform()
        # disable dev toolbar
        ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
        ac.perform()

    def _get_elements(self, xpath):
        try:
            return self.browser.find_elements_by_xpath(xpath)
        except NoSuchElementException, e:
            return None

    def _get_element(self, xpath, parent_element=None):
        try:
            if parent_element:
                return parent_element.find_element_by_xpath(xpath)
            else:
                return self.browser.find_element_by_xpath(xpath)
        except NoSuchElementException, e:
            raise e
            return None

    def _wait(self, ec_condition, timeout):
        if not timeout:
            timeout = self.max_wait

        if ec_condition:
            wait = WebDriverWait(self.browser, self.wait_timeout)
            wait.until(ec_condition)
        else:
            time.sleep(1)
            for i in range(1, timeout, 1):
                current_page_source = self.browser.page_source
                time.sleep(1)
                new_page_source = self.browser.page_source
                if current_page_source!=new_page_source:
                    break

    def get(self, url, ec_condition=None, timeout=None):
        previous_page_source = self.browser.page_source
        for i in range(3):
            try:
                self.browser.get(url)
            except URLError as serr:
                raise serr

            self.scrolled = 0
            self._wait(ec_condition, timeout)

            page_source = self.browser.page_source
            if page_source!=previous_page_source:
                break
            raise Exception("Page source is the same after three retries")

        return Selector(text=page_source)

    def is_displayed(self, xpath, parent_element=None):
        try:
            element = self._get_element(xpath, parent_element)
        except NoSuchElementException,e:
            return False

        if element:
            if element.is_displayed():
                return True
        return False

    def write_in_field(self, xpath, text_to_write):
        element = self._get_element(xpath)
        if element:
            element.send_keys(text_to_write)

    def hover(self, xpath, ec_condition=None, timeout=None):
        element = self._get_element(xpath)
        hov = ActionChains(self.browser).move_to_element(element)
        hov.perform()
        self._wait(ec_condition, timeout)

    def click_element(self, element, ec_condition=None, timeout=None):
        self.browser.execute_script("return arguments[0].scrollIntoView(false);",
                                    element)

        # In some cases, we want to click on element that is 0px width or 0px height due to CSS deactivated or images deactivated
        # This Fix uses JS to insert text inside an element (=> gives it visible size)
        #self.browser.execute_script("var e = $(arguments[0]); if(e.width()
        # == 0 || e.height() == 0){ $(e).append('#'); }",element)
        #wait = WebDriverWait(self.browser, self.wait_timeout)
        #wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if element:
            element.click()
            self._wait(ec_condition, timeout)
            return Selector(text=self.browser.page_source)
        return None

    def click(self, xpath, ec_condition=None, timeout=None):
        element = self._get_element(xpath)
        return self.click_element(element, ec_condition, timeout)

    def click_link(self, xpath, ec_condition=None, timeout=None):
        previous_page_source = self.browser.page_source
        for i in range(3):
            selector = self.click(xpath, ec_condition=ec_condition,
                                  timeout=timeout)
            new_page_source = self.browser.page_source
            if new_page_source!=previous_page_source:
                return selector
            raise Exception("Page source is the same after three retries")

    def _get_element_html(self, element):
        content = self.browser.execute_script("return arguments[0].innerHTML;", element)
        return content

    def switch_to_frame(self, xpath):
        element = self._get_element(xpath)
        self.browser.switch_to.frame(element)
        frame_html = self._get_element("//html")
        frame_source = self._get_element_html(frame_html)
        return Selector(text=frame_source)

    def select(self, select_xpath, value, ec_condition=None, timeout=None):
        element = self._get_element(select_xpath)
        self.browser.execute_script("return arguments[0].scrollIntoView(false);",
                                    element)
        if element:
            select = Select(element)
            select.select_by_visible_text(value)
            self._wait(ec_condition, timeout)
            return Selector(text=self.browser.page_source)
        return None

    def select_by_value(self, select_xpath, value, ec_condition=None,
                     timeout=None):
        element = self._get_element(select_xpath)
        self.browser.execute_script("return arguments[0].scrollIntoView(false);",
                                    element)
        if element:
            select = Select(element)
            select.select_by_value(value)
            self._wait(ec_condition, timeout)
            return Selector(text=self.browser.page_source)
        return None

    def click_list(self, xpath, click_list, ec_condition=None, timeout=None):
        try:
            elements = self.browser.find_elements_by_xpath(xpath)
        except NoSuchElementException, e:
            return  

        if len(elements) == len(click_list):
            for i in range(len(elements)):
                if click_list[i]:
                    elements[i].click()

            self._wait(ec_condition, timeout)
            return Selector(text=self.browser.page_source)

    def scroll(self, scroll_length, scroll_down=True, ec_condition=None, timeout=None):
        if scroll_down:
            self.scrolled = self.scrolled + scroll_length
        else:
            self.scrolled = self.scrolled - scroll_length
        self.browser.execute_script("scroll(0, %d);" % self.scrolled)

        if ec_condition:
            wait = WebDriverWait(self.browser, self.wait_timeout)
            wait.until(ec_condition)
        else:
            time.sleep(self.max_wait)

        return Selector(text=self.browser.page_source)

    def scroll_until_the_end(self, scroll_step, ec_condition=None):
        top_script = "return window.pageYOffset || document.documentElement.scrollTop"
        scroll_top = int(self.browser.execute_script(top_script))

        self.scrolled = 0
        while True:
            self.scrolled = self.scrolled + scroll_step
            self.browser.execute_script("scroll(0, %d);" % self.scrolled)

            if ec_condition:
                wait = WebDriverWait(self.browser, self.wait_timeout)
                wait.until(ec_condition)
            else:
                time.sleep(self.max_wait)

            new_scroll_top = int(self.browser.execute_script(top_script))
            if scroll_top == new_scroll_top:
                return Selector(text=self.browser.page_source)
            else:
                scroll_top = new_scroll_top

    def screenshot_element(self, xpath, source_id, file_identifier):
        file_name = "%d_%s.png" % (source_id, file_identifier)
        file_path = '/var/www/html/' + file_name

        if os.path.isfile(file_path):
            return self.get_hosted_file_address(file_name)

        # now that we have the preliminary stuff out of the way time to get that image :D
        element = self.browser.find_element_by_xpath(xpath) # find part of the page you want image of
        location = element.location
        size = element.size
        self.browser.save_screenshot('/tmp/screenshot.png') # saves screenshot of entire page

        im = Image.open('/tmp/screenshot.png') # uses PIL library to open image in memory

        left = int(location['x'])
        top = int(location['y'])
        right = int(location['x']) + int(size['width'])
        bottom = int(location['y']) + int(size['height'])

        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('/var/www/html/' + file_name) # saves new cropped image
        return self.get_hosted_file_address(file_name)

    @staticmethod
    def get_hosted_file_address(file_name):
        domain_name = socket.getfqdn()
        file_location = "http://" + domain_name + "/" + file_name
        return file_location
