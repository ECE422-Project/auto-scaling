async function updateNumReplications(chart) {
    const response = await fetch('http://10.2.6.145:3000/status');
    const json = await response.json();
    const now = Date.now();
    for (let i = 0; i < json.length; i++) {
        chart.data.datasets[i].data.push({
            x: now,
            y: json[i]
        });
    }
}


const config = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Average Response Time',
                backgroundColor: 'rgba(10, 113, 226, 0.8)',
                borderColor: 'rgb(10, 113, 226)',
                data: [],
            },
            {
                label: 'Number of Replications',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgb(255, 99, 132)',
                data: [], 
            },
            {
                label: 'Workload',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: 'rgba(0, 0, 0)',
                data: [],
            }
        ]
    },
    options: {
        scales: {
            x: {
                type: 'realtime',
                realtime: {
                    onRefresh: updateNumReplications
                }
            }
        }
    }
};


const graph = new Chart(document.getElementById('graph'), config);
