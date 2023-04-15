import requests
import sys
import time

from locust import HttpUser, LoadTestShape, between, events, task
from locust.exception import RescheduleTask


IP = '10.2.6.145'

BALANCER_PORT = 8080
SERVICE_PORT = 8000


if len(sys.argv) < 2:
    lower = 5
    upper = 10




class Visitors(HttpUser):
    wait_time = between(5, 10)

    @task
    def t(self):
        start = time.time()
        with self.client.get(f'/', catch_response=True) as response:
            end = time.time()
            response_time = end - start
            if response.status_code == 200:
                response.success()
                print(f'Response time is {response_time} milliseconds')
                r = requests.post(
                        f'http://{IP}:{BALANCER_PORT}/response_time',
                        json={ 'response_time': response_time }
                )
                if r.status_code == 200:
                    print('Response time is sent')
            else:
                raise RescheduleTask()


class BellShape(LoadTestShape):
    stages = [
            {"duration": 30, "users": 10, "spawn_rate": 5, "user_classes": [Visitors]},
            {"duration": 60, "users": 10, "spawn_rate": 10, "user_classes": [Visitors]},
            {"duration": 90, "users": 20, "spawn_rate": 10, "user_classes": [Visitors]},
            {"duration": 120, "users": 20, "spawn_rate": 15, "user_classes": [Visitors]},
            {"duration": 150, "users": 20, "spawn_rate": 20, "user_classes": [Visitors]},
            {"duration": 180, "users": 30, "spawn_rate": 20, "user_classes": [Visitors]},
            {"duration": 300, "users": 20, "spawn_rate": 20, "user_classes": [Visitors]},
            {"duration": 330, "users": 20, "spawn_rate": 15, "user_classes": [Visitors]},
            {"duration": 360, "users": 20, "spawn_rate": 10, "user_classes": [Visitors]},
            {"duration": 390, "users": 10, "spawn_rate": 10, "user_classes": [Visitors]},
            {"duration": 420, "users": 10, "spawn_rate": 5, "user_classes": [Visitors]},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except:
                    tick_data = (stage["users"], stage["spawn_rate"], [Visitors])
                return tick_data

        return (10, 1, [Visitors])
