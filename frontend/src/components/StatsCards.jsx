function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    ['Total URLs', stats.total_urls],
    ['Total Clicks', stats.total_clicks],
    ['Active Links', stats.active_links],
    ['Expired Links', stats.expired_links],
    ['Protected', stats.protected_links],
    ['One-time', stats.one_time_links],
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
      {cards.map(([label, value]) => (
        <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="text-3xl font-black">{value ?? 0}</div>
          <div className="mt-1 text-sm text-slate-500">{label}</div>
        </div>
      ))}
    </div>
  );
}

export default StatsCards;
