import threading
import json
import psutil
import time
import re
import os
import yaml

from selenium import webdriver
from memory_log import mem_log
import chrome_tab_pid_finder

config_path = './setting.yml'
log_memory_config_file = './target.json'

config = {}

def load_config():
    file = open(config_path, 'r', encoding='utf-8')
    global config
    # config = json.load(file)
    config = yaml.load(file)
    file.close()

def do_auth(driver):
    auth = config.get('auth')
    if auth and auth.get('url') and auth.get('script') and os.path.exists(auth['script']):
        driver.get(config['auth']['url'])
        time.sleep(auth.get("waiting_time", 3))
        file = open(auth['script'], 'r')
        print('[log] execute login script %s' % auth['script'])
        driver.execute_script(file.read(), auth)
        file.close()
        time.sleep(auth.get("waiting_time", 3))

def init_config():
    global config
    dr = webdriver.Chrome()
    do_auth(dr)
    dr.get(config['site'])
    time.sleep(config.get('collect_url_load_waiting_time', 10))

    pages = []
    reg = re.compile('\s*')
    for page in config['page']:
        selector = page.get('selector')
        if not selector:
            break
        dom = dr.find_element_by_css_selector(selector)
        page['href'] = dom.get_attribute('href')
        if not page.get('name'):
            name = dom.get_attribute('innerText')
            page['name'] = reg.sub('', name)
        pages.append(page)
    config['page'] = pages
    dr.quit()


def write_log_config_file():
    file = open(log_memory_config_file, 'w')
    target_config = []
    for page in config['page']:
        target_config.append({
            'name': page['name'],
            'pid': page['pid'],
            'url': page['href'],
            'create_time': page['create_time']
        })
    file.write(json.dumps(target_config, indent=4))
    file.close()

def init_browser():
    global config

    print('there is no way to get the chrome tab pid unless dev channel, may be you need to input pid :)')
    for page in config['page']:
        name = page.get('name')
        if not name:
            break
        dr = webdriver.Chrome()
        is_empty = config.get('start_with_empty', True)
        if is_empty:
            url = config['empty']
        else:
            url = page['href']

        pid = chrome_tab_pid_finder.get_pid({
            'name': page['name'],
            'site': url
        }, dr)

        do_auth(dr)
        dr.get(url)
        dr.refresh()
        p = psutil.Process(pid)

        page['pid'] = pid
        page['create_time'] = p.create_time()
        page['driver'] = dr



def test_single_page():
    global config
    for page in config['page']:
        
        is_current_empty_page = page.get('is_empty')
        if not is_current_empty_page:
            page['is_empty'] = True
            next_url = config['empty']
        else:
            page['is_empty'] = False
            next_url = page['href']
        print('[%s] [%s] navigate to: %s' % (page['name'], config['times'], next_url))
        page['driver'].get(next_url)

def on_task_end():
    mem_log.stop()
    mem_log.save_data()
    input('input "stop" to terminal:')

def do_task():
    global config
    global timer
    test_single_page()
    timer = threading.Timer(config['interval'], do_task)
    if config['times'] >= 0:
        timer.start()
        config['times'] -= 1
    else:
        timer = threading.Timer(config['end_interval'], on_task_end)
        timer.start()
        print('[log] start silent time %s s' % config['end_interval'])

load_config()
init_config()
init_browser()
write_log_config_file()

timer = threading.Timer(config['start_interval'], do_task)
timer.start()

mem_log_target = []
for item in config['page']:
    target = item.copy()
    del target['driver']
    mem_log_target.append(target)
mem_log.init_config({
    "target": mem_log_target
})

if config.get('log_start_interval'):
    time.sleep(config['log_start_interval'])
mem_log.start()