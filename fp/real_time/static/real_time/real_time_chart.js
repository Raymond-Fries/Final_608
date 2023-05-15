function addData(stock_Chart, label,price) {
    nt = label.getHours()+':'+label.getMinutes()+':'+label.getSeconds();
    chart_data.labels.push(nt);
    chart_data.close.push(price);

    let ma_t = moving_avg_add(chart_data.close.slice(-20));
    chart_data.ma_twenty.push(ma_t);

    let ma_s= moving_avg_add(chart_data.close.slice(-60));
    chart_data.ma_sixty.push(ma_s);

    stock_Chart.update();
}

function moving_avg_add(cp){
  const sum = cp.reduce((a, b) => a + b, 0);
  const avg = (sum / cp.length) || 0;
  return avg;
}
let chart_data = JSON.parse(document.getElementById('chart_data').textContent);
let ctx = document.getElementById('company_Chart');
let stock_label = document.getElementById("id_company_select").value;
let graphData = {
    type: 'line',
    data: {
        labels: chart_data.labels,
        datasets: [{

            label: stock_label,
            data: chart_data.close,
            backgroundColor: [
                'rgba(0, 99, 0, 1)',

            ],
            borderColor: [
                'rgba(0, 99, 0, 1)',

            ],
            borderWidth: 1,
            pointRadius: 1,
            yAxisID: 'y',
        },
        {

            label: '20 ma',
            data: chart_data.ma_twenty,
            backgroundColor: [
                'rgba(175, 0, 0, 0.77)',

            ],
            borderColor: [
                'rgba(175, 0, 0, 0.77)',

            ],
            borderWidth: 1,
            pointRadius: 1,
            yAxisID: 'y',
        },
        {

            label: '60 ma',
            data: chart_data.ma_sixty,
            backgroundColor: [
                'rgba(217, 220, 0, 0.77)',

            ],
            borderColor: [
                'rgba(217, 220, 0, 0.77)',

            ],
            borderWidth: 1,
            pointRadius: 1,
            yAxisID: 'y',
        },
      ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                grid: {
                    color: '#383736',
                }
            },
            x: {
                grid: {
                    color: '#383736',
                }
            }
        },
    }
}


let stock_Chart = new Chart(ctx, graphData);
