class DNAv5(object):
    '''
    观察视角：
        5 bits - trend
        4 bits - amp
        7 bits - pos

    1 1 1 11 11 111 111 111
    '''
    name = 'v5'

    amp_10_q50 = 9.09
    amp_20_q50 = 15.23
    amp_30_q50 = 20.33     # dataset['amp_20'].quantile(0.50)
    amp_60_q50 = 32.88     # dataset['amp_20'].quantile(0.50)

    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    @staticmethod
    def to_query(dna):
        self = __class__
        query="(trend_30=={}) & (trend_20=={}) & (trend_10=={}) & (trend_5=={}) & (trend_3=={}) & ".format(
                dna[0],dna[1],dna[2],dna[3],dna[4])

        for i,p in zip([5,6],[60,10]):
            if int(dna[i]) == 0:
                query += "(amp_{}<{}) & ".format(p,
                    eval("self.amp_{}_q50".format(p)))
            if int(dna[i]) == 1:
                query += "(amp_{}>={}) & ".format(p,
                    eval("self.amp_{}_q50".format(p)))


        for i,p in zip([7,8,9,10,11],[30,20,10,5,3]):
            if int(dna[i]) == 0:
                query += "(pos_{}< {}) & ".format(p,50)
            if int(dna[i]) == 1:
                query += "(pos_{}>={}) & ".format(p,50)

        for i,p in zip([12,13],[2,1]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}0) & ".format(p,op)

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
        for i,p in zip([0,1,2,3,4],[30,20,10,5,3]):
            if record['trend_{}'.format(p)] == 0:
                dna[i]=str(0)
            if record['trend_{}'.format(p)] == 1:
                dna[i]=str(1)
        for i,p in zip([5,6],[60,10]):
            if record["amp_{}".format(p)]<eval("self.amp_{}_q50".format(p)):
                dna[i]=str(0)
            if record["amp_{}".format(p)]>=eval("self.amp_{}_q50".format(p)):
                dna[i]=str(1)
        for i,p in zip([7,8,9,10,11],[30,20,10,5,3]):
            if record["pos_{}".format(p)]<50:
                dna[i]=str(0)
            if record["pos_{}".format(p)]>=50:
                dna[i]=str(1)
        for i,p in zip([12,13],[2,1]):
            if record["prev_{}".format(p)]<=0:
                dna[i]=str(0)
            if record["prev_{}".format(p)]>0:
                dna[i]=str(1)
        for i,p in zip([14],[0]):
            if record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_{}".format(p)]<=0 and record["prev_{}".format(p)]>self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)
        return "".join(dna)
