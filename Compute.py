class Compute:
    """ Compute should contain methods such as price calculations or sum squared errors """
    def __init__(self, data):

        self.author = 'MartinGullaksen@AllOptions'
        self.data = data
        self.espd = 1.0 / 2.0  # Expected spread
        self.mspd = 0.4 / 2.0  # Minimum spread
        self.verbose = True
        self.fCol = ()  # tuple of column numbers

    """ Price Functions  """

    def hidden_liquitity_price(self, ask, askvol, bid, bidvol, rho, M):
        """ Hidden Liquidity:
        See Avellaneda, Reed & Stoikov (2010) Forecasting Prices in the Presence of Hidden Liquidity
        """
        from numpy import arctan
        if ask - bid > 2.0 * self.espd:
            return 0.5 * (bid + ask)
        else:
            askvol += M
            bidvol += M
            cons = ((1 + rho) / (1 - rho)) ** 0.5
            up = 0.5 * (1 - arctan(cons * ((askvol - bidvol) / (askvol + bidvol))) / arctan(cons))
            return up * ask + (1 - up) * bid

    def correlated_bbo_price(self, ask, askvol, bid, bidvol, rho):
        """ Correlated arrival rates of bids and offers:
        See Avellaneda, Reed & Stoikov (2010) Forecasting Prices in the Presence of Hidden Liquidity
        """
        from numpy import arctan
        if ask - bid > 2.0 * self.espd:
            return 0.5 * (bid + ask)
        else:
            cons = ((1 + rho) / (1 - rho)) ** 0.5
            up = 0.5 * (1 - arctan(cons * ((askvol - bidvol) / (askvol + bidvol))) / arctan(cons))
            return up * ask + (1 - up) * bid

    def vol_wght_price(self, ask, askvol, bid, bidvol):
        """ Computes mid price as in smart P, but no cap on width """
        up = bidvol / (askvol + bidvol)

        return up * ask + (1-up) * bid

    def mid_price(self, ask, bid):
        """ Computes mid price """
        return 0.5 * (bid + ask)

    def smart_mid(self, ask, askvol, bid, bidvol):
        """ Returns smart midprice """
        if ask - bid > 2.0 * self.espd:
            mid = 0.5 * (bid + ask)
        else:
            mid = (bid * askvol + ask * bidvol) / (bidvol + askvol)
        return mid

    def smart_bidask(self, ask, askvol, bid, bidvol):
        """ Returns the smart p bid and ask """
        mid = self.smart_mid(ask, askvol, bid, bidvol)

        #  Compute for smart bid
        if ask - bid > 2.0 * self.espd:
            smrtbid = mid - self.espd
        elif mid < bid + self.mspd:
            smrtbid = mid - self.mspd
        elif mid <= bid + self.espd:
            smrtbid = bid
        else:
            smrtbid = bid + ((mid - bid - self.espd) * (ask - bid - self.mspd)) / (ask - bid - self.espd)

        # Compute smart ask
        if ask - bid > 2.0 * self.espd:
            smrtask = mid + self.espd
        elif mid > ask - self.mspd:
            smrtask = mid + self.mspd
        elif mid >= ask - self.espd:
            smrtask = ask
        else:
            smrtask = bid + self.mspd + ((mid - bid) * (ask - bid - self.mspd)) / (ask - bid - self.espd)

        return smrtbid, smrtask

    """ Theoretical Price Functions """

    def cmpt_theo_event(self, e, event):
        """ Computes theoretical using order size event """
        out = self.smart_mid(self.data.ask_1s[e-1], self.data.askvol_1s[e-1], self.data.bid_1s[e-1],
                             self.data.bidvol_1s[e-1]) + event.get_events(e)
        return out

    """ Objective Functions """

    def sse_theo_HL(self, para):
        """ Returns the Sum Squared Error """

        rho = para[0]
        M = para[1]
        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.hidden_liquitity_price(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1], rho, M)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print(str(error) + ' ' + str(para) + ' Hidden Liquidity')

        return error


    def sse_theo_CorrBBO(self, para):
        """ Returns the Sum Squared Error """

        rho = para[0]
        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.correlated_bbo_price(self.data.ask_1s[i-1], self.data.askvol_1s[i-1], self.data.bid_1s[i-1], self.data.bidvol_1s[i-1], rho)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print(str(error) + ' ' + str(para) + ' Correlated BBO')

        return error

    def sse_theo_eZero(self, para):
        """ Returns the Sum Squared Error """

        from Event import Event
        evnt = Event(self.data)
        evnt.event_type = 'eZero'
        evnt.decay_type = 'LongMemory'
        evnt.fCol = self.fCol

        #  Set estimation specific paramters
        evnt.paraD = para[0:int(len(para)/2)]
        evnt.paraImp = para[int(len(para)/2):]

        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.cmpt_theo_event(i, evnt)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print(str(error) + ' ' + str(evnt.paraD) + ' ' + str(evnt.paraImp))

        return error

    def sse_theo_event(self, para):
        """ Returns the Sum Squared Error """

        from Event import Event

        evnt = Event(self.data)
        evnt.e4_mean_rev1 = para[0]
        evnt.e4_resp1 = para[1]
        evnt.e4_mean_rev2 = para[2]
        evnt.e4_resp2 = para[3]
        evnt.e4_mean_rev3 = para[4]
        evnt.e4_resp3 = para[5]
        evnt.e4_mean_rev4 = para[6]
        evnt.e4_resp4 = para[7]
        evnt.e4_spread = False
        evnt.e4_voladj = False

        evnt.event_type = 'e4'
        evnt.decay_type = 'exp'

        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.cmpt_theo_event(i, evnt)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print(str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3])
                  + ' ' + str(para[4]) + ' ' + str(para[5]) + ' ' + str(para[6]) + ' ' + str(para[7]))

        return error

    def sse_theo_LT(self, para):
        """ Returns the Sum Squared Error """

        from Event import Event

        evnt = Event(self.data)
        evnt.e2_mean_rev1 = para[0]
        evnt.e2_resp1 = para[1]
        evnt.e2_mean_rev2 = para[2]
        evnt.e2_resp2 = para[3]
        evnt.event_type = 'evntLT'
        evnt.decay_type = 'LastTrade'

        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.cmpt_theo_event(i, evnt)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print('SSE Const ' + str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3]))

        return error

    def sse_theo_eCEP(self, para):
        """ Returns the Sum Squared Error """

        from Event import Event
        evnt = Event(self.data)
        evnt.event_type = 'eOmniPresent'
        evnt.decay_type = 'LongMemory'
        evnt.fCol = self.fCol

        #  Set estimation specific paramters
        evnt.paraD = para[0]
        evnt.paraImp = para[1:]
        # evnt.lots_traded_trigger = round(para[-1])

        error = 0.0
        for i in range(int(len(self.data.events))):
            if self.data.events[i] == 'E':
                est = self.cmpt_theo_event(i, evnt)
                error += (self.data.prices[i] - est) ** 2
        if self.verbose:
            print(str(error) + ' ' + str(evnt.paraD) + ' ' + str(evnt.paraImp))

        return error


            #
    # def sse_theo_spread(self, para):
    #     """ Returns the Sum Squared Error """
    #
    #     from Event import Event
    #
    #     evnt = Event(self.data)
    #     evnt.e4_mean_rev1 = para[0]
    #     evnt.e4_resp1 = para[1]
    #     evnt.e4_mean_rev2 = para[2]
    #     evnt.e4_resp2 = para[3]
    #     evnt.e4_mean_rev3 = para[4]
    #     evnt.e4_resp3 = para[5]
    #     evnt.e4_mean_rev4 = para[6]
    #     evnt.e4_resp4 = para[7]
    #     evnt.e4_spread = True
    #     evnt.e4_voladj = False
    #
    #     evnt.event_type = 'e4'
    #     evnt.decay_type = 'exp'
    #
    #     error = 0.0
    #     for i in range(int(len(self.data.events))):
    #         if self.data.events[i] == 'E':
    #             est = self.cmpt_theo_event(i, evnt)
    #             error += (self.data.prices[i] - est) ** 2
    #     if self.verbose:
    #         print('Spread SSE ' + str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3]))
    #
    #     return error
    #
    # def sse_theo_sprdvol(self, para):
    #     """ Returns the Sum Squared Error """
    #
    #     from Event import Event
    #
    #     evnt = Event(self.data)
    #     evnt.e4_mean_rev1 = para[0]
    #     evnt.e4_resp1 = para[1]
    #     evnt.e4_mean_rev2 = para[2]
    #     evnt.e4_resp2 = para[3]
    #     evnt.e4_mean_rev3 = para[4]
    #     evnt.e4_resp3 = para[5]
    #     evnt.e4_mean_rev4 = para[6]
    #     evnt.e4_resp4 = para[7]
    #     evnt.e4_spread = True
    #     evnt.e4_voladj = True
    #
    #     evnt.event_type = 'e4'
    #     evnt.decay_type = 'exp'
    #
    #     error = 0.0
    #     for i in range(int(len(self.data.events))):
    #         if self.data.events[i] == 'E':
    #             est = self.cmpt_theo_event(i, evnt)
    #             error += (self.data.prices[i] - est) ** 2
    #     if self.verbose:
    #         print('SprdVol SSE ' + str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3]))
    #
    #     return error
    #
    # def sse_theo_multi(self, para):
    #     """ Returns the Sum Squared Error """
    #
    #     error = 0.0
    #     for i in range(int(len(self.data.events))):
    #         if self.data.events[i] == 'E':
    #             est = self.cmpt_theo_multi(para, i)
    #             error += (self.data.prices[i] - est) ** 2
    #     if self.verbose:
    #         print(str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]))
    #
    #     return error
    #
    # def sse_theo_pyramid(self, para):
    #     """ Returns the Sum Squared Error """
    #
    #     from Event import Event
    #
    #     evnt = Event(self.data)
    #     evnt.e2_mean_rev1 = para[0]
    #     evnt.e2_resp1 = para[1]
    #     evnt.e2_mean_rev2 = para[2]
    #     evnt.e2_resp2 = para[3]
    #
    #     error = 0.0
    #     for i in range(int(len(self.data.events))):
    #         if self.data.events[i] == 'E':
    #             est = self.cmpt_theo_pyramid(para[4], i, evnt, 'TRAIN')
    #             error += (self.data.prices[i] - est) ** 2
    #     if self.verbose:
    #         print(str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3]) +
    #               ' ' + str(para[4]))
    #     return error
    #
    # def sse_theo_event_enh(self, para):
    #     """ Returns the Sum Squared Error """
    #
    #     from Event import Event
    #
    #     evnt = Event(self.data)
    #     evnt.mean_rev = para[0]
    #     evnt.e1_resp = para[1]
    #
    #     error = 0.0
    #     for i in range(int(len(self.data.events))):
    #         if self.data.events[i] == 'E':
    #             est = self.cmpt_theo_event_enh(para[2:5], i, evnt)
    #             error += (self.data.prices[i] - est) ** 2
    #     if self.verbose:
    #         print(str(error) + ' ' + str(para[0]) + ' ' + str(para[1]) + ' ' + str(para[2]) + ' ' + str(para[3]) +
    #               ' ' + str(para[4]))
    #
    #     return error
    #
    #
    #
    # def cmpt_theo_multi(self, e):
    #     """ Computes theoretical using 2 order levels (enhanced bid ask) """
    #     out = 0.95 * self.smart_mid(self.data.ask_1s[e - 1], self.data.askvol_1s[e - 1], self.data.bid_1s[e - 1],
    #                                 self.data.bidvol_1s[e - 1]) + \
    #           0.05 * self.vol_wght_price(self.data.ask_2s[e - 1], self.data.askvol_2s[e - 1],
    #                                      self.data.bid_2s[e - 1], self.data.bidvol_2s[e - 1]) + \
    #           0.0 * self.vol_wght_price(self.data.ask_3s[e - 1], self.data.askvol_3s[e - 1],
    #                                     self.data.bid_3s[e - 1], self.data.bidvol_3s[e - 1])
    #     return out
    #
    #
    # def cmpt_theo_event_enh(self, theta, e, event):
    #     """ Computes theoretical using ordersize event and enhanced bid ask """
    #     out = theta[0] * self.smart_mid(self.data.ask_1s[e - 1], self.data.askvol_1s[e - 1], self.data.bid_1s[e - 1],
    #                                     self.data.bidvol_1s[e - 1]) + \
    #           theta[1] * self.vol_wght_price(self.data.ask_2s[e - 1], self.data.askvol_2s[e - 1], self.data.bid_2s[e - 1],
    #                                          self.data.bidvol_2s[e - 1]) + \
    #           theta[2] * self.vol_wght_price(self.data.ask_3s[e - 1], self.data.askvol_3s[e - 1], self.data.bid_3s[e - 1],
    #                                          self.data.bidvol_3s[e - 1]) + \
    #           event.get_events(e)
    #
    #     return out
    #
    #
    # def cmpt_theo_pyramid(self, theta, e, event, cv_stage):
    #     """ Computes theoretical using ordersize event and enhanced bid ask """
    #     if cv_stage == 'TRAIN':
    #         out = self.smart_mid(self.data.ask_1s[e - 1], self.data.askvol_1s[e - 1], self.data.bid_1s[e - 1],
    #                              self.data.bidvol_1s[e - 1]) + theta * (
    #         self.data.pyramidRatio_5[e - 1] - self.data.pyramidRatio_5avg) + event.get_events(e)
    #     elif cv_stage == 'TEST':
    #         out = self.smart_mid(self.data.ask_1s[e - 1], self.data.askvol_1s[e - 1], self.data.bid_1s[e - 1],
    #                              self.data.bidvol_1s[e - 1]) + theta * (
    #         self.data.pyramidRatio_5[e - 1] - 1) + event.get_events(e)
    #
    #     return out
    #
    #


# def hidden_liquitity_price(self, ask, askvol, bid, bidvol, M):
#     """ Hidden Liquidity:
#     See Avellaneda, Reed & Stoikov (2010) Forecasting Prices in the Presence of Hidden Liquidity
#     """
#     if ask - bid > 2.0 * self.espd:
#         return 0.5 * (bid + ask)
#     else:
#         up = (bidvol + M) / (askvol + bidvol + 2.0 * M)
#         return up * ask + (1 - up) * bid
