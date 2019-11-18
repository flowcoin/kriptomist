import logging
log = logging.getLogger("fetcher")

import os
import requests
from urllib.parse import urlparse

from util import sleep


class Cache:
    def __init__(self, folder="cache"):
        self.folder = folder

    def path(self, url):
        scheme, netloc, path, params, query, fragment = urlparse(url)    
        p = [self.folder, netloc] + path.split("/")
        
        if query:
            if not p[-1]:
                p[-1] = query
            else:
                p += [query]
        
        if not p[-1]:
            p[-1] = "index.html"
        
        return os.path.join(*p)
        
    def get(self, url):
        p = self.path(url)
        if os.path.exists(p):
            log.debug("Found in cache: {}".format(url))
            return open(p).read()
        log.debug("Not in cache: {}".format(url))
        return None        
        
    def put(self, url, text):
        p = self.path(url)
        os.makedirs(p.rsplit("/", 1)[0], exist_ok=True)
        open(p, "w").write(text)
        log.debug("Stored to cache: {}".format(url))


class Fetcher:
    cache = Cache()

    def __init__(self, text_handler=None, read_cache=True, write_cache=True):
        self.text_handler = text_handler
        self.read_cache = read_cache
        self.write_cache = write_cache
        
    def get(self, url, retries=10, nap=1):
        err = False
        
        text = None
        
        if self.read_cache and nap < 2:
            text = self.cache.get(url)
        
        if not text:
            try:
                text = requests.get(url).text
                if self.write_cache:
                    self.cache.put(url, text)
            except Exception as e:
                err = True
                log.exception("Failed to get {}".format(url))
                
        ret = text
        if not err:
            if self.text_handler:
                try:
                    ret = self.text_handler(text)
                    if not ret:
                        log.debug("Text produced false value: {} [...]".format(str(text)[:1000]))
                        err = True
                except Exception as e:
                    err = True
                    log.exception("Failed to handle text: {} [...]".format(str(text)[:1000]))
        
        if err:
            if retries == 0:
                log.debug('No retries left; returning None')
                return None
            if nap > 1:
                sleep(nap)
            return self.get(url, retries=retries-1, nap=nap*2)
        
        return ret    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)


    print(Fetcher().get("http://example.com", retries=4))

