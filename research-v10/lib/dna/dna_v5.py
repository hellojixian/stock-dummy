class DNAv5(object):
    '''
    观察视角：
        1bit   prev_3       [x]

        1bit   prev_2       [x]
        1bit   prev_vol_2   [x]

        1bit   prev_1       [x]
        2bits  prev_vol_1   [x]

        2bits  pos_10       [x]
        2bits  pos_ma5      [x]
        2bits  prev_0       [x]
        2bits  pos_vol_0    [x]
        2bits  prev_vol_0   [x]

    '''
    name = 'v5'

    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)

    change_up_q75   = 2.93    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.75)
    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_up_q25   = 0.71    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.25)

    change_down_q25 = -0.75
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)
    change_down_q75 = -2.99

    vol_change_up_q50=29.79
    vol_change_down_q50=-26.33

    pos_ma5_up_q50 = 1.75
    pos_ma5_down_q50 = -1.66

    pos_10_q25=11.9
    pos_10_q50=50.38
    pos_10_q75=89.29

    pos_vol_10_q20=4.61
    pos_vol_10_q50=29.14
    pos_vol_10_q80=70.9

    close_q50 = 7.73

    @staticmethod
    def to_query(dna):
        self = __class__
        query=""

        for i,p in zip([0,1,2],[3,2,1]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}{}) & ".format(p,op,0)

        for i,p in zip([3],[2]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_vol_{}{}{}) & ".format(p,op,0)

        for i,p in zip([4,6],[1,0]):
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

        for i,p in zip([8],[0]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0 and int(dna[i+2])==0:
                    query += "(prev_{}<={}) & ".format(p,self.change_down_q75)
                if int(dna[i+1])==0 and int(dna[i+2])==1:
                    query += "(prev_{}>{} & prev_{}<={}) & ".format(p,self.change_down_q75, p, self.change_down_q50)
                if int(dna[i+1])==1 and int(dna[i+2])==0:
                    query += "(prev_{}>{} & prev_{}<={}) & ".format(p,self.change_down_q50, p, self.change_down_q25)
                if int(dna[i+1])==1 and int(dna[i+2])==1:
                    query += "(prev_{}>{} & prev_{}<=0) & ".format(p,self.change_down_q25,p)
            if int(dna[i]) == 1:
                if int(dna[i+1])==0 and int(dna[i+2])==0:
                    query += "(prev_{}>0 & prev_{}<={}) & ".format(p,p,self.change_up_q25)
                if int(dna[i+1])==0 and int(dna[i+2])==1:
                    query += "(prev_{}>{} & prev_{}<={}) & ".format(p,self.change_up_q25, p, self.change_up_q50)
                if int(dna[i+1])==1 and int(dna[i+2])==0:
                    query += "(prev_{}>{} & prev_{}<={}) & ".format(p,self.change_up_q50, p, self.change_up_q75)
                if int(dna[i+1])==1 and int(dna[i+2])==1:
                    query += "(prev_{}>{}) & ".format(p,self.change_up_q75)

        for i,p in zip([11],[10]):
            if int(dna[i])==0:
                query += "(pos_ma_{}<={}) & ".format(p,0)
            if int(dna[i])==1:
                query += "(pos_ma_{}>{}) & ".format(p,0)

        for i,p in zip([12],[10]):
            if int(dna[i]) == 0:
                if int(dna[i+1])==0:
                    query += "(pos_{}<{}) & ".format(p,self.pos_10_q25)
                if int(dna[i+1])==1:
                    query += "(pos_{}>={} & pos_{}<{}) & ".format(p,self.pos_10_q25, p,self.pos_10_q50)
            if int(dna[i]) == 1:
                if int(dna[i+1])==0:
                    query += "(pos_{}>={} & pos_{}<{}) & ".format(p,self.pos_10_q50, p,self.pos_10_q75)
                if int(dna[i+1])==1:
                    query += ("(pos_{}>={}) & ").format(p,self.pos_10_q75)

        for i,p in zip([14],[10]):
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

        query = query[:-2]
        return query

    @staticmethod
    def to_dna(record):
        self = __class__
        dna = list("0"*16)

        return "".join(dna)
