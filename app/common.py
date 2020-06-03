import urllib.request, json
import requests
from app.formjsonmap import FormJSONMap

def get_nodes(site):
    with urllib.request.urlopen(site) as url:
        nodes = json.loads(url.read().decode())
        return nodes

def get_test_tools(site,  test):

    tools_url = '%s/pscheduler/tests/%s/tools' % (site,  test)
    params = {}
    r = requests.get(url = tools_url, params = params,  verify=False)
    ltools = r.json()
    tools = []
    for t in ltools:
        tspl = t.split('tools/')
        tools.append(tspl[1])
    return tools

def get_all_defined_test_tools():
    tt = {}
    tt['clock'] = ['psclock']
    tt['disk-to-disk'] = ['curl',  'globus']
    tt['dns'] = ['dnspy']
    tt['http'] = ['psurl']
    tt['latency'] = ['owping']
    tt['latencybg'] = ['powstream']
    tt['rtt'] = ['ping']
    tt['simplestream'] = ['simplestreamer']
    tt['throughput'] = ['iperf3',  'iperf2',  'nuttcp']
    tt['trace'] = ['traceroute',  'tracepath',  'paris-traceroute']
    return tt

def create_test_json(data):
    t = {
        "test": { 
            "spec" : {
                "schema" : 1, 
            }
        },
        "schedule" : {}
    } 
    
    for key, value in data.items():
        s = FormJSONMap()
        if key == 'trace-select-tools':
            for i in value :
                s.map_form_to_json(key,  i,  t)
        elif key == 'throughput-select-tools':
            for i in value:
                s.map_form_to_json(key,  i,  t)
        else:
            s.map_form_to_json(key,  value,  t)
    return t
