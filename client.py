import socket
import recoDataStructure as rds
import sys
from PySide import QtGui

class ARTGloveReceiver:
    def __init__(self):
        self._new_frame_arrive = False
        self._data = rds.ARTGloveFrame()

    def receiveGloveFrame(self, msg):
        lines = msg.split('\n')
        self._data._fr = int(lines[0].split(' ')[1])
        self._data._timestamp = float(lines[1].split(' ')[1])
        gl_line = lines[2].split(' ', 2)
        self._data._gl = int(gl_line[1])
        if self._data._gl != 0:
            data = gl_line[2]
            data_lines = data.split('][')
            base = data_lines[0][1:].split(' ')
            pos = [ float(x) for x in data_lines[1].split(' ') ]
            ori = [ float(x) for x in data_lines[2].split(' ') ]
            finger_list = list()
            finger_name_list = ['pouce', 'index', 'majeur','annulaire','auriculaire']
            j = 0
            while j < 5:
                pos_f = [ float(x) for x in data_lines[3+3*j].split(' ') ]
                ori_f = [ float(x) for x in data_lines[4+3*j].split(' ') ]
                if j == 4:
                    data_f = [ float(x) for x in data_lines[5+3*j][:-2].split(' ') ]
                else:
                    data_f = [ float(x) for x in data_lines[5+3*j].split(' ') ]
                
                finger = rds.Finger(finger_name_list[j], pos_f, ori_f, data_f[0], data_f[1:4], data_f[4:])
                finger_list.append(finger)
                j += 1
            
            self._data._glove_list = list()
            self._data._glove_list.append(rds.Glove(self._timestamp, int(base[0]), float(base[1]), int(base[2]), int(base[3]), finger_list, pos, ori))
            self._new_frame_arrive = True
        else:
            self._new_frame_arrive = False



def main(): 
    app = QtGui.QApplication(sys.argv)
    # Create a Label and show it
    label = QtGui.QLabel("Hello World")
    label.show()
    # Enter Qt application main loop
    app.exec_()
    sys.exit()


if __name__ == "__main__":
    UDP_IP = "0.0.0.0"
    UDP_PORT = 6000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    receiver = ARTGloveReceiver()

    main()

    print("after main")

    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        receiver.receiveGloveFrame(data.decode('utf-8'))
        #print(data.decode('utf-8'))
        if receiver._new_frame_arrive:
            print(receiver)	

