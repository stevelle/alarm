from datetime import datetime
from datetime import timedelta

import requests
import yaml

DEFAULT_CONF_FILE = '/etc/alarm/checks.yml'


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
        self.run_checks()
        while continue_checks:
            self.wait_cycle(lambda: self.run_checks())

    def run_checks(self):
        rules = self.config.rules
        cache = {}
        for target in rules['targets']:
            for host in target['target_urls']:
                for check in target['checks']:
                    data = self.resolve(host, check, cache)
                    failures = evaluate(host, check, data)
                    if failures >= check['trigger_on_failures']:
                        alarm_to(check.trigger_url)

    def resolve(self, host, check, cache):
        check_name = check['name']
        if host in cache and check_name in cache[host]:
            return cache[host][check_name]

        if host not in cache:
            cache[host] = {}

        r = requests.get(host + check['metric'])
        cache[host][check_name] = r
        return float(r) 

    @staticmethod
    def alarm_state(check, data):
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
        alarm = self.alarm_state(check, data)

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

    def wait_cycle(self, action):
        sleep(next_time() - datetime.now())
        return action

    def next_time(self):
        return (datetime.now() +
        timedelta(seconds=self.config.rules['check_period_seconds']))

    def alarm_to(self,trigger_url):
        requests.post(trigger_url, body={})

if __name__ == '__main__':
    config = Config()
    monitor = Monitor(config)
    monitor.start()

