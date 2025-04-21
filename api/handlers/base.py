from json import dumps, loads
from tornado.web import RequestHandler

class BaseHandler(RequestHandler):

    # Shortcut to access MongoDB instance
    @property
    def db(self):
        return self.application.db

    # shortcut to access the thread executor
    @property
    def executor(self):
        return self.application.executor

    # Initialise empty response dictionary for each request
    def prepare(self):
        self.response = dict()

    # set CORS and content-type header
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header('Access-Control-Allow-Headers', '*')

    # respond with error message in JSON
    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'
        self.response = kwargs
        self.write_json()

    # serialise and send JSON response
    def write_json(self):
        output = dumps(self.response)
        self.write(output)

    # handle CORS preflight requests
    def options(self):
        self.set_status(204)
        self.finish()

    # duplicate prepare (likely override safety)
    def prepare(self):
        self.response = {}

    # redefined write_json to ensure content-type header is set
    def write_json(self):
        output = dumps(self.response)
        self.set_header("Content-Type", "application/json")
        self.write(output)

    # alternate write_error pattern with default fallback
    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.response = {
            'error': kwargs.get('message', 'Unknown Error')
        }
        self.write_json()
