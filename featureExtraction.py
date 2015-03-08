import recoUtils
from recoDataStructure import *

class FeatureExtractor:
    """This class receives samples from DataReciver, then effectuates a segmentation and outputs a tuple"""
    def __init__(self):
        # the threshold for a segmentation
        self._seg_threshold = 5
        # a list containing lists of sample values for segmentation
        self._sample_list = list()
        # a flag to tell us whether the segmentation is done and we can retrieve the tuple
        self._seg_activated = False
        # the output data structure
        self._tuple = None
    
    def addSampleFrame(self, g):
        """Function to be called whenever a new sample frame arrives
            g --> a data frame, basically a Glove object
        """
        # calculate data for each feature
        d_hand_thumb = recoUtils.distanceOfPosition([0.0, 0.0, 0.0], g._fingers[0]._position)
        d_hand_index = recoUtils.distanceOfPosition([0.0, 0.0, 0.0], g._fingers[1]._position)
        d_hand_middle = recoUtils.distanceOfPosition([0.0, 0.0, 0.0], g._fingers[2]._position)
        d_thumb_index = recoUtils.distanceOfPosition(g._fingers[0]._position, g._fingers[1]._position)
        d_index_middle = recoUtils.distanceOfPosition(g._fingers[1]._position, g._fingers[2]._position)
        d_thumb_middle = recoUtils.distanceOfPosition(g._fingers[0]._position, g._fingers[2]._position)
        
        # add a new list of sample values
        s_list = [d_hand_thumb,d_hand_index,d_hand_middle,d_thumb_index,d_index_middle,d_thumb_middle]
        
        self._sample_list.append(s_list)

        # If we have enough samples to do a segmentation, we will
        # activate the output and create a RecoTuple
        if len(self._sample_list) == self._seg_threshold:
            self._seg_activated = True
            
            # get the average value of each feature sample
            avg_values = [0.0,0.0,0.0,0.0,0.0,0.0]
            
            for slist in self._sample_list:
                i = 0
                while i < len(slist):
                    avg_values[i] += slist[i]
                    i += 1

            if self._seg_threshold != 0:
                i = 0
                while i < len(avg_values):
                    avg_values[i] = avg_values[i]/self._seg_threshold
                    i += 1
        
            self._tuple = RecoTuple(g._timestamp,g._id,g._quality,g._l_or_r,g._finger_number, avg_values)

            print("debug: ",avg_values)
            
            # Reset the list of sample lists
            del self._sample_list[:]
            

    def getRecoTuple(self):
        self._seg_activated = False
        return self._tuple

