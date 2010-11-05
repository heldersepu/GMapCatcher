import urllib2, urlparse
import logging
log = logging.getLogger(__name__)

def fetch(url):
    result = {}
    protocol = urlparse.urlparse(url)[0]
    if not protocol=='http':
        print 'error url %s' % url
        result['data'] = ""
        result['status'] = -1
        return result

    try:
        s = urllib2.urlopen(url)
        result['data'] = s.read()

        result['status'] = 200
        s.close()
    except Exception, inst:
        print "Error:"
        print inst
        result['data'] = ""
        result['status'] = -1
    finally:
        return result

