def gen_DNAset(len):
    bits=[]
    max = "0b"+(''.join(str(e) for e in ['1']*len))
    for i in range(int(max,2)):
        s =  ("{0:0"+str(len)+"b}").format(i)
        bits.append(s)
    return bits
