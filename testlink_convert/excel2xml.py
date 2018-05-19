#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xlrd
from lxml.html import etree


input = 'output.xls'
# test_suite_name=raw_input("Input test suite name:")
# if test_suite_name=='':
# test_suite_name="Gateway VM Deployment"

f_in = xlrd.open_workbook(input)
sheet = f_in.sheet_by_index(0)

# create XML
# testsuite = etree.Element('testsuite', name=test_suite_name)

xmlroot = None

for seq in range(1, sheet.nrows):
    # print(sheet.row_values(seq))
    print(seq)
    try:
        suite_ = sheet.row_values(seq)[0]
        case_ = sheet.row_values(seq)[1]
        pre_ = sheet.row_values(seq)[2]
        step_ = sheet.row_values(seq)[3]
        expect_ = sheet.row_values(seq)[4]
        keywords_ = sheet.row_values(seq)[5]

        if suite_ != '':
            if xmlroot == None:
                xmlroot = etree.Element('testsuite', name=suite_)
                testsuite_ = xmlroot
            else:
                testsuite_ = etree.SubElement(
                    xmlroot, 'testsuite', name=suite_)
            continue
        if case_ == '':
            continue

        # To make lines
        pre_ = '<![CDATA[<p>\n' + \
            pre_.replace('\n', '</p>\n<p>\n') + '</p>\n]]>'
        step_ = '<![CDATA[<p>\n' + \
            step_.replace('\n', '</p>\n<p>\n') + '</p>\n]]>'
        expect_ = '<![CDATA[<p>\n' + \
            expect_.replace('\n', '</p>\n<p>\n') + '</p>\n]]>'

        test_case = etree.SubElement(testsuite_, 'testcase', name=case_)
        preconditions = etree.SubElement(test_case, 'preconditions')
        preconditions.text = u'{0}'.format(pre_)
        steps = etree.SubElement(test_case, 'steps')
        step = etree.SubElement(steps, 'step')
        step_number = etree.SubElement(step, 'step_number')
        step_number.text = u'1'
        actions = etree.SubElement(step, 'actions')
        actions.text = u'{0}'.format(step_)
        expectedresults = etree.SubElement(step, 'expectedresults')
        expectedresults.text = u'{0}'.format(expect_)
        keywords = etree.SubElement(test_case, 'keywords')
        keyword_list = keywords_.split('\n')
        for kw in keyword_list:
            keyword = etree.SubElement(keywords, 'keyword', name=kw)
    except Exception as e:
        print("line:", seq)
        print(str(e))
        for item in sys.exc_info():
            print(item)

s = etree.tostring(xmlroot, pretty_print=True, encoding='utf-8').decode()
s = s.replace('&lt;', '<')   # 临时强制修改，将来碰到内容中包含大于小于的可能会导致XML格式错误，导入失败。
s = s.replace('&gt;', '>')
with open('output.xml', mode='w+', encoding='utf-8') as target:
    target.write(s)
