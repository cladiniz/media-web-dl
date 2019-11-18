from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urlparse import urlparse, parse_qsl
from random import choice
from subprocess import Popen
import json, config
from lib import interface

class Http(BaseHTTPRequestHandler, interface.Interface):
   
    def data_get(self):
        d = urlparse(self.path)
        postvars = {}
        if self.command == 'POST':
            ctype, pdict = parse_header(self.headers['content-type'])
            length = int(self.headers['content-length'])
            postvars = dict(parse_qsl(self.rfile.read(length)))
        return {
            'path': 'layout.html' if d.path == '/' else d.path[1:],
            'post': postvars, 
            'qs': dict(parse_qsl(d.query))
        }

    def do_ADD(self, qs, post):
        self.json_send(self.files.add(qs, post))
  
    def do_GET(self):
        data = self.data_get()
        if data['path'] in config.FILES:
            self.file_serve(data['path'])
        elif hasattr(self, 'do_' + data['path'].upper()):
            getattr(self, 'do_' + data['path'].upper())(data['qs'])
        else:
            self.send_error(404, 'Not Found')

    def do_POST(self):
        data = self.data_get()
        if hasattr(self, 'do_' + data['path'].upper()):
            getattr(self, 'do_' + data['path'].upper())(data['qs'], data['post'])
        else:
            self.send_error(404, 'Not Found')
      
    def file_serve(self, path):
        """Serves the HTML, JS and CSS files""" 
        dir_path = config.DIR_RES + '/' + path
        try:
            f = open(dir_path)
            output = f.read()
            f.close()
            r = (200, config.FILES[path], output)
        except IOError:
            r = (404, 'text/html', path + ' not found')
        self.send_response(r[0])
        self.send_header('Content-type', r[1])
        self.end_headers()
        self.wfile.write(r[2])

    def json_send(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data))
        
    def log_message(self, format, *args):
        self.output(
            '%s %s %s' % (self.address_string(), args[0], args[1]),
            'HTTP', 
            False if args[1] == '200' else True
        )
