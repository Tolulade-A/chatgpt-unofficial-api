"""Make some requests to OpenAI's chatbot"""
#tips https://playwright.tech/blog/end-to-end-tests-with-playwright-python

import time
import os
import flask

from flask import g


from playwright.sync_api import sync_playwright

APP = flask.Flask(__name__)
PLAY = sync_playwright().start()
BROWSER = PLAY.firefox.launch_persistent_context(
    user_data_dir='C:\\XXX\\XXX\\AppData\\Local\\ms-playwright', #location of the playwright installation
    #executable_path= ('C:\\XXX\\XXX\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'), #if you want to change
    #firefox to chromium.
    headless=False,
)
PAGE = BROWSER.new_page()


"""
from playwright.sync_api import sync_playwright

APP = flask.Flask(__name__)
user_data_dir = 'C:\\xxx\\xxx\\AppData\\Local\\ms-playwright'
#user_data_dir = os.path.join(os.getcwd(), user_data_dir)

with sync_playwright() as PLAY:
    BROWSER = PLAY.chromium.launch_persistent_context(
        user_data_dir,
        executable_path=('C:\\XXX\\XXX\\AppData\\Local\\Google\\Chrome\\Application\\new_chrome.exe'),
        headless=False)
    PAGE = BROWSER.new_page()
    PAGE.goto("https://chat.openai.com/")
    #BROWSER.close()
"""


def get_input_box():
    """Get the child textarea of `PromptTextarea__TextareaWrapper`"""
    return PAGE.query_selector("textarea")

def is_logged_in():
    # See if we have a textarea with data-id="root"
    return get_input_box() is not None

def is_loading_response() -> bool:
    """See if the send button is diabled, if it does, we're not loading"""
    return not PAGE.query_selector("textarea ~ button").is_enabled()

def send_message(message):
    # Send the message
    box = get_input_box()
    box.click()
    box.fill(message)
    box.press("Enter")

def get_last_message():
    """Get the latest message"""
    while is_loading_response():
        time.sleep(0.25)
    page_elements = PAGE.query_selector_all("div[class*='markdown prose']")
    last_element = page_elements.pop()
    return last_element.inner_text()

def regenerate_response():
    """Clicks on the Try again button.
    Returns None if there is no button"""
    try_again_button = PAGE.query_selector("button:has-text('Try again')")
    if try_again_button is not None:
        try_again_button.click()
    return try_again_button

def get_reset_button():
    """Returns the reset thread button (it is an a tag not a button)"""
    return PAGE.query_selector("a:has-text('Reset thread')")

@APP.route("/chat", methods=["GET"]) #TODO: make this a POST
def chat():
    message = flask.request.args.get("q")
    print("Sending message: ", message)
    send_message(message)
    response = get_last_message()
    print("Response: ", response)
    return response

# create a route for regenerating the response
@APP.route("/regenerate", methods=["POST"])
def regenerate():
    print("Regenerating response")
    if regenerate_response() is None:
        return "No response to regenerate"
    response = get_last_message()
    print("Response: ", response)
    return response

@APP.route("/reset", methods=["POST"])
def reset():
    print("Resetting chat")
    get_reset_button().click()
    return "Chat thread reset"

@APP.route("/restart", methods=["POST"])
def restart():
    global PAGE,BROWSER,PLAY
    PAGE.close()
    BROWSER.close()
    PLAY.stop()
    time.sleep(0.25)
    PLAY = sync_playwright().start()
    BROWSER = PLAY.firefox.launch_persistent_context(
        user_data_dir='C:\\XXX\\XXX\\AppData\\Local\\ms-playwright',
        #executable_path=('C:\\XXX\\XXX\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'),
        headless=False,
    )
    PAGE = BROWSER.new_page()
    PAGE.goto("https://chat.openai.com/")
    return "API restart!"


def start_browser():
    PAGE.goto("https://chat.openai.com/")
    if not is_logged_in():
        print("Please log in to OpenAI Chat")
        print("Press enter when you're done")
        input()
    else:
        print("Logged in")
        APP.run(host='127.0.0.1', port=5000, threaded=False) #or
        #APP.run(port=5000, threaded=False) #can also be used

if __name__ == "__main__":
    start_browser()


