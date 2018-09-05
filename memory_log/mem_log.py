import psutil
import json
import threading
import time
import os

base_path = os.path.dirname(os.path.realpath(__file__))
def get_file_path(file_path):
    return os.path.normpath(os.path.join(base_path, file_path))

config = {
    'config_file': get_file_path('./setting.json'),
    'json_file': get_file_path('./res/data.json'),
    'js_file': get_file_path('./res/data.js'),
    'interval': 1,
    'target': [],
    'data': {}
}

timer = 0


def init_config(cfg):
    if not cfg:
        cfg = {}

    if cfg.get('target'):
        config['target'] = cfg['target']
    elif cfg.get('config_file'):
        config['config_file'] = cfg['config_file']

    if not cfg.get('target'):
        file = open(config['config_file'], encoding='utf-8')
        config['target'] = json.load(file)
        file.close()

    if cfg.get('interval'):
        config['interval'] = cfg['interval']


def save_data():
    data = config['data']
    json_file = config['json_file']
    js_file = config['js_file']
    if os.path.exists(json_file):
        ori_json_file = open(json_file, 'r')
        ori_json_data = json.load(ori_json_file)
        ori_json_file.close()

        for key in ori_json_data.keys():
            if key in data:
                data[key + '_' + str(time.time())] = ori_json_data[key]
            else:
                data[key] = ori_json_data[key]
        print('json file exist, merge')

    json_target = open(json_file, 'w')
    js_target = open(js_file, 'w')
    json_data = json.dumps(data, indent=4)
    json_target.write(json_data)
    js_target.write('var jsonData = ' + json_data)
    json_target.close()
    js_target.close()
    print('done, write file %s, %s'%(json_file, js_file))


def collect():
    global config
    data = config['data']

    for p in config['target']:
        try:
            stat = psutil.Process(p['pid'])
        except Exception as e:
            print(e)
            continue

        mem = stat.memory_info()
        print("%d(%s): %d Mb" % (p['pid'], p['name'], mem.private / 1024 / 1024))
        key = p['name']
        if data.get(key):
            data[key]['time'].append(time.time())
            data[key]['value'].append({
                "private": mem.private,
                "rss": mem.rss,
                "peak_wset": mem.peak_wset
            })
        else:
            data[key] = p.copy()
            data[key]['time'] = []
            data[key]['value'] = []


def do_task():
    global timer
    collect()
    timer = threading.Timer(config['interval'], do_task)
    timer.start()


def start():
    global timer
    timer = threading.Timer(1, do_task)
    timer.start()


def stop():
    global timer
    timer.cancel()

    


