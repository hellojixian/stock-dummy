class DNAv1(object):
    name = 'v1'

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
        for i,p in zip([5,6,7,8,9],[7,6,5,4,3]):
            op='<='
            if int(dna[i])==1: op='>'
            query += "(prev_{}{}0) & ".format(p,op)

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
        for i,p in zip([0,1,2,3,4],[60,30,20,10,5]):
            if record['trend_{}'.format(p)] == 0:
                dna[i]=str(0)
            if record['trend_{}'.format(p)] == 1:
                dna[i]=str(1)
        for i,p in zip([5,6,7,8,9],[7,6,5,4,3]):
            if record["prev_{}".format(p)]<=0:
                dna[i]=str(0)
            if record["prev_{}".format(p)]>0:
                dna[i]=str(1)
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
