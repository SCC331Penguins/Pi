import nmap, logging
import paho.mqtt.client as mqtt
import socket
import time
from json import dumps
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
    }
]
def scan(s):
    #myIp = socket.gethostbyname(socket.gethostname()) # doesnt work on pi
    actuators = []
    # show all iOS devices in ip range
    #print (s.get())
    print(s)
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
                        obj = {}
                        obj['type'] = target['type']
                        obj['ip'] = ip
                        obj['mac'] = mac
                        actuators.append(obj)
            else:
                pass
        except Exception as e:
            print (e)
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
        # use repr() ?
        print(data)
        return data == expected_reply
    except Exception as e:
        print (e)
        return False

# without expected reply
def send_message(ip, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(message.encode())
        s.close()
    except Exception as e:
        print (e)

# ---- Kettle Functions ----
def findDevices():
        logger.debug("finding Devices")
        nm = nmap.PortScanner()
        # s = []
        # logger.info("finished Devices scan doing parse")
        # time.sleep(3)
        # s.append(getVirtualActuators())
        # return s
        s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
        return scan(s)
def sendNotification(notifObj, msg):
    client = mqtt.Client()
    client.connect("sccug-330-02.lancs.ac.uk",1883,60)
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
}

if __name__ == '__main__':
    print("Start")
    # send_message_lights("410","AC:CF:23:A1:FB:38")
    # send_message_lights("420","AC:CF:23:A1:FB:38")
    kettle = {}
    kettle['ip'] = "192.168.0.102"
    turnOff(kettle)
    # devices = findDevices()
    # print("Lights Off")
    # time.sleep(2)
    # for device in devices:
        # if device['type'] == 'Lights':
            # allLightsOff(device)
