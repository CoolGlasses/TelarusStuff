import time
import logging
from locust import task, between, HttpUser, SequentialTaskSet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

logging.basicConfig(filename="POC/locust_new.log",level=logging.INFO)

USER_CREDENTIALS = [("plttest001@telarus.com","password-1"),
                    ("plttest002@telarus.com","password-1"),
                    ("plttest003@telarus.com","password-1"),
                    ("plttest004@telarus.com","password-1"),
                    ("plttest005@telarus.com","password-1"),
                    ("plttest006@telarus.com","password-1"),
                    ("plttest007@telarus.com","password-1"),
                    ("plttest008@telarus.com","password-1"),
                    ("plttest009@telarus.com","password-1"),
                    ("plttest010@telarus.com","password-1"),
                    ("plttest011@telarus.com","password-1"),
                    ("plttest012@telarus.com","password-1"),
                    ("plttest013@telarus.com","password-1"),
                    ("plttest014@telarus.com","password-1"),
                    ("plttest015@telarus.com","password-1"),
                    ("plttest016@telarus.com","password-1"),
                    ("plttest017@telarus.com","password-1"),
                    ("plttest018@telarus.com","password-1"),
                    ("plttest019@telarus.com","password-1"),
                    ("plttest020@telarus.com","password-1")]

class WebsiteTasks(SequentialTaskSet):

    def on_start(self):
        #self.init_sele_driver()
        if USER_CREDENTIALS:
            self.user_name, self.pass_word = USER_CREDENTIALS.pop()
        else:
            self.user_name, self.pass_word = ("default_user", "default_password")
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        #self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.get("https://telarus--fullstagin.sandbox.my.site.com/partner/s/")
        self.driver.maximize_window()
        logging.info(f"The User is: {self.user_name} is up.")
        self.init_sele_driver(self.user_name, self.pass_word)

    def init_sele_driver(self, user__name, pass__word):
        self.driver.get("https://telarus--fullstagin.sandbox.my.site.com/partner/s/")
        WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,"//button[text()='Log in']")))
        username = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your email']")
        password = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your password']")
        lgnbtn = self.driver.find_element(By.XPATH,"//button[text()='Log in']")
        username.send_keys(user__name)
        time.sleep(1)
        password.send_keys(pass__word)
        time.sleep(1)
        lgnbtn.click()
        time.sleep(2)
                
    def measure_component_page_load_time(self, url,page, cmpxpath):
        self.driver.get(url)
        start_time = time.time()
        cmp = WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,""+cmpxpath+"")))
        end_time = time.time()
        load_time = end_time-start_time
        if cmp.is_displayed():
                print(f"Time to load component: {load_time} ,  on {page} Page is visible for {self.user_name}.")
                logging.info(f"Time to load component: {load_time} ,  on {page} Page is visible for {self.user_name}.")

    @task
    def opportunity_page_component_(self):
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/opportunity/Opportunity/Default",page="Opportunity",cmpxpath="//h3[text()='No results']")
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/opportunity/Opportunity/Default",page="Opportunity",cmpxpath="(//a[contains(@href,'/partner/s/opportunity/006')])[1]")
 
    @task
    def order_page_component_(self):
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="//h3[text()='No results']",page="Order")     
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="(//a[contains(@href,'/partner/s/order/801')])[1]",page="Order")  

    @task
    def customer_page_component_(self):
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/customer-accounts",cmpxpath="//h3[text()='No results']",page="Order")     
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/customer-accounts",cmpxpath="(//a[contains(@href,'/partner/s/account/001')])[1]",page="Customer")  

    @task
    def quote_page_component_(self):
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/quote/Quote/Default",cmpxpath="//h3[text()='No results']",page="Quotes")     
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/quote/Quote/Default",cmpxpath="(//a[contains(@href,'/partner/s/quote/0Q0')])[1]",page="Quotes")  

    @task
    def case_page_component_(self):
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/case/Case/Recent",cmpxpath="//h3[text()='No results']",page="Cases")     
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/case/Case/Recent",cmpxpath="(//a[contains(@href,'/partner/s/case/500')])[1]",page="Cases")  


    def on_stop(self):
            """Close session and clean up"""
            print("Test completed, cleanup.")
            self.driver.close()                                                                                              
            self.driver.quit()                     

class WebsiteUser(HttpUser):
    #user waits for below time to start next task
    host = "https://telarus--fullstagin.sandbox.my.site.com/partner/s/"
    wait_time = between(1,5)
    tasks =[WebsiteTasks]