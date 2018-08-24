import json
import threading
import json
from selenium import webdriver

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
    
    for page in config['page']:
        selector = page.get('selector')
        if not selector:
            break
        dom = dr.find_element_by_css_selector(selector)
        page['href'] = dom.get_attribute('href')
        if not page.get('name'):
            page['name'] = dom.text
    dr.close()


def write_log_config_file():
    file = open(log_memory_config_file, 'w')
    target_config = []
    for page in config['page']:
        target_config.append({
            'name': page['name'],
            'pid': ''
        })
    file.write(json.dumps(target_config, indent=4))
    file.close()

def init_browser():
    for page in config['page']:
        id = page.get('selector')
        if not id:
            break
        page.driver = webdriver.Chrome()
        page.driver.get(config.site)

load_config()
init_config()
write_log_config_file()