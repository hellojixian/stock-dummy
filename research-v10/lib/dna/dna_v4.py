class DNAv4(object):
    '''
    观察视角：3日超细分短线 + 2日细分短线 + 3日涨跌
    1 1 1 11 11 111 111 111
    '''
    name = 'v4'

    amp_20_q25 = 13.83     # dataset['amp_20'].quantile(0.25)
    amp_20_q50 = 20.31     # dataset['amp_20'].quantile(0.50)
    amp_20_q75 = 30.52     # dataset['amp_20'].quantile(0.75)

    change_up_q75   = 2.93    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.75)
    change_up_q50   = 1.52    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.5)
    change_up_q25   = 0.71    # dataset[dataset.prev_0>0]['prev_0'].quantile(0.25)

    change_down_q25 = -0.75
    change_down_q50 = -1.59   # dataset[dataset.prev_0<0]['prev_0'].quantile(0.5)
    change_down_q75 = -2.99

    @staticmethod
    def to_query(dna):
        self = __class__
        query=""

        for i,p in zip([0,1,2],[7,6,5]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}0) & ".format(p,op)

        for i,p in zip([3,5],[4,3]):
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

        for i,p in zip([7,10,13],[2,1,0]):
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
        query = query[:-2]

        return query

    @staticmethod
    def to_dna(record):
        self = __class__
        dna = list("0"*16)
        for i,p in zip([0,1,2],[7,6,5]):
            if record['prev_{}'.format(p)] <= 0:
                dna[i]=str(0)
            if record['prev_{}'.format(p)] > 0:
                dna[i]=str(1)
        for i,p in zip([3,5],[4,3]):
            if record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_{}".format(p)]<=0 and record["prev_{}".format(p)]>self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)
        for i,p in zip([7,10,13],[2,1,0]):
            if record["prev_{}".format(p)]<=self.change_down_q75:
                dna[i],dna[i+1],dna[i+2]=str(0),str(0),str(0)
            if record["prev_{}".format(p)]>self.change_down_q75 and record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1],dna[i+2]=str(0),str(0),str(1)
            if record["prev_{}".format(p)]>self.change_down_q50 and record["prev_{}".format(p)]<=self.change_down_q25:
                dna[i],dna[i+1],dna[i+2]=str(0),str(1),str(0)
            if record["prev_{}".format(p)]>self.change_down_q25 and record["prev_{}".format(p)]<=0:
                dna[i],dna[i+1],dna[i+2]=str(0),str(1),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q25:
                dna[i],dna[i+1],dna[i+2]=str(1),str(0),str(0)
            if record["prev_{}".format(p)]>self.change_up_q25 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1],dna[i+2]=str(1),str(0),str(1)
            if record["prev_{}".format(p)]>self.change_up_q50 and record["prev_{}".format(p)]<=self.change_up_q75:
                dna[i],dna[i+1],dna[i+2]=str(1),str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q75:
                dna[i],dna[i+1],dna[i+2]=str(1),str(1),str(1)
        return "".join(dna)
