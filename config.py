import sys, tempfile

#  Webserver host and port
HTTP_HOST = 'localhost'
HTTP_PORT = 8080

#  DIR_RES is the location of the html, js and css files
#  DIR_DATA is where all the files will be stored, as well SQLITE files
#  DIR_TEMP is the temporary folder, gettempdir() as default
DIR_RES = '%s/res' % sys.path[0]
DIR_DATA = '%s/data' % sys.path[0]
DIR_TEMP = tempfile.gettempdir()

#  Parental lock password
#  if no password is set, parental lock will be disabled
PLOCK = False

#  Youtube-dl and ffmpeg location
YDL_LOCATION = '/usr/bin/youtube-dl'

#  Maximum download rate in bytes per second
#  e.g. 50K or 4.2M
YDL_RATE = None

#  Encode the video to another format if necessary
#  currently supported: mp4|flv|ogg|webm|mkv|avi
YDL_RECODE = False

#  Number of retries
#  default is 10, or "infinite"
YDL_RETRIES = 3

#  youtubedl arguments
YDL_ARGS = [
    YDL_LOCATION,
    '--abort-on-error', 
    '--no-color',
    '--newline',
    '--no-warnings', 
    '--no-playlist',
    '--no-overwrites', 
    '--restrict-filenames',
    '--write-info-json',
    '--write-thumbnail',
    '--prefer-ffmpeg',
    '--no-call-home',
    '--retries',
    str(YDL_RETRIES)
]

if YDL_RATE:
    YDL_ARGS.extend(['--limit-rate', YDL_RATE])

if YDL_RECODE:
    YDL_ARGS.extend(['--recode-video', YDL_RECODE])

FILES = {
    'layout.html': 'text/html',
    'style.css': 'text/css',
    'script.js': 'text/javascript'
}
