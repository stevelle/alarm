from datetime import datetime
from datetime import timedelta
from time import sleep

import argparse
import json
import requests
import sys
import urlparse
import yaml

DEFAULT_CONF_FILE = '/etc/loadmonitor/config.yml'
META_DATA_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'


class Config():
    def __init__(self, config_file=None):
        if not config_file:
            config_file = DEFAULT_CONF_FILE  
        
        self.rules = yaml.load(open(config_file).read())
        self.validate()
       
    def validate(self):
        pass # TODO

class Monitor():
    def __init__(self, config):
        self.config = config
        self.continue_checks = True
        self.alarms = {}

    def start(self):
        while self.continue_checks:
            self.run_checks()
            self.wait_cycle()

    def run_checks(self):
        rules = self.config.rules
        cache = {}
        for host in scaling_group_urls():
            for check in rules['checks']:
                try:
                    data = self.resolve(host, check, cache)
                    alarms = self.evaluate(host, check, data)
                    print ('%s has had %s consecutive alarm states for %s' %
                           (host, alarms, check['name']))
                    if alarms >= check['alarm_states']:
                        requests.post(check['trigger_url'], timeout=5)
                except Error, e:
                    print e.message
        sys.stdout.flush()


    def resolve(self, host, check, cache):
        endpoint = urlparse.urljoin("http://%s:8801" % host, check['metric'])
        check_name = check['name']
        if endpoint in cache:
            return cache[endpoint]

        reply = requests.get(endpoint, timeout=5)
        metric = float(reply.text)
        cache[endpoint] = metric
        return metric 

    @staticmethod
    def check_alarm_state(check, data):
        operator = check['operator']
        threshold = check['threshold']
        if operator == 'gte':
            return data >= threshold
        if operator == 'gt':
            return data > threshold
        if operator == 'lt':
            return data < threshold
        if operator == 'lte':
            return data <= threshold
        if operator == 'eq':
            return data == threshold
        else: 
            return False # WAT DO? validation should cover this

    def evaluate(self, host, check, data):
        alarm = self.check_alarm_state(check, data)

        # ensure a alarm counter exists
        check_name = check['name']
        if host not in self.alarms:
            self.alarms[host] = {}
        if check_name not in self.alarms[host]: 
            self.alarms[host][check_name] = 0

        # adjust failures count
        if alarm:
            self.alarms[host][check_name] += 1
        else:
            self.alarms[host][check_name] = 0
        return self.alarms[host][check_name]

    def wait_cycle(self):
        sleep(self.config.rules['check_period_seconds'])

def scaling_group_urls():
    meta_reply = requests.get(META_DATA_URL)
    json_meta = meta_reply.json()
    return json.loads(json_meta.get('meta',{}).get('servers', '[]'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load Monitor service')
    parser.add_argument('-c', '--config', type=str, default=DEFAULT_CONF_FILE, 
                        help='path to configuration file') 
    args = parser.parse_args()

    config = Config(args.config)
    monitor = Monitor(config)
    monitor.start()
