import { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import ClickChart from '../components/ClickChart';
import StatsCards from '../components/StatsCards';
import TopURLs from '../components/TopURLs';
import URLSearchFilter from '../components/URLSearchFilter';

function AnalyticsDashboard() {
  const [stats, setStats] = useState(null);
  const [urls, setUrls] = useState([]);
  const [view, setView] = useState('daily');
  const [searchQuery, setSearchQuery] = useState('');
  const [isActiveFilter, setIsActiveFilter] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadStats = async () => {
    const res = await analyticsAPI.getStats();
    setStats(res.data);
    setLoading(false);
  };

  const loadURLs = async () => {
    const res = await analyticsAPI.searchURLs(searchQuery || null, isActiveFilter);
    setUrls(res.data);
  };

  useEffect(() => { loadStats(); }, []);
  useEffect(() => { loadURLs(); }, [searchQuery, isActiveFilter]);

  const exportReport = async () => {
    const res = await analyticsAPI.reportCsv();
    const blobUrl = window.URL.createObjectURL(res.data);
    const anchor = document.createElement('a');
    anchor.href = blobUrl;
    anchor.download = 'analytics-report.csv';
    anchor.click();
    window.URL.revokeObjectURL(blobUrl);
  };

  if (loading) {
    return <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">Loading analytics...</div>;
  }

  return (
    <section>
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-600">Insights</p>
          <h1 className="text-3xl font-black">Analytics Dashboard</h1>
          <p className="mt-2 max-w-2xl text-slate-600 dark:text-slate-300">Track click trends, top links, referrers, devices, browsers, and geographic signals.</p>
        </div>
        <button onClick={exportReport} className="rounded-md bg-emerald-600 px-4 py-2 font-bold text-white">Export Report</button>
      </div>

      <StatsCards stats={stats} />

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-black">Click Trend</h2>
            <div className="rounded-md border border-slate-300 p-1 dark:border-slate-700">
              {['daily', 'monthly'].map(item => (
                <button key={item} onClick={() => setView(item)} className={`rounded px-3 py-1 text-sm font-bold capitalize ${view === item ? 'bg-slate-950 text-white dark:bg-white dark:text-slate-950' : ''}`}>
                  {item}
                </button>
              ))}
            </div>
          </div>
          <ClickChart dailyData={stats?.daily_clicks} monthlyData={stats?.monthly_clicks} view={view} />
        </div>

        <div className="space-y-4">
          {[
            ['Countries', stats.countries],
            ['Browsers', stats.browsers],
            ['Devices', stats.devices],
            ['Referrers', stats.referrers],
          ].map(([title, rows]) => (
            <div key={title} className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
              <h3 className="font-black">{title}</h3>
              <div className="mt-3 space-y-2">
                {(rows || []).map(row => (
                  <div key={`${title}-${row.name}`} className="flex items-center justify-between text-sm">
                    <span className="truncate">{row.name}</span>
                    <span className="font-bold">{row.value}</span>
                  </div>
                ))}
                {(!rows || rows.length === 0) && <p className="text-sm text-slate-500">No data yet.</p>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <URLSearchFilter onSearch={setSearchQuery} onFilter={setIsActiveFilter} />
        <TopURLs urls={urls.length ? urls : stats?.top_urls} />
      </div>
    </section>
  );
}

export default AnalyticsDashboard;
