import csv
import time
from datetime import datetime, timedelta
import pickle
import os
from types import NoneType

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import dateparser

import chromedriver_binary

driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')

wait = WebDriverWait(driver, 5)
wait_long = WebDriverWait(driver, 60)
actions = ActionChains(driver)


def write_to_file(obj, fname):
    with open(fname, 'wb') as picklefile:
        pickle.dump(obj, picklefile)


def read_from_file(fname):
    if not os.path.exists(fname):
        return None
    with open(fname, 'rb') as picklefile:
        obj = pickle.load(picklefile)
    return obj


def wait_and_click(el: str | WebElement, driver_wait=wait):
    if type(el) == str:
        target = driver_wait.until(ec.presence_of_element_located((By.XPATH, el)))
    else:
        target = el

    target.click()

    return target


def wait_and_hover(el: str | WebElement):
    if type(el) == str:
        target = wait.until(ec.presence_of_element_located((By.XPATH, el)))
    else:
        target = el

    hover = actions.move_to_element(target)
    hover.perform()
    return target


def react_to(msg):
    wait_and_hover(msg)
    time.sleep(0.25)
    react_button_path = "//span[@data-testid='react']"
    react_button = msg.find_element_by_xpath(react_button_path)
    wait_and_click(react_button)
    time.sleep(0.25)
    wait_and_click('//div[@data-testid="reactions-option-0"]')


def press_send_button():
    """Not used as of now"""
    send_button_path = "//span[@data-testid='send']"
    wait_and_click(send_button_path)


def send_message(message):
    input_box_path = "//div[@title='Type a message']"
    wait_and_click(input_box_path).send_keys(message + Keys.ENTER)


def delete_message(msg):
    wait_and_hover(msg)
    down_arrow_xpath = "//div[@data-testid='icon-down-context']"
    down_arrow = msg.find_element_by_xpath(down_arrow_xpath)
    time.sleep(0.25)
    wait_and_click(down_arrow)
    time.sleep(0.25)

    wait_and_click("//div[contains(text(), 'Delete message')]")
    time.sleep(0.25)
    wait_and_click("//div[contains(text(), 'Delete for me')]")


def new_group(grp_name):
    new_group_path = "//div[@title='New chat']"
    wait_and_click(new_group_path)

    time.sleep(0.25)
    wait_and_click('//div[contains(text(), "New group")]')

    time.sleep(0.25)
    contact_name_box_path = "//input[@placeholder='Type contact name']"
    wait_and_click(contact_name_box_path).send_keys('Aba')

    time.sleep(0.25)
    contact_name_path = "//span[@title='Aba']"
    wait_and_click(contact_name_path)

    time.sleep(0.25)
    wait_and_click("//span[@data-testid='arrow-forward']")

    time.sleep(0.25)
    wait_and_click("//div[@role='textbox']").send_keys(grp_name + Keys.ENTER)

    time.sleep(2)
    wait_and_click(f"//div[contains(text(), 'Cancel')]")

    time.sleep(5)
    print("Created group!")

    send_message("Hello World!")


def go_to_chat(chat_name):
    for x in range(0, 2):
        search_box_path = ' //div[contains(@title, "Search input textbox")]'
        search_bar = wait_and_click(search_box_path)
        time.sleep(0.25)
        search_bar.send_keys(Keys.END)
        search_bar.send_keys(Keys.BACKSPACE * 50)
        time.sleep(0.25)
        search_bar.send_keys(chat_name)
        time.sleep(0.25)

        chat_box_path = f'//span[@title="{chat_name}"]'
        try:
            wait_and_click(chat_box_path)
            return
        except TimeoutException:
            print(f"Finding group chat '{chat_name}' timed out. Retrying...")

    log(f"Could not find group chat '{chat_name}'. Creating group...")
    new_group(chat_name)


def send_message_to_chat(chat_name, message):
    go_to_chat(chat_name)
    send_message(message)


def log(msg):
    send_message_to_chat("Scheduled Message Logs", msg)


class Message:
    def __init__(self, chat_name, msg_text, num_seconds_to_send,
                 is_recurring=False, schedule_date: datetime = None):
        self.chat_name = chat_name
        self.msg_text = msg_text
        self.num_seconds_to_send = num_seconds_to_send
        self.time_to_send = datetime.now() + timedelta(seconds=self.num_seconds_to_send)
        if schedule_date is not None:
            self.time_to_send = schedule_date

        # print(self.time_to_send)

        self.recurring = is_recurring
        self.message_sent = False

        log(f"Scheduled {self.__str__()} in {self.num_seconds_to_send}s")

    def __str__(self):
        if self.recurring:
            r = 'recurring'
        else:
            r = 'non-recurring'

        if self.message_sent:
            s = 'sent'
        else:
            s = 'pending'

        return f"{r} {s} message to {self.get_chat_name()}: {self.get_message_text()}"

    def get_chat_name(self):
        return self.chat_name

    def get_message_text(self):
        return self.msg_text

    def is_sent(self):
        return self.message_sent

    def check_send(self):
        if (not self.message_sent) and self.time_to_send < datetime.now():
            send_message_to_chat(chat_name=self.chat_name, message=self.msg_text)
            log(f"Sent {self.__str__()}")
            if self.recurring:
                self.time_to_send = datetime.now() + timedelta(seconds=self.num_seconds_to_send)
            else:
                self.message_sent = True


