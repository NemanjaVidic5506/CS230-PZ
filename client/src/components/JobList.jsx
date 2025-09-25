import React from 'react'

export default function JobList({ jobs, onCancel }) {
  return (
    <div style={{ display: 'grid', gap: 12 }}>
      {jobs.map(j => (
        <div key={j.task_id} style={{ border: '1px solid #ddd', borderRadius: 12, padding: 12 }}>
          <div><strong>ID:</strong> {j.task_id}</div>
          <div><strong>Tip:</strong> {j.job_type}</div>
          <div><strong>Status:</strong> {j.state}</div>
          <div><strong>Parametri:</strong> <code>{JSON.stringify(j.params)}</code></div>
          {j.result && (
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', background:'#fafafa', padding:10, borderRadius:8 }}>
{JSON.stringify(j.result, null, 2)}
            </pre>
          )}
          {j.error && (<div style={{ color: 'crimson' }}>Error: {j.error}</div>)}
          {onCancel && j.state && !['SUCCESS','FAILURE'].includes(j.state) && (
            <button onClick={() => onCancel(j.task_id)} style={{ marginTop: 8 }}>Otkaži</button>
          )}
        </div>
      ))}
    </div>
  )
}
