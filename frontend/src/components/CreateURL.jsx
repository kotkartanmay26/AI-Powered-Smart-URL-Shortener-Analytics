import { useState } from 'react';
import { urlAPI } from '../services/api';

const initialForm = {
  original_url: '',
  custom_alias: '',
  title: '',
  description: '',
  password: '',
  expires_at: '',
  is_one_time: false,
};

function CreateURL({ onSuccess }) {
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const update = (name, value) => setForm(prev => ({ ...prev, [name]: value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).filter(([, value]) => value !== '' && value !== false)
      );
      await urlAPI.create(payload);
      setForm(initialForm);
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h2 className="text-xl font-black">Create Short URL</h2>
      <p className="mt-1 text-sm text-slate-500">Add optional controls for alias, expiration, password, and one-time access.</p>
      {error && <div className="mt-4 rounded-md bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}

      <div className="mt-5 space-y-4">
        <label className="block text-sm font-semibold">
          Original URL *
          <input
            type="url"
            value={form.original_url}
            onChange={(event) => update('original_url', event.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="https://example.com"
            required
          />
        </label>

        {[
          ['title', 'Title', 'text', 'Campaign name'],
          ['custom_alias', 'Custom Alias', 'text', 'my-custom-link'],
          ['password', 'Password Protection', 'password', 'Optional password'],
          ['expires_at', 'Expiry Date & Time', 'datetime-local', ''],
        ].map(([name, label, type, placeholder]) => (
          <label key={name} className="block text-sm font-semibold">
            {label}
            <input
              type={type}
              value={form[name]}
              onChange={(event) => update(name, event.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder={placeholder}
            />
          </label>
        ))}

        <label className="block text-sm font-semibold">
          Description
          <textarea
            value={form.description}
            onChange={(event) => update('description', event.target.value)}
            className="mt-1 min-h-20 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
          />
        </label>

        <label className="flex items-center gap-2 text-sm font-semibold">
          <input
            type="checkbox"
            checked={form.is_one_time}
            onChange={(event) => update('is_one_time', event.target.checked)}
          />
          One-time URL
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-slate-950 py-2 font-bold text-white disabled:opacity-50 dark:bg-white dark:text-slate-950"
        >
          {loading ? 'Creating...' : 'Create URL'}
        </button>
      </div>
    </form>
  );
}

export default CreateURL;
