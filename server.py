import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

from wsj_to_rss import generate_rss_feed_for_author_link


LINK_STUB = 'https://www.wsj.com/news/author/{}'
AUTHOR_IDS = ['7998']  # Liz Hoffman


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml")
        self.end_headers()

    def do_GET(self):
        if self.path == 'favicon.ico':
            self.send_response(404)
            return

        try:
            o = urlparse(self.path)
            qs_dict = parse_qs(o.query)
            author_ids = qs_dict.get('author_ids') or AUTHOR_IDS
            link = LINK_STUB.format(author_ids[0])
            xml = generate_rss_feed_for_author_link(link)

            self.send_response(200)
            self.send_header("Content-type", "application/rss+xml")
            self.end_headers()

            self.wfile.write(xml.encode())
        except:
            self.send_response(500)


def run(host_name, port):
    with socketserver.TCPServer((host_name, port), Handler) as httpd:
        print("serving at port", port)
        httpd.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host_name', default='')
    parser.add_argument('-p', '--port', type=int, default=8000)
    args = parser.parse_args()

    run(args.host_name, args.port)

