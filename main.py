#!/usr/bin/python2.7
import time
from BaseHTTPServer import HTTPServer
from cmd import Cmd
from threading import Thread
import config
from lib import http, files

class YoutubedlWeb(Cmd, object):

    colors = {'bold': '\033[1m', 'end': '\033[0m', 'red': '\033[91m'}
    intro = 'Welcome! Type ? to list commands'
    prompt = ''
    
    def __init__(self):
        super(YoutubedlWeb, self).__init__()
        try:
            self.files_start()
            self.http_start()
        except Exception as e:
            self.__exit__()
            print str(e)
        except KeyboardInterrupt, SystemExit:
            self.__exit__()

    def __exit__(self):
        pass

    def do_download(self, line):
        """Download media file from [url]\nUsage: download [url]"""
        if line:
            self.files.add(None, {'url': line})
        else:
            self.output('Enter a valid URL address', 'FILE', True)

    def do_search(self, line):
        """Search the database\nUsage: search [arg]"""
        print line

    def do_stats(self, line):
        """Gives some statistics about the files and database\nUsage: stats"""
        print line
        
    #  Start the file check thread (run before the http)
    def files_start(self):
        self.files = files.Files(self.output)
        self.dl_thread = Thread(target = self.files.downlist_check, name = 'dl')
        self.dl_thread.daemon = True
        self.dl_thread.start()
        self.output('File daemon started with success', 'FILE')
       
    #  Start the http server thread
    def http_start(self):        
        http_server = http.Http        
        http_server.output = self.output
        http_server.files = self.files        
        self.http = HTTPServer((config.HTTP_HOST, config.HTTP_PORT), http_server)
        self.http_thread = Thread(target = self.http.serve_forever, name = 'http')
        self.http_thread.daemon = True
        self.http_thread.start()
        self.output('HTTP server started with success', 'HTTP')

    #  Output a message
    def output(self, msg, typep = 'FILE', error = False):
        msg_f = time.strftime('%H:%M:%S') + self.colors['bold'] + ' [' + typep + '] '
        if error:
            msg_f +=  self.colors['red'] + '[ERROR] ' + self.colors['end'] 
        msg_f += self.colors['end'] + msg
        print(msg_f)
       
if __name__ == '__main__':
    YoutubedlWeb().cmdloop()
