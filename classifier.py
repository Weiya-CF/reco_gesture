from recoDataStructure import *

class Rubine:
    """This is a classifier using the algorithm introduced by Rubine"""
    def __init__(self, feature_file):
        self._class_list = list()
        self._feature_file = feature_file
        self._feature_list = self.createFeatureListFromFile()
        
        # empty matrix
        self._cc_matrix = Matrix(len(self._feature_list))
        self._inverted_cc_matrix = None
    
    
    def createFeatureListFromFile(self):
        """Initiate the feature list from file"""
        fea_file = open(self._feature_file, 'r')
        lines = fea_file.readlines()
        fea_file.close()
        
        feature_list = list()
        # Create a list of Features
        for line in lines:
            f = Feature(line[0:-1])
            feature_list.append(f)
        return feature_list

    def hasGestureClass(self, gclass_name):
        """Verify if a geture class exists already in the classifier"""
        for c in self._class_list:
            if c._name == gclass_name:
                return True
        return False

    def createEmptyFeatureList(self):
        f_list = list()
        for f in self._feature_list:
            f_list.append(Feature(f._name))
        return f_list
    
    def createGestureClass(self, gclass_name):
        """Create a gesture class with empty sampleList and weights"""
        
        c = GestureClass(gclass_name, self.createEmptyFeatureList())
        self._class_list.append(c)
        print("New gesture classe <",gclass_name,"> has been added.")

    def getGestureClassByName(self, gclass_name):
        for g in self._class_list:
            if g._name == gclass_name:
                return g
        return None

    def addRecoTupleForTraining(self, rt, gclass_name):
        """Add a frame of data into the sample list of a given gesture class"""
        gclass = self.getGestureClassByName(gclass_name)
        if gclass is not None:
            gclass._sample_list.append(rt._s_list)
        else:
            print("The gesture class <",gclass_name,"> doesn't exist.")

    def calculateCommonCovarianceMatrix(self):
        """Get the common covariance matrix by using the covariance matrix of each gesture class"""
        i = 0
        j = 0
        while i < self._cc_matrix._size:
            while j < self._cc_matrix._size:
                res = 0
                sample_nb = 0
                for gclass in self._class_list:
                    res += gclass._co_matrix.get(i,j)
                    sample_nb += len(gclass._sample_list)
                res = res / (sample_nb - len(self._class_list))
                self._cc_matrix.set(i,j,res)
                j += 1
            j = 0
            i += 1
        print("Common Covariance Matrix is done")
        #print(self._cc_matrix)
        self._inverted_cc_matrix = self._cc_matrix.inverted()
        if self._inverted_cc_matrix is not None:
            print("Inversed CCMatrix is done")
            #print(self._inverted_cc_matrix)
        else:
            print("Can't get inversed CCMatrix")


    def train(self, gclass_name):
        """Use 80 percent of sample list to calculate weight for each feature of a gesture class"""
        gclass = self.getGestureClassByName(gclass_name)
        if gclass is None:
            print("The gesture",gclass_name,"doesn't exist.")
        else:
            gclass._train_sample_nb = int(len(gclass._sample_list) * 0.8)
            if gclass._train_sample_nb < 20:
                # not enough samples
                #print("not enough samples")
                return 1
            else:
                # 1) calculate covariance matrix for this class
                gclass.calculateCovarianceMatrix()
            
                # 2) calculate common covariance matrix
                self.calculateCommonCovarianceMatrix()

                # 3) calculate weight for each feature and base weight
                for g in self._class_list:
                    g.calculateFeatureWeight(self._inverted_cc_matrix)
                    g.calculateBaseWeight()
                self.showTrainingResult()
                print("Training has been done successfully. Gesture",gclass_name,"was updated.")
                return 0

    def showTrainingResult(self):
        for g in self._class_list:
            g.showTrainingResult()

    def recognition(self, s_list):
        """Take the sample list of one RecoTuple and pass it to each gesutre class, then compare the score given by each class,
        return the name of the class who gives the highest score"""
        # get scores and compare them
        mv = -100000
        c_name = ""
        for c in self._class_list:
            v = c.giveScore(s_list)
            print("class:",c._name,"has score",v)
            if v > mv:
                mv = v
                c_name = c._name
                
        print("The highest score",mv,"is given by class:",c_name)
        return c_name
        
    def calcultatePrecision(self, gclass_name):
        """Use 20 percent of sample list to calculate precision of the classification for a given gesture class
            It's the percentage of right guess
        """
        gclass = self.getGestureClassByName(gclass_name)
        total_num = len(gclass._sample_list)
        test_num = total_num - gclass._train_sample_nb
        right_num = 0
        i = gclass._train_sample_nb
        while i < total_num:
            if gclass_name == self.recognition(gclass._sample_list[i]):
                right_num += 1
            i += 1
        print("The precision is:",round(right_num / test_num, 4) * 100,"%")

    def saveClassifierToFile(self, fpath):
        """Save a list of weight for each feature and a list of sample for each gesture class.
            This function is called at the end of the training process"""
        res = ""
        for c in self._class_list:
            res += str(c)
        # write to file
        with open(fpath, 'w') as f:
            f.write(res)
        print("The trained classifier has been saved successfully.")

    def loadClassifierFromFile(self, fpath):
        """Load the classifier directly from file so we don't have to do the training each time we lance the program"""
        c_file = open(fpath, 'r') #'conf/trained_classifier.txt', 'r')
        lines = c_file.readlines()
        c_file.close()

        print(len(lines))
    
        # Create a list of GestureClass
        i = 0
        while i < len(lines):
            if lines[i][:-1] == "<class>":
                i += 1
                c = GestureClass(lines[i][:-1], self._feature_list)
                print("new gesture :",c._name,"added")
                i += 1
                k = 0
                while k < len(c._feature_list):
                    c._feature_list[k]._weight = float(lines[i+k].split(':')[1][:-1])
                    k += 1
                i += k
                c._base_weight = float(lines[i][:-1])
                i += 1
                c._train_sample_nb = int(lines[i][:-1])
                i += 2
                k = 0
                while k < c._train_sample_nb:
                    sample = map(float, lines[i+k].split())
                    c._sample_list.append(sample)
                    k += 1
                self._class_list.append(c)
                i += k+2
            else:
                i += 1
                    
        print(len(self._class_list)," gesture classes have been loaded.")
