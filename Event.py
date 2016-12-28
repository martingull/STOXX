class Event:

    def __init__(self, data):
        self.author = 'AllOptions'
        self.data = data
        self.event_list = []  # magnitude of event
        self.event_init = []  # when event was initiated
        self.decay = []  # identifier of event
        self.constant = 10 ** 6  # adjust dt to millisecond (increases numerical accuracy)
#        self.espd = 1.0 / 2.0

        self.event_type = ''
        self.decay_type = ''
        self.event_limit = 4.0 * 10 ** 9  # 10 sec old events are removed
        self.delay_roundtrip = 10.0 * 10 ** 4  # start event 10 micros after it is observed

        # Event specific parameters
        self.eZero_trig = 200  # trigger event traded volumes are greater than 20
        self.paraImp = []  # paramters for Impulse
        self.paraD = []  # paramters for Decay
        self.fCol = (0, 1)  # column of features to use
        self.mxEvent = 1.25  # |sum events| <= mxEvent
        self.lots_traded_trigger = 5

        self.LT_trig1 = 200
        self.LT_trig2 = 500
        self.LT_trig3 = 1000
        self.LT_trig4 = 1500
        self.LT_decay1 = 2  # 1 - 2 * milliseconds (0 @ 0.5 milliseconds)
        self.LT_decay2 = 2
        self.LT_decay3 = 2
        self.LT_decay4 = 1  # 1 - 1 * milliseconds (0 @ 1.0 milliseconds)
        self.LT_resp1 = 0.1
        self.LT_resp2 = 0.2
        self.LT_resp3 = 0.4
        self.LT_resp4 = 1.0

        # self.e2_trig1 = 10  # trigger: volumes are greater than 20
        # self.e2_trig2 = 30  # end of first trigger, start of second
        # self.e2_resp1 = 0.5  # size of shift
        # self.e2_resp2 = 1.0
        # self.e2_mean_rev1 = 0.5  # mean reversion
        # self.e2_mean_rev2 = 0.5
        # self.e2_tabletop = 0.0  # delay before signal decay starts 200.000 nanoseconds / 200 micro
        # self.e2_spread = False  # adjust with spread
        # self.e2_voladj = False  # adjust with traded volume

    def get_events(self, e):

        # Check for old event, remove event
        for i in range(len(self.event_init)-1, -1, -1):
            if self.data.tgates[e] - self.event_init[i] > self.event_limit:
                del self.event_list[i]
                del self.event_init[i]
                del self.decay[i]

        # Account for decay in events and sum total impulse
        if self.decay_type == 'linear':
            out = self.linear_decay(e)
        elif self.decay_type == 'exp':
            out = self.exponential_decay(e)
        elif self.decay_type == 'LongMemory':
            out = self.LongMemory(e)  # CHECK, Currently no LM term included.
        elif self.decay_type == 'LastTrade':
            out = self.Last_Trade_decay(e)
        else:
            print('WARNING: decay_type not recognised')

        # Check for new event, add event
        if self.event_type == 'eZero':
            self.eZero(self.data.vols[e], self.data.sellbuys[e], self.data.tgates[e], self.data.features[e, self.fCol])
        elif self.event_type == 'evntLT':
            self.evntLT(self.data.vols[e], self.data.sellbuys[e], self.data.tgates[e])

        if self.event_type == 'eOmniPresent':
            self.eOmniPresent(self.data.vols[e], self.data.sellbuys[e], self.data.tgates[e], self.data.features[e, self.fCol])

        return out

    """ Events """
    def eZero(self, trade_vol, sellbuy, timestamp, features):
        # Event is triggered if traded volume >= trigger.
        if trade_vol >= self.eZero_trig:
            if sellbuy == 'BUY':
                bs = 1
            else:
                bs = -1

            # Compute Impulse
            if len(self.paraImp) > 2:  # Multiple regression
                impulse = self.paraImp[0]  # constant/intercept term
                for p in range(1, len(self.paraImp)):
                    impulse += self.paraImp[p] * features[p-1]
                impulse = bs * impulse
            elif len(self.paraImp) == 1:  # Constant term only
                impulse = bs * self.paraImp[0]
            else:
                impulse = bs * (self.paraImp[0] + self.paraImp[1] * features)  # Simple regression

            # Compute Decay
            if len(self.paraD) > 2:
                decay = self.paraD[0]
                for p in range(1, len(self.paraD)):
                    decay += self.paraD[p] * features[p-1]
            elif len(self.paraD) == 1:
                decay = self.paraD[0]
            else:
                decay = self.paraD[0] + self.paraD[1] * features

            self.event_list.append(impulse)
            self.decay.append(decay)
            self.event_init.append(timestamp)

    def eOmniPresent(self, trade_vol, sellbuy, timestamp, features):
        # Event is triggered if traded volume >= trigger.
        if trade_vol >= self.lots_traded_trigger:
            if sellbuy == 'BUY':
                bs = 1.0
            else:
                bs = -1.0

            # Compute Impulse
            if len(self.paraImp) > 2:  # Multiple regression
                impulse = self.paraImp[0]  # constant/intercept term
                for p in range(1, len(self.paraImp)):
                    impulse += self.paraImp[p] * features[p-1]
                impulse = bs * impulse
            elif len(self.paraImp) == 1:  # Constant term only
                impulse = bs * self.paraImp[0]
            else:
                impulse = bs * (self.paraImp[0] + self.paraImp[1] * features)  # Simple regression

            # Compute Decay
            decay = self.paraD

            self.event_list.append(impulse)
            self.decay.append(decay)
            self.event_init.append(timestamp)

    def evntLT(self, trade_vol, sellbuy, timestamp):
        # LT event.
        if trade_vol >= self.LT_trig1:
            if sellbuy == 'BUY':
                bs = 1
            else:
                bs = -1

            if self.LT_trig2 > trade_vol >= self.LT_trig1:  # Bucket 1
                self.event_list.append(bs * self.LT_resp1)
                self.event_init.append(timestamp)
                self.decay.append(self.LT_decay1)
            elif self.LT_trig3 > trade_vol >= self.LT_trig2:  # Bucket 2
                self.event_list.append(bs * self.LT_resp2)
                self.event_init.append(timestamp)
                self.decay.append(self.LT_decay2)
            elif self.LT_trig4 > trade_vol >= self.LT_trig3:  # Bucket 3
                self.event_list.append(bs * self.LT_resp3)
                self.event_init.append(timestamp)
                self.decay.append(self.LT_decay3)
            elif trade_vol >= self.LT_trig4:  # Bucket 4
                self.event_list.append(bs * self.LT_resp4)
                self.event_init.append(timestamp)
                self.decay.append(self.LT_decay4)

    """ Decay """

    def LongMemory(self, e):
        #  Long Memory does not include long memory yet. To be included
        from math import exp
        out = 0.0
        for i in range(len(self.event_init)):  # Go through all events, and discount
            dt = (self.data.tgates[e] - self.event_init[i]) / self.constant
            if dt < 0:
                print('WARNING: TIMESTAMPS NOT IN ORDER, SEE Event.LongMemory, started: ' +
                      str(self.event_init[i]) + ' evaluated: ' + str(self.data.tgates[e]))
            if dt > self.delay_roundtrip / self.constant:  # Only consider signals older than 10 micros,
                if self.decay[i] < 0:  # Error handling: opt tries negative values
                    out += 10.0  # Gives a penalty
                else:
                    out += exp(-self.decay[i] * (dt - self.delay_roundtrip / self.constant)) * self.event_list[i]

        # Cap the total amount of adjustment allowed.
        if out > self.mxEvent:
            out = self.mxEvent
        if out < -self.mxEvent:
            out = -self.mxEvent

        return out

    def exponential_decay(self, e):
        from math import exp
        out = 0.0
        for i in range(len(self.event_init)):
            dt = (self.data.tgates[e] - self.event_init[i]) / self.constant
            if self.decay[i] < 0:  # Error handling, opt tries negative values
                self.decay[i] = 0
            if dt <= self.e2_tabletop:  # Decay starts after 0.2: 200,000 nano-sec
                out += self.event_list[i]
            else:
                out += exp(-self.decay[i] * dt) * self.event_list[i]

        # Cap the total amount of adjustment allowed.
        if out > self.mxEvent:
            out = self.mxEvent
        if out < -self.mxEvent:
            out = -self.mxEvent

        return out

    def linear_decay(self, e):
        out = 0.0
        for i in range(len(self.event_init)):
            dt = (self.data.tgates[e] - self.event_init[i]) / self.constant
            out += max((1 - self.decay[i] * dt), 0.0) * self.event_list[i]

        # Cap the total amount of adjustment allowed.
        if out > self.mxEvent:
            out = self.mxEvent
        if out < -self.mxEvent:
            out = -self.mxEvent

        return out

    def Last_Trade_decay(self, e):
        # Last Trade assumes linear decay, and only cares about last trade.

        if len(self.event_init) > 0:
            dt = (self.data.tgates[e] - self.event_init[-1]) / self.constant
            out = max((1 - self.decay[-1] * dt), 0.0) * self.event_list[-1]
        else:
            out = 0.0

        # Cap the total amount of adjustment allowed.
        if out > self.mxEvent:
            out = self.mxEvent
        if out < -self.mxEvent:
            out = -self.mxEvent

        return out

    # def e2_large_trade(self, trade_vol, sellbuy, timestamp, price, theo):
    #     # Event is triggered if volume1 >= trigger1 < volume2 >= trigger2.
    #     if self.e2_voladj is True:
    #         voladj = trade_vol
    #     else:
    #         voladj = 1
    #
    #     if self.e2_spread is False:
    #
    #         if self.e2_trig2 >= trade_vol >= self.e2_trig1:
    #
    #             if sellbuy == 'BUY':
    #                 self.event_list.append(self.e2_resp1 * voladj)
    #             else:
    #                 self.event_list.append(-self.e2_resp1 * voladj)
    #
    #             self.event_init.append(timestamp)
    #             self.decay.append(self.e2_mean_rev1)
    #         elif trade_vol > self.e2_trig2:
    #             if sellbuy == 'BUY':
    #                 self.event_list.append(self.e2_resp2 * voladj)
    #             else:
    #                 self.event_list.append(-self.e2_resp2 * voladj)
    #             self.event_init.append(timestamp)
    #             self.decay.append(self.e2_mean_rev2)
    #
    #     elif self.e2_spread is True:
    #         if self.e2_trig2 >= trade_vol >= self.e2_trig1:
    #             cross = self.e2_resp1 * abs(price - theo)
    #
    #             if sellbuy == 'BUY':
    #                 self.event_list.append(cross * voladj)
    #             else:
    #                 self.event_list.append(-cross * voladj)
    #
    #             self.event_init.append(timestamp)
    #             self.decay.append(self.e2_mean_rev1)
    #
    #         elif trade_vol > self.e2_trig2:
    #             cross = self.e2_resp2 * abs(price - theo)
    #             if sellbuy == 'BUY':
    #                 self.event_list.append(cross * voladj)
    #             else:
    #                 self.event_list.append(-cross * voladj)
    #             self.event_init.append(timestamp)
    #             self.decay.append(self.e2_mean_rev2)
    #     else:
    #         print('WARNING: self.e2_spread not set correctly \n')
    #
    # def smart_mid(self, ask, askvol, bid, bidvol):
    #     """ Returns smart P """
    #     if bid - ask > self.espd * 2.0 :
    #         mid = 0.5 * (bid + ask)
    #     else:
    #         mid = (bid * askvol + ask * bidvol) / (bidvol + askvol)
    #     return mid
