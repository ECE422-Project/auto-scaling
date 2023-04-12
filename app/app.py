from flask import Flask
from redis import Redis
import random
import time


app = Flask(__name__)
redis = Redis(host='redis', port=6379)


def difficult_function():
    output = 1
    t0 = time.time()
    difficulty = random.randint(1000000, 2000000)
    for i in range(difficulty):
        output = output * difficulty
        output = output / (difficulty - 1)
    t1 = time.time()
    compute_time = t1 - t0
    return compute_time


@app.route('/')
def hello():
    # Number of customers the microservice has servered
    num_visitors = redis.incr('num_visitors')
    num_subscribers = redis.publish('visitors_channel', num_visitors)
    computation_time = difficult_function()

    return f'This microservice has servered {num_visitors} visitors. This problem was solved in {computation_time} seconds.\n'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
