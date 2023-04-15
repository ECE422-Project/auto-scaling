const replicasConfig = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Number of Replications',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgb(255, 99, 132)',
                data: []
            }
        ]
    },
    options: {
        scales: {
            x: {
                type: 'realtime',
                realtime: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000,
                    onRefresh: async (chart) => {
                        const r = await fetch('http://10.2.6.145:3000/replicas');
                        const json = await r.json();
                        const now = Date.now();
                        chart.data.datasets[0].data.push(
                            {
                                x: now,
                                y: json
                            }
                        );
                    }
                }
            }
        }
    }
};

const timeConfig = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Average Response Time',
                backgroundColor: 'rgba(10, 113, 226, 0.8)',
                borderColor: 'rgb(10, 113, 226)',
                data: []
            }
        ]
    },
    options: {
        scales: {
            x: {
                type: 'realtime',
                realtime: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000,
                    onRefresh: async (chart) => {
                        const r = await fetch('http://10.2.6.145:3000/avg_response_time');
                        const json = await r.json();
                        const now = Date.now();
                        chart.data.datasets[0].data.push(
                            {
                                x: now,
                                y: json
                            }
                        );
                    }
                }
            }
        }
    }
};

const workloadConfig = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Workload (Arrival rate within 10 seconds)',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: 'rgba(0, 0, 0)',
                data: []
            }
        ]
    },
    options: {
        scales: {
            x: {
                type: 'realtime',
                realtime: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000,
                    onRefresh: async (chart) => {
                        const r = await fetch('http://10.2.6.145:3000/workload');
                        const json = await r.json();
                        const now = Date.now();
                        chart.data.datasets[0].data.push(
                            {
                                x: now,
                                y: json
                            }
                        );
                    }
                }
            }
        }
    }
};


new Chart(document.getElementById('replicas'), replicasConfig);
new Chart(document.getElementById('time'), timeConfig);
new Chart(document.getElementById('workload'), workloadConfig);
