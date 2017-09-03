# wsj-rss
A tool to create an RSS feed for a particular WSJ author

`docker build . -t wsj-rss`
`docker run --rm -p 8000:8000 wsj-rss`
`curl -v "http://docker-host:8000/rss.html?author_id=123"`

