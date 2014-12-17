from recoDataStructure import *

class DataReceiver:
    """This class helps us to read data into the program.
        During the training stage, it can read data from file
        and during recognition stage, it can get real time tracking data and
        pass it to the Feature Extraction module."""
    def __init__(self, l_or_r):
        # 0 or 1, whether it's for the left or right hand
        self._l_or_r = l_or_r

        # data structure for real time training or recognition
        self._gloveData = None
    
        # data structure for training from file
        self._gloveDataList = list()

    def readDataFromFile(self, filePath):
        """Read a sample file and create a list of ARTGlove data samples"""
        # read the file into a list
        f = open(filePath, 'r')
        lines = f.readlines()
        f.close()

        # create glove data and add it into the glove data list
        indice = 0
        while indice + 53 <= len(lines):
            glove = self.createGloveFromFile(lines[indice:indice+53])
            if glove._l_or_r == self._l_or_r:
                self._gloveDataList.append(glove)
            indice += 53

    def createFingerFromFile(self, n, lines):
        """Function called by the createGloveFromFile function"""
        pos_str = lines[0][0:-1].split(' ')
        pos = list()
        for p in pos_str:
            pos.append(float(p))

        ori_str = lines[1][0:-1] + ' ' + lines[2][0:-1] + ' ' + lines[3][0:-1]
        ori_str = ori_str.split(' ')
        ori = list()
        for o in ori_str:
            ori.append(float(o))

        phalen_str = lines[5][0:-1].split(' ')
        phalen = list()
        for p in phalen_str:
            phalen.append(float(p))

        #print("lines[6]:",lines[6])
        phaang_str = lines[6][0:-1].split(' ')
        phaang = list()
        for p in phaang_str:
            phaang.append(float(p))

        f = Finger(n, pos, ori, float(lines[4][0:-1]), phalen, phaang)
        return f
    
    def createGloveFromFile(self, lines):
        """Function called by the readDataFromFile function"""
        pos_str = lines[5][0:-1].split(' ')
        pos = list()
        for p in pos_str:
            pos.append(float(p))

        ori_str = lines[6][0:-1] + ' ' + lines[7][0:-1] + ' ' + lines[8][0:-1]
        ori_str = ori_str.split(' ')
        ori = list()
        for o in ori_str:
            ori.append(float(o))
        finger_name_list = ['pouce','index','majeur','annulaire','auriculaire']
        i = 11
        n = 0
        fingers = list()
        while n < 5:
            fingers.append(self.createFingerFromFile(finger_name_list[n],lines[i+n*8:i+7+n*8]))
            n += 1

        lr = -1
        if lines[3][0:-1] == 'left':
            lr = 0
        else:
            lr = 1

        g = Glove(lines[1][0:-1], 0, lines[2][0:-1], lr, int(lines[4][0:-1]), fingers, pos, ori)
        return g

    def readRealTimeData(self, g_frame):
        """ Add a glove frame to pass later to the feature extractor """
        for glove in g_frame._glove_list:
            if glove._l_or_r == 1:
                # use only right hand for now
                self._gloveData = glove

    def getOneSampleFrameFile(self):
        """Data from file, return the first data frame in the list"""
        if len(self._gloveDataList) != 0:
            return self._gloveDataList.pop(0)
        else:
            return None

    def getOneSampleFrameRT(self):
        return self._gloveData

    def showGlovesFromFile(self):
        for g in self._gloveDataList:
            print(g._timestamp)

    def getGloveNumberFromFile(self):
        """Return the number of samples that we create from file"""
        return len(self._gloveDataList)

if __name__ == "__main__":
    dr_left = DataReceiver(0)
    dr_right = DataReceiver(1)
    dr_left.readDataFromFile("data/final_dataset2.txt")
    dr_right.readDataFromFile("data/final_dataset2.txt")
    print("finish for left hand", dr_left.getGloveNumberFromFile())
    print("finish for right hand", dr_right.getGloveNumberFromFile())
