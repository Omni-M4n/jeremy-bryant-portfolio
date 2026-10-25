import json
import unittest
from lab import App, exercise, validate
from practice import running, send

def item(name='note.txt',text='Hello\n',kind='text/plain'):
    return {'filename':name,'text':text,'content_type':kind}

class UploadTests(unittest.TestCase):
    def test_names_and_sizes(self):
        self.assertEqual(validate(item(text='a'*128)),('txt',b'a'*128))
        self.assertEqual(validate(item(text='é'*64)),('txt',('é'*64).encode()))
        for name in ('../note.txt','a/b.txt','a\\b.txt','C:\\note.txt','/note.txt','CON.txt','com1.txt','x.txt.exe','x.TXT','x.txt:other','note.txt.'):
            with self.assertRaises(ValueError): validate(item(name))
        for text in ('','a'*129,'é'*65,'\x00'):
            with self.assertRaises(ValueError): validate(item(text=text))

    def test_one_pixel_image_rules(self):
        self.assertEqual(validate(item('pixel.ppm','P3\n1 1\n255\n0 128 255\n','image/x-portable-pixmap'))[0],'ppm')
        for text in ('Hello','P3 2 1 255 0 0 0','P3 1 1 255 0 256 0','P3 1 1 255 0 0'):
            with self.assertRaises(ValueError): validate(item('pixel.ppm',text,'image/x-portable-pixmap'))
        with self.assertRaises(ValueError): validate(item(kind='image/x-portable-pixmap'))

    def test_real_write_no_overwrite_and_cleanup(self):
        app=App()
        root=app.storage
        try:
            with running(app) as port:
                first=send(port,'POST','/upload',json.dumps(item()),{'Content-Type':'application/json'})
                second=send(port,'POST','/upload',json.dumps(item()),{'Content-Type':'application/json'})
                self.assertEqual(first[0],201)
                self.assertNotEqual(first[1]['saved_name'],second[1]['saved_name'])
                self.assertEqual((root/first[1]['saved_name']).read_bytes(),b'Hello\n')
                self.assertEqual((root/first[1]['saved_name']).resolve().parent,root)
                self.assertEqual(send(port,'POST','/upload',json.dumps(item('../note.txt')),{'Content-Type':'application/json'})[0],422)
                self.assertEqual(len(list(root.iterdir())),2)
                duplicate='{"filename":"note.txt","filename":"other.txt","content_type":"text/plain","text":"Hello"}'
                self.assertEqual(send(port,'POST','/upload',duplicate,{'Content-Type':'application/json'})[0],422)
        finally: app.close()
        self.assertFalse(root.exists())

    def test_plan_bounds_and_cap(self):
        with self.assertRaises(ValueError): exercise({'uploads':[item(text='x'*513)]})
        app=App()
        try:
            with running(app) as port:
                results=[send(port,'POST','/upload',json.dumps(item()),{'Content-Type':'application/json'})[0] for _ in range(9)]
                self.assertEqual(results,[201]*8+[429])
        finally: app.close()

    def test_ppm_separators_and_final_whitespace(self):
        for separator in ' \t\r\n\v\f':
            text = separator.join(['P3','1','1','255','0','128','255']) + separator
            self.assertEqual(validate(item('pixel.ppm',text,'image/x-portable-pixmap'))[0],'ppm')
        for separator in ('\x1c','\x1d','\x1e','\x1f','\u00a0'):
            text = separator.join(['P3','1','1','255','0','0','0']) + '\n'
            with self.assertRaises(ValueError): validate(item('pixel.ppm',text,'image/x-portable-pixmap'))
        with self.assertRaises(ValueError):
            validate(item('pixel.ppm','P3 1 1 255 0 0 0','image/x-portable-pixmap'))

    def test_rejected_ppm_writes_nothing_then_valid_upload_works(self):
        app = App()
        try:
            with running(app) as port:
                headers = {'Content-Type':'application/json'}
                bad = item('pixel.ppm','P3\x1c1\x1c1\x1c255\x1c0\x1c0\x1c0\n','image/x-portable-pixmap')
                self.assertEqual(send(port,'POST','/upload',json.dumps(bad),headers)[0],422)
                self.assertEqual(list(app.storage.iterdir()),[])
                good = item('pixel.ppm','P3 1 1 255 0 0 0\n','image/x-portable-pixmap')
                self.assertEqual(send(port,'POST','/upload',json.dumps(good),headers)[0],201)
                self.assertEqual(len(list(app.storage.iterdir())),1)
        finally: app.close()

if __name__ == '__main__': unittest.main()
