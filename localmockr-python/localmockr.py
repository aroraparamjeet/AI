"""
LocalMockr v2 - API Proxy & Mock Studio
Runs two HTTP servers:
  - Proxy server on port 3847  (your app points here)
  - UI  server  on port 3848   (browser dashboard)

Per-endpoint modes:
  always_network   - forward every request to the real external API
  fallback         - try external API first; if it fails use saved response
  always_mock      - always return the saved local response
"""

import sys
import os
import json
import time
import re
import threading
import webbrowser
import socket
import urllib.parse
import urllib.request
import urllib.error
import http.client
import random
import string
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# UI_HTML is injected by embed_ui.py at build time
UI_HTML = None

PROXY_PORT = 3847
UI_PORT    = 3848

def get_config_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'mocks.json')

CONFIG_PATH  = get_config_path()
_config_lock = threading.Lock()

def load_config():
    with _config_lock:
        if not os.path.exists(CONFIG_PATH):
            _write_raw({'mocks': [], 'logs': [], 'globalBaseUrl': ''})
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.setdefault('globalBaseUrl', '')
        return data

def save_config(cfg):
    with _config_lock:
        _write_raw(cfg)

def _write_raw(obj):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)

def match_path(mock_path, req_path):
    pattern = re.escape(mock_path).replace(r'\*', '.*')
    try:
        return bool(re.fullmatch(pattern, req_path))
    except re.error:
        return req_path.startswith(mock_path)

def find_mock(mocks, method, path):
    for m in mocks:
        if not m.get('enabled', True):
            continue
        if m.get('method') in ('*', method) and match_path(m.get('path', ''), path):
            return m
    return None

def apply_templates(body):
    body = body.replace('{{timestamp}}', datetime.utcnow().isoformat() + 'Z')
    body = body.replace('{{random_id}}',
        ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))
    return body

