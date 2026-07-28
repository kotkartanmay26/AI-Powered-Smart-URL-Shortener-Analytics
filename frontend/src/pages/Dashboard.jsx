import { useState } from 'react';
import CreateURL from '../components/CreateURL';
import EditURL from '../components/EditURL';
import URLList from '../components/URLList';
import { urlAPI } from '../services/api';

function Dashboard() {
  const [editingUrl, setEditingUrl] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [notice, setNotice] = useState('');

  const refresh = (message) => {
    if (message) setNotice(message);
    setRefreshKey(prev => prev + 1);
  };

  const handleDeleteUrl = async (urlId) => {
    if (!window.confirm('Delete this URL and all analytics for it?')) return;
    try {
      await urlAPI.delete(urlId);
      refresh('URL deleted successfully.');
    } catch (err) {
      setNotice(err.response?.data?.detail || 'Failed to delete URL.');
    }
  };

  return (
    <>
      <section className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-cyan-600">Link Operations</p>
          <h1 className="text-3xl font-black">Dashboard</h1>
          <p className="mt-2 max-w-2xl text-slate-600 dark:text-slate-300">
            Create branded short links, enforce access rules, generate QR codes, and manage campaign URLs.
          </p>
        </div>
        {notice && <div className="rounded-md bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{notice}</div>}
      </section>

      <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
        <CreateURL onSuccess={() => refresh('URL created successfully.')} />
        <URLList key={refreshKey} onEdit={setEditingUrl} onDelete={handleDeleteUrl} />
      </div>

      {editingUrl && (
        <EditURL
          url={editingUrl}
          onClose={() => setEditingUrl(null)}
          onSuccess={() => refresh('URL updated successfully.')}
        />
      )}
    </>
  );
}

export default Dashboard;
