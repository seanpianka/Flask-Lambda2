from flask import Flask


__all__ = ["FlaskLambda"]

_IDEMPOTENT_METHODS = ["GET", "PUT", "DELETE", "HEAD", "OPTIONS"] # HTTP/1.1


class FlaskLambda(Flask):
    def __call__(self, event, context):
        """ Compatibility layer to dispatch a request using a test client and
        data provided by AWS Lambda. This layer will still allows for requests
        to be dispatched through Flask's built-in request dispatch system.

        :param event: Data sent by user or a WSGI environment
        :param context: AWS Lambda data or a callable accepting a status code,
                        a list of headers and an optional exception context to
                        start the response
        """
        if not context.__dict__.get('function_name'):
            return super(FlaskLambda, self).__call__(event, context)

        method, rule = context.__dict__['function_name'].split('_', 1)
        rule = ''.join(['/', rule.replace("_", "/"), '/'])
        method = method.lower()

        with self.test_client() as client:
            return self.make_response(getattr(client, method)(
                rule, follow_redirects=True,
                **{'query_string' if method in _IDEMPOTENT_METHODS else "data": event})
            ).get_data(as_text=True)
