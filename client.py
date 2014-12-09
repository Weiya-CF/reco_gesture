import socket
import recoDataStructure as rds
import sys
from PySide import QtCore, QtGui, QtNetwork

class ARTGloveClient(QtGui.QMainWindow):
    def __init__(self):
        super(ARTGloveClient, self).__init__()

        # GUI part
        pannel = QtGui.QWidget()
        self.setCentralWidget(pannel)

        self._status_label = QtGui.QLabel("Messages")
        quitButton = QtGui.QPushButton("&Quit")
        quitButton.clicked.connect(self.close)

        startToggleButton = QtGui.QPushButton("Start/Stop", self)
        startToggleButton.clicked.connect(self.startToggle)

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(startToggleButton)
        buttonLayout.addWidget(quitButton)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self._status_label)
        mainLayout.addLayout(buttonLayout)
        pannel.setLayout(mainLayout)

        self.setWindowTitle("ART Glove Receiver")
        self.statusBar().showMessage("Listening for broadcasted messages")

        self.setMinimumSize(160,160)
        self.resize(600,400)

        # UDP client part
        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(6000)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)
        
        # Core application part
        self._new_frame_arrive = False
        self._running = False
        self._data = rds.ARTGloveFrame()
        
    def processPendingDatagrams(self):
        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            try:
                # Python v3.
                datagram = str(datagram, encoding='utf-8')
            except TypeError:
                # Python v2.
                pass
            #self.statusLabel.setText("Received datagram: \"%s\"" % datagram)
            self.buildGloveFrame(datagram)
            print(self._data)

    def startToggle(self):
        self._running = not self._running
        self._status_label.setText(str(self._running))
        #print(self._running)
        
    def buildGloveFrame(self, msg):
        """Convert the message from string to a Glove object
           Store the object inside a list
           Set new_frame_arrive to True if the new frame is not empty
        """
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



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    client_window = ARTGloveClient()
    client_window.show()
    sys.exit(app.exec_())

