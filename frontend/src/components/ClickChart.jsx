import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

function ClickChart({ dailyData, monthlyData, view }) {
  const isDaily = view === 'daily';
  const data = isDaily ? dailyData : monthlyData;

  const chartData = {
    labels: data?.map(item => (isDaily ? item.date : item.month)) || [],
    datasets: [
      {
        label: 'Clicks',
        data: data?.map(item => item.clicks) || [],
        borderColor: 'rgb(8, 145, 178)',
        backgroundColor: 'rgba(8, 145, 178, 0.14)',
        fill: true,
        tension: 0.35,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { precision: 0 } },
    },
  };

  return <div className="h-80"><Line data={chartData} options={options} /></div>;
}

export default ClickChart;
