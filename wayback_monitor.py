import web
import os
from ipwhois import IPWhois
import json
import time

urls = (
    "/", "index",
    "/monitor", "monitor",
    "/status", "status"
)

app = web.application(urls, globals())
application = app.wsgifunc()

template_globals = {
    'datestr': web.datestr
}
render = web.template.render("templates/", base="base", globals=template_globals)
db_url = os.getenv("DATABASE_URL") or "postgres:///wayback-monitor"
db = web.database(db_url)

def _resolve_ip(ip):
    d = IPWhois(ip).lookup_rdap()
    return {
        "asn": d['asn'],
        "asn_cidr": d['asn_cidr'],
        "asn_description": d['asn_description'],
        "asn_country_code": d['asn_country_code'],
        "data": json.dumps(d)
    }

def record_visit(ip, user_agent, http, https):
    if not ip or ip == '127.0.0.1':
        return

    d = _resolve_ip(ip)
    d['ip_address'] = ip
    d['user_agent'] = user_agent
    d['http_working'] = http
    d['https_working'] = https
    db.insert("visit", **d)

class index:
    def GET(self):
        t = time.time()
        return render.index(t=t)

class monitor:
    def GET(self):
        #ip = web.ctx.ip
	ip = web.ctx.env.get('HTTP_X_FORWARDED_FOR') or web.ctx.ip
        user_agent = web.ctx.env['HTTP_USER_AGENT']
        i = web.input(http=None, https=None)
        tf = "true", "false"
        if i.http in tf and i.https in tf:
            record_visit(ip, user_agent, i.http == 'true', i.https == 'true')
	else:
	    print >> web.debug, "bad request to monitor", i
	web.header("Content-type", "application/json")
        return "{}"

class status:
    def GET(self):
        what = "asn_description, asn_country_code, http_working, https_working, created"
        visits = db.select("visit", what=what, order="id desc", limit=500)
        return render.status(visits)

if __name__ == "__main__":
    app.run()
