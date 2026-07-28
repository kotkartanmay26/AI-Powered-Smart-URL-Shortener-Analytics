import { useEffect, useState } from 'react';
import { API_BASE_URL, urlAPI } from '../services/api';

function URLList({ onEdit, onDelete }) {
  const [urls, setUrls] = useState([]);
  const [meta, setMeta] = useState({ page: 1, pages: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const [query, setQuery] = useState('');
  const [qr, setQr] = useState(null);

  const fetchUrls = async () => {
    setLoading(true);
    try {
      const res = await urlAPI.list({ page: meta.page, query: query || undefined });
      setUrls(res.data.items);
      setMeta({ page: res.data.page, pages: res.data.pages, total: res.data.total });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUrls();
  }, [meta.page]);

  const copyToClipboard = async (urlId, shortUrl) => {
    await navigator.clipboard.writeText(shortUrl);
    setCopiedId(urlId);
    setTimeout(() => setCopiedId(null), 1800);
  };

  const showQr = async (id) => {
    const res = await urlAPI.qr(id);
    setQr(res.data);
  };

  const exportCsv = async () => {
    const res = await urlAPI.exportCsv();
    const blobUrl = window.URL.createObjectURL(res.data);
    const anchor = document.createElement('a');
    anchor.href = blobUrl;
    anchor.download = 'urls-export.csv';
    anchor.click();
    window.URL.revokeObjectURL(blobUrl);
  };

  if (loading) {
    return <div className="rounded-lg border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">Loading URLs...</div>;
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-col gap-3 border-b border-slate-200 p-4 dark:border-slate-800 sm:flex-row">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && fetchUrls()}
          placeholder="Search original URL, code, or alias"
          className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
        />
        <button onClick={fetchUrls} className="rounded-md bg-slate-950 px-4 py-2 font-bold text-white dark:bg-white dark:text-slate-950">Search</button>
        <button onClick={exportCsv} className="rounded-md border border-slate-300 px-4 py-2 font-bold dark:border-slate-700">Export</button>
      </div>

      <div className="divide-y divide-slate-200 dark:divide-slate-800">
        {urls.map(url => {
          const shortUrl = url.short_url || `${API_BASE_URL}/${url.custom_alias || url.short_code}`;
          return (
            <div key={url.id} className="p-4">
              <div className="flex flex-col justify-between gap-4 xl:flex-row">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-black">{url.title || url.custom_alias || url.short_code}</h3>
                    <span className={`rounded-full px-2 py-1 text-xs font-bold ${url.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'}`}>
                      {url.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {url.is_password_protected && <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-bold text-amber-700">Protected</span>}
                    {url.is_one_time && <span className="rounded-full bg-cyan-100 px-2 py-1 text-xs font-bold text-cyan-700">One-time</span>}
                  </div>
                  <a href={url.original_url} target="_blank" rel="noopener noreferrer" className="mt-2 block break-all text-sm text-slate-500 hover:underline">
                    {url.original_url}
                  </a>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <span className="break-all rounded-md bg-slate-100 px-2 py-1 text-sm font-semibold text-slate-800 dark:bg-slate-800 dark:text-slate-100">{shortUrl}</span>
                    <button onClick={() => copyToClipboard(url.id, shortUrl)} className="rounded-md border px-2 py-1 text-xs font-bold">
                      {copiedId === url.id ? 'Copied!' : 'Copy'}
                    </button>
                    <button onClick={() => showQr(url.id)} className="rounded-md border px-2 py-1 text-xs font-bold">QR</button>
                  </div>
                  {url.expires_at && <p className="mt-2 text-xs text-amber-600">Expires: {new Date(url.expires_at).toLocaleString()}</p>}
                </div>
                <div className="flex gap-2 xl:ml-4">
                  <button onClick={() => onEdit(url)} className="rounded-md bg-slate-950 px-3 py-2 text-sm font-bold text-white dark:bg-white dark:text-slate-950">Edit</button>
                  <button onClick={() => onDelete(url.id)} className="rounded-md bg-rose-600 px-3 py-2 text-sm font-bold text-white">Delete</button>
                </div>
              </div>
            </div>
          );
        })}
        {urls.length === 0 && <p className="p-8 text-center text-slate-500">No URLs yet. Create your first production-ready short link.</p>}
      </div>

      <div className="flex items-center justify-between border-t border-slate-200 p-4 text-sm dark:border-slate-800">
        <span>{meta.total} URLs</span>
        <div className="flex gap-2">
          <button disabled={meta.page <= 1} onClick={() => setMeta(prev => ({ ...prev, page: prev.page - 1 }))} className="rounded-md border px-3 py-1 disabled:opacity-40">Prev</button>
          <span className="px-2 py-1">Page {meta.page} of {meta.pages || 1}</span>
          <button disabled={meta.pages === 0 || meta.page >= meta.pages} onClick={() => setMeta(prev => ({ ...prev, page: prev.page + 1 }))} className="rounded-md border px-3 py-1 disabled:opacity-40">Next</button>
        </div>
      </div>

      {qr && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4" onClick={() => setQr(null)}>
          <div className="max-w-sm rounded-lg bg-white p-5 text-slate-950" onClick={(event) => event.stopPropagation()}>
            <h3 className="text-lg font-black">QR Code</h3>
            <div className="mt-4" dangerouslySetInnerHTML={{ __html: qr.qr_code_svg }} />
            <a download="smartlink-qr.svg" href={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(qr.qr_code_svg)}`} className="mt-4 block rounded-md bg-slate-950 px-4 py-2 text-center font-bold text-white">Download SVG</a>
          </div>
        </div>
      )}
    </div>
  );
}

export default URLList;
