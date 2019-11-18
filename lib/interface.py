import config

class Interface(object):

    def do_SEARCH(self, qs):
        return (200, 'text/html', str(qs))
