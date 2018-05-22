from __future__ import print_function

import argparse
import copy
import glob
import os.path
import uuid
import webbrowser

from datetime import datetime
import bottle
import i18n
import readid
import serial
from backend.interface.odoo.odooHelper import *
from backend.interface.odoo.odoo import Odoo
from bottle import *
from build import build_firmware
from filereaders import read_svg, read_dxf, read_ngc
import datedecoder
from flash import flash_upload, reset_atmega
from serial import SerialException
from serial_manager import SerialManagerClass
import json
import DebugHelper
import signal
import time
from thread import start_new_thread
from beaker.middleware import SessionMiddleware
import configparser
from interface.interface import ExtInterface

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)
bottle.BaseRequest.MEMFILE_MAX = 20 * 1024 * 1024  # 20MB max upload

print("loading config file", configfile)
config = configparser.RawConfigParser()
config.read("config.ini")
print("Sleeping for 5s...")
time.sleep(5)

SerialManager = SerialManagerClass(config['accounting']['log_file'], config['machine']['influx'], False)

sensor_serial = None
dummy_mode = False
interface = ExtInterface()

def setDummyMode():
    global SerialManager
    SerialManager.dummyMode = True
    global dummy_mode
    dummy_mode = True


def check_sensors():
    while True:
        try:
            global sensor_serial, sensor_values
            str = sensor_serial.readline(1000)
            if str != "":
                sensor_values = str.rstrip().replace("'", '"')
        except IOError, NameError:
            pass
        time.sleep(0.1)


