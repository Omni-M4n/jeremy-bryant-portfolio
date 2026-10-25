"""Two local origins and a harmless colour preference."""
import argparse
from html import escape
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
import secrets
import sys
import time
from urllib.parse import parse_qs, urlencode
from practice import exact, html_reply, main, reply, running, send
ROOT = Path(__file__).resolve().parent
LAB_ID = "csrf-local"

class App:
    def __init__(self):
        self.sessions = {}

    def __call__(self, request):
        cookie=SimpleCookie()
        try:
            cookie.load(request.headers.get("cookie",""))
        except CookieError:
            return reply(400, {"error": "invalid-request"})
        sid=cookie["csrf_training"].value if "csrf_training" in cookie else ""
        self.sessions={key:value for key,value in self.sessions.items() if time.monotonic()<value["until"]}
        session=self.sessions.get(sid)
        if request.method == "GET" and request.path == "/":
            return html_reply('<!doctype html><title>Preference desk</title><h1>Preference desk</h1><p>Fictional reader only.</p><form method="post" action="/login"><button>Start a training visit</button></form><p><a href="/form">Visit form</a> | <a href="/state">Current preference</a></p>')
        if request.method == "POST" and request.path == "/login":
            self.sessions.pop(sid,None)
            sid=secrets.token_urlsafe(24)
            self.sessions[sid]={"token":secrets.token_urlsafe(24),"preference":"grey","until":time.monotonic()+600}
            status,body,headers=html_reply('<!doctype html><title>Visit started</title><p>Training visit started.</p><a href="/form">Open the preference form</a>')
            return status,body,{**headers,"Set-Cookie":f"csrf_training={sid}; Path=/; HttpOnly; SameSite=Strict"}
        if not session:
            return reply(401,{"error":"session-required"})
        if request.method == "GET" and request.path == "/state":
            return reply(200,{"preference":session["preference"]})
        if request.method == "GET" and request.path == "/token":
            return reply(200,{"token":session["token"]})
        if request.method == "GET" and request.path == "/form":
            token=escape(session["token"],quote=True)
            forms=[]
            for label,value in (("Current form",token),("Alternate form","wrong"),("Short form",None)):
                hidden='' if value is None else f'<input type="hidden" name="token" value="{value}">'
                forms.append(f'<h2>{label}</h2><form method="post" action="/protected">{hidden}<select name="preference"><option>blue</option><option>gold</option></select><button>Save</button></form>')
            return html_reply('<!doctype html><title>Visit form</title><h1>Visit form</h1>'+''.join(forms)+'<p><a href="/state">Current preference</a></p>')
        if request.method != "POST" or request.path not in {"/open","/protected"}:
            return reply(404,{"error":"route"})
        if request.headers.get("content-type") != "application/x-www-form-urlencoded":
            return reply(415,{"error":"form-required"})
        values=parse_qs(request.body.decode(),keep_blank_values=True,strict_parsing=True,max_num_fields=2)
        if set(values) not in ({"preference"},{"preference","token"}) or any(len(v)!=1 for v in values.values()) or values["preference"][0] not in ("blue","gold"):
            raise ValueError("preference form")
        if request.path == "/protected":
            token=values.get("token",[""])[0]
            if request.headers.get("origin") != request.origin or not secrets.compare_digest(token.encode(),session["token"].encode()):
                return reply(403,{"error":"csrf-check"})
        session["preference"]=values["preference"][0]
        return reply(200,{"preference":session["preference"]})

class Companion:
    def __init__(self, victim_port):
        self.victim=f"http://127.0.0.1:{victim_port}"

    def __call__(self, request):
        if request.method != "GET" or request.path != "/":
            return reply(404,{"error":"route"})
        forms=[]
        for route in ("open","protected"):
            forms.append(f'<h2>{route} route</h2><form method="post" action="{self.victim}/{route}"><input type="hidden" name="preference" value="blue"><button>Send blue preference</button></form>')
        return html_reply('<!doctype html><title>Other desk</title><h1>Other desk</h1><p>A different port is a different origin. These forms have no token.</p>'+''.join(forms))

def exercise(data):
    exact(data,"rotate requests")
    rows=data["requests"]
    if type(data["rotate"]) is not bool or not isinstance(rows,list) or not 1<=len(rows)<=5:
        raise ValueError("boolean rotate and 1-5 requests required")
    for row in rows:
        exact(row,"route preference origin token cookie")
        if row["route"] not in ("open","protected") or row["preference"] not in ("blue","gold") or row["origin"] not in ("same","other","absent") or row["token"] not in ("valid","wrong","missing","previous") or type(row["cookie"]) is not bool:
            raise ValueError("unsupported request plan")
        if row["token"]=="previous" and not data["rotate"]:
            raise ValueError("previous token needs a second visit")
    checks,evidence=[],[]
    with running(App()) as port:
        with running(Companion(port)) as companion_port:
            cookie=send(port,"POST","/login")[2]["set-cookie"].split(";",1)[0]
            previous=send(port,"GET","/token",headers={"Cookie":cookie})[1]["token"]
            if data["rotate"]:
                cookie=send(port,"POST","/login",headers={"Cookie":cookie})[2]["set-cookie"].split(";",1)[0]
            token=send(port,"GET","/token",headers={"Cookie":cookie})[1]["token"]
            companion_status=send(companion_port,"GET","/")[0]
            for row in rows:
                fields={"preference":row["preference"]}
                if row["token"]!="missing":
                    fields["token"]={"valid":token,"wrong":"wrong","previous":previous}[row["token"]]
                headers={"Content-Type":"application/x-www-form-urlencoded"}
                if row["cookie"]: headers["Cookie"]=cookie
                if row["origin"]!="absent":
                    headers["Origin"]=f"http://127.0.0.1:{port if row['origin']=='same' else companion_port}"
                status,body,_=send(port,"POST","/"+row["route"],urlencode(fields),headers)
                state=send(port,"GET","/state",headers={"Cookie":cookie})[1]["preference"]
                checks.append({"status":status,"preference_after":state})
                evidence.append({"plan":row,"status":status,"body":body,"preference_after":state,
                                 "cookie":"[redacted]" if row["cookie"] else "absent","token":"[redacted]" if row["token"]!="missing" else "absent"})
    return {"checks":checks,"evidence":evidence,"companion_page_status":companion_status,
            "browser_origin_and_cookie_behaviour":"not-observed-by-this-script"}

def serve_pair():
    parser=argparse.ArgumentParser()
    parser.add_argument("serve")
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    if not 1024<=args.port<=65534: parser.error("use port 1024-65534")
    with running(App(),args.port) as port:
        with running(Companion(port),port+1) as other:
            print(f"Preference desk: http://127.0.0.1:{port}\nOther desk: http://127.0.0.1:{other}\nCtrl+C stops both.",flush=True)
            try:
                while True: time.sleep(.2)
            except KeyboardInterrupt: pass

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="serve":
        serve_pair()
    else:
        raise SystemExit(main(ROOT,LAB_ID,App,exercise))
