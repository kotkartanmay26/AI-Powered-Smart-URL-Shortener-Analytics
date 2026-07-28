import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

function Login() {
  const location = useLocation();
  const [form, setForm] = useState({ email: location.state?.email || '', password: '' });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async () => {
    setError('');
    setMessage('');
    try {
      const res = await authAPI.forgotPassword(form.email);
      setMessage(res.data.message);
    } catch {
      setError('Enter a valid email before requesting a reset.');
    }
  };

  const useDemo = (role) => {
    if (role === 'admin') {
      setForm({ email: 'demo.admin@example.com', password: 'Admin@12345' });
    } else {
      setForm({ email: 'demo.user@example.com', password: 'User@12345' });
    }
    setError('');
    setMessage('');
  };

  return (
    <main className="grid min-h-screen w-full place-items-center overflow-x-hidden bg-slate-950 px-4 py-8 text-white">
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-white/5 p-6 shadow-2xl">
        <Link to="/" className="text-sm font-semibold text-cyan-300">Back to home</Link>
        <h1 className="mt-4 text-3xl font-black">Login</h1>
        <p className="mt-2 text-sm text-slate-300">Access your short links, analytics, reports, and settings.</p>
        {error && <div className="mt-4 rounded-md bg-rose-500/15 p-3 text-sm text-rose-100">{error}</div>}
        {message && <div className="mt-4 rounded-md bg-emerald-500/15 p-3 text-sm text-emerald-100">{message}</div>}
        <div className="mt-5 grid gap-2 rounded-md border border-white/10 bg-slate-900/70 p-3 text-sm">
          <div className="font-semibold text-slate-200">Demo accounts</div>
          <div className="grid gap-2 sm:grid-cols-2">
            <button type="button" onClick={() => useDemo('admin')} className="rounded-md border border-cyan-300/40 px-3 py-2 font-semibold text-cyan-200">
              Use Admin Demo
            </button>
            <button type="button" onClick={() => useDemo('user')} className="rounded-md border border-cyan-300/40 px-3 py-2 font-semibold text-cyan-200">
              Use User Demo
            </button>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <label className="block text-sm font-semibold">
            Email
            <input type="email" value={form.email} onChange={(event) => setForm(prev => ({ ...prev, email: event.target.value }))} className="mt-1 w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2" required />
          </label>
          <label className="block text-sm font-semibold">
            Password
            <input type="password" value={form.password} onChange={(event) => setForm(prev => ({ ...prev, password: event.target.value }))} className="mt-1 w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2" required />
          </label>
          <button disabled={loading} className="w-full rounded-md bg-cyan-400 py-2 font-black text-slate-950 disabled:opacity-50">{loading ? 'Logging in...' : 'Login'}</button>
        </form>
        <div className="mt-4 flex items-center justify-between text-sm">
          <button onClick={forgotPassword} className="font-semibold text-cyan-300">Forgot password?</button>
          <Link to="/register" className="font-semibold text-cyan-300">Create account</Link>
        </div>
      </div>
    </main>
  );
}

export default Login;
