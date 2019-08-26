def gen_DNAset(len):
    bits=[]
    max = "0b"+(''.join(str(e) for e in ['1']*len))
    for i in range(int(max,2)):
        s =  ("{0:0"+str(len)+"b}").format(i)
        bits.append(s)
    return bits


class DNAv1(object):

    change_up_q50   = 1.52      # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    @staticmethod
    def to_query(dna):
        self = __class__
        # 4bits for trend       [0-3]
        # 4bits for prev_4-7    [4-7]
        # 8bits for prev_0-4    [8-15]
        query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & (trend_5=={}) & ".format(
                dna[0],dna[1],dna[2],dna[3],dna[4])
        for i in range(5,10):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}0) & ".format(8+4-i,op)
        for i in range(10,16,2):
            periods = 3+int(4-i/2)
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_{}<{}) & ".format(periods,self.change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}<0 & prev_{}>={}) & ".format(periods,periods,self.change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_{}>=0 & prev_{}<{}) & ".format(periods,periods,self.change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}>{}) & ".format(periods,self.change_up_q50)
        query = query[:-2]
        return query

    @staticmethod
    def to_dna(record):
        return 0

class DNAv2(object):

    amp_10_q25 = 5.98     # dataset['amp_10'].quantile(0.25)
    amp_10_q50 = 9.08     # dataset['amp_10'].quantile(0.50)
    amp_10_q75 = 13.97    # dataset['amp_10'].quantile(0.75)

    amp_60_q25 = 22.65    # dataset['amp_60'].quantile(0.25)
    amp_60_q50 = 32.88    # dataset['amp_60'].quantile(0.50)
    amp_60_q75 = 49.67    # dataset['amp_60'].quantile(0.75)

    change_up_q50   = 1.52      # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    @staticmethod
    def to_query(dna):
        self = __class__

        query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & ".format(
                dna[0],dna[1],dna[2],dna[3])

        for i,p in zip((4,6),(60,10)):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += ("(amp_"+str(p)+"<{}) & ").format(
                        eval("self.amp_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q25".format(p)),eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q50".format(p)),eval("self.amp_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(amp_"+str(p)+">{}) & ").format(
                        eval("self.amp_{}_q75".format(p)))

        for i,p in zip([8,10,12,14],[3,2,1,0]):
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_{}<{}) & ".format(p,self.change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}<0 & prev_{}>={}) & ".format(p,p,self.change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_{}>=0 & prev_{}<{}) & ".format(p,p,self.change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}>{}) & ".format(p,self.change_up_q50)

        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        return 0

class DNAv3(object):
    '''
    观察视角：6日短线，长30短10日振幅 和 趋势
    '''
    amp_10_q25 = 5.98     # dataset['amp_10'].quantile(0.25)
    amp_10_q50 = 9.08     # dataset['amp_10'].quantile(0.50)
    amp_10_q75 = 13.97    # dataset['amp_10'].quantile(0.75)

    amp_30_q25 = 13.83     # dataset['amp_10'].quantile(0.25)
    amp_30_q50 = 20.31     # dataset['amp_10'].quantile(0.50)
    amp_30_q75 = 30.52     # dataset['amp_10'].quantile(0.75)

    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    @staticmethod
    def to_query(dna):
        self = __class__

        query="(trend_20=={}) & (trend_10=={}) & ".format(dna[0],dna[1])

        for i,p in zip([2,3],[30,10]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += ("(amp_"+str(p)+"<{}) & ").format(
                        eval("self.amp_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q25".format(p)),eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q50".format(p)),eval("self.amp_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(amp_"+str(p)+">{}) & ").format(
                        eval("self.amp_{}_q75".format(p)))

        for i,p in zip([4,6,8,10,12,14],[5,4,3,2,1,0]):
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_{}<{}) & ".format(p,self.change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}<0 & prev_{}>={}) & ".format(p,p,self.change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_{}>=0 & prev_{}<{}) & ".format(p,p,self.change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}>{}) & ".format(p,self.change_up_q50)

        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        return 0


class DNAv4(object):
    '''
    观察视角：3日超细分短线 + 2日细分短线 + 3日涨跌 + 20日趋势 +振幅
    1 11 1 1 1 11 11 111 111 111
    '''
    amp_20_q25 = 13.83     # dataset['amp_20'].quantile(0.25)
    amp_20_q50 = 20.31     # dataset['amp_20'].quantile(0.50)
    amp_20_q75 = 30.52    # dataset['amp_20'].quantile(0.75)

    change_up_q75   = 2.93    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.75)
    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_up_q25   = 0.71    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.25)

    change_down_q25 = -0.75
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)
    change_down_q75 = -2.99

    @staticmethod
    def to_query(dna):
        self = __class__

        query="(trend_20=={}) & (trend_10=={}) & ".format(dna[0],dna[1])

        for i,p in zip([2,3],[30,10]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += ("(amp_"+str(p)+"<{}) & ").format(
                        eval("self.amp_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q25".format(p)),eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += ("(amp_"+str(p)+">{} & amp_"+str(p)+"<={}) & ").format(
                        eval("self.amp_{}_q50".format(p)),eval("self.amp_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(amp_"+str(p)+">{}) & ").format(
                        eval("self.amp_{}_q75".format(p)))

        for i,p in zip([4,6,8,10,12,14],[5,4,3,2,1,0]):
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_{}<{}) & ".format(p,self.change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}<0 & prev_{}>={}) & ".format(p,p,self.change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_{}>=0 & prev_{}<{}) & ".format(p,p,self.change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}>{}) & ".format(p,self.change_up_q50)

        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        return 0
