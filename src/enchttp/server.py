import http.server
import socketserver
import urllib
import os
import io

PORT = 8000
KEY = 42  # Simple XOR key for encryption/decryption

class EncryptedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            file_list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        file_list.sort(key=lambda a: a.lower())

        f = io.BytesIO()
        displaypath = urllib.parse.unquote(self.path)
        f.write(b'<!DOCTYPE html>\n<html>\n<head>\n')
        f.write(b'<meta charset="utf-8">\n')
        f.write(b'<title>Directory listing for %s</title>\n' % displaypath.encode('utf-8'))
        f.write(b'</head>\n<body>\n')
        f.write(b'<h2>Directory listing for %s</h2>\n' % displaypath.encode('utf-8'))
        f.write(b'<ul>\n')

        # Include JavaScript for decryption
        f.write(b'<script>\n')
        f.write(b'''
function downloadAndDecrypt(filename) {
    fetch(filename)
    .then(response => response.arrayBuffer())
    .then(data => {
        const key = %d;
        const encrypted = new Uint8Array(data);
        const decrypted = new Uint8Array(encrypted.length);
        for (let i = 0; i < encrypted.length; i++) {
            decrypted[i] = encrypted[i] ^ key;
        }
        const blob = new Blob([decrypted]);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    });
}
</script>
''' % KEY)

        # Generate directory listing
        for name in file_list:
            fullname = os.path.join(path, name)
            displayname = name
            linkname = urllib.parse.quote(name)
            if os.path.isdir(fullname):
                displayname += '/'
                linkname += '/'
                f.write(b'<li><a href="%s">%s</a></li>\n' % (linkname.encode('utf-8'), displayname.encode('utf-8')))
            else:
                f.write(b'<li><a href="#" onclick="downloadAndDecrypt(\'%s\')">%s</a></li>\n' % (linkname.encode('utf-8'), displayname.encode('utf-8')))
        f.write(b'</ul>\n</body>\n</html>\n')

        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = 'utf-8'
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                self.send_response(301)
                new_parts = (parts.scheme, parts.netloc, parts.path + '/', parts.query, parts.fragment)
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            else:
                return self.list_directory(path)
        elif os.path.isfile(path):
            try:
                ctype = self.guess_type(path)
                with open(path, 'rb') as f:
                    data = f.read()
                encrypted_data = bytes([b ^ KEY for b in data])
                self.send_response(200)
                self.send_header("Content-type", ctype)
                self.send_header("Content-Length", str(len(encrypted_data)))
                self.end_headers()
                return io.BytesIO(encrypted_data)
            except Exception:
                self.send_error(404, "File not found")
                return None
        else:
            self.send_error(404, "File not found")
            return None

def start_server(bind='0.0.0.0', port=8000):
    """Start the encrypted HTTP server.
    
    Args:
        bind (str): The address to bind to
        port (int): The port to listen on
    """
    Handler = EncryptedHTTPRequestHandler
    with socketserver.TCPServer((bind, port), Handler) as httpd:
        host = bind if bind else '0.0.0.0'
        print(f"Serving HTTP on {host} port {port} "
              f"(http://{host}:{port}/) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")

def main():
    """Entry point for the command-line script."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='0.0.0.0', metavar='ADDRESS',
                       help='Specify alternate bind address '
                            '[default: 0.0.0.0]')
    parser.add_argument('port', action='store',
                       default=8000, type=int,
                       nargs='?',
                       help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    start_server(args.bind, args.port)

if __name__ == '__main__':
    main()
