from flask import request
from flask import json
from app import app
from app.common import *
from app.requesterror import RequestError
from flask import jsonify
import requests
import numpy as np

@app.route('/api/nodes')
def nodes():
    url = app.config['MADDASH']
    nodes = get_nodes(url)
    return nodes

@app.route('/api/runm', methods = ['POST'])
def runm():
    if request.method == 'POST':
        data = request.get_json()

        url = 'https://%s/pscheduler/tasks' % data['select-source']
        header = {"content-type": "application/json"}

        jsondata = create_test_json(data)
        try:
            #https://requests.readthedocs.io/en/master/user/advanced/#timeouts
            response = requests.post(url, json.dumps(jsondata),  headers=header,  verify=False,  timeout=(20, 60))
        except requests.exceptions.HTTPError as errh:
            app.logger.error('Http Error: %s', repr(errh))
            raise RequestError('Http Error', 400, { 'ext': repr(errh) })
        except requests.exceptions.ConnectionError as errc:
            app.logger.error('Connection Error: %s', repr(errc))
            raise RequestError('Connection Error', 400, { 'ext': repr(errc) })
        except requests.exceptions.Timeout as errt:
            app.logger.error('Timeout Error: %s', repr(errt))
            raise RequestError('Timeout Error', 400, { 'ext': repr(errt) })
        except requests.exceptions.RequestException as err:
            app.logger.error("Unknown Error: %s" + repr(err))
            raise RequestError('Unknown Error', 400, { 'ext': repr(err) })

        res = ''
        if response.status_code == requests.codes.ok:
            res = response.json()

            try:
                response = requests.get(res,  params={'detail':True},  verify=False)
            except requests.exceptions.RequestException as err:
                app.logger.error("Unknown Error: %s" + repr(err))
                raise RequestError('Unknown Error', 400, { 'ext': repr(err) })

            if response.status_code == requests.codes.ok:
                res = response.json()
            else:
                app.logger.error("Request code not OK")
                raise RequestError('Request code not OK', 400, { 'ext': '' })

            try:
                first_run_url = res["detail"]["first-run-href"]
            except requests.exceptions.RequestException as err:
                app.logger.error("JSON response error: %s", repr(err))
                raise RequestError('JSON response error', 400, { 'ext': repr(err) })

            return jsonify(first_run_url)
        else:
            app.logger.error("Request code not OK")
            raise RequestError('Serv error', 400, { 'ext': 'Far server response code not OK' })

@app.route('/api/getfirstrun', methods = ['POST'])
def getjson():
    if request.method == 'POST':
        data = request.get_json()
        try:
            r = requests.get(data, verify=False)
            return r.json()
        except requests.exceptions.RequestException as err:
            app.logger.error("Unknown Error: %s" + repr(err))
            raise RequestError('Unknown Error', 400, { 'ext': repr(err) })


@app.route('/api/getresults', methods = ['POST'])
def resgetjson():
    if request.method == 'POST':
        data = request.get_json()
        taskurl = ''
        testtype = ''
        if(data.endswith('/runs/first')) :
            taskurl = data[0:-11]
            try:
                t = requests.get(taskurl, verify=False)
                tr = t.json()
                testtype = tr['test']['type']
            except requests.exceptions.RequestException as err:
                app.logger.error("Unknown Error: %s" + repr(err))
                raise RequestError('Unknown Error', 400, { 'ext': repr(err) })
        try:
            if((testtype == 'throughput') ):
                data = data + '?wait-merged=1'
            r = requests.get(data, verify=False)
            a = r.json()
            if(a['state'] == 'finished') :
                a['result']['testtype'] = testtype
                a['result']['tr'] = tr
                if((testtype == 'latency') ):
                    b = a['result']['raw-packets']
                    totlatency = 0
                    recpkts = 0
                    prevlatency = 0
                    totaljitter = 0
                    ca = []
                    for i in range(len(b)):
                        calclatency = round(1000 * (b[i]['dst-ts'] - b[i]['src-ts'] ) / (2**32),  2)
                        if(prevlatency == 0) :
                            prevlatency = calclatency
                        totaljitter += abs(calclatency - prevlatency)
                        a['result']['raw-packets'][i]['calclatency'] = calclatency
                        a['result']['raw-packets'][i]['prevlatency'] = prevlatency
                        totlatency += calclatency
                        recpkts += 1
                        prevlatency = calclatency
                        ca.append(calclatency)
                    p50 = np.percentile(ca, 50)
                    p25 = np.percentile(ca, 25)
                    p75 = np.percentile(ca, 75)
                    p95 = np.percentile(ca, 95)
                    median = np.median(ca)
                    minimum = np.amin(ca)
                    maximum = np.amax(ca)
                    a['result']['stats'] = {}
                    a['result']['stats']['p25'] = round(p25,  2)
                    a['result']['stats']['p50'] = round(p50,  2)
                    a['result']['stats']['p75'] = round(p75,  2)
                    a['result']['stats']['p95'] = round(p95,  2)
                    a['result']['stats']['p95p50'] = round(p95 - p50, 2)
                    a['result']['stats']['p75p25'] = round(p75 - p25, 2)
                    a['result']['stats']['median'] = round(median,  2)
                    a['result']['stats']['minimum'] = round(minimum,  2)
                    a['result']['stats']['maximum'] = round(maximum,  2)
                    a['result']['stats']['avglatency'] = 0
                    a['result']['stats']['rfcjitter'] = 0
                    a['result']['stats']['totlatency'] = round(totlatency, 2)
                    a['result']['stats']['totaljitter'] = round(totaljitter,  2)
                    a['result']['stats']['recpkts'] = recpkts
                    if(recpkts > 0):
                        a['result']['stats']['avglatency']  = round(totlatency / recpkts,  2)
                        a['result']['stats']['rfcjitter']  = round(totaljitter / recpkts,  2)
                elif((testtype == 'throughput') ):
                    a['result']['testtype'] = testtype
            return a
        except requests.exceptions.RequestException as err:
            app.logger.error("Unknown Error: %s" + repr(err))
            raise RequestError('Unknown Error', 400, { 'ext': repr(err) })

@app.route('/api/gettests', methods = ['POST'])
def getpschedulertests():
    if request.method == 'POST':
        tests = get_all_defined_tests()
        data = request.get_json()

        surl = 'https://%s/pscheduler/tests' % data['select-source']
        durl = 'https://%s/pscheduler/tests' % data['select-dest']
        slst = []
        dlst = []

        try:
            s = requests.get(surl, verify=False,  timeout=5)
            sres = s.json()
            for x in sres:
                slst.append(x.rsplit('/', 1)[1])
        except requests.exceptions.RequestException as err:
            app.logger.error("Unknown Error: %s" + repr(err))

        try:
            d = requests.get(durl, verify=False,  timeout=5)
            dres = d.json()
            for x in dres:
                dlst.append(x.rsplit('/', 1)[1])
        except requests.exceptions.RequestException as err:
            app.logger.error("Unknown Error: %s" + repr(err))

        result = list(set(tests).intersection(slst, dlst))
        print(result)

        return jsonify(result)


@app.errorhandler(RequestError)
def handle_error(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 400
