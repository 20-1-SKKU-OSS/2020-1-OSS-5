from collections import Counter
import urllib
import random
import webbrowser
from konlpy.tag import Hannanum
from lxml import html
import pytagcloud
import sys

if sys.version_info[0] >=3:
    urlopen = urllib.request.urlopen


r = lambda: random.randint(0,255)
color = lambda: (r(), r(), r())

def get_bill_text(billnum):
    url = 'http://pokr.kr/bill/%s/text' % billnum
    response = urlopen(url).read().decode('udf-8')
    page = html.fromstring(response)
    text = page.xpath(".//div[@id='bill-secions']/pre/text()")
    return text

def get_tags(text, ntags=50, multiplier=10):
    h=Hannanum()
    nouns = h.nouns(text)
    count = Counter(nouns)
    return [{'color': color(), 'tag': n, 'size': c*multiplier }\
            for n, c in count.most_common(ntags)]

def draw_cloud(tags, filename, fontname='Noto Sans CJK', size = (800,600)):
    pytagcloud.create_tag_image(tags, filename, fontname=fontname, size=size)
    webbrowser.open(filename)

bill_num = '1904882'
text = get_bill_text(bill_num)
tags = get_tags(text)
print(tags)
draw_cloud(tags, 'wordcloud.png')

