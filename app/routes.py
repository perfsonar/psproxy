from flask import request
from flask import json
from app import app
from app.common import *
from app.requesterror import RequestError
from flask import jsonify
import requests

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
            response = requests.post(url, json.dumps(jsondata),  headers=header,  verify=False,  timeout=60)
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

@app.errorhandler(RequestError)
def handle_error(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status
    payload['message'] = error.message
    return jsonify(payload), 400
