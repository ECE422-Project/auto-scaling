import docker
import math
import random
import threading
import time

from flask import Flask, request, render_template
from redis import Redis


BALANCER_SLEEP_TIME = 10

app = Flask('Load Balancer')

redis = Redis(host='10.2.6.145', port=6379) 

response_times = []


"""
Load Balancer is responible to balance the load and observe the average response time
"""
class LoadBalancer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.redis = Redis(host='10.2.6.145', port=6379)
        self.client = docker.from_env()

    def get_num_visitors(self) -> int:
        return 0 if self.redis.get('num_visitors') == None else int(self.redis.get('num_visitors'))

    def get_avg_response_time(self) -> float:
        return 0.0 if self.redis.get('avg_response_time') == None else float(self.redis.get('avg_response_time'))

    # Get the Service Object => contains number of attribute including number of Replicas
    def get_services(self):
        return self.client.services.list(filters={'name': 'ping-app_web'})[0]

    # Update the number of Replicas in Redis
    def update_num_replications(self, num_replications):
        self.redis.set('num_replications', num_replications)
        self.redis.publish('replications_channel', num_replications)

    def run(self):
        print('Load balancer activated...')
        prev = self.get_num_visitors()  # Number of visitors in previous sleep section
        current = prev  # Number of visitors in the current sleep section
        diff = current - prev
        while True:
            time.sleep(BALANCER_SLEEP_TIME)
            
            current = self.get_num_visitors()
            if current == 0 and prev > 0:
                current = 0
                prev = 0
                continue

            diff = current - prev # arrival rate per 20 seconds -> lambda

            # average response time per worker -> 1 / mu
            avg_response_time = self.get_avg_response_time()
            
            # p = lambda / mu
            traffic_intensity = (diff / BALANCER_SLEEP_TIME) * avg_response_time              

            self.redis.set('workload', traffic_intensity if traffic_intensity > 0 else 0)

            # p + sqrt(p)
            thersold = traffic_intensity + math.sqrt(traffic_intensity)  

            # max(1, p + sqrt(p))
            factor = max(1, thersold)

            num_replications = self.get_services().attrs['Spec']['Mode']['Replicated']['Replicas']
            self.update_num_replications(num_replications)

            print(f'\nIn {BALANCER_SLEEP_TIME} seconds:\n' \
                  f'{diff} visitors has arrived, arrival rate (lambda) = {diff / BALANCER_SLEEP_TIME} visitors / seconds\n' \
                  f'Average Response Time (1 / mu)  = {avg_response_time}\n' \
                  f'Traffic Intensity (p = lambda / mu) = {traffic_intensity}\n' \
                  f'Thersold (p + sqrt(p)) = {thersold}\n' \
                  f'Factor (max(1, (p + sqrt(p)) = {factor}\n' \
                  f'Number of Replications = {num_replications}'
            )

            # Scale Up / Down / Stable
            if num_replications >= factor and (num_replications - factor) / num_replications >= 0.5:
                scale_down = math.floor(factor)
                warning = self.get_services().scale(scale_down)

                if warning['Warnings'] != None:
                    print(f'\n{warning["Warnings"]}\n')
                else:
                    print(f'\nScale down replications from {num_replications} to {scale_down}\n') 
                    self.update_num_replications(scale_down)

            elif num_replications < factor:
                scale_up = math.ceil(factor)
                warning = self.get_services().scale(scale_up)

                if warning['Warnings'] != None:
                    print(f'\n{warning["Warnings"]}\n')
                else:
                    print(f'\nScale up replications from {num_replications} to {scale_up}\n')
                    self.update_num_replications(scale_up)

            prev = current


@app.route('/response_time', methods=['GET', 'POST'])
def post_response_time():
    if request.method == 'GET':
        return get_response_time()
    
    data = request.json

    response_time = data.get('response_time')
    
    response_times.append(response_time)

    # average response time per worker
    if len(response_times) >= 10:
        avg_response_time = sum(response_times[len(response_times) - 10:len(response_times)]) / 10
    else:
        avg_response_time = 0.0 if len(response_times) == 0 else \
            sum(response_times) / len(response_times)

    redis.set('avg_response_time', avg_response_time)

    return ''


@app.route('/')
def get_response_time():
    if len(response_times) == 0:
        return 'No response data yet'

    return render_template(
            'index.html', 
            avg=sum(response_times) / len(response_times), 
            times=response_times
    ) 

@app.route('/reset')
def reset():
    redis.set('avg_response_time', 0)
    redis.set('num_visitors', 0)
    redis.set('workload', 0)

    return 'Reset'


if __name__ == '__main__':
    load_balancer_thread = LoadBalancer()
    load_balancer_thread.start()

    app.run(host='0.0.0.0', port=8080, debug=False)
