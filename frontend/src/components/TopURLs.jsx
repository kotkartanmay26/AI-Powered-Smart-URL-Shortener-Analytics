function TopURLs({ urls = [] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="border-b border-slate-200 p-4 dark:border-slate-800">
        <h3 className="text-lg font-black">Top URLs</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            <tr>
              <th className="p-3">URL</th>
              <th className="p-3">Short Link</th>
              <th className="p-3 text-right">Clicks</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {urls.map(url => (
              <tr key={url.id} className="border-t border-slate-200 dark:border-slate-800">
                <td className="max-w-sm truncate p-3">
                  <a href={url.original_url} target="_blank" rel="noopener noreferrer" className="hover:underline">{url.original_url}</a>
                </td>
                <td className="p-3">{url.short_url || url.custom_alias || url.short_code}</td>
                <td className="p-3 text-right font-black">{url.click_count}</td>
                <td className="p-3">
                  <span className={`rounded-full px-2 py-1 text-xs font-bold ${url.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'}`}>
                    {url.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {urls.length === 0 && <p className="p-6 text-center text-slate-500">No analytics data yet.</p>}
      </div>
    </div>
  );
}

export default TopURLs;
