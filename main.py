
from multiprocessing import Pool
from DataProcessing import DataCleaner
from Fitter import Fitter
from Simulation import Simulation
from PerformanceMetrics import DescriptiveStatistics

vector = [15, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]

# Import training data instance
dataTrain = DataCleaner('TRAIN', merge_new_data=True)

fit = Fitter(dataTrain)
fit.fit_theo_CorrBBO()
fit.fit_theo_HL()


# fit = Fitter(dataTrain)
# # Find model parameters
# if __name__ == '__main__':
#     with Pool(processes=6) as p:
#         p.map(fit.fit_theo_eOmniPresent, vector)

# Import test data instance
dataTest = DataCleaner('TEST')

# Simulate using test data
sim = Simulation(dataTest)
sim.pred_theo_midprice()
sim.pred_theo_smartp()
sim.pred_theo_weigted_mid()
sim.pred_theo_smart_mid()
sim.pred_theo_HL()
sim.pred_theo_CorrBBO()
sim.pred_theo_LT()
# for i in vector:
#    sim.pred_theo_eOmniPresent(fCol=i)
