# -*- coding: utf-8 -*-
from lxml import etree, html


class SafeXMLParser(etree.XMLParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('resolve_entities', False)
        super(SafeXMLParser, self).__init__(*args, **kwargs)


_ctgroup = {
    'html': {
        '_parser': html.HTMLParser,
        '_tostring_method': 'html',
    },
    'xml': {
        '_parser': SafeXMLParser,
        '_tostring_method': 'xml',
    },
}
_default_type = None


def _st(st):
    if st is None:
        return 'html'
    elif st in _ctgroup:
        return st
    else:
        raise ValueError('Invalid type: %s' % st)


def create_root_node(text, base_url=None, doc_type='html'):
    """Create root node for text using given parser class.
    """
    st = _st(doc_type or _default_type)
    parser_cls = _ctgroup[st]['_parser']
    body = text.strip().replace('\x00', '').encode('utf8') or b'<html/>'
    parser = parser_cls(recover=True, encoding='utf8')
    root = etree.fromstring(body, parser=parser, base_url=base_url)
    if root is None:
        root = etree.fromstring(b'<html/>', parser=parser, base_url=base_url)
    return root


def ele_to_string(ele):
    html_source = etree.tostring(ele, encoding='unicode')
    return html_source

