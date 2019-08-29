class DNAv6(object):
    '''
    观察视角：
    16bits

    4bits   trends
    2bits   ma5_bias
    2bits   ma10_bias
    2bits   ma60_bias
    2bits   prev_0
    2bits   prev_1
    2bits   prev_2
    '''
    name = 'v6'
    pos_ma_60_q25=-6.53
    pos_ma_60_q50=1.11
    pos_ma_60_q75=9.11

    pos_ma_30_q25=-4.62
    pos_ma_30_q50=0.69
    pos_ma_30_q75=6.2

    pos_ma_20_q25=-3.76
    pos_ma_20_q50=0.55
    pos_ma_20_q75=4.82

    pos_ma_10_q25=-2.55
    pos_ma_10_q50=0.28
    pos_ma_10_q75=3.08

    pos_ma_5_q25=-1.7
    pos_ma_5_q50=0.14
    pos_ma_5_q75=1.95

    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    pos_vol_10_q20=4.61
    pos_vol_10_q50=29.14
    pos_vol_10_q80=70.9

    @staticmethod
    def to_query(dna):
        self = __class__
        query="(trend_60=={})  & (trend_10=={}) & ".format(
                dna[0],dna[1])

        for i,p in zip([2,3],[1,0]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_vol_{}{}{}) & ".format(p,op,0)

        for i,p in zip([4,6],[60,20]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += "(pos_ma_{}<{}) & ".format(p,
                        eval("self.pos_ma_{}_q25".format(p)))
                if int(dna[i+1])==1:
                    # q25-50
                    query += "(pos_ma_{}>={} & pos_ma_{}<{}) & ".format(
                        p,eval("self.pos_ma_{}_q25".format(p)),p,eval("self.pos_ma_{}_q50".format(p)))
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += "(pos_ma_{}>={} & pos_ma_{}<{}) & ".format(
                        p,eval("self.pos_ma_{}_q50".format(p)),p,eval("self.pos_ma_{}_q75".format(p)))
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(pos_ma_{}>={}) & ").format(
                        p,eval("self.pos_ma_{}_q75".format(p)))

        for i,p in zip([8],[10]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    query += "(pos_vol_{}<{}) & ".format(p,self.pos_vol_10_q20)
                if int(dna[i+1])==1:
                    query += "(pos_vol_{}>={} & pos_vol_{}<{}) & ".format(p,self.pos_vol_10_q20, p,self.pos_vol_10_q50)
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    query += "(pos_vol_{}>={} & pos_vol_{}<{}) & ".format(p,self.pos_vol_10_q50, p,self.pos_vol_10_q80)
                if int(dna[i+1])==1:
                    query += ("(pos_vol_{}>={}) & ").format(p,self.pos_vol_10_q80)

        for i,p in zip([10,12,14],[2,1,0]):
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

        for i,p in zip([0,1,2,3],[60,30,20,10]):
            if record['trend_{}'.format(p)] == 0:
                dna[i]=str(0)
            if record['trend_{}'.format(p)] == 1:
                dna[i]=str(1)

        for i,p in zip([4,6,8],[60,20,5]):
            if record["pos_ma_{}".format(p)]<eval("self.pos_ma_{}_q25".format(p)):
                dna[i],dna[i+1]=str(0),str(0)
            if record["pos_ma_{}".format(p)]>=eval("self.pos_ma_{}_q25".format(p)) and record["pos_ma_{}".format(p)]<eval("self.pos_ma_{}_q50".format(p)):
                dna[i],dna[i+1]=str(0),str(1)
            if record["pos_ma_{}".format(p)]>=eval("self.pos_ma_{}_q50".format(p)) and record["pos_ma_{}".format(p)]<eval("self.pos_ma_{}_q75".format(p)):
                dna[i],dna[i+1]=str(1),str(0)
            if record["pos_ma_{}".format(p)]>=eval("self.pos_ma_{}_q75".format(p)):
                dna[i],dna[i+1]=str(1),str(1)

        for i,p in zip([10,12,14],[2,1,0]):
            if record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_{}".format(p)]<=0 and record["prev_{}".format(p)]>self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)
        return "".join(dna)
