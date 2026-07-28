import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/settings', label: 'Settings' },
  { to: '/admin', label: 'Admin', adminOnly: true },
];

function AppShell({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950 dark:bg-slate-950 dark:text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900 lg:block">
        <NavLink to="/" className="block text-xl font-black tracking-tight">SmartLink</NavLink>
        <div className="mt-1 text-xs uppercase text-slate-500">URL Intelligence</div>
        <nav className="mt-8 space-y-1">
          {navItems.filter(item => !item.adminOnly || user?.is_admin).map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm font-semibold transition ${
                  isActive
                    ? 'bg-slate-950 text-white dark:bg-white dark:text-slate-950'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
          <div className="flex min-h-16 items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
            <div>
              <div className="font-bold">Welcome, {user?.full_name || user?.username}</div>
              <div className="text-xs text-slate-500">{user?.email}</div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => document.documentElement.classList.toggle('dark')}
                className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold dark:border-slate-700"
              >
                Theme
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md bg-rose-600 px-3 py-2 text-sm font-semibold text-white hover:bg-rose-700"
              >
                Logout
              </button>
            </div>
          </div>
          <nav className="flex gap-2 overflow-x-auto px-4 pb-3 lg:hidden">
            {navItems.filter(item => !item.adminOnly || user?.is_admin).map(item => (
              <NavLink key={item.to} to={item.to} className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700">
                {item.label}
              </NavLink>
            ))}
          </nav>
        </header>
        <main className="px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}

export default AppShell;
