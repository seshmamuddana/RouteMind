import { useState } from 'react'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import { ErrorState, LoadingState } from '../components/StateBlocks'
import { useAsync } from '../hooks/useAsync'
import { disruptionLabel, riskColor, shortRouteId } from '../utils/formatters'

export default function Disruptions() {
  const { data: routes } = useAsync(() => api.routes(), [])
  const [routeFilter, setRouteFilter] = useState('')
  const { data: disruptions, loading, error } = useAsync(
    () => api.disruptions(routeFilter || undefined),
    [routeFilter]
  )

  if (loading) return <LoadingState label="Loading disruptions…" />
  if (error || !disruptions) return <ErrorState message={error ?? 'Failed to load disruptions'} />

  const byType = disruptions.reduce<Record<string, number>>((acc, d) => {
    acc[d.DisruptionType] = (acc[d.DisruptionType] ?? 0) + 1
    return acc
  }, {})

  return (
    <>
      <PageHeader
        title="Disruption Monitor"
        description="Live disruption scenarios from route_disruptions.csv or computed on demand when the file is absent."
      >
        <select
          value={routeFilter}
          onChange={(e) => setRouteFilter(e.target.value)}
          className="input-field w-56"
        >
          <option value="">All routes</option>
          {routes?.map((r) => (
            <option key={r.routeId} value={r.routeId}>{shortRouteId(r.routeId)}</option>
          ))}
        </select>
      </PageHeader>

      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(byType).map(([type, count]) => (
            <div key={type} className="card p-5">
              <p className="text-2xl font-semibold text-slate-900">{count}</p>
              <p className="text-sm text-slate-500">{disruptionLabel(type)}</p>
            </div>
          ))}
        </div>

        <div className="card overflow-hidden">
          <div className="border-b border-slate-200 px-6 py-4">
            <h3 className="font-semibold text-slate-900">Active Disruptions ({disruptions.length})</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="table-head">
                <tr>
                  <th className="px-6 py-3">Route</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Severity</th>
                  <th className="px-6 py-3">Delay</th>
                  <th className="px-6 py-3">Capacity</th>
                  <th className="px-6 py-3">Stop</th>
                  <th className="px-6 py-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {disruptions.map((d) => (
                  <tr key={d.DisruptionID} className="hover:bg-slate-50">
                    <td className="px-6 py-3 font-mono text-xs text-brand-700">{shortRouteId(d.RouteID)}</td>
                    <td className="px-6 py-3">{disruptionLabel(d.DisruptionType)}</td>
                    <td className="px-6 py-3"><span className={`badge ${riskColor(d.Severity)}`}>{d.Severity}</span></td>
                    <td className="px-6 py-3">{d.DelayMinutes > 0 ? `${d.DelayMinutes} min` : '—'}</td>
                    <td className="px-6 py-3">{d.CapacityReduction > 0 ? `${d.CapacityReduction}%` : '—'}</td>
                    <td className="px-6 py-3 text-slate-600">{d.StopID}</td>
                    <td className="max-w-xs truncate px-6 py-3 text-slate-600">{d.Description}</td>
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
