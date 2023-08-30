import re
from typing import List

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

    def _process_p_blank(self, p: etree.Element) -> str:
        """
        不带任何属性的p标签，内含文本
        暂时考虑异常处理
        """
        # 添加非空判定，并且string()能直接提取p标签下的所有文本，包含子标签文本
        text = p.xpath("string()") if p.xpath("string()") else ""

        skips = (
            re.compile(r"\s*更多相关内容请关注.*?"),
            re.compile(r"\s*更多相关内容请关注.*?"),
            re.compile(r"\s*更多相关资讯请关注.*?"),
            re.compile(r"\s*责任编辑.*?"),
            re.compile(r"\s*gsVideo.*?")
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

    def _process_special_tag(self, t: etree.Element) -> str:
        """
        文本都在ul/li/text
        把每个li里面的文本加入结果，有些li里面装一个a，跟小标题一样
        li.text需要非空判断
        """
        res = t.xpath("string()") if t.xpath("string()") else ""
        return res

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
                return self._process_special_tag(t=tag)
            case {"class": "GsWeTxt2", **extra}:
                return self._process_special_tag(t=tag)
            case {"class": "GsWeTxt3", **extra}:
                return self._process_special_tag(t=tag)
            case {"class": "GSWeLi", **extra}:
                return self._process_special_tag(t=tag)
            case _:  # 空字典
                return self._process_gomi()

    def get_raw_content(self):
        try:
            mid2l_con = self.html.xpath("//div[@class='Mid2L_con']")[0]
        except IndexError:
            # 若mid2l_con为空
            return ""
        raw_content = etree.tostring(mid2l_con, encoding="unicode", with_tail=True, method="html")
        return raw_content

    def get_clean_content(self) -> list[str]:
        # 正文目前来看是在Mid2L_con里面
        try:
            mid2l_con = self.html.xpath("//div[@class='Mid2L_con']")[0]
        except IndexError:
            # 若mid2l_con为空
            return [""]
        # 内容都在下面的p标签里面，div标签里面也有
        self.tag_list = mid2l_con.xpath("./child::*")
        self.res: list[str] = []
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

    def get_next_page_link(self):
        # 正文目前来看是在Mid2L_con里面
        try:
            span_element = self.html.xpath('//span[@id="pe100_page_contentpage" and contains(@class, "pagecss")]')[0]
        except IndexError:
            # 若mid2l_con为空
            return None
        a_elements = span_element.xpath('.//a')
        next_page_link = None
        if len(a_elements) > 0 and a_elements[-1].text == '下一页':
            next_page_link = a_elements[-1].get('href')

        return next_page_link

    def get_game_name(self):
        try:
            game_title = self.html.xpath('//div[@class="box_game"]//*[contains(concat(" ", normalize-space(@class), " "), " tit ")]/a/text()')[0]
        except IndexError:
            # 若为空
            return ""
        return game_title
