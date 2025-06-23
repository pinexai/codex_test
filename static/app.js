function JobList() {
  const [jobs, setJobs] = React.useState([]);
  const [query, setQuery] = React.useState('');

  const fetchJobs = React.useCallback(() => {
    const params = query ? `?q=${encodeURIComponent(query)}` : '';
    fetch(`/api/jobs${params}`)
      .then(res => res.json())
      .then(data => setJobs(data))
      .catch(err => console.error('Failed to fetch jobs', err));
  }, [query]);

  React.useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return (
    <div>
      <h1>Job Aggregator</h1>
      <input
        type="text"
        placeholder="Search jobs"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
      <button onClick={fetchJobs}>Search</button>
      {jobs.length === 0 ? (
        <p>No jobs available.</p>
      ) : (
        jobs.map((job, idx) => (
          <div key={idx} className="job">
            <div className="company">{job.company}</div>
            <div className="title">{job.title}</div>
            <div className="location">{job.location}</div>
            <div><a href={job.link} target="_blank" rel="noreferrer">Apply</a></div>
          </div>
        ))
      )}
    </div>
  );
}

ReactDOM.render(<JobList />, document.getElementById('root'));
