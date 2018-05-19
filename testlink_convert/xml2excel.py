#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from collections import OrderedDict
from xlwt import Workbook
from lxml.html import etree
import sys

pattern = re.compile(r'<p>\n</p>\n|</p>|<p>\n')


class XML2ExcelManager:

    def __init__(self, xml_file_name):
        self._tree = etree.parse(xml_file_name)
        self.root = self._tree.getroot()
        self.content = []

    def xmlnode_to_list(self, node):
        columns = (
            ("suitename", ""),
            ("casename", ""),
            ("preconditions", ""),
            ("steps", ""),
            ("expected", ""),
            ("keywords", ""),
            ("caseid", "")
        )
        line = OrderedDict(columns)
        if node.tag == 'testsuite':
            line["suitename"] = node.get("name")
            self.content.append(line)
        if node.tag == 'testcase':
            line["casename"] = node.get("name")
            line["caseid"] = node.find("externalid").text
            line["preconditions"] = node.find("preconditions").text

            for index, step in enumerate(node.findall("steps/step")):
                action = step.find("actions").text.replace('\n', '').replace('\t', '').replace('<p>', '').replace(
                    '</p>', '')
                expected = step.find("expectedresults").text.replace('\n', '').replace('\t', '').replace('<p>',
                                                                                                         '').replace(
                    '</p>', '')

                line["steps"] += "%d、%s\r\n" % (index + 1, action)
                line["expected"] += "%d、%s\r\n" % (index + 1, expected)
            line["steps"] = line["steps"][:-1]
            line["expected"] = line["expected"][:-1]
            line["keywords"] = []
            for keyword in node.findall("keywords/keyword"):
                line["keywords"].append(keyword.get("name"))
            self.content.append(line)
        for child in node.getchildren():
            self.xmlnode_to_list(child)

    def xmlnode_to_json(self, node):
        columns = (
            ("suitename", ""),
            ("casename", ""),
            ("preconditions", ""),
            ("steps", ""),
            ("expected", ""),
            ("keywords", ""),
            ("caseid", "")
        )
        line = OrderedDict(columns)
        if node.tag == 'testsuite':
            line["suitename"] = node.get("name")
            self.content.append(line)
        if node.tag == 'testcase':
            line["casename"] = node.get("name")
            line["caseid"] = node.find("externalid").text
            line["preconditions"] = node.find("preconditions").text

            for index, step in enumerate(node.findall("steps/step")):
                action = step.find("actions").text.replace('\n', '').replace('\t', '').replace('<p>', '').replace(
                    '</p>', '')
                expected = step.find("expectedresults").text.replace('\n', '').replace('\t', '').replace('<p>',
                                                                                                         '').replace(
                    '</p>', '')

                line["steps"] += "%d、%s\r\n" % (index + 1, action)
                line["expected"] += "%d、%s\r\n" % (index + 1, expected)
            line["steps"] = line["steps"][:-1]
            line["expected"] = line["expected"][:-1]
            line["keywords"] = []
            for keyword in node.findall("keywords/keyword"):
                line["keywords"].append(keyword.get("name"))
            self.content.append(line)
        for child in node.getchildren():
            self.xmlnode_to_list(child)

    def write_list_to_excel(self, excel_file_name):
        excel = Workbook()
        sheet1 = excel.add_sheet('Sheet1')
        # write title name
        row = sheet1.row(0)
        for idx, key in enumerate(self.content[0]):
            row.write(idx, key)

        for i in range(len(self.content)):
            row = sheet1.row(i + 1)  # Offset for title
            for idx, key in enumerate(self.content[i]):
                val = self.content[i][key]
                if key != "keywords":  # Because keywords is list, not string
                    val = pattern.sub('', val)
                else:
                    val = '\n'.join(val)
                row.write(idx, val)
        excel.save(excel_file_name)


if __name__ == '__main__':
    # f_xml = sys.argv[1]
    f_xml = 'data/小岛旅行管理后台.testproject-deep.xml'
    xem = XML2ExcelManager(f_xml)
    xem.xmlnode_to_list(xem.root)
    xem.write_list_to_excel('output.xls')
