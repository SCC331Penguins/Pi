import nmap
import socket

actuators = []

def scan(message, expected_reply, set_port=None):
    myIp = socket.gethostbyname(socket.gethostname()) # doesnt work on pi
    nm = nmap.PortScanner()
    s = nm.scan(hosts="192.168.0.0/24", arguments='-T4 -F')
    # show all iOS devices in ip range
    #print (s.get())
    for ip in s["scan"]:
        print ip
        try:
            for port in s["scan"][ip]["tcp"]:
                if(set_port == port or set_port== None):
                    print port
                    if verify_connection(ip, port, message, expected_reply):
                        print "Added" + ip + "/" +str(port)
                        actuators.append(ip+"/"+str(port))
                    # ignore 80 and 22 + self
            print("\n")
        except:
            print "Probably TCP Error"

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
    except:
        return False

# without expected reply
def send_message(ip, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(message)
        s.close()
    except:
        print "Conection Failed"

if __name__ == '__main__':
    print("Start")
    scan("HELLOKETTLE\n", u"HELLOAPP\r",2000)
