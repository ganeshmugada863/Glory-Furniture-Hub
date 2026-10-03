import os
import http.server
import socketserver

PORT = int(os.environ.get("PORT", 10000))

REDIRECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Glory Furniture Hub — Redirecting</title>
  <script>
    (function() {
      var hash = window.location.hash || '';
      var path = window.location.pathname || '/';
      var search = window.location.search || '';
      
      // If access_token hash is present from Supabase OAuth, forward to Vercel supabase-callback
      if (hash.includes('access_token=')) {
        window.location.replace('https://glory-furniture-hub.vercel.app/accounts/supabase-callback/' + hash);
        return;
      }
      
      // Forward all other routes to Vercel
      window.location.replace('https://glory-furniture-hub.vercel.app' + path + search + hash);
    })();
  </script>
</head>
<body style="background:#140D09;color:#EADBCE;font-family:system-ui,-apple-system,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0;padding:20px;text-align:center;">
  <div style="max-width:400px;background:#1E140F;border:1px solid #5C3D2E;border-radius:24px;padding:32px;box-shadow:0 20px 40px rgba(0,0,0,0.5);">
    <h2 style="color:#C9963F;margin:0 0 12px;font-size:20px;font-weight:800;">Glory Furniture Hub</h2>
    <p style="color:#A89F91;font-size:13px;line-height:1.5;margin:0 0 20px;">Moving you to the official storefront on Vercel...</p>
    <a href="https://glory-furniture-hub.vercel.app/" style="display:inline-block;background:#C9963F;color:#140D09;padding:10px 24px;border-radius:12px;text-decoration:none;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Continue to Store &rarr;</a>
  </div>
</body>
</html>"""

class InstantRedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(REDIRECT_HTML.encode("utf-8"))

    def do_POST(self):
        self.do_GET()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        # Concise logging
        print(f"[Render->Vercel Forward] {self.path}")

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), InstantRedirectHandler) as httpd:
        print(f"[Redirect Bridge] Listening on port {PORT} -> Redirecting to glory-furniture-hub.vercel.app")
        httpd.serve_forever()