def call_external(external_url, network_timeout_ms, method, req_path, req_headers, req_body):
    base = external_url.rstrip('/')
    target = base + req_path
    timeout = max(1, int(network_timeout_ms or 8000)) / 1000
    skip = {'host', 'connection', 'transfer-encoding', 'content-length', 'accept-encoding'}
    fwd = {k: v for k, v in req_headers.items() if k.lower() not in skip}
    body_data = req_body if req_body else None
    request = urllib.request.Request(target, data=body_data, headers=fwd, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            body_bytes = resp.read()
            elapsed    = int((time.time() - t0) * 1000)
            return resp.status, dict(resp.headers), body_bytes, elapsed
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        elapsed    = int((time.time() - t0) * 1000)
        return e.code, dict(e.headers), body_bytes, elapsed

def local_response(mock):
    status       = int(mock.get('statusCode') or 200)
    content_type = mock.get('contentType') or 'application/json'
    body         = apply_templates(mock.get('responseBody') or '{}')
    return status, content_type, body.encode('utf-8')

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def _send(self, status, headers, body_bytes):
        self.send_response(status)
        skip_out = {'transfer-encoding', 'content-length', 'connection'}
        for k, v in headers.items():
            if k.lower() not in skip_out:
                try: self.send_header(k, v)
                except Exception: pass
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def _handle(self):
        parsed   = urllib.parse.urlparse(self.path)
        req_path = parsed.path
        method   = self.command
        length   = int(self.headers.get('Content-Length', 0))
        req_body = self.rfile.read(length) if length > 0 else None
        cfg  = load_config()
        mock = find_mock(cfg.get('mocks', []), method, req_path)
        log_entry = {
            'id':        str(int(time.time() * 1000)) + os.urandom(2).hex(),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'method':    method, 'path': req_path,
            'mockId':    mock['id'] if mock else None,
            'mode':      mock.get('mode', 'always_mock') if mock else 'no-rule',
        }
        if not mock:
            global_base = cfg.get('globalBaseUrl', '').rstrip('/')
            if global_base:
                try:
                    sc, hdrs, body_bytes, elapsed = call_external(
                        global_base, 8000, method, req_path, dict(self.headers), req_body)
                    self._send(sc, hdrs, body_bytes)
                    log_entry.update({'statusCode': sc, 'delayMs': elapsed, 'source': 'passthrough'})
                except Exception as e:
                    body_bytes = json.dumps({'error': str(e)}).encode()
                    self._send(503, {'Content-Type': 'application/json'}, body_bytes)
                    log_entry.update({'statusCode': 503, 'delayMs': 0, 'source': 'passthrough-error'})
            else:
                body_bytes = json.dumps({
                    'error': 'No rule configured', 'path': req_path, 'method': method,
                    'hint': 'Add a rule in LocalMockr at http://localhost:' + str(UI_PORT)
                }).encode()
                self._send(503, {'Content-Type': 'application/json'}, body_bytes)
                log_entry.update({'statusCode': 503, 'delayMs': 0, 'source': 'no-rule'})
            _append_log(log_entry)
            return

        mode             = mock.get('mode', 'always_mock')
        configured_delay = int(mock.get('delayMs') or 0)
        external_url     = mock.get('externalUrl') or cfg.get('globalBaseUrl', '')
        timeout_ms       = int(mock.get('networkTimeoutMs') or 8000)
        source = 'unknown'; status = 200
        resp_hdrs = {'Content-Type': 'application/json'}; body_bytes = b'{}'

        if mode == 'always_network':
            if not external_url:
                status = 503; body_bytes = json.dumps({'error': 'No external URL configured'}).encode()
                source = 'config-error'
            else:
                try:
                    sc, hdrs, body_bytes, _ = call_external(
                        external_url, timeout_ms, method, req_path, dict(self.headers), req_body)
                    status = sc; resp_hdrs = hdrs; source = 'network'
                except Exception as e:
                    status = 503; source = 'network-error'
                    body_bytes = json.dumps({'error': 'External API unreachable', 'detail': str(e)}).encode()
        elif mode == 'fallback':
            network_ok = False
            if external_url:
                try:
                    sc, hdrs, body_bytes, _ = call_external(
                        external_url, timeout_ms, method, req_path, dict(self.headers), req_body)
                    status = sc; resp_hdrs = hdrs; source = 'network'; network_ok = True
                except Exception: pass
            if not network_ok:
                status, ct, body_bytes = local_response(mock)
                resp_hdrs = {'Content-Type': ct, 'X-LocalMockr-Fallback': 'true'}
                source = 'mock-fallback'
        else:
            status, ct, body_bytes = local_response(mock)
            resp_hdrs = {'Content-Type': ct}; source = 'mock'

        forced = mock.get('forceStatusCode')
        if forced and int(forced) > 0: status = int(forced)
        if configured_delay > 0: time.sleep(configured_delay / 1000)
        resp_hdrs['X-LocalMockr-Mode']   = mode
        resp_hdrs['X-LocalMockr-Source'] = source
        resp_hdrs['X-LocalMockr-Delay']  = str(configured_delay)
        self._send(status, resp_hdrs, body_bytes)
        log_entry.update({'statusCode': status, 'delayMs': configured_delay, 'source': source})
        _append_log(log_entry)

    def do_GET(self):     self._handle()
    def do_POST(self):    self._handle()
    def do_PUT(self):     self._handle()
    def do_DELETE(self):  self._handle()
    def do_PATCH(self):   self._handle()
    def do_HEAD(self):    self._handle()
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

def _append_log(entry):
    cfg = load_config()
    cfg.setdefault('logs', []).insert(0, entry)
    cfg['logs'] = cfg['logs'][:500]
    save_config(cfg)

class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    def _json(self, code, obj):
        body = json.dumps(obj, indent=2).encode('utf-8')
        self.send_response(code); self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length).decode('utf-8') if length else '{}'
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ('/', '/index.html', ''):
            html = UI_HTML.encode('utf-8')
            self.send_response(200); self._cors()
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers(); self.wfile.write(html); return
        if path == '/api/mocks': self._json(200, load_config().get('mocks', [])); return
        if path == '/api/logs':  self._json(200, load_config().get('logs', [])); return
        if path == '/api/settings':
            cfg = load_config()
            self._json(200, {'globalBaseUrl': cfg.get('globalBaseUrl', '')}); return
        self._json(404, {'error': 'not found'})
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/api/mocks':
            mock = json.loads(self._read_body())
            mock['id'] = 'mock_' + str(int(time.time() * 1000))
            mock['createdAt'] = datetime.utcnow().isoformat() + 'Z'
            mock.setdefault('enabled', True); mock.setdefault('mode', 'always_mock')
            cfg = load_config(); cfg.setdefault('mocks', []).append(mock)
            save_config(cfg); self._json(201, mock); return
        if path == '/api/test':
            payload = json.loads(self._read_body())
            tpath = payload.get('path', '/'); meth = payload.get('method', 'GET')
            t0 = time.time()
            try:
                conn = http.client.HTTPConnection('localhost', PROXY_PORT, timeout=35)
                conn.request(meth, tpath, headers={'Content-Type': 'application/json'})
                r = conn.getresponse(); rbody = r.read().decode('utf-8', errors='replace')
                self._json(200, {'statusCode': r.status, 'headers': dict(r.getheaders()),
                                  'body': rbody, 'elapsedMs': int((time.time()-t0)*1000)})
            except Exception as e: self._json(200, {'error': str(e)})
            return
        if path == '/api/probe':
            payload = json.loads(self._read_body()); url = payload.get('url', '')
            try:
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=5) as r:
                    self._json(200, {'reachable': True, 'status': r.status})
            except Exception as e: self._json(200, {'reachable': False, 'error': str(e)})
            return
        self._json(404, {'error': 'not found'})
    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path
        m = re.fullmatch(r'/api/mocks/([^/]+)', path)
        if m:
            mid = m.group(1); data = json.loads(self._read_body())
            cfg = load_config()
            idx = next((i for i, x in enumerate(cfg.get('mocks', [])) if x.get('id') == mid), -1)
            if idx >= 0:
                cfg['mocks'][idx].update(data); save_config(cfg)
                self._json(200, cfg['mocks'][idx])
            else: self._json(404, {'error': 'not found'})
            return
        if path == '/api/settings':
            data = json.loads(self._read_body()); cfg = load_config()
            cfg['globalBaseUrl'] = data.get('globalBaseUrl', '')
            save_config(cfg); self._json(200, {'globalBaseUrl': cfg['globalBaseUrl']}); return
        self._json(404, {'error': 'not found'})
    def do_DELETE(self):
        path = urllib.parse.urlparse(self.path).path
        m = re.fullmatch(r'/api/mocks/([^/]+)', path)
        if m:
            mid = m.group(1); cfg = load_config()
            before = len(cfg.get('mocks', []))
            cfg['mocks'] = [x for x in cfg.get('mocks', []) if x.get('id') != mid]
            if len(cfg['mocks']) < before:
                save_config(cfg); self.send_response(204); self._cors(); self.end_headers()
            else: self._json(404, {'error': 'not found'})
            return
        if path == '/api/logs':
            cfg = load_config(); cfg['logs'] = []; save_config(cfg)
            self.send_response(204); self._cors(); self.end_headers(); return
        self._json(404, {'error': 'not found'})

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try: s.bind(('', port)); return True
        except OSError: return False

