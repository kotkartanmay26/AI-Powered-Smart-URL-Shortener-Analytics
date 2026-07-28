import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Register() {
  const [form, setForm] = useState({ full_name: '', email: '', username: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [existingAccount, setExistingAccount] = useState(false);
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (name, value) => setForm(prev => ({ ...prev, [name]: value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setExistingAccount(false);
    setSuccess('');
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await register({
        full_name: form.full_name || null,
        email: form.email,
        username: form.username,
        password: form.password,
      });
      setSuccess('Registration successful. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1200);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed.';
      setError(detail);
      setExistingAccount(String(detail).toLowerCase().includes('already'));
    } finally {
      setLoading(false);
    }
  };

  const goToLogin = () => {
    navigate('/login', { state: { email: form.email } });
  };

  return (
    <main className="grid min-h-screen w-full place-items-center overflow-x-hidden bg-slate-950 px-4 py-8 text-white">
      <div className="w-full max-w-lg rounded-lg border border-white/10 bg-white/5 p-6 shadow-2xl">
        <Link to="/" className="text-sm font-semibold text-cyan-300">Back to home</Link>
        <h1 className="mt-4 text-3xl font-black">Create Account</h1>
        <p className="mt-2 text-sm text-slate-300">Build secure short links and analytics reports for your project portfolio.</p>
        {error && (
          <div className="mt-4 rounded-md bg-rose-500/15 p-3 text-sm text-rose-100">
            <div className="font-semibold">
              {existingAccount ? 'This account already exists.' : error}
            </div>
            {existingAccount && (
              <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <span>Use the login page with this email instead of creating it again.</span>
                <button
                  type="button"
                  onClick={goToLogin}
                  className="rounded-md bg-cyan-400 px-3 py-2 text-sm font-black text-slate-950"
                >
                  Go to Login
                </button>
              </div>
            )}
          </div>
        )}
        {success && <div className="mt-4 rounded-md bg-emerald-500/15 p-3 text-sm text-emerald-100">{success}</div>}
        <form onSubmit={handleSubmit} className="mt-5 grid gap-4 sm:grid-cols-2">
          {[
            ['full_name', 'Full name', 'text'],
            ['email', 'Email', 'email'],
            ['username', 'Username', 'text'],
            ['password', 'Password', 'password'],
            ['confirmPassword', 'Confirm password', 'password'],
          ].map(([name, label, type]) => (
            <label key={name} className={name === 'full_name' ? 'block text-sm font-semibold sm:col-span-2' : 'block text-sm font-semibold'}>
              {label}
              <input
                type={type}
                value={form[name]}
                onChange={(event) => update(name, event.target.value)}
                className="mt-1 w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2"
                required={name !== 'full_name'}
              />
            </label>
          ))}
          <button disabled={loading} className="rounded-md bg-cyan-400 py-2 font-black text-slate-950 disabled:opacity-50 sm:col-span-2">
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-300">
          Already have an account? <Link to="/login" className="font-semibold text-cyan-300">Login</Link>
        </p>
      </div>
    </main>
  );
}

export default Register;
