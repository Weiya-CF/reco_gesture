from dataAcquisition import DataReceiver
from recoPipeline import RecoPipeline

print("Test begin")

rp = RecoPipeline()
rp.train("data/flat_twohands.txt", "flat")
rp.calcultatePrecision("flat")

rp.recognitionFromFile("data/final_dataset2.txt")

print("End.")