def start_server(handler_class, port, label):
    srv = HTTPServer(('', port), handler_class)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print('  OK  ' + label)

def try_systray():
    try:
        import pystray
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(img).rounded_rectangle([4,4,60,60], radius=12, fill=(91,95,199,255))
        def open_ui(icon, item): webbrowser.open('http://localhost:' + str(UI_PORT))
        def quit_app(icon, item): icon.stop(); os._exit(0)
        menu = pystray.Menu(pystray.MenuItem('Open Dashboard', open_ui, default=True),
                            pystray.MenuItem('Quit LocalMockr', quit_app))
        pystray.Icon('LocalMockr', img, 'LocalMockr', menu).run()
    except Exception:
        threading.Event().wait()

def main():
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception: pass
        try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass

    print('')
    print('  ==========================================')
    print('   LocalMockr v2  -  API Proxy & Mock Studio')
    print('  ==========================================')
    print('')
    for port in (PROXY_PORT, UI_PORT):
        if not is_port_free(port):
            print('  ERROR: Port ' + str(port) + ' is already in use!')
            input('  Press Enter to exit...')
            sys.exit(1)
    print('  Starting servers...')
    start_server(ProxyHandler, PROXY_PORT, 'Proxy server -> http://localhost:' + str(PROXY_PORT))
    start_server(UIHandler,    UI_PORT,    'UI dashboard -> http://localhost:' + str(UI_PORT))
    print('')
    print('  Dashboard  : http://localhost:' + str(UI_PORT))
    print('  Proxy      : http://localhost:' + str(PROXY_PORT))
    print('  Config     : ' + CONFIG_PATH)
    print('  Point your app at: http://localhost:' + str(PROXY_PORT))
    print('  Keep this window open. Close it to stop.')
    print('')
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:' + str(UI_PORT))).start()
    try_systray()

if __name__ == '__main__':
    main()
