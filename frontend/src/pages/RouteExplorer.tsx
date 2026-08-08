import { useState } from 'react'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import RouteMap from '../components/RouteMap'
import { ErrorState, LoadingState } from '../components/StateBlocks'
import { useAsync } from '../hooks/useAsync'
import { formatKm, shortRouteId } from '../utils/formatters'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export default function RouteExplorer() {
  const { data: routes, loading: routesLoading, error: routesError } = useAsync(() => api.routes(), [])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const activeId = selectedId ?? routes?.[0]?.routeId ?? null
  const { data: route, loading: routeLoading, error: routeError } = useAsync(
    () => (activeId ? api.route(activeId) : Promise.reject('No route')),
    [activeId]
  )

  if (routesLoading) return <LoadingState label="Loading routes…" />
  if (routesError || !routes?.length) return <ErrorState message={routesError ?? 'No routes found'} />

  return (
    <>
      <PageHeader
        title="Route Explorer"
        description="Browse delivery routes and stops dynamically from processed_dataset.csv."
      />

      <div className="space-y-6">
        <div className="card p-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">Select route</label>
          <select
            value={activeId ?? ''}
            onChange={(e) => setSelectedId(e.target.value)}
            className="input-field max-w-xl"
          >
            {routes.map((r) => (
              <option key={r.routeId} value={r.routeId}>
                {shortRouteId(r.routeId)} — {r.totalStops} stops — {formatKm(r.totalDistance)}
              </option>
            ))}
          </select>
        </div>

        {routeLoading && <LoadingState label="Loading route stops…" />}
        {routeError && <ErrorState message={routeError} />}

        {route && !routeLoading && (
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="card p-6 lg:col-span-2">
              <h3 className="font-semibold text-slate-900">Delivery Map</h3>
              <p className="mb-4 text-xs text-slate-500">
                Station {route.station} · {route.date} · {route.totalStops} stops
              </p>
              <RouteMap stops={route.stops} height="420px" />
            </div>

            <div className="space-y-4">
              <div className="card p-6">
                <h3 className="font-semibold text-slate-900">Route Details</h3>
                <dl className="mt-4 space-y-3 text-sm">
                  <div className="flex justify-between"><dt className="text-slate-500">Route ID</dt><dd className="font-mono text-xs text-brand-700">{shortRouteId(route.routeId)}</dd></div>
                  <div className="flex justify-between"><dt className="text-slate-500">Departure</dt><dd>{route.departureTime}</dd></div>
                  <div className="flex justify-between"><dt className="text-slate-500">Capacity</dt><dd>{route.capacity.toLocaleString()} cm³</dd></div>
                  <div className="flex justify-between"><dt className="text-slate-500">Score</dt><dd><span className="badge border-brand-200 bg-brand-50 text-brand-700">{route.routeScore}</span></dd></div>
                </dl>
              </div>

              {route.features && (
                <div className="card p-6">
                  <h3 className="font-semibold text-slate-900">Engineered Features</h3>
                  <dl className="mt-4 space-y-3 text-sm">
                    {[
                      ['Total Distance', formatKm(route.features.totalDistance)],
                      ['Avg Stop Distance', `${route.features.averageStopDistance.toFixed(3)} km`],
                      ['Departure', `${route.features.departureHour}:00 · ${DAYS[route.features.dayOfWeek]}`],
                      ['Dropoff Ratio', `${(route.features.dropoffRatio * 100).toFixed(1)}%`],
                      ['Stops / KM', route.features.stopsPerKM.toFixed(2)],
                      ['Capacity Util.', `${(route.features.capacityUtilization * 100).toFixed(2)}%`],
                    ].map(([label, value]) => (
                      <div key={label as string} className="flex justify-between">
                        <dt className="text-slate-500">{label}</dt>
                        <dd className="font-medium text-slate-900">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  )
}
