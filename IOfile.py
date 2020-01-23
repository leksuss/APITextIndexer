try:
    import chardet
except ImportError:
    exit("You should install packages: chardet")

import zipfile
from xml.etree.ElementTree import XML


def read(file, file_ext):
    if file_ext in ['txt', 'md']:
        return read_textlike_file(file)
    elif file_ext == 'docx':
        return read_docx_file(file)


def read_textlike_file(file, block_size=4096):
    try:
        with open(file, 'rb') as f:
            block = f.read(block_size)
            charset = chardet.detect(block)
            if not charset['encoding']:
                return False, 'This is not a plain text file'
    except (IOError, FileNotFoundError) as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
    with open(file, 'r', encoding=charset['encoding']) as f:
        return True, f.read()


def read_docx_file(file, block_size=4096):
    word_namespace = \
        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    par = word_namespace + 'p'
    text = word_namespace + 't'
    try:
        with zipfile.ZipFile(file) as document:
            xml_content = document.read('word/document.xml')
            tree = XML(xml_content)
    except Exception as e:
        return False, str(e).replace('zip', 'docx')
    paragraphs = []
    for paragraph in tree.getiterator(par):
        texts = [node.text
                 for node in paragraph.getiterator(text)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))
    return True, '\n'.join(paragraphs)
