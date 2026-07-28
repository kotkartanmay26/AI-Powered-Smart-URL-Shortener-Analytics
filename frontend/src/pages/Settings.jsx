import { useState } from 'react';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

function Settings() {
  const { user, refreshUser } = useAuth();
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
    email: user?.email || '',
    password: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    setError('');
    try {
      const payload = Object.fromEntries(Object.entries(form).filter(([, value]) => value !== ''));
      await authAPI.updateMe(payload);
      await refreshUser();
      setMessage('Profile updated successfully.');
      setForm(prev => ({ ...prev, password: '' }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update profile.');
    }
  };

  return (
    <section className="mx-auto max-w-3xl">
      <h1 className="text-3xl font-black">Settings</h1>
      <form onSubmit={handleSubmit} className="mt-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {message && <div className="mb-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-700">{message}</div>}
        {error && <div className="mb-4 rounded-md bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}
        <div className="grid gap-4 sm:grid-cols-2">
          {[
            ['full_name', 'Full name', 'text'],
            ['username', 'Username', 'text'],
            ['email', 'Email', 'email'],
            ['password', 'New password', 'password'],
          ].map(([name, label, type]) => (
            <label key={name} className="text-sm font-semibold">
              {label}
              <input
                type={type}
                value={form[name]}
                onChange={(event) => setForm(prev => ({ ...prev, [name]: event.target.value }))}
                className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              />
            </label>
          ))}
        </div>
        <button className="mt-5 rounded-md bg-slate-950 px-5 py-2 font-bold text-white dark:bg-white dark:text-slate-950">Save Changes</button>
      </form>
    </section>
  );
}

export default Settings;
