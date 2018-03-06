import nmap, logging
import paho.mqtt.client as mqtt
import socket
import time
from json import dumps
import requests
logger = logging.getLogger()
# this is used to determine the actuators on the network
criteria = [
    {
        'mac':'AC:CF:23',
        'type':'Lights',
        'functions': ['allLightsOn','allLightsOff','g1LightsOn','g1LightsOff','g2LightsOn','g2LightsOff','g3LightsOn','g3LightsOff']
    },
    {
        'message':'HELLOKETTLE\n',
        'expected_reply':'HELLOAPP\r',
        'port':2000,
        'type':'Kettle',
        'functions': ['turnOn','turnOff','set100C','set95C','set80C','set65C','setWarm']
    },
    {
        'message': 'hello',
        'expected_reply': 'hello',
        'type': 'Plug',
        'port':2000,
        'request_type': 'get',
        'functions': ['turn_on_plug', 'turn_off_plug', 'toggle_plug', 'get_plug_state']
    }
]
def scan(s):
    #myIp = socket.gethostbyname(socket.gethostname()) # doesnt work on pi
    actuators = []
    # show all iOS devices in ip range
    for ip in s["scan"]:
        currentGuess = None
        mac = None
        try:
            if 'tcp' in s["scan"][ip]:
                if 'mac' in s["scan"][ip]['addresses']:
                    mac = s["scan"][ip]['addresses']['mac'] # get mac address
                else:
                    mac = ""
                for target in criteria:
                    if('mac' in target.keys() and mac.startswith(target['mac'])):
                        obj = {}
                        obj['type'] = target['type']
                        obj['ip'] = ip
                        obj['mac'] = mac
                        actuators.append(obj)
                    if("port" in target.keys() and target["port"] in s['scan'][ip]['tcp']):
                        if(verify_plug(ip,target["request_type"],target["message"], target["expected_reply"])):
                            obj = {}
                            obj['type'] = 'Plug'
                            obj['ip'] = ip
                            obj['mac'] = mac
                            actuators.append(obj)
                        elif(verify_connection(ip, target["port"], target['message'], target['expected_reply'])):
                            obj = {}
                            obj['type'] = "Kettle"
                            obj['ip'] = ip
                            obj['mac'] = mac
                            actuators.append(obj)
            else:
                pass
        except Exception as e:
            logger.error(e)
        for act in actuators:
            for crit in criteria:
                if crit['type'] == act['type']:
                    act['functions'] = crit['functions']
    actuators.append(getVirtualActuators())
    return actuators

def getVirtualActuators():
    return {'type':'notifications', 'ip':'localhost','mac':'NOTIFICATIONS', 'functions':['sendNotification'] }

def verify_connection(ip, port, message, expected_reply):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.settimeout(5) # wait for 5 seconds
        s.sendall(message)
        data = s.recv(1024)
        s.close()
        return data == expected_reply
    except Exception as e:
        logger.error(e)
        return False

