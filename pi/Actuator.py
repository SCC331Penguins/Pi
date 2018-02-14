import nmap
import socket


criteria = [
    {
        'mac':'AC:CF:23',
        'type':'Lights',
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
    actuators = {}
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
                        actuators[mac] = {}
                        actuators[mac]['type'] = target['type']
                        actuators[mac]['ip'] = ip
                        actuators[mac]['mac'] = mac
                        currentGuess = target['type']
                    if("port" in target.keys() and target["port"] in s['scan'][ip]['tcp']):
                        actuators[mac] = {}
                        actuators[mac]['type'] = target['type']
                        actuators[mac]['ip'] = ip
                        actuators[mac]['mac'] = mac
            else:
                pass
        except Exception as e:
            print (e)
    return actuators

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
        s.sendall(message)
        s.close()
    except Exception as e:
        print (e)

# ---- Kettle Functions ----
def findDevices():
        nm = nmap.PortScanner()
        s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
        return scan(s)

def turnOn(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x4")

def turnOff(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x0")

def set100C(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x80")

def set95C(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x2")

def set80C(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x4000")

def set65C(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x200")

def setWarm(kettle):
    send_message(kettle.ip, 2000, "set sys output 0x8")


# ---- Lights Functions ----

def allLightsOn(lights):
    send_message_lights("420",lights.mac)

def allLightsOff(lights):
    send_message_lights("410",lights.mac)

def g1LightsOn(lights):
    send_message_lights("450",lights.mac)

def g1LightsOff(lights):
    send_message_lights("460",lights.mac)

def g2LightsOn(lights):
    send_message_lights("470",lights.mac)

def g2LightsOff(lights):
    send_message_lights("480",lights.mac)

def g3LightsOn(lights):
    send_message_lights("490",lights.mac)

def g3LightsOff(lights):
    send_message_lights("4a0",lights.mac)

def send_message_lights(number, mac):
    send_message("178.62.58.245",38899, "APP#"+mac+'#CMD#'+number+'\n')
#APPAC:CF:23:28:C2:2C
#OKAC:CF:23:28:C2:2C


if __name__ == '__main__':
    print("Start")

    print(findDevices())
