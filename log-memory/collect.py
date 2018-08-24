import psutil
import json
import threading
import time
import os

json_data_file_path = './res/data.json'
json_file = open('./res/target.json', encoding='utf-8')
target_process =json.load(json_file)
interval = 1
json_file.close()
data = {}

def collect():
    global data
    for p in target_process:
        try:
            stat = psutil.Process(p['pid'])
        except Exception as e:
            print(e)
            continue

        mem = stat.memory_info()
        print ("%d(%s): %d Mb" % (p['pid'], p['name'], mem.private / 1024 / 1024))
        key = p['name']
        if data.get(key):
            data[key]['time'].append(time.time())
            data[key]['value'].append({
                "private": mem.private,
                "rss": mem.rss,
                "peak_wset": mem.peak_wset
            })
        else:
            data[key] = {}
            data[key]['time'] = []
            data[key]['value'] = []

def do_collect():
    collect()
    global timer
    timer = threading.Timer(interval, do_collect)
    timer.start()

timer = threading.Timer(1, do_collect)
timer.start()

cmd = input('input "stop" to stop')

if cmd == 'stop':
    timer.cancel()
    # print(repr(data))
    if os.path.exists(json_data_file_path):
        ori_json_file = open(json_data_file_path, 'r')
        ori_json_data = json.load(ori_json_file)
        ori_json_file.close()
        
        for key in ori_json_data.keys():
            if key in data:
                data[key + '_' + str(time.time())] = ori_json_data[key]
            else:
                data[key] = ori_json_data[key]
        print('json file exist, merge')

    json_target = open(json_data_file_path, 'w')
    js_target = open('./res/data.js', 'w');
    json_data = json.dumps(data, indent=4)
    json_target.write(json_data)
    js_target.write('var jsonData = ' + json_data)
    json_target.close()
    js_target.close()
    print('done, gen file data.json, data.js')

    


