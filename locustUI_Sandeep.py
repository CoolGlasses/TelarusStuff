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
import ast

def read_credentials(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        for line in file:
            credential_tuple = ast.literal_eval(line.strip())
            credentials.append(credential_tuple)
    return credentials

# Read credentials from 'users.txt'
USER_CREDENTIALS = read_credentials('users')

logging.basicConfig(level=logging.INFO)

class WebsiteTasks(SequentialTaskSet):


    
    def on_start(self):
        #self.init_sele_driver()
        if USER_CREDENTIALS:
            self.user_name, self.pass_word = USER_CREDENTIALS.pop()
        else:
            self.user_name, self.pass_word = ("default_user", "default_password")
        self.chrome_options = Options()
        #self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.chrome_options)
        #self.driver.get("https://telarus--fullstagin.sandbox.my.site.com/partner/s/")
        #self.driver.maximize_window()
        self.init_sele_driver(self.user_name, self.pass_word)
    
    def init_sele_driver(self, user__name, pass__word):
        self.driver.get("https://telarus--fullstagin.sandbox.my.site.com/partner/s/")
        WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,"//button[text()='Log in']")))
        username = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your email']")
        password = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your password']")
        #self.driver.get_
        lgnbtn = self.driver.find_element(By.XPATH,"//button[text()='Log in']")
        username.send_keys(user__name)
        time.sleep(1)
        password.send_keys(pass__word)
        time.sleep(1)
        lgnbtn.click()
        time.sleep(1)
                
    def measure_component_page_load_time(self, url,page, cmpxpath):
        no_results_xpath = "//h3[text()='No results']"
        self.driver.get(url)
        start_time = time.time()
        # cmp = WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,""+cmpxpath+"")))
        # end_time = time.time()
        # load_time = end_time-start_time
        # if cmp.is_displayed():
        #     logging.info(f"{self.user_name} - Time to load {page} for , {load_time}")
        try:
            cmp = WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, no_results_xpath)),
                    EC.presence_of_element_located((By.XPATH, cmpxpath))
                )
            )
            end_time = time.time()
            load_time = end_time - start_time

            if cmp.is_displayed():
                cmp_text = cmp.get_attribute("innerText").strip()
                if "No results" in cmp_text:
                    logging.info(f"{self.user_name} - Time to load {page}: {load_time:.2f} seconds")
                    return
                logging.info(f"{self.user_name} - Time to load {page}: {load_time:.2f} seconds")



                # If "No results" is found, exit early to avoid unnecessary refresh
                # if "No results" in cmp.text:
                #     logging.info(f"{self.user_name} - No results found on {page}, skipping refresh")
                #     return

        except Exception as e:
            logging.error(f"Error loading {page}: {e}")

    @task(1)
    def load_home_page(self):
        response = self.client.get("/partner/s", allow_redirects=True)
        logging.info(f"Home page status: {response.status_code}")

    @task(1)
    def opportunity_page_component_(self):
        no_results_xpath = "//h3[text()='No results']"
        anchor_xpath = "(//a[contains(@href,'/partner/s/opportunity/006')])[1]"
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/opportunity/Opportunity/Default",page="Opportunity",cmpxpath="//h3[text()='No results']")
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/opportunity/Opportunity/Default",page="Opportunity",cmpxpath=f"{anchor_xpath}")

    @task(1)
    def order_page_component_(self):
        no_results_xpath = "//h3[@class='avonni-illustration__title' and text()='No results']"
        #self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="//h3[text()='No results']",page="Order")
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",page="Order", cmpxpath=f"(//a[contains(@href,'/partner/s/order/801')])[1]|{no_results_xpath}")

    @task(1)
    def case_page_component_(self):
        no_results_xpath = "//h3[@class='avonni-illustration__title' and text()='No results']"
        # self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="//h3[text()='No results']",page="Order")
        self.measure_component_page_load_time(
            url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/case/Case/Default",page="Case",
            cmpxpath=f"(//a[contains(@href,'/partner/s/case/500')])[1]|{no_results_xpath}")
        #self.driver.quit()
        self.interrupt(reschedule=False)

    def on_stop(self):
            """Close session and clean up"""
            print("Test completed, cleanup.")
            if hasattr(self, 'driver') and self.driver:  # Ensure driver exists
                try:
                    self.driver.quit()  # Properly close the browser
                    print("Browser closed successfully.")
                except Exception as e:
                    print(f"Error while closing browser: {e}")

class WebsiteUser(HttpUser):
    #user waits for below time to start next task
    wait_time = between(1,5)
    tasks =[WebsiteTasks]
        

 
