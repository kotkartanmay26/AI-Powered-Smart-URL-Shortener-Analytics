import { Link } from 'react-router-dom';

function Landing() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="relative overflow-hidden px-6 py-8 sm:px-10 lg:px-16">
        <nav className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="text-2xl font-black">SmartLink</div>
          <div className="flex gap-2">
            <Link className="rounded-md px-4 py-2 text-sm font-semibold hover:bg-white/10" to="/login">Login</Link>
            <Link className="rounded-md bg-white px-4 py-2 text-sm font-semibold text-slate-950" to="/register">Create Account</Link>
          </div>
        </nav>
        <div className="mx-auto grid max-w-7xl gap-10 py-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <h1 className="max-w-4xl text-5xl font-black leading-tight sm:text-6xl">Smart URL Shortener & Analytics Platform</h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-300">
              Create secure short links, monitor every click, generate QR codes, and manage campaigns from a polished engineering-grade dashboard.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="rounded-md bg-cyan-400 px-5 py-3 font-bold text-slate-950 hover:bg-cyan-300" to="/register">Start Shortening</Link>
              <Link className="rounded-md border border-white/25 px-5 py-3 font-bold hover:bg-white/10" to="/login">Open Dashboard</Link>
            </div>
          </div>
          <div className="rounded-lg border border-white/10 bg-white/5 p-5 shadow-2xl">
            <div className="rounded-md bg-slate-900 p-4">
              <div className="mb-4 grid grid-cols-3 gap-3">
                {['Links', 'Clicks', 'QR Codes'].map((item, index) => (
                  <div key={item} className="rounded-md bg-slate-800 p-3">
                    <div className="text-2xl font-black">{[248, 18420, 91][index]}</div>
                    <div className="text-xs text-slate-400">{item}</div>
                  </div>
                ))}
              </div>
              <div className="space-y-3">
                {['Product launch', 'Campus placement drive', 'Final year project demo'].map(item => (
                  <div key={item} className="flex items-center justify-between rounded-md border border-slate-700 p-3">
                    <span>{item}</span>
                    <span className="text-cyan-300">Active</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Landing;
