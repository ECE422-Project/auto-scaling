async function updateNumReplications(chart) {
    const response = await fetch('http://10.2.6.145:3000/query?key=num_replications');
    const json = await response.json();
    const now = Date.now();
    chart.data.datasets[0].data.push({
        x: now,
        y: json
    });
}


const config = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Number of Servers',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgb(255, 99, 132)',
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
