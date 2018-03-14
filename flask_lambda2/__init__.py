from flask import Flask


_IDEMPOTENT_METHODS = ["GET", "PUT", "DELETE", "HEAD", "OPTIONS"] # HTTP/1.1


class FlaskLambda(Flask):
    def __call__(self, event, context):
        """ Compatibility layer to dispatch a request using a test client and
        data provided by AWS Lambda. This layer will still allows for requests
        to be dispatched through Flask's built-in request dispatch system.
        Specifically, the calling convention requires that both the rule and
        the method associated with the specific rule endpoint is specified
        within the body of the data sent to the endpoint. Technically, all data
        sent to the lambda route will be within the `dict`:event.

        :param event: Data sent by user or a WSGI environment
        :param context: AWS Lambda data or a callable accepting a status code,
                        a list of headers and an optional exception context to
                        start the response
        """
        if 'aws_request_id' not in context.__dict__:
            return super(FlaskLambda, self).__call__(event, context)

        method, rule = event['method'].lower(), event['route']
        if not rule.startswith('/'):
            rule = '/' + rule
        if not rule.endswith('/'):
            rule += '/'

        with self.test_client() as client:
            return self.make_response(getattr(client, method)(
                rule, follow_redirects=True,
                **{'query_string' if method in _IDEMPOTENT_METHODS else "data": event})
            ).get_data(as_text=True)
