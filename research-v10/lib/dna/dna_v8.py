class DNAv8(object):
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
    name = 'v8'

    close_q25 = 4.84
    close_q50 = 7.73
    close_q75 = 12.66

    pos_vol_10_q20=4.61
    pos_vol_10_q50=29.14
    pos_vol_10_q80=70.9


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

    vol_change_up_q50=29.79
    vol_change_down_q50=-26.33

    @staticmethod
    def to_query(dna):
        self = __class__
        query="(trend_10=={}) & (trend_5=={}) & ".format(
                dna[0],dna[1])

        for i,p in zip([2],[10]):
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

        for i,p in zip([4],[0]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    # q0-25
                    query += "(close<{}) & ".format(self.close_q25)
                if int(dna[i+1])==1:
                    # q25-50
                    query += "(close>={} & close<{}) & ".format(self.close_q25, self.close_q50)
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    # q50-75
                    query += "(close>={} & close<{}) & ".format(self.close_q50, self.close_q75)
                if int(dna[i+1])==1:
                    # q75-100
                    query += ("(close>={}) & ").format(self.close_q75)

        for i,p in zip([6],[10]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(amp_{}{}{}) & ".format(p,op,eval("self.amp_{}_q50".format(p)))


        for i,p in zip([7,8],[60,5]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(pos_ma_{}{}{}) & ".format(p,op,eval("self.pos_ma_{}_q50".format(p)))

        for i,p in zip([9,10],[2,1]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}{}) & ".format(p,op,0)

        for i,p in zip([11],[0]):
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

        for i,p in zip([13],[1]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_vol_{}{}{}) & ".format(p,op,0)

        for i,p in zip([14],[0]):
            if int(dna[i])==0:
                if int(dna[i+1])==0:
                    query += "(prev_vol_{}<={}) & ".format(p,self.vol_change_down_q50)
                if int(dna[i+1])==1:
                    query += "(prev_vol_{}<=0 & prev_vol_{}>{}) & ".format(p,p,self.vol_change_down_q50)
            if int(dna[i])==1:
                if int(dna[i+1])==0:
                    query += "(prev_vol_{}>0 & prev_vol_{}<={}) & ".format(p,p,self.vol_change_up_q50)
                if int(dna[i+1])==1:
                    query += "(prev_vol_{}>{}) & ".format(p,self.vol_change_up_q50)

        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        self = __class__
        dna = list("0"*16)
        for i,p in zip([0,1],[10,5]):
            if record['trend_{}'.format(p)] == 0:
                dna[i]=str(0)
            if record['trend_{}'.format(p)] == 1:
                dna[i]=str(1)

        for i,p in zip([2],[10]):
            if record["pos_vol_{}".format(p)]<self.pos_vol_10_q20:
                dna[i],dna[i+1]=str(0),str(0)
            if record["pos_vol_{}".format(p)]>=self.pos_vol_10_q20 and record["pos_vol_{}".format(p)]<self.pos_vol_10_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["pos_vol_{}".format(p)]>=self.pos_vol_10_q50 and record["pos_vol_{}".format(p)]<self.pos_vol_10_q80:
                dna[i],dna[i+1]=str(1),str(0)
            if record["pos_vol_{}".format(p)]>=self.pos_vol_10_q80:
                dna[i],dna[i+1]=str(1),str(1)

        for i,p in zip([4],[0]):
            if record["close"]<self.close_q25:
                dna[i],dna[i+1]=str(0),str(0)
            if record["close"]>=self.close_q25 and record["close"]<self.close_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["close"]>=self.close_q50 and record["close"]<self.close_q75:
                dna[i],dna[i+1]=str(1),str(0)
            if record["close"]>=self.close_q75:
                dna[i],dna[i+1]=str(1),str(1)

        for i,p in zip([6],[10]):
            if record['amp_{}'.format(p)] <= self.amp_10_q50:
                dna[i]=str(0)
            if record['amp_{}'.format(p)] >  self.amp_10_q50:
                dna[i]=str(1)

        for i,p in zip([7,8],[60,5]):
            if record['pos_ma_{}'.format(p)] <= eval("self.pos_ma_{}_q50".format(p)):
                dna[i]=str(0)
            if record['pos_ma_{}'.format(p)] >  eval("self.pos_ma_{}_q50".format(p)):
                dna[i]=str(1)

        for i,p in zip([9,10],[2,1]):
            if record['prev_{}'.format(p)] <= 0:
                dna[i]=str(0)
            if record['prev_{}'.format(p)] >  0:
                dna[i]=str(1)

        for i,p in zip([11],[0]):
            if record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_{}".format(p)]<=0 and record["prev_{}".format(p)]>self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)

        for i,p in zip([13],[1]):
            if record['prev_vol_{}'.format(p)] <= 0:
                dna[i]=str(0)
            if record['prev_vol_{}'.format(p)] >  0:
                dna[i]=str(1)

        for i,p in zip([14],[0]):
            if record["prev_vol_{}".format(p)]<=self.vol_change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_vol_{}".format(p)]<=0 and record["prev_vol_{}".format(p)]>self.vol_change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_vol_{}".format(p)]>0 and record["prev_vol_{}".format(p)]<=self.vol_change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_vol_{}".format(p)]>self.vol_change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)
        return "".join(dna)
