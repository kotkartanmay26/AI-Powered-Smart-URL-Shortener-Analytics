function URLSearchFilter({ onSearch, onFilter }) {
  return (
    <div className="mb-4 flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 md:flex-row">
      <input
        type="text"
        placeholder="Search analytics URLs..."
        onChange={(event) => onSearch(event.target.value)}
        className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
      />
      <select
        onChange={(event) => {
          const value = event.target.value;
          onFilter(value === 'all' ? null : value === 'active');
        }}
        className="rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
      >
        <option value="all">All statuses</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
  );
}

export default URLSearchFilter;