class MessageScheduler:
    def __init__(self, filename='./message_scheduler'):
        self.filename = filename
        self.scheduled_messages = list()
        write_to_file(self, filename)

    def schedule_message(self, msg: Message):
        self.scheduled_messages.append(msg)
        write_to_file(self, self.filename)

    def send_scheduled_messages(self):
        for msg in self.scheduled_messages:
            msg.check_send()
        write_to_file(self, self.filename)

    def get_scheduled_messages(self):
        return self.scheduled_messages[:]

    def delete_scheduled_messages(self):
        self.scheduled_messages = list()
        write_to_file(self, self.filename)


def get_messages_from_chat(chat_name):
    messages = list()
    go_to_chat(chat_name)
    msg_container_path = "//div[@class='copyable-text']"
    for element in driver.find_elements(by=By.XPATH, value=msg_container_path):
        message = element.get_attribute('innerText')
        messages.append(message)
        delete_message(element)
        time.sleep(0.25)

    return messages


def delete_scheduling_groups(scheduling_opts):
    # Not working
    for key in scheduling_opts:
        go_to_chat(f"Scheduled Messages {key}")
        time.sleep(0.25)
        wait_and_click(f"//span[@title='Scheduled Messages {key}']")
        time.sleep(0.25)
        wait_and_click("//div[@title='Exit group']")
        time.sleep(0.25)
        wait_and_click(f"//div[contains(text(), 'Exit group')]")
        time.sleep(0.25)
        wait_and_click(f"//div[contains(text(), 'Delete group')]")
        time.sleep(0.25)
        wait_and_click(f"//div[contains(text(), 'Continue')]")
        time.sleep(0.25)


def reset_scheduling_options():
    scheduling_options = {
        '10sec': '10',
        '30sec': '30',
        '1min': '60',
        '10min': '600',
        '1hr': '3600',
        '1day': '86400',
    }

    save_scheduling_dict(scheduling_options)


def save_scheduling_dict(scheduling_dict):
    with open('scheduling_options.csv', 'w+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[key for key in scheduling_dict])
        writer.writeheader()
        writer.writerows([scheduling_dict])


def add_scheduling_group(name, secs):
    SCHEDULING_OPTIONS[name] = secs
    save_scheduling_dict(SCHEDULING_OPTIONS)
    new_group(f"Scheduled Messages {name}")


def get_scheduling_options():
    with open('./scheduling_options.csv', 'r') as schedule_options_file:
        scheduling_options = csv.DictReader(schedule_options_file)
        try:
            scheduling_options = next(scheduling_options)
        except Exception as e:
            log(f"Error: {e}")

        return scheduling_options


TIME_ABBRS = {'sec': 1, 'min': 60, 'hr': 3600, 'day': 86400}
SCHEDULING_OPTIONS = get_scheduling_options()
READ_FROM_FILE = True

if READ_FROM_FILE:
    sch = read_from_file('./message_scheduler')
    if sch is None:
        sch = MessageScheduler()
else:
    sch = MessageScheduler()

print(f"Scheduled messages: {sch.get_scheduled_messages()}")

time.sleep(30)

wait_and_click(' //div[contains(@title, "Search input textbox")]', wait_long)

while True:
    for option in SCHEDULING_OPTIONS:
        sch.send_scheduled_messages()

        time.sleep(1)
        try:
            messages = get_messages_from_chat(f"Scheduled Messages {option}")
        except Exception as e:
            log(f"Error: {e}")
            continue

        for m in messages:
            recurring = False
            if "&" in m:
                m = m.replace('&', '')
                recurring = True

            num_seconds = int(SCHEDULING_OPTIONS[option])

            if m.count('; ') == 1:
                contact_name = m.split('; ')[0]
                message_text = m.split('; ')[1]
                # print(f"Sending message to {contact_name}: {message_text}")
                message = Message(contact_name, message_text, num_seconds, recurring)

            elif m.count('; ') == 2:
                contact_name = m.split('; ')[0]
                message_text = m.split('; ')[1]
                time_to_send = m.split('; ')[2]
                schedule_time = dateparser.parse(time_to_send)
                # print(f"Schedule time: {schedule_time}")
                if schedule_time is None:
                    log(f"Warning: Could not parse datetime string '{time_to_send}'...")
                    continue

                message = Message(contact_name, message_text, num_seconds, recurring, schedule_date=schedule_time)

            else:
                log(f"Warning: Wrong number ({m.count('; ')}) of '; ' found...")
                continue

            sch.schedule_message(message)
    time.sleep(1)

    try:
        new_scheduling_groups = get_messages_from_chat("New Scheduling Groups")
    except Exception as e:
        log(f"Error creating scheduling group: {e}")
        continue
    for grp_name in new_scheduling_groups:
        try:
            num = int(grp_name.split(' ')[0])
            abbr = grp_name.split(' ')[1]
            coeff = TIME_ABBRS[abbr]
            add_scheduling_group(f"{num}{abbr}", num * coeff)
            SCHEDULING_OPTIONS = get_scheduling_options()
        except ValueError:
            log(f"Warning: Invalid scheduling preset: {grp_name}")

    try:
        commands = get_messages_from_chat("Schedule Message Commands")
    except Exception as e:
        log(f"Error executing commands: {e}")
        continue
    for command in commands:
        if command == "delete all":
            sch.delete_scheduled_messages()
            log("Deleted all scheduled messages.")
    time.sleep(0.25)
