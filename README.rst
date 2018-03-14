Flask-Lambda2
=============

Flask-Lambda2 is a python package to add a compatibility layer between a
Flask application and AWS Lambda for creating RESTful applications.

This package is `opinionated <https://stackoverflow.com/questions/802050/what-is-opinionated-software>`_, in that "it locks or guides you into [our] way of doing things" or "doesn't make it easy to diverse from [our] golden path."

Installation
============

.. code:: bash

    $ pip install flask-lambda2 

Requirements
------------

The main assumption here is that your project can comfortably and reasonably fit into a single endpoint, or you separate your Lambda functions to group certain, related API endpoints together.

Firstly, ensure your Lambda `handler` is set to `project_api.app`, where `project_api` is the filename (excluding the `.py` extension) containing your project's API endpoint implementations and where `app` is the Flask instance (actually a `FlaskLambda` instance) with which you have added the URL rules onto.

Lastly, ensure that invokation convention from the location you plan to invoke the endpoints from roughly follows the calling convention shown below:

.. code:: python

    import boto3


    client = boto3.client('lambda')
    client.invoke(FunctionName='project_api',
                  InvocationType='RequestResponse',
                  Payload=json.dumps({'route':'/users/',
                                      'method':'get',
                                      'token':'123abc'}))


That's it!


Tests
-----

Tests are available in ``Flask-Lambda2/tests`` through invoking
``test.py`` with ``python test.py``. Ensure all dependencies are
installed through invoking ``pip install -r requirements.txt``.

Functional Examples
-------------------

GridLight-API
~~~~~~~~~~~~~

I have created a backend for a mobile application using this library,
it's source code is available `here at the GridLight-API
repository <https://github.com/seanpianka/GridLight-API>`__.

If you have any questions, feel free to e-mail me at pianka@eml.cc.


Built With
----------

-  `Flask <https://github.com/pallets/flask>`__ - Micro web-framework
   based on Werkzeug and Jinja2


License
-------

This project is licensed under the Apache 2.0 License - see the
LICENSE.md file for details
