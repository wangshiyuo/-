import time
from multiprocessing.dummy import Pool

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service


def get_email_list():
    with open('email_list.txt', 'r') as email_file:
        email_list = email_file.readlines()
    return email_list


def login(email):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 设置为开发者模式
    options.add_argument("headless")  # 隐藏浏览器
    s = Service("./chromedriver")
    browser = webdriver.Chrome(service=s, options=options)
    WebDriverWait(browser, 5)
    browser.get("https://www.amazon.cn")
    sign_button = browser.find_element(By.CSS_SELECTOR, '#nav-link-accountList > div')  # 定义登录页面按钮
    sign_button.click()
    input_edit = browser.find_element(By.CSS_SELECTOR, '#ap_email')  # 定义邮箱输入框
    input_edit.clear()  # 清除输入框内容
    input_edit.send_keys(email)  # 发送登录邮箱到输入框框
    ap_legal_agreement_check_box = browser.find_element(By.CSS_SELECTOR, '#ap_legal_agreement_check_box')  # 定义阅读声明按钮
    ap_legal_agreement_check_box.click()  # 点击动作
    continue_button = browser.find_element(By.CSS_SELECTOR, '#continue')  # 定义继续按钮
    continue_button.click()  # 点击动作
    page = browser.page_source  # 保存源码

    if "我们找不到具有该电子邮件地址的账户" in page:
        return None
    else:
        with open('amazon_id.txt', 'a') as file:
            file.write(email)
            file.write('\n')
        browser.quit()
        # browser.back()
        # browser.refresh()


def run1():
    """单线程"""
    for email in get_email_list():
        login(email)
    print('单线程over！')


def run2():
    """多线程"""
    pool = Pool(20)
    email_list = get_email_list()
    pool.map(login, email_list)
    pool.close()
    pool.join()
    print('多线程over！')


start = time.time()
run1()
end = time.time()
print(f"单线程运行时间：{end - start}s")

start = time.time()
run2()
end = time.time()
print(f"多线程运行时间：{end - start}s")
