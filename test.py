from win32com import client  
def doc2docx(doc_name,docx_name):
    """
    :doc转docx
    """
    # 首先将doc转换成docx
    word = client.Dispatch("Word.Application")
    doc = word.Documents.Open(doc_name)
    #使用参数16表示将doc转换成docx
    doc.SaveAs(docx_name,16)
    doc.Close()
    word.Quit()

if __name__ == '__main__':
    doc2docx('E:/Github/python/data/测试文稿/苏州市吴江区柳亚子纪念馆-2018.5.18-杨静-（录音）.doc','e:/a.docx')