import docker
import math
import random
import threading
import time

from flask import Flask, request, render_template
from redis import Redis


BALANCER_SLEEP_TIME = 20
OBSERVER_SLEEP_TIME = 4

app = Flask('Load Balancer')

redis = Redis(host='10.2.6.145', port=6379) 

responses: dict = {}


"""
Load Balancer is responible to balance the load and observe the average response time
"""
class LoadBalancer(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.redis = Redis(host='10.2.6.145', port=6379)
        self.client = docker.from_env()

    def get_num_workers(self) -> int:
        return 0 if self.redis.get('num_workers') == None else int(self.redis.get('num_workers'))

    def get_avg_response_time(self) -> float:
        return 0.0 if self.redis.get('avg_response_time') == None else float(self.redis.get('avg_response_time'))

    def get_services(self):
        return self.client.services.list(filters={'name': 'ping-app_web'})[0]

    def run(self):
        print('Load balancer activated...')
        prev = self.get_num_workers()  # Number of workers in previous sleep section
        current = prev  # Number of workers in the current sleep section
        diff = current - prev
        while True:
            time.sleep(BALANCER_SLEEP_TIME)
            
            current = self.get_num_workers()
            diff = current - prev # arrival rate per 20 seconds -> lambda

            # average response time per worker -> 1 / mu
            avg_response_time = self.get_avg_response_time()
            
            traffic_intensity = (diff / BALANCER_SLEEP_TIME) * avg_response_time # lambda / mu
            
            thersold = traffic_intensity + math.sqrt(traffic_intensity)
            factor = max(1, thersold)

            num_servers = self.get_services().attrs['Spec']['Mode']['Replicated']['Replicas']

            print(f'\nIn {BALANCER_SLEEP_TIME} seconds:\n{diff} workers has arrived\nAverage Response Time = {avg_response_time}\nTraffic Intensity = {traffic_intensity}\nThersold = {thersold}\nNumber of Replication = {num_servers}\nFactor = {factor}')

            if num_servers >= factor and (num_servers - factor) / num_servers > 0.5:
                scale_down = math.floor(factor)
                warning = self.get_services().scale(scale_down)
                if warning['Warnings'] != None:
                    print(f'\n{warning["Warnings"]}\n')
                else:
                    print(f'\nScale down replications from {num_servers} to {scale_down}\n')
            elif num_servers < factor:
                scale_up = math.floor(factor)
                warning = self.get_services().scale(scale_up)
                if warning['Warnings'] != None:
                    print(f'\n{warning["Warnings"]}\n')
                else:
                    print(f'\nScale up replications from {num_servers} to {scale_up}\n')

            prev = current


@app.route('/response_time', methods=['GET', 'POST'])
def post_response_time():
    if request.method == 'GET':
        return get_response_time()
    
    data = request.json

    thread_id = data.get('thread_id')
    response_time = data.get('response_time')
    
    responses[thread_id] = response_time

    # average response time per worker
    if len(responses) == 0:
        redis.set('avg_response_time', 0.0)
    else:
        redis.set('avg_response_time', sum(responses.values()) / len(responses))

    return ''


@app.route('/')
def get_response_time():
    if len(responses) == 0:
        return 'No response data yet'

    stats = []
    total = 0
    for thread_id, time in responses.items():
        stats.append(f'Worker {thread_id}: {time}')
        total += time
    avg = total / len(stats)

    return render_template('index.html', avg=avg, stats=stats) 


if __name__ == '__main__':
    load_balancer_thread = LoadBalancer()
    load_balancer_thread.start()

    app.run(host='0.0.0.0', port=8080, debug=True)

