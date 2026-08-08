import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import { ErrorState, LoadingState } from '../components/StateBlocks'
import { useAsync } from '../hooks/useAsync'
import { formatKm, formatPercent, shortRouteId } from '../utils/formatters'

export default function Optimization() {
  const { data: optimizer, loading, error } = useAsync(() => api.optimizer(), [])
  const [selected, setSelected] = useState<string | null>(null)

  if (loading) return <LoadingState label="Loading optimizer results…" />
  if (error || !optimizer?.length) return <ErrorState message={error ?? 'No optimizer data'} />

  const activeId = selected ?? optimizer[0].RouteID
  const route = optimizer.find((r) => r.RouteID === activeId)!

  const comparisonData = [
    { algo: 'Original', distance: route['OriginalDistance(KM)'] },
    { algo: 'Nearest Neighbor', distance: route['NNDistance(KM)'] },
    { algo: 'Constrained', distance: route['BaselineConstrainedDistance(KM)'] },
    { algo: 'Improved (2-opt)', distance: route['OptimizedDistance(KM)'] },
  ]

  const fleetComparison = optimizer.slice(0, 10).map((r) => ({
    route: shortRouteId(r.RouteID),
    original: r['OriginalDistance(KM)'],
    nn: r['NNDistance(KM)'],
    improved: r['OptimizedDistance(KM)'],
  }))

  return (
    <>
      <PageHeader
        title="Route Optimization"
        description="Compare nearest-neighbor, constrained, and improved 2-opt optimizers — data loaded live from improved_optimizer_results.csv."
      />

      <div className="space-y-6">
        <div className="card p-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">Select route</label>
          <select
            value={activeId}
            onChange={(e) => setSelected(e.target.value)}
            className="input-field max-w-xl"
          >
            {optimizer.map((r) => (
              <option key={r.RouteID} value={r.RouteID}>
                {shortRouteId(r.RouteID)} — {r.TotalStops} stops — {formatPercent(r['Improvement(%)'])} improvement
              </option>
            ))}
          </select>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: 'Total Stops', value: route.TotalStops },
            { label: 'Optimized Stops', value: route.OptimizedStops },
            { label: 'Unserved Stops', value: route.UnservedStops },
            { label: 'Improvement', value: formatPercent(route['Improvement(%)']) },
          ].map((s) => (
            <div key={s.label} className="card p-4">
              <p className="text-xs font-medium text-slate-500">{s.label}</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">{s.value}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900">Algorithm Comparison</h3>
            <p className="mb-4 text-xs text-slate-500">Distance (km) for selected route</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="algo" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
                <Bar dataKey="distance" fill="#2563eb" radius={[4, 4, 0, 0]} name="Distance (km)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-6">
            <h3 className="font-semibold text-slate-900">Fleet Comparison</h3>
            <p className="mb-4 text-xs text-slate-500">Original vs NN vs Improved (top 10)</p>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={fleetComparison}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="route" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
                <Legend />
                <Bar dataKey="original" fill="#94a3b8" name="Original" />
                <Bar dataKey="nn" fill="#8b5cf6" name="Nearest Neighbor" />
                <Bar dataKey="improved" fill="#2563eb" name="Improved" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="border-b border-slate-200 px-6 py-4">
            <h3 className="font-semibold text-slate-900">All Routes</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="table-head">
                <tr>
                  <th className="px-6 py-3">Route</th>
                  <th className="px-6 py-3">Stops</th>
                  <th className="px-6 py-3">Original</th>
                  <th className="px-6 py-3">NN</th>
                  <th className="px-6 py-3">Improved</th>
                  <th className="px-6 py-3">Improvement</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {optimizer.map((r) => (
                  <tr key={r.RouteID} className="hover:bg-slate-50">
                    <td className="px-6 py-3 font-mono text-xs text-brand-700">{shortRouteId(r.RouteID)}</td>
                    <td className="px-6 py-3">{r.OptimizedStops}/{r.TotalStops}</td>
                    <td className="px-6 py-3">{formatKm(r['OriginalDistance(KM)'])}</td>
                    <td className="px-6 py-3">{formatKm(r['NNDistance(KM)'])}</td>
                    <td className="px-6 py-3 font-medium text-emerald-700">{formatKm(r['OptimizedDistance(KM)'])}</td>
                    <td className="px-6 py-3 font-medium text-emerald-700">{formatPercent(r['Improvement(%)'])}</td>
                    <td className="px-6 py-3">
                      <span className={`badge ${r.AllStopsServed ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-amber-200 bg-amber-50 text-amber-800'}`}>
                        {r.AllStopsServed ? 'Compliant' : `${r.UnservedStops} unserved`}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
