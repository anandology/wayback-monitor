import web
import os
from ipwhois import IPWhois

urls = (
    "/", "index",
    "/monitor", "monitor",
    "/status", "status"
)

app = web.application(urls, globals())
application = app.wsgifunc()

render = web.template.render("templates/")
db_url = os.getenv("DATABASE_URL") or "postgres:///wayback-monitor"
db = web.database(db_url)

def _resolve_ip(ip):
    d = IPWhois(ip).lookup_rdap()
    return {
        "asn": d['asn'],
        "asn_cidr": d['asn_cidr'],
        "asn_decription": d['asn_description'],
        "asn_country_code": d['asn_country_code'],
        "data": d
    }

def record_visit(ip, user_agent, http, https):
    if not ip or ip == '127.0.0.1':
        return

    d = _resolve_ip(ip)
    d['ip'] = ip
    d['user_agent'] = user_agent
    d['http'] = http
    d['https'] = https
    db.insert("visit", **d)

class index:
    def GET(self):
        return render.index()

class monitor:
    def GET(self):
        ip = web.ctx.ip
        user_agent = web.ctx.env['HTTP_USER_AGENT']
        i = web.input(http=None, https=None)
        tf = "true", "false"
        if i.http in tf and i.https in tf:
            record_visit(ip, user_agent, i.http == 'true', i.https == 'true')
        return ""

class status:
    def GET(self):
        return render.status()

if __name__ == "__main__":
    app.run()
