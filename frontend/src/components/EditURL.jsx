import { useEffect, useState } from 'react';
import { urlAPI } from '../services/api';

function EditURL({ url, onClose, onSuccess }) {
  const [form, setForm] = useState({
    original_url: '',
    custom_alias: '',
    title: '',
    description: '',
    password: '',
    expires_at: '',
    is_active: true,
    is_one_time: false,
    clear_password: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!url) return;
    const expiresAt = url.expires_at
      ? new Date(new Date(url.expires_at).getTime() - new Date(url.expires_at).getTimezoneOffset() * 60000).toISOString().slice(0, 16)
      : '';
    setForm({
      original_url: url.original_url,
      custom_alias: url.custom_alias || '',
      title: url.title || '',
      description: url.description || '',
      password: '',
      expires_at: expiresAt,
      is_active: url.is_active,
      is_one_time: url.is_one_time,
      clear_password: false,
    });
  }, [url]);

  const update = (name, value) => setForm(prev => ({ ...prev, [name]: value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        original_url: form.original_url,
        custom_alias: form.custom_alias || null,
        title: form.title || null,
        description: form.description || null,
        expires_at: form.expires_at || null,
        is_active: form.is_active,
        is_one_time: form.is_one_time,
        clear_password: form.clear_password,
      };
      if (form.password) payload.password = form.password;
      await urlAPI.update(url.id, payload);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update URL.');
    } finally {
      setLoading(false);
    }
  };

  if (!url) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4">
      <form onSubmit={handleSubmit} className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6 text-slate-950 shadow-xl dark:bg-slate-900 dark:text-slate-100">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-2xl font-black">Edit URL</h2>
          <button type="button" onClick={onClose} className="rounded-md border px-3 py-1">Close</button>
        </div>
        {error && <div className="mt-4 rounded-md bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          {[
            ['original_url', 'Original URL', 'url'],
            ['title', 'Title', 'text'],
            ['custom_alias', 'Custom Alias', 'text'],
            ['password', 'New Password', 'password'],
            ['expires_at', 'Expiry Date & Time', 'datetime-local'],
          ].map(([name, label, type]) => (
            <label key={name} className={name === 'original_url' ? 'block text-sm font-semibold sm:col-span-2' : 'block text-sm font-semibold'}>
              {label}
              <input
                type={type}
                value={form[name]}
                onChange={(event) => update(name, event.target.value)}
                className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
                required={name === 'original_url'}
              />
            </label>
          ))}
          <label className="block text-sm font-semibold sm:col-span-2">
            Description
            <textarea
              value={form.description}
              onChange={(event) => update('description', event.target.value)}
              className="mt-1 min-h-24 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            />
          </label>
          {[
            ['is_active', 'Active'],
            ['is_one_time', 'One-time URL'],
            ['clear_password', 'Remove password protection'],
          ].map(([name, label]) => (
            <label key={name} className="flex items-center gap-2 text-sm font-semibold">
              <input type="checkbox" checked={form[name]} onChange={(event) => update(name, event.target.checked)} />
              {label}
            </label>
          ))}
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button type="button" onClick={onClose} className="rounded-md border px-4 py-2 font-bold">Cancel</button>
          <button disabled={loading} className="rounded-md bg-slate-950 px-4 py-2 font-bold text-white disabled:opacity-50 dark:bg-white dark:text-slate-950">
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditURL;
