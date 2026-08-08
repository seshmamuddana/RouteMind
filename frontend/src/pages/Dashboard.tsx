import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import RouteMap from '../components/RouteMap'
import StatCard from '../components/StatCard'
import { ErrorState, LoadingState } from '../components/StateBlocks'
import { useAsync } from '../hooks/useAsync'
import { formatPercent, shortRouteId } from '../utils/formatters'

const RISK_COLORS = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#10b981' }

export default function Dashboard() {
  const { data: summary, loading, error } = useAsync(() => api.dashboard(), [])
  const { data: route } = useAsync(
    () => (summary ? api.route(summary.defaultRouteId) : Promise.reject()),
    [summary?.defaultRouteId]
  )

  if (loading) return <LoadingState label="Loading dashboard…" />
  if (error || !summary) return <ErrorState message={error ?? 'Unknown error'} />

  const riskDist = Object.entries(summary.riskDistribution).map(([name, value]) => ({
    name,
    value,
    fill: RISK_COLORS[name as keyof typeof RISK_COLORS],
  }))

  const topRoutes = summary.topRoutes.map((r) => ({
    name: shortRouteId(r.RouteID),
    improvement: r['Improvement(%)'],
  }))

  return (
    <>
      <PageHeader
        title="Operations Dashboard"
        description="Live metrics from your route optimization pipeline and AI decision engine."
      />

      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Active Routes" value={summary.totalRoutes} sub={`${summary.totalStops} delivery stops`} />
          <StatCard
            label="Avg. Improvement"
            value={formatPercent(summary.avgImprovement)}
            sub="Improved optimizer vs original"
            accent="green"
          />
          <StatCard
            label="Fully Served Routes"
            value={summary.allStopsServed}
            sub="Within stop & time constraints"
            accent="blue"
          />
          <StatCard
            label="High Risk Alerts"
            value={summary.highRiskAlerts}
            sub="Requires immediate attention"
            accent="amber"
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900">Top Route Improvements</h3>
            <p className="mb-4 text-xs text-slate-500">Distance saved by improved optimizer</p>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topRoutes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} unit="%" />
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
                <Bar dataKey="improvement" fill="#2563eb" radius={[4, 4, 0, 0]} name="Improvement %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card p-6">
            <h3 className="font-semibold text-slate-900">Risk Distribution</h3>
            <p className="mb-4 text-xs text-slate-500">Current disruption risk levels</p>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={riskDist} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                  {riskDist.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {route && (
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900">Sample Route — {route.station}</h3>
            <p className="mb-4 text-xs text-slate-500">
              {route.date} · {route.totalStops} stops · loaded from processed_dataset.csv
            </p>
            <RouteMap stops={route.stops} height="320px" />
          </div>
        )}
      </div>
    </>
  )
}
