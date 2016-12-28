class Simulation:
    """" PREDICTORS """
    def __init__(self, data):
        self.data = data

    """" PREDICTORS """
    def pred_theo_eZero(self, fCol):

        from statistics import mean
        from Compute import Compute
        from Event import Event
        import re

        summary = open('Parameters/fit_' + str(fCol) + '_eZero.txt', 'r')
        out = open('Predicted/pred_' + str(fCol) + '_eZero.txt', 'w')

        cmpt = Compute(self.data)
        evnt = Event(self.data)

        para = []
        for line in summary:
            if re.search('Parameters', line):
                temp = re.findall('Parameters\s\[\s?(.*)\]', line)[0].split()
                for t in temp:  # IF ERROR HERE: Check parameters file for newline commands
                    para.append(float(t))

        # Set estimation specific paramters
        evnt.paraD = para[0:int(len(para)/2)]
        evnt.paraImp = para[int(len(para)/2):]

        evnt.event_type = 'eZero'
        evnt.decay_type = 'LongMemory'
        evnt.fCol = fCol

        sqerr = []
        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.cmpt_theo_event(i, evnt)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE eZero ' + str(fCol) + ' ' + str(mean(sqerr)))

    def pred_theo_LT(self):

        from statistics import mean
        from Compute import Compute
        from Event import Event

        printfile = 'Predicted/pred_LT.txt'

        out = open(printfile, 'w')

        cmpt = Compute(self.data)
        evnt = Event(self.data)

        # Which decay function and which event type
        evnt.event_type = 'evntLT'
        evnt.decay_type = 'LastTrade'

        sqerr = []
        for i in range(len(self.data.events)-2):
            if self.data.events[i] == 'E':
                pred = cmpt.cmpt_theo_event(i, evnt)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + '\n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE LT ' + str(mean(sqerr)))

    def pred_theo_smart_mid(self):
        from Compute import Compute
        from statistics import mean

        out = open('Predicted/Pred_theo_smart_mid.txt', 'w')

        cmpt = Compute(self.data)

        sqerr = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.smart_mid(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1])
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(pred - self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE smartMid ' + str(mean(sqerr)))

    def pred_theo_weigted_mid(self):
        from Compute import Compute
        from statistics import mean

        out = open('Predicted/Pred_theo_weighted_mid.txt', 'w')

        cmpt = Compute(self.data)

        sqerr = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.vol_wght_price(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1])
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(pred - self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE WeightedMid ' + str(mean(sqerr)))

    def pred_theo_smartp(self):

        from Compute import Compute
        from statistics import mean

        out = open('Predicted/Pred_theo_smartp.txt', 'w')

        cmpt = Compute(self.data)
        sqerr = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                [b, a] = cmpt.smart_bidask(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1])
                pred = 0.5 * (b + a)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE smartP ' + str(mean(sqerr)))

    def pred_theo_midprice(self):
        from Compute import Compute
        from statistics import mean

        out = open('Predicted/Pred_theo_midprice.txt', 'w')

        cmpt = Compute(self.data)

        sqerr = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.mid_price(self.data.ask_1s[i-1], self.data.bid_1s[i-1])
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + '\n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE midprice ' + str(mean(sqerr)))

    def pred_theo_eOmniPresent(self, fCol):

        from statistics import mean
        from Compute import Compute
        from Event import Event
        import re

        summary = open('Parameters/fit_' + str(fCol) + '_eOmniPresent.txt', 'r')
        out = open('Predicted/pred_' + str(fCol) + '_eOmniPresent.txt', 'w')

        cmpt = Compute(self.data)
        evnt = Event(self.data)

        para = []
        for line in summary:
            if re.search('Parameters', line):
                temp = re.findall('Parameters\s\[\s?(.*)\]', line)[0].split()
                for t in temp:  # IF ERROR HERE: Check parameters file for newline commands
                    para.append(float(t))

        # Set estimation specific paramters
        evnt.paraD = para[0]
        evnt.paraImp = para[1:]
        # evnt.lots_traded_trigger = para[-1]

        evnt.event_type = 'eOmniPresent'
        evnt.decay_type = 'LongMemory'
        evnt.fCol = fCol

        sqerr = []
        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.cmpt_theo_event(i, evnt)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE eOmniPresent ' + str(fCol) + ' ' + str(mean(sqerr)))

    def pred_theo_HL(self):

        from statistics import mean
        from Compute import Compute
        from Event import Event
        import re

        fCol = None  # just for convention

        summary = open('Parameters/fit_' + str(fCol) + '_HiddenLiquidity.txt', 'r')
        out = open('Predicted/pred_' + str(fCol) + '_HiddenLiquidity.txt', 'w')

        cmpt = Compute(self.data)

        para = []
        for line in summary:
            if re.search('Parameters', line):
                temp = re.findall('Parameters\s\[\s?(.*)\]', line)[0].split()
                for t in temp:  # IF ERROR HERE: Check parameters file for newline commands
                    para.append(float(t))

        rho = para[0]
        M = para[1]

        sqerr = []
        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.hidden_liquitity_price(self.data.ask_1s[i-1], self.data.askvol_1s[i-1],
                                                   self.data.bid_1s[i-1], self.data.bidvol_1s[i-1], rho, M)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE HiddenLiquidity ' + ' ' + str(mean(sqerr)))

    def pred_theo_CorrBBO(self):

        from statistics import mean
        from Compute import Compute
        import re

        fCol = None  # just for convention

        summary = open('Parameters/fit_' + str(fCol) + '_CorrelatedBBO.txt', 'r')
        out = open('Predicted/pred_' + str(fCol) + '_CorrelatedBBO.txt', 'w')

        cmpt = Compute(self.data)

        for line in summary:
            if re.search('Parameters', line):
                para = float(re.findall('Parameters\s\[\s?(.*)\]', line)[0])

        sqerr = []
        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                pred = cmpt.correlated_bbo_price(self.data.ask_1s[i-1], self.data.askvol_1s[i-1],
                                                   self.data.bid_1s[i-1], self.data.bidvol_1s[i-1], para)
                out.write(str(self.data.tgates[i]) + ' ' + str(pred) + ' ' + str(self.data.prices[i]) +
                          ' ' + str(self.data.bid_1s[i]) + ' ' + str(self.data.ask_1s[i]) + ' \n')
                sqerr.append(abs(pred - self.data.prices[i]))

        print('MAE CorrelatedBBO ' + ' ' + str(mean(sqerr)))

    """" PERFORMANCE ANALYSIS """

    def perf_theo_vs_smartp(self):

        import numpy as np
        from Compute import Compute
        from Event import Event
        import re

        summary = []
        summary.append(open('Parameters/fit_()_eZero.txt', 'r'))
        summary.append(open('Parameters/fit_0_eZero.txt', 'r'))
        summary.append(open('Parameters/fit_1_eZero.txt', 'r'))
        summary.append(open('Parameters/fit_2_eZero.txt', 'r'))
        summary.append(open('Parameters/fit_(0, 1)_eZero.txt', 'r'))
        summary.append(open('Parameters/fit_(0, 1, 2)_eZero.txt', 'r'))

        out = open('Performance/MSE_2_0.txt', 'w')

        cmpt = Compute(self.data)

        events = []
        events.append(Event(self.data))  # LM
        events[0].event_type = 'evntLT'
        events[0].decay_type = 'LastTrade'

        for i in range(len(summary)):
            events.append(Event(self.data))
            # Load Parameters and settings for Large Lot
            para = []
            for line in summary[i]:
                if re.search('Parameters', line):
                    temp = re.findall('Parameters\s\[\s?(.*)\]', line)[0].split()
                    for t in temp:
                        para.append(float(t))
                if re.search('fCol', line):
                    fCol = eval(re.findall('fCol\s(.*)', line)[0])

            # Set estimation specific paramters
            events[i+1].paraD = para[0:int(len(para) / 2)]
            events[i+1].paraImp = para[int(len(para) / 2):]

            events[i+1].event_type = 'eZero'
            events[i+1].decay_type = 'LongMemory'
            events[i+1].fCol = fCol

        predMid = []
        predWght = []
        predSmart = []
        predLT = []
        predCons = []
        predVol = []
        predCross = []
        predCrossVol = []
        predVol_Cross = []
        predFull = []
        bench = []
        ind = []
        indexe = []
        pw1 = []
        b1 = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                p0 = cmpt.cmpt_theo_event(i, events[0])  # loop through all, events need to be started
                p1 = cmpt.cmpt_theo_event(i, events[1])
                p2 = cmpt.cmpt_theo_event(i, events[2])
                p3 = cmpt.cmpt_theo_event(i, events[3])
                p4 = cmpt.cmpt_theo_event(i, events[4])
                p5 = cmpt.cmpt_theo_event(i, events[5])
                p6 = cmpt.cmpt_theo_event(i, events[6])

                if self.data.vols[i-2] >= 200 and self.data.tgates[i] - self.data.tgates[i-2] <= 2.0 * 10 ** 6:
                    # ind.append(i)
                    # indexe.append(i-2)
                    # pw1.append(cmpt.smart_mid(self.data.ask_1s[i-3], self.data.askvol_1s[i-3], self.data.bid_1s[i-3], self.data.bidvol_1s[i-3]))
                    # b1.append(self.data.prices[i-2])
                    predMid.append(cmpt.mid_price(self.data.ask_1s[i-1], self.data.bid_1s[i-1]))
                    predWght.append(cmpt.smart_mid(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1]))
                    [b, a] = cmpt.smart_bidask(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1])
                    predSmart.append(0.5 * (b + a))
                    predLT.append(p0)
                    predCons.append(p1)
                    predVol.append(p2)
                    predCross.append(p3)
                    predCrossVol.append(p4)
                    predVol_Cross.append(p5)
                    predFull.append(p6)
                    bench.append(self.data.prices[i])

        eMid = np.zeros(len(predMid))
        eWght = np.zeros(len(predMid))
        eSmart = np.zeros(len(predMid))
        eLT = np.zeros(len(predMid))
        eCons = np.zeros(len(predMid))
        eVol = np.zeros(len(predMid))
        eCross = np.zeros(len(predMid))
        eCrossVol = np.zeros(len(predMid))
        eVol_Cross = np.zeros(len(predMid))
        eFull = np.zeros(len(predMid))
        # debubavg = np.zeros(len(predMid))

        for i in range(len(predMid)):
        #    debug.write(str(self.data.tgates[ind[i]]) + ' ' + str(self.data.tgates[indexe[i]]) + ' ' +
        #                str(predWght[i]) + ' ' + str(bench[i]) + ' ' + str(pw1[i]) + ' ' + str(b1[i]) + ' \n')
            eMid[i] = abs(predMid[i] - bench[i])
            eWght[i] = abs(predWght[i] - bench[i])
            eSmart[i] = abs(predSmart[i] - bench[i])
            eLT[i] = abs(predLT[i] - bench[i])
            eCons[i] = abs(predCons[i] - bench[i])
            eVol[i] = abs(predVol[i] - bench[i])
            eCross[i] = abs(predCross[i] - bench[i])
            eCrossVol[i] = abs(predCrossVol[i] - bench[i])
            eVol_Cross[i] = abs(predVol_Cross[i] - bench[i])
            eFull[i] = abs(predFull[i] - bench[i])
            # debubavg[i] = abs(pw1[i] - b1[i])
            out.write(str(eMid[i]) + ' ' + str(eWght[i]) + ' ' + str(eSmart[i]) + ' ' + str(eLT[i]) + ' ' +
                      str(eCons[i]) + ' ' + ' ' + str(eVol[i]) + ' ' + str(eCross[i]) + ' ' + str(eCrossVol[i]) +
                      str(eVol_Cross[i]) + ' ' + str(eFull[i]) + ' \n' )

        print(str(eMid.mean()) + ' \n' +
              str(eWght.mean()) + ' \n' +
              str(eSmart.mean()) + ' \n' +
              str(eLT.mean()) + ' \n' +
              str(eCons.mean()) + ' \n' +
              str(eVol.mean()) + ' \n' +
              str(eCross.mean()) + ' \n' +
              str(eCrossVol.mean()) + ' \n' +
              str(eVol_Cross.mean()) + ' \n' +
              # str(debubavg.mean()) + ' \n' +
              str(eFull.mean()))

    def perf_theo_vs_smartpOLD(self):

        import numpy as np
        from Compute import Compute
        from Event import Event
        import re

        summary = open('Parameters/fit_theo_event.txt', 'r')
        summaryCross = open('Parameters/fit_theo_spread.txt', 'r')

        out = open('Performance/MSE_2_0.txt', 'w')

        cmpt = Compute(self.data)
        evnt = Event(self.data)
        evntCross = Event(self.data)

        # Load Parameters and settings for Large Lot
        para = []
        for line in summary:
            if re.search('Parameters', line):
                temp = re.findall('Parameters\s\[\s(.*)\]', line)[0].split()
                for t in temp:
                    para.append(float(t))

        evnt.e2_spread = False
        evnt.e2_voladj = False
        evnt.e2_mean_rev1 = para[0]
        evnt.e2_resp1 = para[1]
        evnt.e2_mean_rev2 = para[2]
        evnt.e2_resp2 = para[3]

        # Load Parameters and settings for Spread adjusted
        paraCross = []
        for line in summaryCross:
            if re.search('Parameters', line):
                temp = re.findall('Parameters\s\[\s(.*)\]', line)[0].split()
                for t in temp:
                    paraCross.append(float(t))

        evntCross.e2_spread = True
        evntCross.e2_voladj = False
        evntCross.e2_mean_rev1 = paraCross[0]
        evntCross.e2_resp1 = paraCross[1]
        evntCross.e2_mean_rev2 = paraCross[2]
        evntCross.e2_resp2 = paraCross[3]



        predMid = []
        predSmart = []
        predEvent = []
        predCross = []
        bench = []

        for i in range(len(self.data.events)):
            if self.data.events[i] == 'E':
                theo = cmpt.cmpt_theo_event(i, evnt)
                theoCross = cmpt.cmpt_theo_event(i, evntCross)
                if self.data.vols[i-2] > 200 and self.data.tgates[i] - self.data.tgates[i-2] <= 2.0 * 10 ** 9:
                    predMid.append(cmpt.mid_price(self.data.ask_1s[i-1], self.data.bid_1s[i-1]))
                    predSmart.append(cmpt.smart_mid(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1]))
                    predEvent.append(theo)
                    predCross.append(theoCross)
                    bench.append(self.data.prices[i])

        eMid = np.zeros(len(predMid))
        eSmart = np.zeros(len(predMid))
        eEvent = np.zeros(len(predMid))
        eCross = np.zeros(len(predMid))

        for i in range(len(predMid)):
            eMid[i] = abs(predMid[i] - bench[i])
            eSmart[i] = abs(predSmart[i] - bench[i])
            eEvent[i] = abs(predEvent[i] - bench[i])
            eCross[i] = abs(predCross[i] - bench[i])
            out.write(str(eMid[i]) + ' ' + str(eSmart[i]) + ' ' + str(eEvent[i]) + ' ' + str(eCross[i]) + ' \n' )

        print(str(eMid.mean()) + ' \n' + str(eSmart.mean()) + ' \n' + str(eEvent.mean()) + ' \n' + str(eCross.mean()))

    # def pred_theo_multi(self):
    #     from Compute import Compute
    #     from statistics import mean
    #
    #     out = open('Predicted/Pred_theo_multi.txt', 'w')
    #
    #     cmpt = Compute(self.data)
    #
    #     sqerr = []
    #
    #     for i in range(len(self.data.events)):
    #         if self.data.events[i] == 'E':
    #             pred = cmpt.cmpt_theo_multi(i)
    #             out.write(str(pred) + ' ' + str(self.data.prices[i]) + '\n')
    #             sqerr.append(abs(pred - self.data.prices[i]))
    #
    #     print('MAE Multi ' + str(mean(sqerr)))
    #
    #
    # def pred_theo_pyramid(self):
    #     import numpy as np
    #     from Compute import Compute
    #     from Event import Event
    #     import re
    #
    #     summary = open('Parameters/fit_theo_pyramid.txt', 'r')
    #     out = open('Predicted/Pred_theo_pyramid.txt', 'w')
    #
    #     cmpt = Compute(self.data)
    #     evnt = Event(self.data)
    #
    #     para = []
    #     for line in summary:
    #         if re.search('Parameters', line):
    #             temp = re.findall('Parameters\s\[\s(.*)\]', line)[0].split()
    #             for t in temp:
    #                 para.append(float(t))
    #
    #     evnt.e2_mean_rev1 = para[0]
    #     evnt.e2_resp1 = para[1]
    #     evnt.e2_mean_rev2 = para[2]
    #     evnt.e2_resp2 = para[3]
    #
    #     pred = np.zeros(len(self.data.events))
    #     sqerr = np.zeros(len(self.data.events))
    #
    #     for i in range(len(self.data.events)):
    #         if self.data.events[i] == 'E':
    #             pred[i] = cmpt.cmpt_theo_pyramid(para[4], i, evnt, 'TEST')
    #             out.write(str(pred[i]) + ' ' + str(self.data.prices[i]) + '\n')
    #             sqerr[i] = (pred[i] - self.data.prices[i]) ** 2
    #
    #     print('MSE pyramid smartP ' + str(sqerr.mean()))


    # def pred_theo_event(self, spread=False, voladj=False, decay_type='exp', event_type='e2', printfile='pred_event.txt'):
    #     from statistics import mean
    #     from Compute import Compute
    #     from Event import Event
    #     import re
    #
    #     if spread is False and decay_type == 'exp' and event_type == 'e2':
    #         summary = open('Parameters/fit_theo_event.txt', 'r')
    #     elif spread is False and decay_type == 'linear' and event_type == 'evntLT':
    #         summary = open('Parameters/fit_theo_LT.txt', 'r')
    #     elif spread is True and decay_type == 'exp' and event_type == 'e2' and voladj is False:
    #         summary = open('Parameters/fit_theo_spread.txt', 'r')
    #     elif spread is True and decay_type == 'exp' and event_type == 'e2' and voladj is True:
    #         summary = open('Parameters/fit_theo_sprdvol.txt', 'r')
    #
    #     out = open(printfile, 'w')
    #
    #     cmpt = Compute(self.data)
    #     evnt = Event(self.data)
    #
    #     para = []
    #     for line in summary:
    #         if re.search('Parameters', line):
    #             temp = re.findall('Parameters\s\[\s(.*)\]', line)[0].split()
    #             for t in temp:
    #                 para.append(float(t))
    #
    #     # Pass specs to e2
    #     evnt.e2_mean_rev1 = para[0]
    #     evnt.e2_resp1 = para[1]
    #     evnt.e2_mean_rev2 = para[2]
    #     evnt.e2_resp2 = para[3]
    #     evnt.e2_spread = spread
    #     evnt.e2_voladj = voladj
    #
    #     # Which decay function and
    #     evnt.event_type = event_type
    #     evnt.decay_type = decay_type
    #
    #     sqerr = []
    #     for i in range(len(self.data.events) - 2):
    #         if self.data.events[i] == 'E':
    #             pred = cmpt.cmpt_theo_event(i, evnt)
    #             out.write(str(pred) + ' ' + str(self.data.prices[i]) + '\n')
    #             sqerr.append(abs(pred - self.data.prices[i]))
    #
    #     print('MAE e2 ' + str(mean(sqerr)))