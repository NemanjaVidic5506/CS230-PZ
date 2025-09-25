export async function createJob(body = {}) {
  const r = await fetch('/api/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!r.ok) throw new Error('Job submit failed')
  return r.json()
}
export async function getJob(taskId) {
  const r = await fetch(`/api/jobs/${taskId}`)
  if (!r.ok) throw new Error('Fetch job failed')
  return r.json()
}
export async function listJobs() {
  const r = await fetch('/api/jobs')
  if (!r.ok) throw new Error('Jobs list failed')
  return r.json()
}
export async function cancelJob(taskId) {
  const r = await fetch(`/api/jobs/${taskId}/cancel`, { method: 'POST' })
  if (!r.ok) throw new Error('Cancel failed')
  return r.json()
}
export async function previewDataset(name, n=5) {
  const url = `/api/external/preview?name=${encodeURIComponent(name)}&n=${n}`
  const r = await fetch(url)
  if (!r.ok) throw new Error('Preview failed')
  return r.json()
}
