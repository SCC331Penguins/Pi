import nmap
import socket

actuators = {}

def scan(message, expected_reply, set_port=None, type=None):
    #myIp = socket.gethostbyname(socket.gethostname()) # doesnt work on pi
    nm = nmap.PortScanner()
    s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
    # show all iOS devices in ip range
    #print (s.get())
    for ip in s["scan"]:
        print(ip)
        try:
            if 'tcp' in s["scan"][ip]:
                if 'mac' in s["scan"][ip]['addresses']:
                    print(s["scan"][ip]['addresses']['mac'])
                    mac = s["scan"][ip]['addresses']['mac']

                for port in s["scan"][ip]["tcp"]:
                    if (set_port == port or set_port == None):
                        print (port)
                        if verify_connection(ip, port, message, expected_reply):
                            actuators[mac] = {}
                            actuators[mac]['type'] = type
                            actuators[mac]['ip'] = ip
                            actuators[mac]['mac'] = mac
                            print ("Added" + ip + "/" + str(port))
                            actuators.append(ip + "/" + str(port) + "-" + mac)
                            # ignore 80 and 22 + self ?
                print("\n")
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
    except:
        print ("Conection Failed")


if __name__ == '__main__':
    print("Start")
    scan("HELLOKETTLE\n", "HELLOAPP\r",2000)
    print(actuators)

# ---- Kettle Functions ----
def turn_kettle_on(ip, port):
    send_message(ip, port, "set sys output 0x4")

def turn_kettle_off(ip, port):
    send_message(ip, port, "set sys output 0x0")

