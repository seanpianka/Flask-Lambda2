Flask-Lambda2
=============

Flask-Lambda2 is a python package to add a compatibility layer between a
Flask application and AWS Lambda for creating RESTful applications.

Explanation
-----------

The main assumption is that the lambda function, on the AWS Lambda
dashboard, must be named with the following scheme:

::

    httpMethod_route_to_desired_endpoint

This scheme translates to the HTTP statement:

::

    HTTPMETHOD /route/to/desired/endpoint

Which then propagates to the following Flask endpoint:

::

    app.route('/route/to/desired/endpoint/', methods=["HTTPMETHOD"])

This is a *convention* and it is assumed that users of this class will
follow the outlined convention. Behavior during use while deviating from
the required convention is undefined -- as in it likely will not work
:).

Getting Started
---------------

We will create an endpoint named ``get_users``; this is a endpoint which
theoretically can be accessed via the HTTP request ``GET /users/``
(however, it must be accessed in a manner compliant with AWS Lambda's
calling convention).

Steps
~~~~~

1. .. rubric:: Locally clone ``Flask-Lambda2`` via:
      :name: locally-clone-flask-lambda2-via

   ``git clone https://github.com/seanpianka/Flask-Lambda2 && mv Flask-Lambda2/flask_lambda2/ . && rm -rf Flask-Lambda2/``

   or

   ``pip install -t . flask-lambda2`` (**Note**: Flask-Lambda2 is
   currently not available on pip)

2. .. rubric:: Create AWS Lambda function with name ``get_users``.
      :name: create-aws-lambda-function-with-name-get_users.

   **Note**: The HTTP method at the beginning of the name can any
   capitalization, but it will be transformed to lowercase. However, the
   "\_route\_to\_desired\_endpoint" string and its capitalization matter
   as that's what will be exactly translated into a URL rule.
3. .. rubric:: Create a local file named ``get_users.py`` that contains
      the following boilerplate:
      :name: create-a-local-file-named-get_users.py-that-contains-the-following-boilerplate

   .. code:: python

       from flask_lambda2 import FlaskLambda

       app = FlaskLambda(__name__)

       app.route('/users/', methods=["GET"]) # ensure `methods` match the method specified by the lambda function name
       def get_users():                      # function identifier is irrelevant to functionality
           return {'message': 'Hello, World!', 'status_code': 200}

4. .. rubric:: Package Flask-Lambda2 along with ``get_users.py`` into a
      zip (which we name ``get_users.py.zip``):
      :name: package-flask-lambda2-along-with-get_users.py-into-a-zip-which-we-name-get_users.py.zip

   .. code:: bash

       $ zip --recurse-paths get_users.py.zip get_users.py flask-lambda2/

5. .. rubric:: Use either ``aws-cli`` or the web interface for AWS
      Lambda to upload the zip:
      :name: use-either-aws-cli-or-the-web-interface-for-aws-lambda-to-upload-the-zip

   1. Create a new AWS Lambda function:
      ``aws lambda create-function --function-name get_users --runtime python3.6 --zip-file fileb://get_users.py.zip --role user_supplied_aws_role_here --handler get_users.app``

      1. ``--handler get_users.app`` implies that:

         1. The single Python file you're uploading is named
            ``get_users``
         2. The instance of the ``FlaskLambda`` class is named ``app``,
            like: ``app = FlaskLambda()`` If this line was changed to
            ``application = FlaskLambda``, then the ``handler`` flag
            should be given as ``--handler get_users.application``.

      2. You will need to create your own AWS execution/IAM role, see
         `this
         link <https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-create-iam-role.html>`__
         for more details. Afterwards, specify this role as
         ``--role arn:aws:iam::###:role/iam_role_name``.
      3. Once you've created your AWS Lambda function, you can update
         the zipped code with:
         ``aws lambda update-function-code --function-name get_users --zip-file fileb://get_users.py.zip``

