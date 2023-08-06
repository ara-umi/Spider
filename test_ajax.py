# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/5 上午12:42
import random
import time
import urllib.parse

import requests

url = "https://db2.gamersky.com/LabelJsonpAjax.aspx?callback={callback}&jsondata={json_data}&_={timestamp_ms}"
timestamp_ms = int(time.time() * 1e3)
random_suffix = ''.join(random.choice("0123456789") for _ in range(20))  # 今天看是1830开头的，看看明天变不变
callback = f"jQuery{random_suffix}_{timestamp_ms}"
json_data = {
    "type": "updatenodelabel",
    "isCache": "true",
    "cacheTime": 60,
    "nodeId": "18",  # 不知道是什么，但它一直都是18，17错误19没记录
    "isNodeId": "true",
    "page": 111
}

json_data_quote = urllib.parse.quote(str(json_data))
url = url.format(
    callback=callback,
    json_data=json_data_quote,
    timestamp_ms=timestamp_ms
)

response = requests.get(url=url)
print(response.text)

if __name__ == "__main__":
    pass
