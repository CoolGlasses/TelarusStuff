import time
import logging
import csv
import threading
import os
from locust import task, between, HttpUser, SequentialTaskSet, events
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

users = []
for i in range(1, 111):
    i_str = str(i)
    if len(i_str) == 1:
        formatted_i = "00" + i_str
    elif len(i_str) == 2:
        formatted_i = "0" + i_str
    else:
        formatted_i = i_str
    username = f"plttest{formatted_i}@telarus.com"
    password = "password-1"
    new_user = {"username": username, "password": password}
    users.append(new_user)

USER_CREDENTIALS = [(user["username"], user["password"]) for user in users]
logging.info(users)

CSV_FILE = "performance_data.csv"
CSV_HEADER = ["Time", "User", "Component", "Load Time"]
csv_lock = threading.Lock()

def write_to_csv(current_time, user, component, load_time):
    with csv_lock:
        file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
        with open(CSV_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(CSV_HEADER)
            writer.writerow([current_time, user, component, load_time])


class WebsiteTasks(SequentialTaskSet):

    def on_start(self):
        # Initialize WebDriver for each user
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        self.driver.maximize_window()

        # Assign one credential per user (simple approach: pop first available)
        # For production, consider a queue or other distribution method
        self.username, self.password = USER_CREDENTIALS.pop(0)
        print(f"Spawning user: {self.username}, Remaining credentials: {len(USER_CREDENTIALS)}")
        self.task_count = 0
        self.total_tasks = 1000
        self.init_sele_driver(self.username, self.password)

    def init_sele_driver(self, username, password):
        self.driver.get("https://telarus--fullstagin.sandbox.my.site.com/partner/s/")
        WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,"//button[text()='Log in']")))
        username_field = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your email']")
        password_field = self.driver.find_element(By.XPATH,"//input[@placeholder='Enter your password']")
        lgnbtn = self.driver.find_element(By.XPATH,"//button[text()='Log in']")
        username_field.send_keys(username)
        time.sleep(1)
        password_field.send_keys(password)
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
                    logging.info(f"{self.username} - Time to load {page}: {load_time:.2f} seconds")
                    return
                logging.info(f"{self.username} - Time to load {page}: {load_time:.2f} seconds")



                # If "No results" is found, exit early to avoid unnecessary refresh
                # if "No results" in cmp.text:
                #     logging.info(f"{self.user_name} - No results found on {page}, skipping refresh")
                #     return

        except Exception as e:
            logging.error(f"Error loading {page}: {e}")

        print(f"User: {self.username}, Component is visible for {page}, Load Time: {load_time:.2f}")
     

    @task
    def opportunity_page_component_(self):
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/opportunity/Opportunity/Default",page="Oppurtunity",cmpxpath="(//a[contains(@href,'/partner/s/opportunity/006')])[1]")
        self.task_count += 1
        if self.task_count >= self.total_tasks:
            self.on_stop()
    @task
    def order_page_component_(self):
        self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="(//a[contains(@href,'/partner/s/order/801')])[1]",page="Order") 
        self.task_count += 1
        if self.task_count >= self.total_tasks:
            self.on_stop()
    
    @task
    def case_page_component_(self):
        no_results_xpath = "//h3[@class='avonni-illustration__title' and text()='No results']"
        # self.measure_component_page_load_time(url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/order/Order/Default",cmpxpath="//h3[text()='No results']",page="Order")
        self.measure_component_page_load_time(
            url="https://telarus--fullstagin.sandbox.my.site.com/partner/s/case/Case/Default",page="Case",
            cmpxpath=f"(//a[contains(@href,'/partner/s/case/500')])[1]|{no_results_xpath}")


    def on_stop(self):
        logging.info(f"Stopping user: {self.username}")
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            logging.info(f"Browser closed for user: {self.username}")
            print(f"Browser closed for user: {self.username}")


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    tasks = [WebsiteTasks]

 # Event handler to ensure process exits when test stops
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("Test stopped, cleaning up and exiting.")
    if environment.runner and hasattr(environment.runner, 'users'):
        for user in environment.runner.users:
             if hasattr(user, 'task_set') and user.task_set:
                user.task_set.stop()
    if environment.runner:
        environment.runner.quit()
    logging.info("Forcing process exit.")
    print("Forcing process exit.")
    os._exit(0)

# Handle quitting event to ensure cleanup
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    logging.info("Locust is quitting, ensuring cleanup.")
    print("Locust is quitting, ensuring cleanup.")
    if environment.runner and hasattr(environment.runner, 'users'):
        for user in environment.runner.users:
            if hasattr(user, 'task_set') and user.task_set:
                user.task_set.stop()