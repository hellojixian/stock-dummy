{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<style>.container { width:98% !important; }</style>"
      ],
      "text/plain": [
       "<IPython.core.display.HTML object>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "from IPython.core.display import display, HTML\n",
    "display(HTML(\"<style>.container { width:98% !important; }</style>\"))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Gen 0 :  O/r.X.,hwDN\"?%WB~x& Vw(Dy}~X~CVmacqJb+h%.tOY}_Q^Dk 2y&J\n",
      "[  5.92371024e-04   5.92311793e-08   5.92371024e-04 ...,   1.18468282e-03\n",
      "   5.92311793e-08   5.92371024e-04] 3000 3000\n",
      "Gen 1 :  7=oua\\DSAU[O3lcy8)2|}oJ\\;@7N4H|x{mD],tB$r5dRgR!kc3$M)5h\n",
      "[  4.37725691e-04   2.18851903e-08   2.18873788e-04 ...,   6.56577594e-04\n",
      "   2.18873788e-04   2.18873788e-04] 3000 3000\n",
      "Gen 2 :  v|2%Gt$MdW~+$?tefPt}.P+idiGOyAo)FttRS9&Af>\")gvtY^hVCPQ%\n",
      "[  1.69845286e-04   5.09501894e-04   3.39673590e-04 ...,   5.09501894e-04\n",
      "   3.39673590e-04   1.69828304e-08] 3000 3000\n",
      "Gen 3 :  nW)?QI:?4sG|9qQia3*ofoFDaI r=U Wrtq1B8h\".(a%}[QnSk.2yZI\n",
      "[  2.67919575e-04   4.01872664e-04   4.01872664e-04 ...,   4.01872664e-04\n",
      "   1.33966485e-04   1.33953090e-08] 3000 3000\n",
      "Gen 4 :  5%q\\aGU8\\FPeYeriXPUlngAiWh\\ t{_Vz7r\"}-P0'@d7A6n!EvI[WeE\n",
      "[ 0.000444    0.000444    0.000222   ...,  0.00055499  0.000444    0.000444  ] 3000 3000\n",
      "Gen 5 :  nos$QciTGfG|PlQPW #)}b`Wtk:2evuW!tqF.e4\"Pt:rs;BoSkrcqZ,\n",
      "[  2.81956336e-04   9.39917108e-05   9.39917108e-05 ...,   2.81956336e-04\n",
      "   2.81956336e-04   3.75938648e-04] 3000 3000\n",
      "Gen 6 :  $]=SQciKf :ePWQ{;-z)g?TFW u m&\\m1>qq.-P\"vt+yYQ/)/hr|?ek\n",
      "[  4.05447483e-04   4.86535358e-04   2.43271734e-04 ...,   8.10959837e-05\n",
      "   4.05447483e-04   3.24359609e-04] 3000 3000\n",
      "Gen 7 :  r.>$ul@sbMG>nm[/?Nl`8C=1L8GNtu5mazc E{GrHt.!@Rt pku#gHW\n",
      "[ 0.00036385  0.00043662  0.00036385 ...,  0.00021831  0.00036385\n",
      "  0.00050938] 3000 3000\n",
      "Gen 8 :  $Ik'0BiTo;SnDeuuc !]g!slYh* ms o-tXa4F}Lvt6ysC-oN]r|Ie,\n",
      "[ 0.00032712  0.00032712  0.00013085 ...,  0.0002617   0.0002617\n",
      "  0.00039254] 3000 3000\n",
      "Gen 9 :  Vs<>aOC);4GnnrliZMmEkPLC+m6aZ7JmFwcRotY:Q/cC\\e} OhI\\ser\n",
      "[ 0.00047542  0.00023771  0.00029714 ...,  0.000416    0.00035657  0.000416  ] 3000 3000\n",
      "Gen 10 :  V&AG*liF\"U>>Pj]iO5Vl`g-i+i6a[z H|Jc*kBle'c1C*etiphIa;eL\n",
      "[ 0.00032651  0.00010884  0.00038093 ...,  0.0002721   0.00021768\n",
      "  0.0002721 ] 3000 3000\n",
      "Gen 11 :  Vl^u@ziKeU>e@M]i}5Vl`g-i+i61t8 m|#P*kBle'cPC=etjph}_$Hk\n",
      "[ 0.00035156  0.00055246  0.0002009  ...,  0.00035156  0.00035156\n",
      "  0.00035156] 3000 3000\n",
      "Gen 12 :  CI)YGl}S^ [q}%wEBMAlIdritq3 tBg^a.c* ch_0y1Rge_^Dh!JWS.\n",
      "[ 0.00018508  0.00037015  0.00023134 ...,  0.00032388  0.00037015\n",
      "  0.00023134] 3000 3000\n",
      "Gen 13 :  =[su?@9*e{[emeWPz 37V$a7w31 fo.-atce rw088&rg6!:ph^aWlI\n",
      "[ 0.00029743  0.00033992  0.00029743 ...,  0.00029743  0.00038241\n",
      "  0.00050988] 3000 3000\n",
      "Gen 14 :  biDu#,i*e{2e~etPc 5L&0.%ww7 <oXmW>cf^rRe18.Rge!:pxra7ep\n",
      "[ 0.00031784  0.00027811  0.00035757 ...,  0.00043703  0.00031784\n",
      "  0.00035757] 3000 3000\n",
      "Gen 15 :  V]kuackzb5G$n%tb-)&4V@.itIc h' mamcqoDsu0zaqyet ph7RKmh\n",
      "[ 0.00040626  0.0004432   0.00025853 ...,  0.00029547  0.00036933\n",
      "  0.0003324 ] 3000 3000\n"
     ]
    },
    {
     "ename": "KeyboardInterrupt",
     "evalue": "",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mKeyboardInterrupt\u001b[0m                         Traceback (most recent call last)",
      "\u001b[0;32m<ipython-input-47-74dc66824ef0>\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[1;32m     75\u001b[0m         \u001b[0;32mif\u001b[0m \u001b[0mbest_phrase\u001b[0m \u001b[0;34m==\u001b[0m \u001b[0mTARGET_PHRASE\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     76\u001b[0m             \u001b[0;32mbreak\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 77\u001b[0;31m         \u001b[0mga\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mevolve\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[0;32m<ipython-input-47-74dc66824ef0>\u001b[0m in \u001b[0;36mevolve\u001b[0;34m(self)\u001b[0m\n\u001b[1;32m     60\u001b[0m         \u001b[0;32mfor\u001b[0m \u001b[0mparent\u001b[0m \u001b[0;32min\u001b[0m \u001b[0mpop\u001b[0m\u001b[0;34m:\u001b[0m  \u001b[0;31m# for every parent\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     61\u001b[0m             \u001b[0mchild\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mcrossover\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mparent\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mpop_copy\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 62\u001b[0;31m             \u001b[0mchild\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mmutate\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mchild\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     63\u001b[0m             \u001b[0mparent\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m]\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mchild\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     64\u001b[0m         \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mpop\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mpop\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m<ipython-input-47-74dc66824ef0>\u001b[0m in \u001b[0;36mmutate\u001b[0;34m(self, child)\u001b[0m\n\u001b[1;32m     51\u001b[0m     \u001b[0;32mdef\u001b[0m \u001b[0mmutate\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mchild\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     52\u001b[0m         \u001b[0;32mfor\u001b[0m \u001b[0mpoint\u001b[0m \u001b[0;32min\u001b[0m \u001b[0mrange\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mDNA_size\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 53\u001b[0;31m             \u001b[0;32mif\u001b[0m \u001b[0mnp\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mrandom\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mrand\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m \u001b[0;34m<\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mmutate_rate\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     54\u001b[0m                 \u001b[0mchild\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0mpoint\u001b[0m\u001b[0;34m]\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mnp\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mrandom\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mrandint\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m*\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mDNA_bound\u001b[0m\u001b[0;34m)\u001b[0m  \u001b[0;31m# choose a random ASCII index\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     55\u001b[0m         \u001b[0;32mreturn\u001b[0m \u001b[0mchild\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;31mKeyboardInterrupt\u001b[0m: "
     ]
    }
   ],
   "source": [
    "\"\"\"\n",
    "Visualize Genetic Algorithm to match the target phrase.\n",
    "Visit my tutorial website for more: https://morvanzhou.github.io/tutorials/\n",
    "\"\"\"\n",
    "import numpy as np\n",
    "\n",
    "TARGET_PHRASE = 'Visualize Genetic Algorithm to match the target phrase.'       # target DNA\n",
    "POP_SIZE = 3000                      # population size\n",
    "CROSS_RATE = 0.4                    # mating probability (DNA crossover)\n",
    "MUTATION_RATE = 0.01                # mutation probability\n",
    "N_GENERATIONS = 1000\n",
    "\n",
    "DNA_SIZE = len(TARGET_PHRASE)\n",
    "TARGET_ASCII = np.fromstring(TARGET_PHRASE, dtype=np.uint8)  # convert string to number\n",
    "ASCII_BOUND = [32, 126]\n",
    "\n",
    "\n",
    "\n",
    "class GA(object):\n",
    "    def __init__(self, DNA_size, DNA_bound, cross_rate, mutation_rate, pop_size):\n",
    "        self.DNA_size = DNA_size\n",
    "        DNA_bound[1] += 1\n",
    "        self.DNA_bound = DNA_bound\n",
    "        self.cross_rate = cross_rate\n",
    "        self.mutate_rate = mutation_rate\n",
    "        self.pop_size = pop_size\n",
    "\n",
    "        self.pop = np.random.randint(*DNA_bound, size=(pop_size, DNA_size)).astype(np.int8)  # int8 for convert to ASCII\n",
    "\n",
    "    def translateDNA(self, DNA):                 # convert to readable string\n",
    "        a = DNA.tostring().decode('ascii')\n",
    "        return a\n",
    "\n",
    "    def get_fitness(self):                      # count how many character matches\n",
    "        match_count = (self.pop == TARGET_ASCII).sum(axis=1)\n",
    "        return match_count\n",
    "\n",
    "    def select(self):\n",
    "        fitness = self.get_fitness() + 1e-4     # add a small amount to avoid all zero fitness\n",
    "        idx = np.random.choice(np.arange(self.pop_size), size=self.pop_size, replace=True, p=fitness/fitness.sum())\n",
    "        print(fitness/fitness.sum(), len(idx), self.pop_size)\n",
    "        return self.pop[idx]\n",
    "\n",
    "    def crossover(self, parent, pop):\n",
    "        if np.random.rand() < self.cross_rate:\n",
    "            i_ = np.random.randint(0, self.pop_size, size=1)                        # select another individual from pop\n",
    "            cross_points = np.random.randint(0, 2, self.DNA_size).astype(np.bool)   # choose crossover points\n",
    "            parent[cross_points] = pop[i_, cross_points]                            # mating and produce one child\n",
    "        return parent\n",
    "\n",
    "    def mutate(self, child):\n",
    "        for point in range(self.DNA_size):\n",
    "            if np.random.rand() < self.mutate_rate:\n",
    "                child[point] = np.random.randint(*self.DNA_bound)  # choose a random ASCII index\n",
    "        return child\n",
    "\n",
    "    def evolve(self):\n",
    "        pop = self.select()\n",
    "        pop_copy = pop.copy()\n",
    "        for parent in pop:  # for every parent\n",
    "            child = self.crossover(parent, pop_copy)\n",
    "            child = self.mutate(child)\n",
    "            parent[:] = child\n",
    "        self.pop = pop\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    ga = GA(DNA_size=DNA_SIZE, DNA_bound=ASCII_BOUND, cross_rate=CROSS_RATE,\n",
    "            mutation_rate=MUTATION_RATE, pop_size=POP_SIZE)\n",
    "\n",
    "    for generation in range(N_GENERATIONS):\n",
    "        fitness = ga.get_fitness()\n",
    "        best_DNA = ga.pop[np.argmax(fitness)]\n",
    "        best_phrase = ga.translateDNA(best_DNA)\n",
    "        print('Gen', generation, ': ', best_phrase)\n",
    "        if best_phrase == TARGET_PHRASE:\n",
    "            break\n",
    "        ga.evolve()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([4, 8])"
      ]
     },
     "execution_count": 53,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.random.choice(np.arange(0, 10), size=2, replace=False)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[3, 8, 2, 4, 3, 3, 3, 7, 5, 3],\n",
       "       [2, 7, 2, 7, 5, 2, 2, 3, 3, 4],\n",
       "       [7, 3, 2, 3, 5, 3, 8, 2, 4, 7],\n",
       "       [5, 6, 8, 7, 4, 8, 4, 5, 6, 2],\n",
       "       [7, 2, 5, 2, 4, 5, 6, 6, 8, 3]])"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.random.randint(*[2,9], size=(5, 10))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.6627194002930898"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.random.rand()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.5.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