def resources_dir():
    """This is to be used with all relative file access.
       _MEIPASS is a special location for data files when creating
       standalone, single file python apps with pyInstaller.
       Standalone is created by calling from 'other' directory:
       python pyinstaller/pyinstaller.py --onefile app.spec
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        # root is one up from this file
        return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))


def storage_dir():
    directory = os.path.join(os.path.expanduser('~'), "." + "lasaurapp")

    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def tick():
        SerialManager.send_queue_as_ready()
        server.handle_request()
        time.sleep(0.0004)


def start():
    print("Persistent storage root is: " + storage_dir())
    SerialManager.connect(config['machine']['port'], config['machine']['port'])

    if config['sensors']['use'] and not dummy_mode:
        try:
            sensor_serial = serial.Serial(config['sensors']['port'], config['sensors']['baud'], timeout=1)
            time.sleep(1)
            sensor_serial.flushInput()
            start_new_thread(check_sensors, ())
            print("Connected to sensor board!")
        except(SerialException):
            sensor_serial = None
            print("Unable to connect to sensor board!")
    start_new_thread(tick, ())


def has_valid_id():
    if not USE_ID_CARD_ACCESS_RESTRICTION:
        return True
    return True # Todo disable access when not loged in


@app.route('/css/:path#.+#')
def static_css_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/css'))


@app.route('/js/:path#.+#')
def static_js_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/js'))


@app.route('/img/:path#.+#')
def static_img_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/img'))


@app.route('/fonts/:path#.+#')
def static_img_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/fonts'))


@app.route('/favicon.ico')
def favicon_handler():
    return static_file('favicon.ico', root=os.path.join(resources_dir(), 'frontend/img'))


### LIBRARY

@app.route('/library/get/:path#.+#')
def static_library_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'library'), mimetype='text/plain')


@app.route('/library/list')
def library_list_handler():
    # return a json list of file names
    file_list = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(os.path.join(resources_dir(), 'library'))
        file_list = glob.glob('*')
    finally:
        os.chdir(cwd_temp)
    return json.dumps(file_list)


### ID

@app.route('/has_valid_id')
def has_valid_id_handler():
    return json.dumps(has_valid_id())

### QUEUE

def encode_filename(name):
    str(time.time()) + '-' + base64.urlsafe_b64encode(name)


def decode_filename(name):
    index = name.find('-')
    return base64.urlsafe_b64decode(name[index + 1:])


@app.route('/accounting')
def accounting():
    return json.dumps(SerialManager.job_accounting)


@app.route('/jobs/history')
def jobs_history():
    jobs = SerialManager.lastJobs
    if "limit" in request.params.keys():
        limit = int(request.params["limit"])
        jobs = jobs[:limit]
    return json.dumps(jobs, default=datedecoder.default)


@app.route('/interface/getData')
def erp_get_data():
    return json.dumps(interface.get_info(), default=datedecoder.default)

@app.route('/interface/setData', method='POST')
def erp_set_data():
    data = json.loads(request.body.read())
    SerialManager.job_additional_data = data


@app.route('/material/services')
def material_services():
    return json.dumps(erp.services, default=datedecoder.default)


@app.route('/material/products')
def material_products():
    return json.dumps(erp.materials, default=datedecoder.default)

sensor_values = ""

@app.route('/sensors')
def get_sensors(): #ToDO: Finish
    return sensor_values

@app.route('/checkLogin', method='POST')
def checkLogin():
    session_id = bottle.request.get_cookie('session_id')
    user_name = bottle.request.get_cookie('user_name')
    if not session_id or not user_name or len(session_info) < 1:
        bottle.response.delete_cookie('user_name')
        bottle.response.delete_cookie('session_id')
        return "false"
    info = None
    for item in session_info:
        if item['session_id'] == session_id:
            info = item
    if info is None:
        bottle.response.delete_cookie('user_name')
        bottle.response.delete_cookie('session_id')
        return "false"
    if info['user_name'] != user_name:
        bottle.response.delete_cookie('user_name')
        bottle.response.delete_cookie('session_id')
        return "false"
    return "true"


@app.route('/login', method='POST')
def login():
    login_email = request.forms.get('login_email')
    login_password = request.forms.get('login_password')  # TODO dont save plaintext passwords
    if not login_email:
        return "Email missing"
    if not login_password:
        return "Password missing"
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", login_email):
        return "Invalid Email entered!"
    helper = OdooHelper(login_email, login_password, ODOO_URL, ODOO_DB)
    if not helper.connected:
        return "Could not connect to Odoo, please contact philip@caroli.de!"
    else:
        uid = helper.callAPI('/machine_management/getCurrentUser')
    if not uid:
        return "Invalid Email or Password!"
    info = {
        'session_id': str(uuid.uuid4()),
        'odoo_uid': uid,
        'user_name': login_email,
        'last_login': datetime.now(),
    }
    session_info.append(info)
    with open("session_info.json", "w") as file:
        file.write(json.dumps(session_info, default=datedecoder.default))

    bottle.response.set_cookie('user_name', info['user_name'])
    bottle.response.set_cookie('session_id', info['session_id'])
    return "true"


@app.route('/queue/get/:name#.+#')
def static_queue_handler(name):
    return static_file(name, root=storage_dir(), mimetype='text/plain')


@app.route('/queue/list')
def library_list_handler():
    # base64.urlsafe_b64encode()
    # base64.urlsafe_b64decode()
    # return a json list of file names
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(storage_dir())
        files = filter(os.path.isfile, glob.glob("*"))
        files.sort(key=lambda x: os.path.getmtime(x))
    finally:
        os.chdir(cwd_temp)
    return json.dumps(files)


@app.route('/queue/save', method='POST')
def queue_save_handler():
    ret = '0'
    if 'job_name' in request.forms and 'job_data' in request.forms:
        name = request.forms.get('job_name')
        job_data = request.forms.get('job_data')
        filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
        if os.path.exists(filename) or os.path.exists(filename + '.starred'):
            return "file_exists"

        fp = None
        try:
            fp = open(filename, 'w')
            fp.write(job_data)
            print("file saved: " + filename)
            ret = '1'
        finally:
            if fp:
                fp.close()
    else:
        print("error: save failed, invalid POST request")
    return ret


@app.route('/queue/rm/:name')
def queue_rm_handler(name):
    # delete queue item, on success return '1'
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print("file deleted: " + filename)
                ret = '1'
            finally:
                pass
    return ret


@app.route('/queue/clear')
def queue_clear_handler():
    # delete all queue items, on success return '1'
    ret = '0'
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(storage_dir())
        files = filter(os.path.isfile, glob.glob("*"))
        files.sort(key=lambda x: os.path.getmtime(x))
    finally:
        os.chdir(cwd_temp)
    for filename in files:
        if not filename.endswith('.starred'):
            filename = os.path.join(storage_dir(), filename)
            try:
                os.remove(filename)
                print("file deleted: " + filename)
                ret = '1'
            finally:
                pass
    return ret


@app.route('/queue/star/:name')
def queue_star_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            os.rename(filename, filename + '.starred')
            ret = '1'
    return ret


@app.route('/queue/unstar/:name')
def queue_unstar_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename + '.starred'):
            os.rename(filename + '.starred', filename)
            ret = '1'
    return ret


@app.route('/')
@app.route('/index.html')
@app.route('/app.html')
def default_handler():
    filename = os.path.join(os.path.join(resources_dir(), 'frontend', 'app.html'))
    return template(filename, list(I18N))


@app.route('/stash_download', method='POST')
def stash_download():
    """Create a download file event from string."""
    filedata = request.forms.get('filedata')
    fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    filename = fp.name
    with fp:
        fp.write(filedata)
        fp.close()
    print(filedata)
    print("file stashed: " + os.path.basename(filename))
    return os.path.basename(filename)


@app.route('/download/:filename/:dlname')
def download(filename, dlname):
    print("requesting: " + filename)
    return static_file(filename, root=tempfile.gettempdir(), download=dlname)


@app.route('/serial/:connect')
def serial_handler(connect):
    if connect == '1':
        # print 'js is asking to connect serial'
        if not SerialManager.is_connected():
            try:
                global SERIAL_PORT, BITSPERSECOND, GUESS_PREFIX
                if not SERIAL_PORT:
                    SERIAL_PORT = SerialManager.match_device(GUESS_PREFIX, BITSPERSECOND)
                SerialManager.connect(SERIAL_PORT, BITSPERSECOND)
                ret = "Serial connected to %s:%d." % (SERIAL_PORT, BITSPERSECOND) + '<br>'
                time.sleep(1.0)  # allow some time to receive a prompt/welcome
                SerialManager.flush_input()
                SerialManager.flush_output()
                return ret
            except SerialException:
                SERIAL_PORT = None
                print("Failed to connect to serial.")
                return ""
    elif connect == '0':
        # print 'js is asking to close serial'
        if SerialManager.is_connected():
            if SerialManager.close():
                return "1"
            else:
                return ""
    elif connect == "2":
        # print 'js is asking if serial connected'
        if SerialManager.is_connected():
            return "1"
        else:
            return ""
    else:
        print('ambigious connect request from js: ' + connect)
        return ""


@app.route('/status')
def get_status():
    status = copy.deepcopy(SerialManager.get_hardware_status())
    status['serial_connected'] = SerialManager.is_connected()
    status['lasaurapp_version'] = VERSION
    status['has_valid_id'] = has_valid_id()
    status['id_card_status'] = "access"
    return json.dumps(status)


@app.route('/pause/:flag')
def set_pause(flag):
    if not has_valid_id():
        return '0'

    # returns pause status
    if flag == '1':
        if SerialManager.set_pause(True):
            print("pausing ...")
            return '1'
        else:
            return '0'
    elif flag == '0':
        print("resuming ...")
        if SerialManager.set_pause(False):
            return '1'
        else:
            return '0'


@app.route('/reset_atmega')
def reset_atmega_handler():
    reset_atmega(HARDWARE)
    return '1'


@app.route('/gcode', method='POST')
def job_submit_handler():
    if not has_valid_id():
        print("cancel gcode post request because no valid ID is inserted")
        return "no_id"

    name = request.forms.get('name')
    job_data = request.forms.get('job_data')
    if job_data and SerialManager.is_connected():
        SerialManager.queue_gcode(job_data, name, erp.last_user)
        return "__ok__"
    else:
        return "serial disconnected"


@app.route('/queue_pct_done')
def queue_pct_done_handler():
    return SerialManager.get_queue_percentage_done()


@app.route('/file_reader', method='POST')
def file_reader():
    print("/file_reader invoked")
    """Parse SVG string."""
    filename = request.forms.get('filename')
    filedata = request.forms.get('filedata')
    dimensions = request.forms.get('dimensions')
    try:
        dimensions = json.loads(dimensions)
    except TypeError:
        dimensions = None
    # print "dims", dimensions[0], ":", dimensions[1]


    dpi_forced = None
    try:
        dpi_forced = float(request.forms.get('dpi'))
    except:
        pass

    optimize = True
    try:
        optimize = bool(int(request.forms.get('optimize')))
    except:
        pass

    print("  checkes done")

    try:
        if filename and filedata:
            print("You uploaded %s (%d bytes)." % (filename, len(filedata)))
            if filename[-4:] in ['.dxf', '.DXF']:
                res = read_dxf(filedata, TOLERANCE, optimize)
            elif filename[-4:] in ['.svg', '.SVG']:
                print("parsing svg")
                res = read_svg(filedata, dimensions, TOLERANCE, dpi_forced, optimize)
            elif filename[-4:] in ['.ngc', '.NGC']:
                res = read_ngc(filedata, TOLERANCE, optimize)
            else:
                print("error: unsupported file format")
                return None

            # print boundarys
            jsondata = json.dumps(res)
            # print "returning %d items as %d bytes." % (len(res['boundarys']), len(jsondata))
            return jsondata
    except Exception as e:
        msg = "Failed to parse file" + e.message
        print(msg)
        return msg
    return "You missed a field."


### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run LasaurApp.', prog='lasaurapp')
argparser.add_argument('--dummy', dest='dummy', action='store_true',
                       default=False, help='use this for developing without hardware')
args = argparser.parse_args()

if args.dummy or config.get("dummy_mode", False):
    print("starting in Dummy Mode")
    setDummyMode()
else:
    # run
    if args.debug:
        debug(True)
        if hasattr(sys, "_MEIPASS"):
            print("Data root is: " + sys._MEIPASS)
    else:
            start()
            bottle.run(app=app, host='0.0.0.0', port=config['web']['port'])