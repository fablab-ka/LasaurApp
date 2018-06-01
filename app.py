from __future__ import print_function

import argparse
import copy
import glob
import json
import os.path
import time
import threading

import bottle
import configparser
import serial
from beaker.middleware import SessionMiddleware
from bottle import *
from ldap3 import Connection, ALL_ATTRIBUTES
from serial import SerialException

import datedecoder
from filereaders import read_svg, read_dxf, read_ngc
from interface.interface import ExtInterface
from serial_manager import SerialManagerClass

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)
bottle.BaseRequest.MEMFILE_MAX = 20 * 1024 * 1024  # 20MB max upload

config = configparser.RawConfigParser()
config.read("config.ini")
#print("Sleeping for 5s...")
#time.sleep(5) #ToDo uncomment

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
        except IOError:
            pass
        time.sleep(0.1)


def tick():
        SerialManager.send_queue_as_ready()
        time.sleep(0.0004)


def start():
    SerialManager.connect(config['machine']['port'], config['machine']['port'])

    if config['sensors']['use'] and not dummy_mode:
        try:
            sensor_serial = serial.Serial(config['sensors']['port'], config['sensors']['baud'], timeout=1)
            time.sleep(1)
            sensor_serial.flushInput()
            threading.Thread(target=check_sensors).start()
            print("Connected to sensor board!")
        except(SerialException):
            sensor_serial = None
            print("Unable to connect to sensor board!")

    threading.Thread(target=tick).start()


@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


@route('/static/<path:path>')
def static_file_handler(path):
    path = "static/" + path
    print(path)
    return static_file(path, root=".") #ToDo fix


### LIBRARY

@route('/library/get/:path#.+#')
def static_library_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'library'), mimetype='text/plain')


@route('/library/list')
def library_list_handler():
    # return a json list of file names
    file_list = []
    # cwd_temp = os.getcwd()
    # try:
    #     os.chdir(os.path.join(resources_dir(), 'library'))
    #     file_list = glob.glob('*')
    # finally:
    #     os.chdir(cwd_temp)
    return json.dumps(file_list)


### QUEUE

def encode_filename(name):
    str(time.time()) + '-' + base64.urlsafe_b64encode(name)


def decode_filename(name):
    index = name.find('-')
    return base64.urlsafe_b64decode(name[index + 1:])


@route('/accounting')
def accounting():
    return json.dumps(SerialManager.job_accounting)


@route('/jobs/history')
def jobs_history():
    jobs = SerialManager.lastJobs
    if "limit" in request.params.keys():
        limit = int(request.params["limit"])
        jobs = jobs[:limit]
    return json.dumps(jobs, default=datedecoder.default)


@route('/interface/getData')
def erp_get_data():
    data = json.dumps(interface.get_info(), default=datedecoder.default)
    print(data)
    return data

@route('/interface/setData', method='POST')
def erp_set_data():
    data = json.loads(request.body.read())
    SerialManager.job_additional_data = data


@route('/material/services')
def material_services():
    return json.dumps(erp.services, default=datedecoder.default)


@route('/material/products')
def material_products():
    return json.dumps(erp.materials, default=datedecoder.default)

sensor_values = ""

@route('/sensors')
def get_sensors():
    return sensor_values

@post('/checkLogin')
def checkLogin():
    return "true"

@route('/login', method='POST')
def login():
    login_email = request.forms.get('login_email')
    login_password = request.forms.get('login_password')
    if not login_email:
        return "Email missing"
    if not login_password:
        return "Password missing"

    ldapAdmin = Connection(server=config['ldap']['server'],
                          user=config['ldap']['bind_dn'],
                          password=config['ldap']['password'],
                          auto_bind=True)
    users = ldapAdmin.search(search_base=(config['ldap']['users'] + "," + config['ldap']['base']),
                     search_filter="(&(objectClass=inetOrgPerson)(|(mail={0})(uid={0})))".format(login_email),
                     attributes=ALL_ATTRIBUTES)
    if len(users) != 1:
        return "User not found!"
    user_dn = users[0]['dn']
    try:
        Connection(server=config['ldap']['server'],
                   user=user_dn,
                   password=login_password,
                   auto_bind=True)
    except ldap3.core.exceptions.LDAPBindError:
        return warning("Password not valid!")

    request.session['user'] = users[0]['attributes']['mail'][0] #ToDo set to uid when new DB is online
    return "true"

@route('/logout')
def logout():
    if 'user' in request.session:
        del request.session['user']


@route('/')
@route('/index.html')
@route('/app.html')
def default_handler():
    return template("static/app.html")


@route('/stash_download', method='POST')
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


@route('/download/:filename/:dlname')
def download(filename, dlname):
    print("requesting: " + filename)
    return static_file(filename, root=tempfile.gettempdir(), download=dlname)


@route('/serial/:connect')
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


@route('/status')
def get_status():
    status = copy.deepcopy(SerialManager.get_hardware_status())
    status['serial_connected'] = SerialManager.is_connected()
    status['lasaurapp_version'] = "2.0"
    status['id_card_status'] = "access"
    return json.dumps(status)


@route('/pause/:flag')
def set_pause(flag):
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


@route('/reset_atmega')
def reset_atmega_handler():
    reset_atmega(HARDWARE)
    return '1'


@route('/gcode', method='POST')
def job_submit_handler():

    name = request.forms.get('name')
    job_data = request.forms.get('job_data')
    if job_data and SerialManager.is_connected():
        SerialManager.queue_gcode(job_data, name, erp.last_user)
        return "__ok__"
    else:
        return "serial disconnected"


@route('/queue_pct_done')
def queue_pct_done_handler():
    return SerialManager.get_queue_percentage_done()


@route('/file_reader', method='POST')
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
                res = read_svg(filedata, dimensions, float(config['machine']['tolerance']), dpi_forced, optimize)
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
        msg = "Failed to parse file: " + str(e.message)
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
    start()
else:
    start()

bottle.run(app=app, host='0.0.0.0', port=config['web']['port'], debug=True)