6. .. rubric:: Use the appropriate method for invoking your AWS Lambda
      function for your platform.
      :name: use-the-appropriate-method-for-invoking-your-aws-lambda-function-for-your-platform.

Deployment
----------

Here's an example ``makefile`` that you can use for deploying your
functions.

.. code:: makefile

    ZIP_ALL_ROUTES=sh -c '\
    rm *.zip; \
    cd libs; \
    for i in ../*.py; \
    do \
        zip -r $$i.zip $$i * > /dev/null 2>&1; \
        echo "Zipped $$i"; \
    done; \
    cd ..;'

    default: zip

    zip:
        $(ZIP_ALL_ROUTES)

    clean:
        @rm *.zip
        @echo "Cleaned: *"

    update-all-functions: # make update-all-functions
        $(ZIP_ALL_ROUTES)
        @for i in *.zip; do \
            func_name=$$(python -c "print(\"$$i\".split(\".\")[0])"); \
            aws lambda update-function-code --function-name $$func_name --zip-file fileb://$$i > /dev/null 2>&1; \
            echo "Updated: $$i"; \
        done

    update-function: # make update-function FUNC=get_users
        @cd libs && \
         zip -r ../$$FUNC.py.zip ../$$FUNC.py * > /dev/null 2>&1 && \
         echo "Zipped: $$FUNC" && \
         aws lambda update-function-code --function-name $$FUNC --zip-file fileb://../$$FUNC.py.zip > /dev/null 2>&1;
        @echo "Updated: $$FUNC";

    set-environment-vars: # requires env_vars.txt to be in current working directory and to be in JSON format, see aws-cli documentation for update-function configuration
        $(ZIP_ALL_ROUTES)
        @for i in *.zip; do \
            func_name=$$(python -c "print(\"$$i\".split(\".\")[0])"); \
            aws lambda update-function-configuration --function-name $$func_name --environment $$(<env_vars.txt) > /dev/null 2>&1; \
            echo "Updated: $$i"; \
        done

The following ``makefile`` expects a directory structure as follows:

::

    .
    ├── get_users.py
    ├── libs
    │   ├── click
    │   ├── click-6.7.dist-info
    │   ├── flask
    │   ├── Flask-0.12.2.dist-info
    │   ├── flask_lambda2
    │   ├── itsdangerous-0.24.dist-info
    │   ├── itsdangerous.py
    │   ├── jinja2
    │   ├── Jinja2-2.9.6.dist-info
    │   ├── markupsafe
    │   ├── MarkupSafe-1.0.dist-info
    │   ├── werkzeug
    │   └── Werkzeug-0.12.2.dist-info
    └── makefile

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
Additionally, I have created a ``makefile`` that optimizes the
deployment process of the routes to AWS CLI.

If you have any questions, feel free to e-mail me at pianka@eml.cc.

Translation Examples
--------------------

Route: get\_users -> GET /users/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. | Lambda Function Name:
   | ``get_users``

2. | HTTP Translation:
   | ``GET /users/``

3. | Flask Propogation:
   | ``app.route('/users/', methods=["GET"])``

Route: post\_users\_contracts -> POST /users/contracts/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. | Lambda Function Name:
   | ``post_users_contracts``

2. | HTTP Translation:
   | ``POST /users/contracts/``

3. | Flask Propogation:
   | ``app.route('/users/contracts/', methods=["POST"])``

Route: delete\_users\_contracts\_id -> DELETE /users/contracts/<id>/
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Lambda Function Name:
   ``delete_users_contracts_id``
2. HTTP Translation:
   ``DELETE /users/contracts/<id>/``
3. Flask Propogation:
   ``app.route('/users/contracts/<id>/', methods=["DELETE"])``

Built With
----------

-  `Flask <https://github.com/pallets/flask>`__ - Micro web-framework
   based on Werkzeug and Jinja2

License
-------

This project is licensed under the Apache 2.0 License - see the
LICENSE.md file for details
