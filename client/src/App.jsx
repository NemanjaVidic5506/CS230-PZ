import React, { useEffect, useState } from 'react'
import { createJob, getJob, previewDataset, listJobs, cancelJob } from './api'
import JobList from './components/JobList'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [mode, setMode] = useState('synthetic')
  const [dataset, setDataset] = useState('diabetes')
  const [preview, setPreview] = useState(null)

  async function submitJob() {
    try {
      setSubmitting(true)
      const body = mode === 'openml' ? { job_type: 'openml', dataset } : { job_type: 'synthetic', n_samples: 800, n_features: 15, noise: 0.2 }
      const job = await createJob(body)
      setJobs(prev => [{ task_id: job.task_id, state: 'PENDING', job_type: body.job_type, params: body }, ...prev])
    } catch (e) {
      alert(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function refreshJobs() {
    try {
      setJobs(prev => {
        const copy = [...prev]
        copy.forEach(async (j, idx) => {
          if (j.state && !['SUCCESS', 'FAILURE'].includes(j.state)) {
            try {
              const data = await getJob(j.task_id)
              copy[idx] = { ...copy[idx], ...data }
              setJobs([...copy])
            } catch {}
          }
        })
        return copy
      })
      const latest = await listJobs()
      const map = new Map()
      ;[...latest, ...jobs].forEach(j => map.set(j.task_id, j))
      setJobs(Array.from(map.values()))
    } catch {}
  }

  useEffect(() => {
    const t = setInterval(refreshJobs, 1500)
    return () => clearInterval(t)
  }, [])

  async function doPreview() {
    try {
      const p = await previewDataset(dataset, 5)
      setPreview(p)
    } catch (e) {
      alert(e.message)
    }
  }

  async function onCancel(taskId) {
    try {
      await cancelJob(taskId)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'Inter, system-ui, Arial' }}>
      <h1>Distribuirani ML</h1>
      

      <div style={{ display:'flex', gap:16, alignItems:'center', flexWrap:'wrap' }}>
        <label>
          <input type="radio" name="mode" value="synthetic" checked={mode==='synthetic'} onChange={() => setMode('synthetic')} /> Synthetic Regression
        </label>
        <label>
          <input type="radio" name="mode" value="openml" checked={mode==='openml'} onChange={() => setMode('openml')} /> OpenML Dataset
        </label>
        {mode==='openml' && (
          <>
            <input value={dataset} onChange={e=>setDataset(e.target.value)} placeholder="npr. diabetes, iris, wine" />
            <button onClick={doPreview}>Preview</button>
          </>
        )}
        <button onClick={submitJob} disabled={submitting} style={{ padding: '10px 16px', borderRadius: 10 }}>
          {submitting ? 'Slanje…' : 'Pokreni posao'}
        </button>
      </div>

      {preview && (
        <div style={{ marginTop: 16 }}>
          <h3>Preview dataset-a: {preview.dataset}</h3>
          <div><strong>Kolone:</strong> {preview.columns.join(', ')}</div>
          <pre style={{ background:'#fafafa', padding:12, borderRadius:12 }}>{JSON.stringify(preview.preview, null, 2)}</pre>
        </div>
      )}

      <h2 style={{ marginTop: 24 }}>Poslovi</h2>
      <JobList jobs={jobs} onCancel={onCancel} />
    </div>
  )
}
