import json

from flask import jsonify

import env
from flask_lambda2 import FlaskLambda

app = FlaskLambda(__name__)
app.config['DEBUG'] = True

@app.route('/users/', methods=["GET"]) # ensure `methods` match the method specified by the lambda function name
def get_users():                      # function identifier is irrelevant to functionality
    return jsonify({'status_code': 200})

context = lambda: 0
context.__dict__['function_name'] = 'get_users'
res = json.loads(app(event={}, context=context))
assert(res['status_code'] == 200)

