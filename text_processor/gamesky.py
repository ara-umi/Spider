import re
from lxml import etree
from .interface import IProcessor


class GameskyTextProcessor(IProcessor):
    encoding = "utf-8"

    def __init__(self, html: etree.HTML):
        """
        传入获取的html对象进行文本提取、文本处理
        """
        self.html = html
        self.res = None
        self.tag_list = None

    def preprocess(self, html):
        # 正文目前来看是在Mid2L_con里面
        mid2l_con = html.xpath("//div[@class='Mid2L_con']")[0]
        # 内容都在下面的p标签里面，div标签里面也有
        self.tag_list = mid2l_con.xpath("./child::*")
        self.res: list[str] = []

    def _process_p_blank(self, p: etree.Element) -> str:
        """
        不带任何属性的p标签，内含文本
        暂时考虑异常处理
        """
        # 添加非空判定
        text = p.xpath("./text()")[0] if p.xpath("./text()") else ""

        skips = (
            re.compile(r"\s*更多相关内容请关注.*?"),
            re.compile(r"\s*更多相关内容请关注.*?"),
            re.compile(r"\s*更多相关资讯请关注.*?"),
            re.compile(r"\s*责任编辑.*?")
        )
        for skip in skips:
            if skip.match(text):
                return ""

        return text

    def _process_gomi(self):
        """
        不需要的标签，refer,top等。
        """
        return ""

    def _process_p_image(self, p: etree.Element) -> str:
        """
        带有class=GsImageLabel的p标签，下面的a标签的href属性是图片地址
        """
        return p.xpath("./a/@href")[0]

    def _process_p_del_image(self):
        """
        有水印的图片直接删除
        """
        return ""

    def _process_div_h(self, d: etree.Element) -> str:
        """
        小标题
        保存div下面元素的文本，通常是div里面装一个a链接，把a的text保存下来
        div.text需要非空判断
        """
        res = ""
        if len(d.xpath(".//*")) > 0:
            for element in d:
                res += element.text if element.text else ""
        # 判断div本身文本不为空，不然索引不存在
        res += d.xpath("./text()")[0] if d.xpath("./text()") else ""
        return res

    def _process_ul(self, u: etree.Element) -> str:
        """
        文本都在ul/li/text
        把每个li里面的文本加入结果，有些li里面装一个a，跟小标题一样
        li.text需要非空判断
        """
        res = ""
        for li in u.xpath(".//*"):
            if len(li.xpath(".//*")) > 0:
                for element in li:
                    res += element.text if element.text else ""
            res += li.xpath("./text()")[0] if li.xpath("./text()") else ""
        return res

    def process_p(self, p: etree.Element) -> str:
        """
        目前包括以下情况
        1、不带任何属性的p标签，内含文本
        2、带有class=GsImageLabel的p标签，下面的a标签的href属性是图片地址

        不包括以下情况
        视频
        小标题
        ...
        """
        attribute_dict: dict = dict(p.attrib)
        match attribute_dict:
            case {"class": "GsImageLabel", **extra}:
                return self._process_p_image(p=p)
            case _:  # 空字典
                return self._process_p_blank(p=p)

    def process_tag_p(self, p: etree.Element) -> str:
        """
        带image的p删掉，有水印基本用不了。
        不带标签的p就是文本，直接保留。
        """
        attribute_dict: dict = dict(p.attrib)
        match attribute_dict:
            case {"class": "GsImageLabel", **extra}:
                return self._process_p_del_image()
            case _:  # 空字典
                return self._process_p_blank(p=p)

    def process_tag(self, tag: etree.Element) -> str:
        """
        包含div的小标题。
        """
        attribute_dict: dict = dict(tag.attrib)
        match attribute_dict:
            case {"class": "GsWeTxt1", **extra}:
                return self._process_div_h(d=tag)
            case {"class": "GsWeTxt2", **extra}:
                return self._process_div_h(d=tag)
            case {"class": "GsWeTxt3", **extra}:
                return self._process_div_h(d=tag)
            case {"class": "GSWeLi", **extra}:
                return self._process_ul(u=tag)
            case _:  # 空字典
                return self._process_gomi()

    def get_text(self):
        self.preprocess(self.html)
        for tag in self.tag_list:
            if tag.tag == 'p':
                # 专门处理p标签
                res = self.process_tag_p(p=tag)
                self.res.append(res)
            else:
                # 其余标签
                res = self.process_tag(tag=tag)
                self.res.append(res)
        return self.res