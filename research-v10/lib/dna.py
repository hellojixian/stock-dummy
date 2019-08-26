def gen_DNAset(len):
    bits=[]
    max = "0b"+(''.join(str(e) for e in ['1']*len))
    for i in range(int(max,2)):
        s =  ("{0:0"+str(DNA_LEN)+"b}").format(i)
        bits.append(s)
    return bits

def to_query_v1(dna):
    # 4bits for trend
    # 4bits for prev_4-7
    # 8bits for prev_0-4
    step = 2
    query="(trend_60=={}) & (trend_30=={}) & (trend_20=={}) & (trend_10=={}) & (trend_5=={}) & ".format(
            dna[0],dna[1],dna[2],dna[3],dna[4])
    for i in range(5,10):
        op='<'
        if int(dna[i])==1: op='>'
        query += "(prev_{}{}0) & ".format(8+4-i,op)
    for i in range(10,16,2):
        val, op = 0,'<'
        if int(dna[i+1])==1: val,op=-step,'<='
        if int(dna[i])==1:
            val, op = 0,'>'
            if int(dna[i+1])==1: val,op=step,'>='

        query += "(prev_{}{}{}) & ".format(3+int(4-i/2),op,val)
    query = query[:-2]
    return query

def to_dna_v1(record):
    return 0
