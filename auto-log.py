import threading
import json
import psutil
import time
import re
from selenium import webdriver
from memory_log import mem_log

config_path = './page.json'
log_memory_config_file = './target.json'

config = {}

def load_config():
    file = open(config_path, 'r')
    global config
    config = json.load(file)
    file.close()

def init_config():
    global config
    dr = webdriver.Chrome()
    dr.get(config['site'])
    time.sleep(20)
    print('start collect target url')
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
    for page in config['page']:
        name = page.get('name')
        if not name:
            break
        dr = webdriver.Chrome()
        dr.get(config['empty'])
        page['is_empty'] = True
        process = psutil.Process(dr.service.process.pid)

        p = process.children()[0]
        handles = dr.window_handles

        page['pid'] = p.pid
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
        print('[%s] navigate to: %s' % (page['name'], next_url))
        page['driver'].get(next_url)

def on_task_end():
    mem_log.stop()
    mem_log.save_data()
    input('input anything to terminal:')

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
mem_log.start()