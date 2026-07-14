import { useEffect, useMemo, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function formatTimestamp(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(seconds ?? 0))
  const mins = Math.floor(total / 60)
  const secs = total % 60
  return `${mins}m ${secs}s`
}

export default function App() {
  const [settings, setSettings] = useState({
    personality_prompt: '',
    voice_id: '',
    is_available: true,
  })
  const [calls, setCalls] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const canSave = useMemo(
    () => settings.personality_prompt.trim() && settings.voice_id.trim(),
    [settings],
  )

  async function fetchAll() {
    setLoading(true)
    setError('')
    try {
      const [settingsResp, historyResp] = await Promise.all([
        fetch(`${API_BASE}/api/settings`),
        fetch(`${API_BASE}/api/call-history`),
      ])

      if (!settingsResp.ok || !historyResp.ok) {
        throw new Error('Failed to fetch dashboard data.')
      }

      setSettings(await settingsResp.json())
      setCalls(await historyResp.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  async function saveSettings(event) {
    event.preventDefault()
    if (!canSave) return

    setSaving(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/api/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...settings,
          personality_prompt: settings.personality_prompt.trim(),
          voice_id: settings.voice_id.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to save settings.')
      }

      setSettings(await response.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl p-6 md:p-10">
      <div className="space-y-8">
        <header>
          <h1 className="text-3xl font-semibold text-gray-900">AI Voice Agent Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Configure your ElevenLabs voice agent and review completed calls.
          </p>
        </header>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
        ) : null}

        <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900">Agent Settings</h2>
          <form className="mt-4 space-y-4" onSubmit={saveSettings}>
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-gray-700">System Prompt</span>
              <textarea
                className="min-h-28 w-full rounded-lg border border-gray-300 p-3 text-sm"
                value={settings.personality_prompt}
                onChange={(event) =>
                  setSettings((current) => ({ ...current, personality_prompt: event.target.value }))
                }
              />
            </label>

            <label className="block">
              <span className="mb-1 block text-sm font-medium text-gray-700">ElevenLabs Voice ID</span>
              <input
                className="w-full rounded-lg border border-gray-300 p-3 text-sm"
                value={settings.voice_id}
                onChange={(event) =>
                  setSettings((current) => ({ ...current, voice_id: event.target.value }))
                }
              />
            </label>

            <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                className="size-4"
                checked={settings.is_available}
                onChange={(event) =>
                  setSettings((current) => ({ ...current, is_available: event.target.checked }))
                }
              />
              Agent Availability ({settings.is_available ? 'ON' : 'OFF'})
            </label>

            <button
              type="submit"
              disabled={!canSave || saving}
              className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save Settings'}
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-medium text-gray-900">Call Logs</h2>

          {loading ? <p className="mt-4 text-sm text-gray-600">Loading…</p> : null}

          {!loading && calls.length === 0 ? (
            <p className="mt-4 text-sm text-gray-600">No completed calls yet.</p>
          ) : null}

          <ul className="mt-4 space-y-4">
            {calls.map((call) => (
              <li key={call.id} className="rounded-lg border border-gray-200 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                  <p className="font-medium text-gray-900">{formatTimestamp(call.started_at)}</p>
                  <p className="text-gray-600">Duration: {formatDuration(call.duration_seconds)}</p>
                </div>

                <div className="mt-3 rounded-md bg-gray-50 p-3 text-sm text-gray-700">
                  {call.transcript.length === 0 ? (
                    <p>No transcript available.</p>
                  ) : (
                    <ul className="space-y-1">
                      {call.transcript.map((line, index) => (
                        <li key={`${call.id}-${index}`}>
                          <span className="font-semibold uppercase">{line.speaker}:</span> {line.text}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {call.audio_url ? (
                  <audio className="mt-3 w-full" controls src={`${API_BASE}${call.audio_url}`}>
                    Your browser does not support the audio element.
                  </audio>
                ) : (
                  <p className="mt-3 text-xs text-gray-500">Audio recording unavailable.</p>
                )}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  )
}