# without expected reply
def send_message(ip, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(message.encode())
        s.close()
    except Exception as e:
        logger.error(e)

# ---- Kettle Functions ----
def findDevices():
        logger.debug("finding Devices")
        # nm = nmap.PortScanner()
        # s = []
        # logger.info("finished Devices scan doing parse")
        time.sleep(3)
        # s.append(getVirtualActuators())
        # return s
        # s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
        # return scan(s)
        return [
          {
          'type':'notifications',
          'ip':'localhost',
          'mac':'NOTIFICATIONS',
          'functions':['sendNotification']
          },
          {
          'type':'Kettle',
          'ip':'192.168.0.114',
          'mac':'CC:D2:9B:F4:41:2E',
          'functions': ['turnOn','turnOff','set100C','set95C','set80C','set65C','setWarm']
          },
          {
          'type':'Lights',
          'ip':'192.168.0.101',
          'mac':'AC:CF:23:28:C2:2C',
          'functions':['allLightsOn','allLightsOff','g1LightsOn','g1LightsOff','g2LightsOn','g2LightsOff','g3LightsOn','g3LightsOff']
          },
          {
          'type':'Plug',
          'ip':'192.168.0.108',
          'mac':'00:15:61:F1:83:DE',
          'functions':['turn_on_plug', 'turn_off_plug', 'toggle_plug', 'get_plug_state']
          },
        ];
def sendNotification(notifObj, msg):
    client = mqtt.Client()
    client.connect("sccug-330-02.lancs.ac.uk",1883,60)
    # token shouldn't be hardcoded
    json = {
    'type':'NOTIF',
    'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlNDQzMzMTAyX1IwMSJ9.XopN05KKB6am2sbuEl9kXPji-Z11bgxK8MdzAac1XPw',
    'payload':{"message":msg}
    }
    client.publish('SCC33102_R01', dumps(json))
    # time.sleep(30)
    client.disconnect()

def turnOn(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x4\n")

def turnOff(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x0\n")

def set100C(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x80\n")

def set95C(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x2\n\n")

def set80C(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x4000\n")

def set65C(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x200\n")

def setWarm(kettle):
    send_message(kettle['ip'], 2000, "set sys output 0x8\n")


# ---- Lights Functions ----

def allLightsOn(lights):
    send_message_lights("420",lights['mac'])

def allLightsOff(lights):
    send_message_lights("410",lights['mac'])

def g1LightsOn(lights):
    send_message_lights("450",lights['mac'])

def g1LightsOff(lights):
    send_message_lights("460",lights['mac'])

def g2LightsOn(lights):
    send_message_lights("470",lights['mac'])

def g2LightsOff(lights):
    send_message_lights("480",lights['mac'])

def g3LightsOn(lights):
    send_message_lights("490",lights['mac'])

def g3LightsOff(lights):
    send_message_lights("4a0",lights['mac'])

def send_message_lights(number, mac):
    send_message("178.62.58.245",38899, "APP#"+mac+'#CMD#'+number+'\n')
#APPAC:CF:23:28:C2:2C
#OKAC:CF:23:28:C2:2C

# ---- Plug Functions ----
def verify_plug(ip,request_type,message,expected_reply):
    try:
        r = requests.get('http://'+ip+'/cgi-bin/json.cgi?'+request_type+'='+message)
        content = r.text
        content = content[:len(content)-1]
        logger.debug(content)
        return expected_reply == content
    except Exception as e:
        logger.error(e)
        return False

# create objects??

def turn_on_plug(ip):
    requests.get('http://' + ip['ip'] + '/cgi-bin/json.cgi?set=on')

def turn_off_plug(ip):
    requests.get('http://' + ip['ip'] + '/cgi-bin/json.cgi?set=off')

def toggle_plug(ip):
    requests.get('http://' + ip['ip'] + '/cgi-bin/json.cgi?set=toggle')

def get_plug_state(ip):
    r = requests.get('http://' + ip['ip'] + '/cgi-bin/json.cgi?get=state')
    content = r.text
    content = content[:len(content) - 1]
    logger.info('Plug state: '+content)
    return content


ActuatorFunctions = {
"turnOn":turnOn,
"turnOff":turnOff,
"set100C":set100C,
"set95C":set95C,
"set80C":set80C,
"set65C":set65C,
"setWarm":setWarm,
"allLightsOn":allLightsOn,
"allLightsOff":allLightsOff,
"g1LightsOn":g1LightsOn,
"g1LightsOff":g1LightsOff,
"g2LightsOn":g2LightsOn,
"g2LightsOff":g2LightsOff,
"g3LightsOn":g3LightsOn,
"g3LightsOff":g3LightsOff,
"send_message_lights":send_message_lights,
"sendNotification":sendNotification,
"turn_on_plug":turn_on_plug,
"turn_off_plug":turn_off_plug,
"toggle_plug":toggle_plug,
"get_plug_state":get_plug_state,
}

if __name__ == '__main__':
    # send_message_lights("410","AC:CF:23:A1:FB:38")
    # send_message_lights("420","AC:CF:23:A1:FB:38")
    kettle = {}
    kettle['ip'] = "192.168.0.102"
    turnOff(kettle)
