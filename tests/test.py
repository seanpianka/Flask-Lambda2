import json
import unittest

from flask import jsonify

import env
from flask_lambda2 import FlaskLambda


class BasicRouteCase(unittest.TestCase):
    def test_app_invokation(self):
        app = FlaskLambda(__name__)
        app.config['DEBUG'] = True

        @app.route('/users/', methods=["GET"])
        def get_users():
            return jsonify({'status_code': 200})

        context = lambda: 0
        context.__dict__['aws_request_id'] = 'foobarbaz'
        res = json.loads(app(event={"route":"/users/", "method":"get"}, context=context))
        self.assertEqual(res['status_code'], 200)


if __name__ == '__main__':
    unittest.main()
