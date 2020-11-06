from urllib.parse import urlparse
from threading import Thread, Lock
from multiprocessing import Process, cpu_count
import json
import threading
import time
import logging
import random
import sys
import requests
import io
import codecs
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#parser of way back and gau data
class parse_info(object):
    def __init__(self, start = 0):
        self.value = start
        self.PROCESS = cpu_count() * 2
        self.THREADS = 4
        self.subdomains_found = []
        self.paths_found = []
        self.domains_found = []
        self.lock = Lock()


    def set_default(self,obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError
        

    def parse_info(self, addresses):
        
        for address in addresses:
            self.lock.acquire()

            try:
                logging.debug('Acquired a lock')
                self.value = self.value + 1
                info = urlparse(address)
                subdomain = info.hostname.split('.')[0]
                self.subdomains_found.append(subdomain)
                pathfound = info.path
                self.paths_found.append(pathfound)
                netlocation = info.netloc
                self.domains_found.append(netlocation)
                

            finally:
                logging.debug('Released a lock')
                self.lock.release()




    def get_urls(self,dataset_path):
        ips = []
        with codecs.open(dataset_path, 'r', encoding='utf-8',
                 errors='ignore') as fdata:
                 
           dataset = list(filter(None, fdata.read().split("\n")))
          
        
           for line in dataset:
                # line = json.loads(line)
                # ips.append(line['IP'])
                #line = line.decode('latin-1').encode("utf-8")
                ips.append(line.rstrip())
                

        return ips
        
        
        
    def urls_to_process(self,a, n):
        # ode to devil from htb the best coder i know ;)
        k, m = divmod(len(a), n)
        for i in range(n):
            yield a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]





if __name__ == "__main__":
    parsed_info = parse_info()
    ip_list = parsed_info.get_urls(sys.argv[1])
    urls_to_test = parsed_info.urls_to_process(ip_list, parsed_info.PROCESS)

    for _ in range(parsed_info.PROCESS):
        p = Thread(target=parsed_info.parse_info, args=(next(urls_to_test),))
        p.daemon = True
        p.start()

    for _ in range(parsed_info.PROCESS):
        p.join()

    final_info = {}
    final_info['subdomains'] = set(parsed_info.subdomains_found)
    final_info['paths_found'] = set(parsed_info.paths_found)
    final_info['domains_found'] = set(parsed_info.domains_found)
    final_info = json.dumps(final_info,default=parsed_info.set_default)
    print(final_info)
    #easily write the json info to file and save it this is justa mockup if u guys see use ill mod it per request for features
    
