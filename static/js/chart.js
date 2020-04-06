(function chartLoader() {
    fetch('https://ieee-registration.herokuapp.com/team/chart')
        .then(response => {
            if (!response.ok) throw new Error('Server encountered an error')
            return response.json()
        })
        .then(data => {
            const ctx = document.getElementById('myChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['First', 'Second', 'Third', 'Final'],
                    datasets: [{
                        label: 'Applications',
                        backgroundColor: 'rgb(255, 99, 132)',
                        data: [data.First, data.Second, data.Third, data.Fourth]
                    }]
                },
                options: {
                    legend: {display: false},
                    title: {
                        display: true,
                        text: 'YEARWISE CANDIDATE APPLICATION'
                    }
                }
            })
        })
        .catch(err => showMsg(err.message, 'danger'))


})();




