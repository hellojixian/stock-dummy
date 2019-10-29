from .ZhuiZhangStrategy import ZhuiZhangStrategy
from .FanTanStrategy import FanTanStrategy
from .WPatternStrategy import WPatternStrategy
from .BoxPatternStrategy import BoxPatternStrategy

strategies = {
    'zhuizhang':ZhuiZhangStrategy,
    'fantan':FanTanStrategy,
    'wpattern':WPatternStrategy,
    'boxpattern':BoxPatternStrategy
}
