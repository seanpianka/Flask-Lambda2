import decimal
import json
from pprint import pprint

from flask import Flask
from flask.json import JSONEncoder


IDEMPOTENT_METHODS = ["GET", "PATCH", "PUT", "DELETE", "HEAD", "OPTIONS"]  # HTTP/1.1


class FlaskLambdaEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)

        if isinstance(obj, FlaskLambdaResponse):
            return dict(obj.__dict__)

        return JSONEncoder.default(self, obj)


class FlaskLambdaResponse:

    def __init__(
        self,
        body=None,
        headers=None,
        status_code=200,
        is_base64_encoded=False,
        json_encoder=FlaskLambdaEncoder,
    ):
        """
        :param body: dict containing data for body of response, will be dumped as JSON
                     when returned to caller
        :param headers: headers for response
        :param statusCode: status code of response
        :param isBase64Encoded: is body base64 encoded
        """
        self.body = {} if not body else dict(body)
        self.body["message"] = (
            "" if "message" not in self.body else self.body["message"]
        )

        self.headers = {} if not headers else dict(headers)
        self.status_code = int(status_code)
        self.is_base64_encoded = bool(is_base64_encoded)

        self.json_encoder = json_encoder

    @property
    def message(self) -> str:
        return str(self.body["message"])

    @message.setter
    def message(self, _message: str):
        self.body["message"] = str(_message)

    @property
    def __dict__(self):
        return {
            "body": json.dumps(self.body, cls=self.json_encoder),
            "headers": dict(self.headers),
            "statusCode": int(self.status_code),
            "isBase64Encoded": json.dumps(bool(self.is_base64_encoded)),
        }


class FlaskLambda(Flask):

    def __init__(self, *args, **kwargs):
        super(FlaskLambda, self).__init__(*args, **kwargs)
        self.json_encoder = FlaskLambdaEncoder

    def __call__(self, event, context):
        """ Compatibility layer to dispatch a request using a test client and
        data provided by AWS Lambda. This layer will still allows for requests
        to be dispatched through Flask's built-in request dispatch system.

        :param event: Data sent by user or a WSGI environment
        :param context: AWS Lambda data or a callable accepting a status code,
                        a list of headers and an optional exception context to
                        start the response
        """
        if "aws_request_id" not in context.__dict__:
            # In this "context" `event` is `environ` and
            # `context` is `start_response`, meaning the request didn't
            # occur via API Gateway and Lambda
            return super(FlaskLambda, self).__call__(event, context)

        try:
            method = event["httpMethod"].upper()
        except KeyError:
            raise Exception("Invalid invocation, method not specified by the event.")

        try:
            rule = event["path"]
        except KeyError:
            raise Exception("Invalid invocation, URL path not specified by the event.")

        request_data = {}

        if method in IDEMPOTENT_METHODS:
            request_data['query_string'] = event['queryStringParameters']
        else:
            request_data['data'] = json.loads(event['body'])

        with self.test_client() as client:
            response = json.loads(self.make_response(
                getattr(client, method.lower())(
                    rule,
                    follow_redirects=True,
                    **request_data
                )
            ).get_data())

        return response


if __name__ == "__main__":
    from flask import Flask, jsonify

    app = FlaskLambda(__name__)
    with app.test_client() as c:
        c.get("/")
        res = FlaskLambdaResponse()
        print(jsonify(res).get_data(as_text=True))
