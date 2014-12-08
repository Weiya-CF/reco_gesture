import math

def distanceOfPosition(pos1, pos2):
    """To get the distance between 2 given 3D points."""
    return math.sqrt(pow(pos1[0]-pos2[0],2) + pow(pos1[1]-pos2[1],2) + pow(pos1[2]-pos2[2],2))


class Matrix:
    def __init__(self, n):
        self._rowlist = list()
        self._size = n
        i = 0
        while i < n:
            row = [0]*n
            self._rowlist.append(row)
            i += 1

    def __str__(self):
        res = ""
        for row in self._rowlist:
            for element in row:
                res += str(element) + ' '
            res += '\n'
        return res

    def get(self, r, c):
        """Get an element with the row and column number, start from 0"""
        return self._rowlist[r][c]

    def set(self, r, c, v):
        self._rowlist[r][c] = v

    def createSubMatrix(self, i, j):
        """Create a new matrix by deleting the row i and the column j"""
        m = Matrix(self._size-1)
        x = 0
        y = 0
        while x < self._size:
            while y < self._size:
                #print("boucle: x=",x,", y=",y)
                if x < i and y < j:
                    m._rowlist[x][y] = self._rowlist[x][y]
                elif x < i and y > j:
                    m._rowlist[x][y-1] = self._rowlist[x][y]
                elif x > i and y < j:
                    m._rowlist[x-1][y] = self._rowlist[x][y]
                elif x > i and y > j:
                    m._rowlist[x-1][y-1] = self._rowlist[x][y]
                y += 1
            y = 0
            x += 1
        #print("subMatrix")
        #print("i=",i,", j=",j)
        #print(self)
        #print(m)
        return m
    

    def determinant(self):
        #print("determinant")
        #print(self)
        if self._size == 2:
            return self._rowlist[0][0]*self._rowlist[1][1] - self._rowlist[0][1]*self._rowlist[1][0]
        else:
            res = 0
            i = 0
            while i < len(self._rowlist[0]):
                res += pow(-1, i) * self._rowlist[0][i] * self.createSubMatrix(0,i).determinant()
                i += 1
            return res

    def transpose(self):
        matrix = Matrix(self._size)
        i = 0
        j = 0
        while i < matrix._size:
            while j < matrix._size:
                matrix._rowlist[i][j] = self._rowlist[j][i]
                j += 1
            j = 0
            i += 1
        return matrix

    def minor(self, i, j):
        return self.createSubMatrix(i,j).determinant()
        
    def adjoint(self):
        i = 0
        j = 0
        
        # create a matrix of cofactors
        matrix = Matrix(self._size)
        while i < self._size:
            while j < self._size:
                matrix._rowlist[i][j] = pow(-1, i+j) * self.minor(i,j)
                j += 1
            j = 0
            i += 1
        return matrix.transpose()

    def inverted(self):
        """Get an inversed copy of the matrix.
            a) Find the determinant of A -- |A|, shouldn't be 0
            b) Find the adjoint of A -- adj(A)
            c) The formula: Inv(A) = adj(A)/|A|"""
        det = self.determinant()
        if det == 0:
            print("Impossible to get inverse, det=0")
            return None
        else:
            m = self.adjoint()
            i = 0
            j = 0
            while i < m._size:
                while j < m._size:
                    m._rowlist[i][j] = m._rowlist[i][j] / det
                    j += 1
                j = 0
                i += 1
            return m

if __name__ == "__main__":
    # test for 4
    m = Matrix(4)
    m.set(0,0,1)
    m.set(0,1,3)
    m.set(0,2,1)
    m.set(0,3,1)
    
    m.set(1,0,1)
    m.set(1,1,1)
    m.set(1,2,2)
    m.set(1,3,2)
    
    m.set(2,0,2)
    m.set(2,1,3)
    m.set(2,2,4)
    m.set(2,3,4)
    
    m.set(3,0,1)
    m.set(3,1,5)
    m.set(3,2,7)
    m.set(3,3,2)
    
    print(m)
    print(m.inverted())
    
    # test for 3
    m = Matrix(3)
    m.set(0,0,1)
    m.set(0,1,3)
    m.set(0,2,1)
    
    m.set(1,0,1)
    m.set(1,1,1)
    m.set(1,2,2)
    
    m.set(2,0,2)
    m.set(2,1,3)
    m.set(2,2,4)

    print(m)
    print(m.inverted())

