"""
This script takes an author link from the Wall Street Journal and producess an RSS feed.

http://topics.wsj.com/person/H/liz-hoffman/7998
"""
import requests
import bs4
import re
import datetime
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
from xml.etree import ElementTree
from xml.dom import minidom

# July 20, 2017 02:40 pm ET
pattern = (r'(?P<month>\w+) (?P<day>\d+), (?P<year>\d+) '
            '(?P<hour>\d+):(?P<minute>\d+) '
            '(?P<meridiem>[ap]m)')
DT_PATTERN = re.compile(pattern)


def get_soup(link):
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    return soup


def parse_pub_date_from_release_str(dt_str):
    year = DT_PATTERN.match(dt_str).group('year')    
    month = DT_PATTERN.match(dt_str).group('month')
    day = DT_PATTERN.match(dt_str).group('day')
    hour = DT_PATTERN.match(dt_str).group('hour')
    minute = DT_PATTERN.match(dt_str).group('minute')
    meridiem = DT_PATTERN.match(dt_str).group('meridiem').replace('.', '')
    
    if len(day) < 2:
        day = '0' + day
    
    cleaned_dt_str = ' '.join((
        year,
        month,
        day,
        hour,
        minute,
        meridiem,
    ))
    
    dt = datetime.datetime.strptime(cleaned_dt_str, '%Y %B %d %H %M %p')
    
    # Wed, 02 Oct 2002 08:00:00 EST
    pub_date = datetime.datetime.strftime(dt, '%a, %d %b %Y %H:%M:%S EST')

    return pub_date


def parse_li_node(li_node):
    try:
        link_node = li_node.find('a')
        link = link_node.get('href')
        title = li_node.find('h3').get_text()

        description = li_node.find('p', class_=re.compile('WSJTheme__summary')).get_text().strip()

        release_dt_str = li_node.find('p', class_=re.compile('style__timestamp')).get_text()
        pub_date = parse_pub_date_from_release_str(release_dt_str)
        
    except:
        return None
    
    else:
        return {
            'link': link,
            'title': title,
            'description': description,
            'pubDate': pub_date,
        }


def parse_soup_for_story_dicts(soup):
    
    li_list = soup.find_all('article', class_=re.compile('WSJTheme__story_')) 
    story_dicts = list(filter(bool, (parse_li_node(li) for li in li_list)))
    return story_dicts


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def dict_to_xml(tag, d):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def generate_rss_feed_for_author_link(author_link):
    soup = get_soup(author_link)
    items = parse_soup_for_story_dicts(soup)
    item_elements = [dict_to_xml('item', d) for d in items]
    channel_element = Element('channel')
    for item_element in item_elements:
        channel_element.append(item_element)

    root = Element('rss')
    root.set('version', '2.0')
    root.append(channel_element)
    return prettify(root)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('author_link')
    args = parser.parse_args()

    print(generate_rss_feed_for_author_link(args.author_link))

if __name__ == '__main__':
    main()
