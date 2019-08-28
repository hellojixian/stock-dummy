class DNAv2(object):
    name = 'v2'

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

        for i,p in zip([8,10,12,14],[3,2,1,0]):
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
        for i,p in zip([4,6],[60,10]):
            if record["amp_{}".format(p)]<eval("self.amp_{}_q25".format(p)):
                dna[i],dna[i+1]=str(0),str(0)
            if record["amp_{}".format(p)]>=eval("self.amp_{}_q25".format(p)) and record["amp_{}".format(p)]<eval("self.amp_{}_q50".format(p)):
                dna[i],dna[i+1]=str(0),str(1)
            if record["amp_{}".format(p)]>=eval("self.amp_{}_q50".format(p)) and record["amp_{}".format(p)]<eval("self.amp_{}_q75".format(p)):
                dna[i],dna[i+1]=str(1),str(0)
            if record["amp_{}".format(p)]>=eval("self.amp_{}_q75".format(p)):
                dna[i],dna[i+1]=str(1),str(1)
        for i,p in zip([8,10,12,14],[3,2,1,0]):
            if record["prev_{}".format(p)]<=self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(0)
            if record["prev_{}".format(p)]<=0 and record["prev_{}".format(p)]>self.change_down_q50:
                dna[i],dna[i+1]=str(0),str(1)
            if record["prev_{}".format(p)]>0 and record["prev_{}".format(p)]<=self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(0)
            if record["prev_{}".format(p)]>self.change_up_q50:
                dna[i],dna[i+1]=str(1),str(1)
        return "".join(dna)
