from html.parser import HTMLParser
import unittest
from urllib.parse import urlencode
from lab import App, exercise
from practice import running, send

class MarkerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
        self.text=[]
    def handle_starttag(self,tag,attrs): self.tags.append(tag)
    def handle_data(self,data): self.text.append(data)

class OutputTests(unittest.TestCase):
    def test_html_tags_vs_literal_text(self):
        with running(App()) as port:
            query='?' + urlencode({'marker':'<b>LOCAL MARKER</b>'})
            raw=send(port,'GET','/reflect'+query)
            safe=send(port,'GET','/encoded'+query)
            first,second=MarkerParser(),MarkerParser()
            first.feed(raw[1]); second.feed(safe[1])
            self.assertIn('b',first.tags)
            self.assertNotIn('b',second.tags)
            self.assertIn('<b>LOCAL MARKER</b>',second.text)
            self.assertEqual(send(port,'GET','/text'+query)[2]['content-type'],'text/plain; charset=utf-8')
            self.assertIn("default-src 'none'",safe[2]['content-security-policy'])

    def test_ampersand_is_encoded_once_at_output(self):
        with running(App()) as port:
            value=send(port,'GET','/encoded?marker=A+%26amp%3B+B')[1]
            self.assertIn('A &amp;amp; B',value)
            parser=MarkerParser(); parser.feed(value)
            self.assertIn('A &amp; B',parser.text)

    def test_only_harmless_inputs(self):
        with running(App()) as port:
            self.assertEqual(send(port,'GET','/reflect?marker=unknown')[0],400)
            self.assertEqual(send(port,'GET','/reflect?marker=hello&marker=hello')[0],400)
            self.assertEqual(send(port,'GET','/')[0],200)
        with self.assertRaises(ValueError): exercise({'marker':'hello','modes':['unknown']})

if __name__ == '__main__': unittest.main()
