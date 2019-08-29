class DNAv7(object):
    '''
    观察视角：
    16bits

    6bits   trends
    2bits   amp_60
    1bits   amp_10
    2bits   ma60_bias
    1bits   ma5_bias
    1bits   prev_2
    1bits   prev_1
    2bits   prev_0
    '''
    name = 'v7'

    close_q50 = 7.73

    amp_10_q25 = 5.98     # dataset['amp_10'].quantile(0.25)
    amp_10_q50 = 9.08     # dataset['amp_10'].quantile(0.50)
    amp_10_q75 = 13.97    # dataset['amp_10'].quantile(0.75)

    amp_60_q25 = 22.65    # dataset['amp_60'].quantile(0.25)
    amp_60_q50 = 32.88    # dataset['amp_60'].quantile(0.50)
    amp_60_q75 = 49.67    # dataset['amp_60'].quantile(0.75)

    pos_ma_60_q25=-6.53
    pos_ma_60_q50=1.11
    pos_ma_60_q75=9.11

    pos_ma_5_q25=-1.7
    pos_ma_5_q50=0.14
    pos_ma_5_q75=1.95

    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    @staticmethod
    def to_query(dna):
        self = __class__
        query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & (trend_5=={}) & ".format(
                dna[0],dna[1],dna[2],dna[3],dna[4])

        for i,p in zip([5],[0]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(close{}{}) & ".format(p,op,eval("self.close_q50".format(p)))

        for i,p in zip([6],[10]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(amp_{}{}{}) & ".format(p,op,eval("self.amp_{}_q50".format(p)))

        for i,p in zip([7],[60]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += "(amp_{}<{}) & ".format(p,
                        eval("self.amp_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += "(amp_{}>={} & amp_{}<{}) & ".format(
                        p,eval("self.amp_{}_q25".format(p)),p,eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += "(amp_{}>={} & amp_{}<{}) & ".format(
                        p,eval("self.amp_{}_q50".format(p)),p,eval("self.amp_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(amp_{}>={}) & ").format(
                        p,eval("self.amp_{}_q75".format(p)))

        for i,p in zip([9],[5]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(pos_ma_{}{}{}) & ".format(p,op,eval("self.pos_ma_{}_q50".format(p)))


        for i,p in zip([10],[60]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += "(amp_{}<{}) & ".format(p,
                        eval("self.amp_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += "(amp_{}>={} & amp_{}<{}) & ".format(
                        p,eval("self.amp_{}_q25".format(p)),p,eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += "(amp_{}>={} & amp_{}<{}) & ".format(
                        p,eval("self.amp_{}_q50".format(p)),p,eval("self.amp_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(amp_{}>={}) & ").format(
                        p,eval("self.amp_{}_q75".format(p)))

        for i,p in zip([12,13],[2,1]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}{}) & ".format(p,op,0)


        for i,p in zip([14],[0]):
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_{}<={}) & ".format(p,self.change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}<=0 & prev_{}>{}) & ".format(p,p,self.change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_{}>0 & prev_{}<={}) & ".format(p,p,self.change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_{}>{}) & ".format(p,self.change_up_q50)

        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        self = __class__
        dna = list("0"*16)

        for i,p in zip([0,1,2,3,4,5],[60,30,20,10,5,3]):
            pass
        for i,p in zip([6],[10]):pass
        for i,p in zip([7],[60]):pass
        for i,p in zip([9],[5]):pass
        for i,p in zip([10],[60]):pass
        for i,p in zip([12,13],[2,1]):
            pass
        for i,p in zip([14],[0]):
            pass
        return "".join(dna)
