from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import getopt
import requests
from functools import partial
from urllib.parse import urlparse

html = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Hello world!</title>
    </head>
    <body>
        <h1>Welcome to the Resiliency Workshop!</h1>
        <p>Data from the request client&server side</p>
        <p>{Content}<p>
        <img src="{WebSiteImage}" alt="alternative text" scale="0">
    </body>
</html>"""


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, url_image, *args, **kwargs):
        self.url_image = url_image
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        message_parts = [
            'Metadata IP:%s' % requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").content,
            'client_address=%s (%s)' % (self.client_address,
                                        self.address_string()),
            'command=%s' % self.command,
            'path=%s' % self.path,
            'real path=%s' % parsed_path.path,
            'query=%s' % parsed_path.query,
            'request_version=%s' % self.request_version,
            'server_version=%s' % self.server_version,
            'sys_version=%s' % self.sys_version,
            'protocol_version=%s' % self.protocol_version,
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '<br>'.join(message_parts)

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(
            bytes(
                html.format(Content=message, WebSiteImage=self.url_image),
                "utf-8"
            )
        )

        return


def run(argv):
    imageurl = ''
    try:
        opts, args = getopt.getopt(
            argv,
            "hu:",
            [
                "ibucket="
            ]
        )
    except getopt.GetoptError:
        print('server.py -u <imageurl>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -u <imageurl>')
            sys.exit()
        elif opt in ("-u", "--bfile"):
            imageurl = arg

    print('Image url: ', imageurl)
    # image = "https://s3.us-east-2.amazonaws.com/arc327-well-architected-for-reliability/Cirque_of_the_Towers.jpg"
    print('starting server...')
    server_address = ('0.0.0.0', 80)

    handler = partial(RequestHandler, imageurl)
    httpd = HTTPServer(server_address, handler)
    print('running server...')
    httpd.serve_forever()


if __name__ == "__main__":
    run(sys.argv[1:])
