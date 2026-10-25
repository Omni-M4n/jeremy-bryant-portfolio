"""Bounded text or one-pixel PPM uploads, in an owned temporary folder."""
from hashlib import sha256
from pathlib import Path
import json
import re
import secrets
import tempfile
from practice import exact, main, reply, running, send, strict_json
ROOT = Path(__file__).resolve().parent
LAB_ID = "file-upload-path"
RESERVED = {"con","prn","aux","nul", *["com"+str(i) for i in range(1,10)], *["lpt"+str(i) for i in range(1,10)]}
# plain PPM uses these six separators, including one after the final value
PPM_PIXEL = re.compile(
    r"P3[ \t\r\n\v\f]+1[ \t\r\n\v\f]+1[ \t\r\n\v\f]+255[ \t\r\n\v\f]+"
    r"([0-9]{1,3})[ \t\r\n\v\f]+([0-9]{1,3})[ \t\r\n\v\f]+"
    r"([0-9]{1,3})[ \t\r\n\v\f]+")

def validate(value):
    exact(value,"filename content_type text")
    if not all(isinstance(v,str) for v in value.values()):
        raise ValueError("text fields only")
    name, kind, text = value["filename"], value["content_type"], value["text"]
    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]{0,31})\.(txt|ppm)",name)
    if not match or match[1].lower() in RESERVED:
        raise ValueError("filename")
    payload = text.encode("utf-8")
    if not 1 <= len(payload) <= 128:
        raise ValueError("size")
    suffix = match[2]
    if suffix == "txt":
        if kind != "text/plain" or any((ord(c)<32 and c not in "\n\t") or 127<=ord(c)<=159 for c in text):
            raise ValueError("plain text")
    else:
        pixel = PPM_PIXEL.fullmatch(text)
        if kind != "image/x-portable-pixmap" or pixel is None:
            raise ValueError("one pixel PPM")
        if any(int(v)>255 for v in pixel.groups()):
            raise ValueError("colour value")
    return suffix, payload

class App:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="upload-practice-")
        self.storage = Path(self.temp.name).resolve()
        self.saved = []

    def close(self):
        self.temp.cleanup()

    def __call__(self, request):
        if request.path != "/upload" or request.method != "POST":
            return reply(404,{"error":"route"})
        if request.headers.get("content-type") != "application/json":
            return reply(415,{"error":"json-required"})
        try:
            suffix, payload = validate(strict_json(request.body))
        except (ValueError, UnicodeError):
            return reply(422,{"error":"upload-rules"})
        if len(self.saved) >= 8:
            return reply(429,{"error":"practice-cap"})
        # ignore the supplied name for storage; never form a disk path from it
        target = self.storage / (secrets.token_hex(8) + "." + suffix)
        if self.storage.is_symlink() or getattr(self.storage.stat(), "st_file_attributes", 0) & 1024 or target.resolve().parent != self.storage:
            raise ValueError("containment")
        with target.open("xb") as stream:
            stream.write(payload)
        self.saved.append(target)
        return reply(201,{"saved_name":target.name,"bytes":len(payload),"sha256":sha256(payload).hexdigest()})

def exercise(data):
    exact(data,"uploads")
    rows = data["uploads"]
    if not isinstance(rows,list) or not 1 <= len(rows) <= 5:
        raise ValueError("use 1-5 uploads")
    for row in rows:
        exact(row,"filename content_type text")
        if not all(isinstance(v,str) and len(v.encode()) <= 512 for v in row.values()):
            raise ValueError("bounded text fields required")
    app = App()
    checks, evidence = [], []
    try:
        with running(app) as port:
            for row in rows:
                status, body, _ = send(port,"POST","/upload",json.dumps(row),{"Content-Type":"application/json"})
                stored = app.storage / body["saved_name"] if status == 201 else None
                contained = stored is not None and stored.resolve().parent == app.storage
                matched = contained and stored.read_bytes() == row["text"].encode()
                checks.append({"status":status,"bytes":body.get("bytes"),"contained":contained,"content_matches":matched})
                evidence.append({"request":row,"status":status,"response":body,"stored_below_temp_root":contained})
    finally:
        app.close()
    return {"checks":checks,"evidence":evidence,"temporary_uploads_removed":not app.storage.exists()}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, App, exercise))
