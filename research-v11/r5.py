'''
每种策略应该都对应自己的风险控制，由于买入原则不同 风险控制机制也应该不同
可以单独被训练


长策略
    下跌一个波段，前压力位
    变量：
    - 前压力位置

W底部匹配
    下跌后 反弹 再次回踩则买入

短策略
    最多持有3天
    - 瞬间超跌反弹

追涨策略
    红柱之后3日高位十字星
    吃到红柱就出来


训练模式
    入口点是 fitting()
    用基因算法动态微调参数 然后决定去留

生产模式
    入口点就是 should_buy()
'''

class strategy(object):
    def __init__(self,dataset):
        self.stop_winning = NULL
        self.stop_lossing = NULL
        return

    def should_buy(dataset):
        decision = False
        return
    def should_sell(self, dataset):
        return

    def fitting(dataset):

        pass

    def _update(self, dataset):
        return

pattern_triggers = []
def should_buy(subset):
    decision = False
    for func in pattern_triggers:
        if func(subset):
            decision = True
            break
    return decision
