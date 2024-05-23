const getBacteriaChartOptions = () => {
  let bacteriaChartColors = {}

  if (document.documentElement.classList.contains('dark')) {
    bacteriaChartColors = {
      borderColor: '#374151',
      labelColor: '#9CA3AF',
      opacityFrom: 0,
      opacityTo: 0.15,
    };
  } else {
    bacteriaChartColors = {
      borderColor: '#F3F4F6',
      labelColor: '#6B7280',
      opacityFrom: 0.45,
      opacityTo: 0,
    }
  }

  // Iterate over series data and disable if all data numbers are zero
  const seriesData = bacteria_monthly.series.map(series => {
    const allZero = series.data.every(val => val === 0);
    return {
      name: series.name,
      data: series.data,
      color: series.color,
      disabled: allZero
    };
  });

  return {
    chart: {
      height: 420,
      type: 'area',
      fontFamily: 'Inter, sans-serif',
      foreColor: bacteriaChartColors.labelColor,
      toolbar: {
        show: false
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
        enabled: true,
        opacityFrom: bacteriaChartColors.opacityFrom,
        opacityTo: bacteriaChartColors.opacityTo
      }
    },
    dataLabels: {
      enabled: false
    },
    tooltip: {
      style: {
        fontSize: '14px',
        fontFamily: 'Inter, sans-serif',
      },
    },
    grid: {
      show: true,
      borderColor: bacteriaChartColors.borderColor,
      strokeDashArray: 1,
      padding: {
        left: 35,
        bottom: 15
      }
    },
    series: seriesData,
    markers: {
      size: 5,
      strokeColors: '#ffffff',
      hover: {
        size: undefined,
        sizeOffset: 3
      }
    },
    xaxis: {
      categories: bacteria_monthly.categories,
      labels: {
        style: {
          colors: [bacteriaChartColors.labelColor],
          fontSize: '14px',
          fontWeight: 500,
        },
      },
      axisBorder: {
        color: bacteriaChartColors.borderColor,
      },
      axisTicks: {
        color: bacteriaChartColors.borderColor,
      },
      crosshairs: {
        show: true,
        position: 'back',
        stroke: {
          color: bacteriaChartColors.borderColor,
          width: 1,
          dashArray: 10,
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: [bacteriaChartColors.labelColor],
          fontSize: '14px',
          fontWeight: 500,
        }
      },
    },
    legend: {
      fontSize: '14px',
      fontWeight: 500,
      fontFamily: 'Inter, sans-serif',
      labels: {
        colors: [bacteriaChartColors.labelColor]
      },
      itemMargin: {
        horizontal: 10
      }
    },
    responsive: [
      {
        breakpoint: 1024,
        options: {
          xaxis: {
            labels: {
              show: false
            }
          }
        }
      }
    ]
  };
}

if (document.getElementById('bacteria-chart')) {
  const chart = new ApexCharts(document.getElementById('bacteria-chart'), getBacteriaChartOptions());
  chart.render();

  // init again when toggling dark mode
  document.addEventListener('dark-mode', function () {
    chart.updateOptions(getBacteriaChartOptions());
  });
}
