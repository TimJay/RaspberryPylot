'''
Short

Long ...

:author: TimJay@github
:date: 2012-09-05
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''


def range_convert(in_low, in_high, out_low, out_high, value):
    return (value - in_low) / (in_high - in_low) * (out_high - out_low) + out_low
