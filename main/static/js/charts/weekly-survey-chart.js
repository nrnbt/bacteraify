
if (document.getElementById('classification-weekly')) {
const options = {
  colors: ['#1A56DB', '#FDBA8C'],
  series: [
    {
      name: 'Quantity',
      color: '#1A56DB',
      data: data[0]
    }
  ],
  chart: {
    type: 'bar',
    height: '140px',
    fontFamily: 'Inter, sans-serif',
    foreColor: '#4B5563',
    toolbar: {
      show: false
    }
  },
  plotOptions: {
    bar: {
      columnWidth: '90%',
      borderRadius: 3
    }
  },
  tooltip: {
    shared: false,
    intersect: false,
    style: {
      fontSize: '14px',
      fontFamily: 'Inter, sans-serif'
    },
  },
  states: {
    hover: {
      filter: {
        type: 'darken',
        value: 1
      }
    }
  },
  stroke: {
    show: true,
    width: 5,
    colors: ['transparent']
  },
  grid: {
    show: false
  },
  dataLabels: {
    enabled: false
  },
  legend: {
    show: false
  },
  xaxis: {
    floating: false,
    labels: {
      show: false
    },
    axisBorder: {
      show: false
    },
    axisTicks: {
      show: false
    },
  },
  yaxis: {
    show: false
  },
  fill: {
    opacity: 1
  }
};

const chart = new ApexCharts(document.getElementById('classification-weekly'), options);
chart.render();
}