import docker

from flask import Flask, request, render_template


app = Flask('Load Balancer')

client = docker.from_env()  # Connect to docker daemon

responses = {}


@app.route('/response_time', methods=['GET', 'POST'])
def post_response_time():
    if request.method == 'GET':
        return get_response_time()
    
    data = request.json

    thread_id = data.get('thread_id')
    response_time = data.get('response_time')
    
    responses[thread_id] = response_time

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
    app.run(host='0.0.0.0', port=8080, debug=True)

