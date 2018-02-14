import nmap
import socket

actuators = {}

def scan(message, expected_reply, set_port=None, type=None, mac=None):
    #myIp = socket.gethostbyname(socket.gethostname()) # doesnt work on pi
    old_mac = mac
    nm = nmap.PortScanner()
    s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
    print (s)
    # show all iOS devices in ip range
    #print (s.get())
    for ip in s["scan"]:
        print(ip)
        try:
            if 'tcp' in s["scan"][ip]:
                if 'mac' in s["scan"][ip]['addresses'] and mac == None:
                    print(s["scan"][ip]['addresses']['mac'])
                    mac = s["scan"][ip]['addresses']['mac'] # get mac address

                if mac.startswith("AC:CF:23"):
                    # Light manufacturer mac address found
                    actuators[mac] = {}
                    actuators[mac]['type'] = type
                    actuators[mac]['ip'] = ip
                    actuators[mac]['mac'] = mac

                for port in s["scan"][ip]["tcp"]:
                    if set_port == port or set_port == None and message != None:
                        print (port)
                        if verify_connection(ip, port, message, expected_reply):
                            # Saving
                            actuators[mac] = {}
                            actuators[mac]['type'] = type
                            actuators[mac]['ip'] = ip
                            actuators[mac]['mac'] = mac
                            print ("Added" + ip + "/" + str(port))
                            actuators.append(ip + "/" + str(port) + "-" + mac)
                mac = old_mac # overwrite mac
                print("\n")
            else:
                print("TCP Failed")
        except Exception as e:
            print (e)

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
def find_kettle():
    scan("HELLOKETTLE\n", "HELLOAPP\r", 2000, "Kettle")

def turn_kettle_on(ip, port):
    send_message(ip, port, "set sys output 0x4")

def turn_kettle_off(ip, port):
    send_message(ip, port, "set sys output 0x0")

def set_kettle_100C(ip, port):
    send_message(ip, port, "set sys output 0x80")

def set_kettle_95C(ip, port):
    send_message(ip, port, "set sys output 0x2")

def set_kettle_80C(ip, port):
    send_message(ip, port, "set sys output 0x4000")

def set_kettle_warm(ip, port):
    send_message(ip, port, "set sys output 0x8")


# ---- Kettle Functions ----
def find_light():
    scan(None, None, None, "Light") 

def turn_all_lights_on(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#420\n")

def turn_all_lights_off(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#410\n")

def turn_group_1_on(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#450\n")

def turn_group_1_off(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#460\n")

def turn_group_2_on(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#470\n")

def turn_group_2_off(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#480\n")

def turn_group_3_on(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#490\n")

def turn_group_3_off(mac):
    send_message("178.62.58.245", 38899, "APP#" + mac + "#CMD#4a0\n")
#APPAC:CF:23:28:C2:2C
#OKAC:CF:23:28:C2:2C


if __name__ == '__main__':
    print("Start")
    # find_kettle()
    #find_light()
    turn_group_1_off("AC:CF:23:A1:FB:38")
    print(actuators)
