import { useEffect, useState } from 'react';
import { adminAPI } from '../services/api';

function Admin() {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [summaryRes, usersRes] = await Promise.all([adminAPI.summary(), adminAPI.users()]);
      setSummary(summaryRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Admin data is unavailable.');
    }
  };

  useEffect(() => { load(); }, []);

  const toggleUser = async (user) => {
    await adminAPI.setUserStatus(user.id, !user.is_active);
    await load();
  };

  if (error) return <div className="rounded-md bg-rose-50 p-4 text-rose-700">{error}</div>;

  return (
    <section>
      <h1 className="text-3xl font-black">Admin Dashboard</h1>
      <div className="mt-6 grid gap-4 sm:grid-cols-4">
        {summary && Object.entries(summary).map(([key, value]) => (
          <div key={key} className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <div className="text-2xl font-black">{value}</div>
            <div className="text-sm capitalize text-slate-500">{key.replace('_', ' ')}</div>
          </div>
        ))}
      </div>
      <div className="mt-6 overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100 dark:bg-slate-800">
            <tr><th className="p-3">User</th><th className="p-3">Role</th><th className="p-3">Status</th><th className="p-3 text-right">Action</th></tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-t border-slate-200 dark:border-slate-800">
                <td className="p-3"><div className="font-semibold">{user.username}</div><div className="text-slate-500">{user.email}</div></td>
                <td className="p-3">{user.is_admin ? 'Admin' : 'User'}</td>
                <td className="p-3">{user.is_active ? 'Active' : 'Blocked'}</td>
                <td className="p-3 text-right"><button onClick={() => toggleUser(user)} className="rounded-md border px-3 py-1">{user.is_active ? 'Block' : 'Activate'}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default Admin;
