import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useAuthStore } from '../store/authStore'
import StarField from '../components/Layout/StarField'
import { Telescope, Loader2 } from 'lucide-react'

export default function Register() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '', display_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await authApi.register(form)
      setTokens(data.access_token, data.refresh_token)
      const me = await authApi.me()
      setUser(me)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-space-gradient flex items-center justify-center p-4 relative">
      <StarField />
      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-nebula-purple/20 border border-nebula-purple/30 flex items-center justify-center mx-auto mb-4">
            <Telescope className="w-7 h-7 text-nebula-purple" />
          </div>
          <h1 className="text-2xl font-bold">Create account</h1>
          <p className="text-white/50 text-sm mt-1">Start tracking the night sky</p>
        </div>

        <form onSubmit={handleSubmit} className="glass p-6 space-y-4">
          {error && (
            <div className="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="text-xs font-medium text-white/50 block mb-1.5">Display name (optional)</label>
            <input
              type="text"
              className="input"
              placeholder="Stargazer"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs font-medium text-white/50 block mb-1.5">Email</label>
            <input
              type="email"
              className="input"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="text-xs font-medium text-white/50 block mb-1.5">Password</label>
            <input
              type="password"
              className="input"
              placeholder="Choose a strong password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={8}
            />
          </div>

          <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2" disabled={loading}>
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating account…</> : 'Create account'}
          </button>
        </form>

        <p className="text-center text-sm text-white/40 mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-nebula-purple hover:text-violet-400 transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
