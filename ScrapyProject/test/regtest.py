# -*- coding:utf-8 -*-
__author__ = 'hei'

import re

# line = "booooooobbbbbbby123"
# regex_str = ".*?(b.*?b).*"
# regex_str = ".*(b.+?b).*"
# line = "study in 南京大学"
# regex_str = ".*?([\u4E00-\u9FA5]+大学)"

line = "xxx出生于2001年6月1日"
line = "xxx出生于2001/6/1"
line = "xxx出生于2001-6-1"
line = "xxx出生于2001-06-01"
# line = "xxx出生于2001-06"
regex_str = ".*出生于(\d{4}[年/-]\d{1,2}([月/-]\d{1,2}|[月/-]$|$))"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(1))