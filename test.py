from recoUtils import Matrix

GP = 4

class R:
    def __init__(self):
        self._class_list = list()

        self._cc_matrix = Matrix(4)
        self._inverted_cc_matrix = None

    def calculateCommonCovarianceMatrix(self):
        """Get the common covariance matrix by using the covariance matrix of each gesture class"""
        i = 0
        j = 0
        while i < self._cc_matrix._size:
            while j < self._cc_matrix._size:
                res = 0
                sample_nb = 0
                for gclass in self._class_list:
                    res += gclass._cv_matrix.get(i,j)
                    sample_nb += len(gclass._s_list)
                res = res / (sample_nb - len(self._class_list))
                self._cc_matrix.set(i,j,round(res,GP))
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

    def recognition(self, sample):
        """Compare the score given by each class, return the name of the class who gives the highest score"""
        # get scores and compare them
        mv = -100000
        c_name = ""
        for c in self._class_list:
            v = c.giveScore(sample)
            print("class:",c._name,"has score",v)
            if v > mv:
                mv = v
                c_name = c._name
                
        print("The highest score",mv,"is given by class:",c_name)
        return c_name



class C:
    def __init__(self, n):
        self._name = n
        self._f_list = [0.0, 0.0, 0.0, 0.0] # list of weights
        self._s_list = list() # list of samples, a sample is a list of data
        self._cv_matrix = Matrix(4)
        self._base_weight = 0

    def __str__(self):
        res = "<class>\n" + self._name + "\n"
        for f in self._f_list:
            res += str(f) + "\n"
        res += "base weight" + str(self._base_weight) + "\n"
        res += str(len(self._s_list)) + "\n<samples>\n"
        for s in self._s_list:
            for ele in s:
                res += str(ele) + " "
            res += "\n"
        res += "</samples>\n</class>\n"
        return res

    def readData(self, file_path):
        f = open(file_path)
        lines = f.readlines()
        f.close()

        for line in lines:
            l = line.split(" ")
            l_d = list()
            for c in l:
                l_d.append(float(c))
            self._s_list.append(l_d)

    def getFeatureAverage(self, f_id):
        """Calcultate the average value of a given feature"""
        res = 0
        i = 0
        while i < len(self._s_list):
            res += self._s_list[i][f_id]
            i += 1
        res = round(res / len(self._s_list), GP)
        return res

    def calculateCovarianceMatrix(self):
        i = 0
        j = 0
        while i < self._cv_matrix._size:
            while j < self._cv_matrix._size:
                res = 0
                k = 0
                while k < len(self._s_list):
                    res += (self._s_list[k][i] - self.getFeatureAverage(i)) * (self._s_list[k][j] - self.getFeatureAverage(j))
                    k += 1
                self._cv_matrix.set(i,j,round(res,GP))
                j += 1
            j = 0
            i += 1

        print("Covariance Matrix is done for gesture <",self._name,">")
        print(self._cv_matrix)

    def calculateFeatureWeight(self, inv_ccmatrix):
        if inv_ccmatrix is None:
            print("Calculate common inverse matrix first")
            return None
        else:
            w = 0
            i = 0
            f_id = 0
            while f_id < len(self._f_list):
                while i < len(self._f_list):
                    w += inv_ccmatrix.get(i,f_id) * self.getFeatureAverage(i)
                    i += 1
                i = 0
                self._f_list[f_id] = round(w,GP)
                f_id += 1
            print("Feature weights calculation is done.")
        
    def calculateBaseWeight(self):
        w = 0
        i = 0
        while i < len(self._f_list):
            w += self._f_list[i] * self.getFeatureAverage(i)
            i += 1
        w = - (w / 2)
        self._base_weight = round(w,GP)
        print("Base weight calculation is done.")

    def giveScore(self, sample):
        """Give a score for the input recoTuple"""
        res = 0
        i = 0
        while i < len(self._f_list):
            res += self._f_list[i] * sample[i]
            i += 1
        return res + self._base_weight

if __name__ == "__main__":
    r = R()
    a = C("A")
    b = C("B")
    a.readData("testD/ds1.txt")
    a.calculateCovarianceMatrix()
    b.readData("testD/ds2.txt")
    b.calculateCovarianceMatrix()

    r._class_list.append(a)
    r._class_list.append(b)

    r.calculateCommonCovarianceMatrix()
    print(r._cc_matrix)
    print(r._inverted_cc_matrix)

    # compute weight
    for c in r._class_list:
        c.calculateFeatureWeight(r._inverted_cc_matrix)
        c.calculateBaseWeight()
        print(c)

    # pass A as test
    for s in a._s_list:
        print(r.recognition(s))
    

