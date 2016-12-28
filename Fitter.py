class Fitter:
    """ The fitter class contains all of our model fitting algorithms. Running  a fitter such as fit_theo_eZero will
      create a file in the Parameters directory. This file contains obtained parameters etc. Hence; you only need to
      run a fitter once to get your model parameters.

      example: OBTAINING PARAMETERS FOR eZero and eOmniPresent.

          fit_instance = Fitter(DataCleaner.py instance)
          fit_instance.fit_theo_eZero(fCol=())

          Different fCol can be passed.
          () - just use constant term
          1 - use column 1 in features data provided by DataCleaner
          (0, 1) - use column 0 and 1

      example: OBTAINING PARAMETERS FOR eCEP.

          fit_instance = Fitter(DataCleaner.py instance)
          fit_instance.fit_theo_eZero(fCol=())

          Different fCol can be passed.
          () - just use constant term
          1 - use column 1 in features data provided by DataCleaner
          (0, 1) - use column 0 and 1



      """

    def __init__(self, data):
        self.data = data
        self.opt_met = 'L-BFGS-B'

    def fit_multiple_eOmniPresent(self, feature_vector):
        # Fits multiple features.
        # Example: fit models (), 1, 4 and (1, 5, 6)
        # feature_vector = [(), 1, 4, (1, 5, 6)]

        fit = Fitter(self.data)

        # Find model parameters
        from joblib import Parallel, delayed
        import multiprocessing
        num_cores = multiprocessing.cpu_count()

        if __name__ == '__main__':
            Parallel(n_jobs=num_cores)(delayed(fit.fit_theo_eOmniPresent)(i) for i in feature_vector)

    def fit_theo_eZero(self, fCol):
        # fCol - Which feature columns to use. See DataCleaner.py

        from scipy.optimize import minimize
        from Compute import Compute

        #  Initialise Event
        cmpt = Compute(self.data)
        cmpt.fCol = fCol


        if fCol == ():
            x0 = [4.0, 0]  # 1 parameter, fCol is ()
        elif isinstance(fCol, int):
            x0 = [4.0, 0.0, 0.0, 0.0]  # 2 parameter, fCol has length 1, exs (1, 2)
        elif len(fCol) == 2:
            x0 = [4.0, 0, 0, 0, 0, 0]  # 3 parameters, fCol has length 2
        elif len(fCol) == 3:
            x0 = [4.0, 0, 0, 0, 0, 0, 0, 0]

        res = minimize(cmpt.sse_theo_eZero, x0, method=self.opt_met, options={'maxiter': 125})
        res.fCol = fCol
        res.opt_met = self.opt_met

        self.print_results(res, 'eZero')

    def fit_theo_eCEP(self, events):
        # CEP initiates a different event for for every feature. Give a vector of event numbers to start a variety of events.
        # To find event numbers See DataProcessing.DataCleaner.py
        from scipy.optimize import minimize
        from Compute import Compute
        from numpy.matlib import repmat

        #  Initialise Event
        cmpt = Compute(self.data)
        cmpt.events = events

        # Set up
        x0 = repmat([4.0, 0.0], 1, len(events))
        bounds = repmat([(0.0, None), (None, None)], 1, len(events))

        res = minimize(cmpt.sse_theo_eCEP, x0, method=self.opt_met, options={'maxiter': 125}, bounds=bounds)
        # res = differential_evolution(cmpt.sse_theo_eOmniPresent, bounds)
        # res = cma.fmin(cmpt.sse_theo_eOmniPresent, x0, 0.5)
        res.fCol = events
        res.opt_met = self.opt_met

        self.print_results(res, 'eCEP')

    def fit_theo_eOmniPresent(self, fCol):
        # fCol - Which feature columns to use. See DataCleaner.py
        from scipy.optimize import minimize
        from Compute import Compute

        #  Initialise Event
        cmpt = Compute(self.data)
        cmpt.fCol = fCol

        if fCol == ():
            x0 = [4.0, 0.0]  # 1 parameter, fCol is ()
            bounds = [(0.0, None), (None, None)]
        elif isinstance(fCol, int):
            x0 = [4.0, 0.0, 0.0]  # 2 parameter, fCol has length 1
            bounds = [(0.0, None), (None, None), (None, None)]
        elif len(fCol) == 2:
            x0 = [4.0, 0.0, 0.0, 0.0]  # 3 parameters, fCol has length 2

        res = minimize(cmpt.sse_theo_eOmniPresent, x0, method=self.opt_met, options={'maxiter': 125}, bounds=bounds)
        # res = differential_evolution(cmpt.sse_theo_eOmniPresent, bounds)
        # res = cma.fmin(cmpt.sse_theo_eOmniPresent, x0, 0.5)
        res.fCol = fCol
        res.opt_met = self.opt_met

        self.print_results(res, 'eOmniPresent')

    def fit_theo_LT(self):
        # Fit the LT model using
        # DOES CURRENTLY NOY SUPPORT 4 BASKETS, ADD MORE BOUNDS
        from scipy.optimize import differential_evolution
        from Compute import Compute

        cmpt = Compute(self.data)

        bounds = [(0.0, 0.5), (0.0, 0.7), (0.0, 0.5), (0.0, 1.0)]
        res = differential_evolution(cmpt.sse_theo_LT, bounds)

        self.print_results(res, 'fit_theo_LT.txt')

    def fit_theo_HL(self):
        # fCol - Which feature columns to use. See DataCleaner.py
        from scipy.optimize import minimize
        from Compute import Compute

        #  Initialise Event
        cmpt = Compute(self.data)

        x0 = [0.0, 10]  # 1 parameter, fCol is ()
        bounds = [(-0.999, 0.999), (0, None)]

        res = minimize(cmpt.sse_theo_HL, x0, method=self.opt_met, options={'maxiter': 125}, bounds=bounds)
        res.fCol = None
        res.opt_met = self.opt_met

        self.print_results(res, 'HiddenLiquidity')

    def fit_theo_CorrBBO(self):
        # fCol - Which feature columns to use. See DataCleaner.py
        from scipy.optimize import minimize
        from Compute import Compute

        #  Initialise Event
        cmpt = Compute(self.data)

        x0 = [0.0]
        bounds = [(-0.9999, 0.9999)]

        res = minimize(cmpt.sse_theo_CorrBBO, x0, method=self.opt_met, options={'maxiter': 125}, bounds=bounds)
        res.fCol = None
        res.opt_met = self.opt_met

        self.print_results(res, 'CorrelatedBBO')

    def print_results(self, res, method):
        out = open('Parameters' + '//' + 'fit' + '_' + str(res.fCol) + '_' + method + '.txt', 'w')

        out.write('Converged ' + str(res.success) + '\n')
        out.write('Number of iterations ' + str(res.nit) + '\n')
        out.write('Method ' + method + '\n')
        out.write('OptMethod ' + res.opt_met + '\n')
        out.write('Parameters ' + str(res.x) + '\n')
        out.write('SSE ' + str(res.fun) + '\n')
        out.write('fCol ' + str(res.fCol) + '\n')
        out.write('Cause of termination: ' + str(res.message) + '\n')

    # def fit_theo_event(self):
    #     from scipy.optimize import minimize
    #     from Compute import Compute
    #
    #     cmpt = Compute(self.data)
    #
    #     x0 = [1.0, 0.2, 2.0, 0.25, 3.0, 0.25, 3.0, 0.25]
    #     res = minimize(cmpt.sse_theo_event, x0, method=self.opt_met)
    #
    #     self.print_results(res, 'fit_theo_event.txt')
    #
    #
    # def fit_theo_spread(self, resultfile='fit_theo_spread.txt'):
    #     from scipy.optimize import minimize
    #     from Compute import Compute
    #
    #     cmpt = Compute(self.data)
    #
    #     x0 = [1.0, 0.2, 2.0, 0.25, 3.0, 0.25, 3.0, 0.25]
    #     res = minimize(cmpt.sse_theo_spread, x0, method=self.opt_met)
    #
    #     self.print_results(res, resultfile)
    #
    #
    # def fit_theo_sprdvol(self, resultfile='fit_theo_sprdvol.txt'):
    #     from scipy.optimize import minimize
    #     from Compute import Compute
    #
    #     cmpt = Compute(self.data)
    #
    #     x0 = [1.0, 0.2, 2.0, 0.25, 3.0, 0.25, 3.0, 0.25]
    #     res = minimize(cmpt.sse_theo_sprdvol, x0, method=self.opt_met)
    #
    #     self.print_results(res, resultfile)
