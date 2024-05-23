


const getEmployeeChart = () => {
  let employeeChartColors = {}

  if (document.documentElement.classList.contains('dark')) {
    employeeChartColors = {
      backgroundBarColors: ['#374151', '#374151', '#374151', '#374151', '#374151', '#374151', '#374151']
    };
  } else {
    employeeChartColors = {
      backgroundBarColors: ['#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB', '#E5E7EB']
    };
  }

const xData = new_employee_weekly_report.map(item => item.x);
const yData = new_employee_weekly_report.map(item => item.y);
return {
  series: [{
    name: 'Шинэ Ажилчид',
    data: yData
  }],
  labels: xData,
  chart: {
    type: 'bar',
    height: '140px',
    foreColor: '#4B5563',
    fontFamily: 'Inter, sans-serif',
    toolbar: {
      show: false
    }
  },
  theme: {
    monochrome: {
      enabled: true,
      color: '#1A56DB'
    }
  },
  plotOptions: {
    bar: {
      columnWidth: '25%',
      borderRadius: 3,
      colors: {
        backgroundBarColors: employeeChartColors.backgroundBarColors,
        backgroundBarRadius: 3
      },
    },
    dataLabels: {
      hideOverflowingLabels: false
    }
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
  tooltip: {
    shared: true,
    intersect: false,
    style: {
      fontSize: '14px',
      fontFamily: 'Inter, sans-serif'
    }
  },
  states: {
    hover: {
      filter: {
        type: 'darken',
        value: 0.8
      }
    }
  },
  fill: {
    opacity: 1
  },
  yaxis: {
    show: false
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
};
}

if (document.getElementById('week-signups-chart')) {
  const chart = new ApexCharts(document.getElementById('week-signups-chart'), getEmployeeChart());
  chart.render();

  // init again when toggling dark mode
  document.addEventListener('dark-mode', function () {
    chart.updateOptions(getEmployeeChart());
  });
}