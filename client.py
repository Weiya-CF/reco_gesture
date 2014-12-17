import sys, os
from PySide import QtCore, QtGui, QtNetwork

import recoDataStructure as rds
from recoPipeline import RecoPipeline

class ARTGloveClient(QtGui.QMainWindow):
    def __init__(self):
        super(ARTGloveClient, self).__init__()

        # GUI part
        pannel = QtGui.QWidget()
        self.setCentralWidget(pannel)

        tabWidget = QtGui.QTabWidget()
        tab_training = QtGui.QWidget()
        tab_reco = QtGui.QWidget()
        tabWidget.addTab(tab_training, "Training")
        tabWidget.addTab(tab_reco, "Recognition")

        # --- training part ---
        tr_global_layout = QtGui.QVBoxLayout()
        tr_uname_layout = QtGui.QHBoxLayout()
        self._tr_uname_field = QtGui.QLineEdit()
        self._tr_uname_button = QtGui.QPushButton("Confirm")
        self._tr_uname_button.clicked.connect(self.trConfirmUserName)
        tr_uname_layout.addWidget(QtGui.QLabel("Provide a user name:"))
        tr_uname_layout.addWidget(self._tr_uname_field)
        tr_uname_layout.addWidget(self._tr_uname_button)

        tr_gname_layout = QtGui.QHBoxLayout()
        self._tr_gname_field = QtGui.QLineEdit()
        self._tr_gname_button = QtGui.QPushButton("Confirm")
        self._tr_gname_button.setEnabled(False)
        self._tr_gname_button.clicked.connect(self.trConfirmGestureName)
        tr_gname_layout.addWidget(QtGui.QLabel("Provide a gesture name:"))
        tr_gname_layout.addWidget(self._tr_gname_field)
        tr_gname_layout.addWidget(self._tr_gname_button)

        tr_record_file_layout = QtGui.QHBoxLayout()
        self._tr_record_file_confirm_button = QtGui.QPushButton("Record")
        self._tr_record_file_confirm_button.setEnabled(False)
        self._tr_record_file_confirm_button.clicked.connect(self.trRecordDataToFile)
        tr_record_file_layout.addWidget(QtGui.QLabel("Record Training File:"))
        tr_record_file_layout.addWidget(self._tr_record_file_confirm_button)

        tr_file_layout = QtGui.QHBoxLayout()
        self._tr_file_fpath_field = QtGui.QLineEdit()
        self._tr_file_select_button = QtGui.QPushButton("Browse")
        self._tr_file_confirm_button = QtGui.QPushButton("Confirm")
        self._tr_file_confirm_button.setEnabled(False)
        self._tr_file_select_button.setEnabled(False)
        self._tr_file_confirm_button.clicked.connect(self.trFileTraining)
        tr_file_layout.addWidget(QtGui.QLabel("File:"))
        tr_file_layout.addWidget(self._tr_file_fpath_field)
        tr_file_layout.addWidget(self._tr_file_select_button)
        tr_file_layout.addWidget(self._tr_file_confirm_button)

        tr_rt_layout = QtGui.QHBoxLayout()
        self._tr_rt_toggle_button = QtGui.QPushButton("Start")
        self._tr_rt_toggle_button.setEnabled(False)
        self._tr_rt_toggle_button.clicked.connect(self.trRealtimeTraining)
        tr_rt_layout.addWidget(self._tr_rt_toggle_button)

        self._tr_msg_box = QtGui.QTextEdit("This is the message window for training")

        # --- recognition part ---
        re_global_layout = QtGui.QVBoxLayout()
        re_uname_layout = QtGui.QHBoxLayout()
        self._re_uname_label = QtGui.QLabel("Undefined")
        re_uname_layout.addWidget(QtGui.QLabel("Recognition for user:"))
        re_uname_layout.addWidget(self._re_uname_label)

        re_action_layout = QtGui.QHBoxLayout()
        self._re_gname_field = QtGui.QLabel("Undefined")
        self._re_toggle_button = QtGui.QPushButton("Start")
        self._re_toggle_button.setEnabled(False)
        self._re_toggle_button.clicked.connect(self.reRealtimeRecognition)
        re_action_layout.addWidget(QtGui.QLabel("Current gesture"))
        re_action_layout.addWidget(self._re_gname_field)
        re_action_layout.addWidget(self._re_toggle_button)
        
        self._re_msg_box = QtGui.QTextEdit("This is the message window for recognition")

        # --- global layout ---
        tr_global_layout.addLayout(tr_uname_layout)
        tr_global_layout.addLayout(tr_gname_layout)
        tr_global_layout.addWidget(QtGui.QLabel("<Training from file>"))
        tr_global_layout.addLayout(tr_record_file_layout)
        tr_global_layout.addLayout(tr_file_layout)
        tr_global_layout.addWidget(QtGui.QLabel("<Real-time Training>"))
        tr_global_layout.addLayout(tr_rt_layout)
        tr_global_layout.addWidget(self._tr_msg_box)
        re_global_layout.addLayout(re_uname_layout)
        re_global_layout.addLayout(re_action_layout)
        re_global_layout.addWidget(self._re_msg_box)
        tab_training.setLayout(tr_global_layout)
        tab_reco.setLayout(re_global_layout)
        """quitButton = QtGui.QPushButton("&Quit")
        quitButton.clicked.connect(self.close)"""

        """buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(startToggleButton)
        buttonLayout.addWidget(quitButton)"""
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        pannel.setLayout(mainLayout)
        
        self.setWindowTitle("ART Gesture Analyser")
        self.statusBar().showMessage("Version 1.0")

        self.setMinimumSize(160,160)
        self.resize(450,500)

        # UDP client part
        self.udpSocket = QtNetwork.QUdpSocket(self)
        self.udpSocket.bind(6000)
        self.udpSocket.readyRead.connect(self.processPendingDatagrams)
        
        # Core application part
        self._uname = ""
        self._gname = ""
        self._new_frame_arrive = False
        self._tr_rt_running = False
        self._re_rt_running = False
        self._tr_recording = False
        
        self._data = rds.ARTGloveFrame()
        self._glove_recorder = None
        self._tr_recording_nb = 0 # how many samples are recorded in the file
        
        self._rp = RecoPipeline()
        
    def processPendingDatagrams(self):
        while self.udpSocket.hasPendingDatagrams():
            datagram, host, port = self.udpSocket.readDatagram(self.udpSocket.pendingDatagramSize())
            #str(datagram, encoding='utf-8')
            if self._tr_rt_running:
                self.buildGloveFrame(datagram.__str__())
                if self._new_frame_arrive:
                    #print(self._data)
                    self._rp.trainRealTime(self._gname, self._data)
            elif self._re_rt_running:
                    self.buildGloveFrame(datagram.__str__())
                    if self._new_frame_arrive:
                        reco_gname = self._rp.recognition(self._data)
                        if reco_gname is not None:
                            self._re_gname_field.setText(reco_gname)
            else:
                if self._tr_recording:
                    self.buildGloveFrame(datagram.__str__())
                    if self._new_frame_arrive:
                        self.recordGloveToFile()
                        self._tr_recording_nb += 1
                    

    def trConfirmUserName(self):
        """ If the user does not exist, create a directory with the given name
            Otherwise load the trained classifier into memory
            Activate buttons for training if the name is valid
        """
        self._uname = self._tr_uname_field.text()
        if self._uname == "":
            self._tr_msg_box.append("Please provide a valid user name.")
        else:
            if not os.path.exists("conf/"+self._uname):
                os.makedirs("conf/"+self._uname)

            # enable buttons
            self._tr_gname_button.setEnabled(True)
            self._re_uname_label.setText(self._uname)
            self._re_toggle_button.setEnabled(True)

            # load the classifier
            fname = "conf/"+self._uname+"/trained_classifier.txt"
            if os.path.isfile(fname):
                self._rp._classifier.loadClassifierFromFile(fname)
            
            self._tr_msg_box.append("Ready to train for user <"+self._uname+">.")

    def trConfirmGestureName(self):
        self._gname = self._tr_gname_field.text()
        if self._gname == "":
            self._tr_msg_box.append("Please provide a valid gesture name.")
        else:
            self._tr_msg_box.append("The gesture <"+self._gname+"> is ready for training.")

        # enable buttons
        self._tr_file_confirm_button.setEnabled(True)
        self._tr_rt_toggle_button.setEnabled(True)
        self._tr_record_file_confirm_button.setEnabled(True)

    def trRealtimeTraining(self):
        """ Start/Stop training for a given gesture with a valid name
            Start: pass received data to pipeline
            Stop: save the classifier to file
        """
        if not self._tr_rt_running:
            # to start
            self._tr_rt_running = True
            if not self._rp._classifier.hasGestureClass(self._gname):
                self._rp._classifier.createGestureClass(self._gname)
            self._tr_rt_toggle_button.setText("Stop")
            self._tr_msg_box.append("Start training for <"+self._gname+">.")
        else:
            # to stop
            self._tr_rt_running = False
            self._tr_rt_toggle_button.setText("Start")

            # start to process training data
            res = self._rp._classifier.train(self._gname)
            if res == 0:
                self._rp._classifier.showTrainingResult()
                self._rp._classifier.saveClassifierToFile("conf/"+self._uname+"/trained_classifier.txt")
                self._tr_msg_box.append("Stop training for <"+self._gname+">. Classifier saved.")
            elif res == 1:
                self._tr_msg_box.append("Stop training for <"+self._gname+">. Not enough samples so nothing changed.")

    def trFileTraining(self):
        """Train the classifier with samples recorded in files """
        f_path = self._tr_file_fpath_field.text()
        self._rp.trainFromFile(f_path, self._gname)
        self._rp.calcultatePrecision(self._gname)
        self._rp._classifier.saveClassifierToFile("conf/"+self._uname+"/trained_classifier.txt") 
        self._tr_msg_box.append("Training for <"+self._gname+"> is finished. Classifier saved.")

    def trRecordDataToFile(self):
        """ Save tracking data into files, one file for a gesture, then do the training with these files """
        if not self._tr_recording:
            # to start
            if not os.path.exists("data/"+self._uname):
                os.makedirs("data/"+self._uname)
            self._glove_recorder = open("data/"+self._uname+"/"+self._gname+".dat", 'w+')
            self._tr_recording = True
            self._tr_recording_nb = 0
            self._tr_record_file_confirm_button.setText("Stop")
            self._tr_msg_box.append("Start recording data to file for gesture "+self._gname+" ...")
        else:
            self._tr_recording = False
            self._tr_record_file_confirm_button.setText("Record")
            self._glove_recorder.close()
            self._tr_msg_box.append(str(self._tr_recording_nb)+" samples are saved in data/"+self._uname+"/"+self._gname+".dat")
        

    def reRealtimeRecognition(self):
        """ Start/Stop recognition
            Start: pass received data to pipeline
            Stop: just stop
        """
        if not self._re_rt_running:
            # to start
            if len(self._rp._classifier._class_list) == 0:
                self._re_msg_box.append("The pipeline is not trained yet.")
            else:
                self._re_rt_running = True
                self._re_toggle_button.setText("Stop")
                self._re_msg_box.append("Start recognition process...")
        else:
            # to stop
            self._re_rt_running = False
            self._re_toggle_button.setText("Start")
            self._re_msg_box.append("Recognition stopped.")
                

    def buildGloveFrame(self, msg):
        """Convert ART message from string to a Glove object
           Store the object inside a list (1 or more hands at a time)
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
            self._data._glove_list.append(rds.Glove(self._data._timestamp, int(base[0]), float(base[1]), int(base[2]), int(base[3]), finger_list, pos, ori))
            self._new_frame_arrive = True
        else:
            self._new_frame_arrive = False

    def recordGloveToFile(self):
        # Attention, only for one hand
        glove = self._data._glove_list[0]
        self._glove_recorder.write(glove.toFile())
        self._glove_recorder.flush()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    client_window = ARTGloveClient()
    client_window.show()
    sys.exit(app.exec_())

