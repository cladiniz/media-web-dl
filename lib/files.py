from uuid import uuid4
from subprocess import Popen
from tempfile import gettempdir
from threading import Thread
from urlparse import urlparse
import os, json, time, re, config

class Files(object):

    def __init__(self, output):
        self.output = output
        self.downlist = []
        self.downlist_err = {}
        
    def add(self, qs, post):
        r = {'error': None}
        if 'url' not in post:
            r['error'] = 'Enter a valid URL address'
            self.output(r['error'], 'FILE', True)
        elif not os.access(config.DIR_DATA, os.W_OK):
            r['error'] = 'config.DIR_DATA is not writable'
            self.output(r['error'], 'FILE', True)
        else:
            uid = uuid4().hex[:10]
            rec = config.DIR_TEMP + '/' + uid
            std = rec + '-%s.txt'
            tpl = rec + '.%(ext)s'
            ydl_args = config.YDL_ARGS            
            try:
                ydl_args.extend(['-o', tpl, post['url']])
                with open(std % 'out', 'wb') as out, open(std % 'err', 'wb') as err:
                    popen = Popen(ydl_args, stdout = out, stderr = err)
            except Exception, error:
                r['error'] = str(error)
                self.output(r['error'], 'FILE', True)
            else:
                r['uid'] = uid
                self.downlist.append({
                    'data': None,
                    'down': [], 
                    'pid': popen.pid, 
                    'pla': post['pla'] if 'pla' in post else None, 
                    'uid': uid,
                    'url': post['url']
                })
                self.output('Starting download...')
        return r
                
    def video(self, qs):
        f = open(config.DIR_DATA + '/01.mp4', 'rb')
        fs = os.fstat(f.fileno())
        size = fs[6]
        start = 0
        end = size
        
        self.send_response(200)
        self.send_header('Content-type', 'video/mp4')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', 'bytes %s-%s/%s' % (start, end, size))
        self.send_header('Content-Length', str(size))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()

        self.wfile.write(f.read())

    def downlist_check(self):
        while True:
            for i in range(len(self.downlist)):
                    
                rec = config.DIR_TEMP + '/' + self.downlist[i]['uid']
                std = rec + '-%s.txt'
                err_exists = os.path.isfile(std % 'err')
                out_exists = os.path.isfile(std % 'out')
                json_exists = os.path.isfile(rec + '.info.json')

                #  Error exists
                if err_exists and os.path.getsize(std % 'err'):

                    err = open(std % 'err', 'r').read().strip()
                    self.downlist_err[self.downlist[i]['uid']] = err
                    self.output(self.extractor_name(i) + err, 'FILE', True)
                    self.downlist_del(i)
                    
                else:

                    #  Extract json data if it doesn't exist already
                    if not self.downlist[i]['data'] and json_exists:
                        json_src = open(rec + '.info.json')
                        self.downlist[i]['data'], self.downlist[i]['down'] = self.json_data_extract(json.load(json_src))
                        
                    #  Process Status
                    pstat = self.proc_by_pid(self.downlist[i]['pid'])

                    if not pstat or pstat == 'Z':
                        out_src = open(std % 'out', 'r').read() if out_exists else None
                        self.downlist_finish(i, out_src)

                    elif out_exists:
                        self.downlist_update(i, open(std % 'out', 'r').read())
                            
            time.sleep(5)

    def downlist_del(self, i):
        del self.downlist[i]

    def downlist_finish(self, i, out_src):
        self.output(self.extractor_name(i) + 'Finishing...')
        uid = self.downlist[i]['uid']
        dir_data = '/'. join((config.DIR_DATA, uid[0], uid[1]))
        if not os.path.exists(dir_data):
            os.makedirs(dir_data, '0755')

        if os.access(dir_data, os.W_OK):

            #  Main file
            file_src = None
            extension = self.downlist[i]['data']['extension']
            file_src_test = [uid, uid + '.' + extension]

            #  ffmpeg merging mainly for youtube files
            #  will have different extensions most times
            merge = re.search(r"Merging formats into \"%s/(.*)\"" % config.DIR_TEMP,
                              out_src, re.MULTILINE)
            if merge:
                file_src_test.append(merge.group(1))
                
            for fst in file_src_test:
                if os.path.isfile(config.DIR_TEMP + '/' + fst):
                    file_src = fst

            #  Thumbnail
            thumbnail_src = None
            for thumb_ext in ('jpg', 'png', 'gif'):
                if os.path.isfile('%s/%s.%s' % (config.DIR_TEMP, uid, thumb_ext)):
                    thumbnail_src = '%s.%s' % (uid, thumb_ext)

            if file_src:
                self.output(self.extractor_name(i) + ' ' + file_src)
                self.output(self.extractor_name(i) + ' ' + thumbnail_src)
            else:
                self.output(self.extractor_name(i) + 'Couldn\'t access main file.', 'FILE', True)
            
        else:
            self.output(self.extractor_name(i) + 'Couldn\'t access the filesystem to write.', 'FILE', True)

        #  Remove
        self.downlist_del(i)

    def downlist_update(self, i, out_src):
        lines = out_src.splitlines()
        num_lines = len(lines)

        if num_lines > 0:
            
            last_line = lines[num_lines - 1].strip()

            if self.downlist[i]['data'] and '[download]' in out_src:
                down_in = -1
                for line in lines:
                    if 'Destination:' in line:
                        down_in += 1
                    elif '[download]' in line:
                        down_line = line.replace('[download]', '').strip()
                        self.downlist[i]['down'][down_in] = down_line
                down_msg = '[%i/%i] %s' % (down_in + 1, len(self.downlist[i]['down']), down_line)
                self.output(self.extractor_name(i) + down_msg)

            else:
                self.output(self.extractor_name(i) + last_line)

        else:       
            self.output(self.extractor_name(i) + 'Working...')

    def extractor_name(self, i):
        try:
            return '[' + self.downlist[i]['data']['extractor_key'] + '] '
        except:
            return ''

    def json_data_extract(self, json):
        data = {}
        check = ('title', 'thumbnail', 'description', 'categories',
                 'duration', 'extractor', 'width', 'height', 'resolution',
                 'fps', 'ext', 'age_limit', 'extractor_key')
        
        for c in check:
            if c in json:
                data[c] = json[c]

        #  Number of chunks
        if 'format_id' in json and '+' in json['format_id']:
            down = [None] * len(json['format_id'].split('+'))
        else:
            down = [None]
            
        return data, down

    def proc_by_pid(self, pid):
        if os.name == 'posix':
            proc_src = '/proc/%d/status' % pid 
            if os.path.isfile(proc_src):
                with open(proc_src) as lines:
                    for line in lines:
                        if line.startswith('State:'):
                            return line.split(':', 1)[1].strip().split(' ')[0]
        return None
