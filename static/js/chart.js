anychart.onDocumentReady(function () {
    fetch('https://ieee-registration.herokuapp.com/team/chart')
        .then(response => {
            if (!response.ok) throw new Error('Server encountered an error')
            return response.json()
        })
        .then(data => {
            //ENTER THE CANDIDATE YEARS HERE (NUMBER OF FIRST, SECOND, THIRD AND FINAL YEAR)
            const chartData = {
                header: ["YEAR", "CANDIDATES"],
                rows: [
                    ["FIRST", data.First],
                    ["SECOND", data.Second],
                    ["THIRD", data.Third],
                    ["FINAL", data.Fourth]
                ]
            };

            // create the chart
            // let chart = anychart.bar();

            // add data


// create the chart
            const chart = anychart.column();

            chart.data(chartData);

            // set the chart title
            chart.title("YEARWISE CANDIDATE APPLICATION");

            // draw
            chart.container("container");
            chart.draw();
        })
        .catch(err => showMsg(err.message, 'danger'))


});




