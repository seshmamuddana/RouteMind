import { useState } from 'react'
import { api } from '../api/client'
import PageHeader from '../components/PageHeader'
import { ErrorState, LoadingState } from '../components/StateBlocks'
import { useAsync } from '../hooks/useAsync'
import { decisionLabel, riskColor, shortRouteId } from '../utils/formatters'

export default function AIDecisions() {
  const [riskFilter, setRiskFilter] = useState('ALL')
  const { data: decisions, loading, error } = useAsync(
    () => api.aiDecisions(riskFilter === 'ALL' ? undefined : { riskLevel: riskFilter }),
    [riskFilter]
  )

  if (loading) return <LoadingState label="Running AI decision engine…" />
  if (error || !decisions) return <ErrorState message={error ?? 'Failed to load decisions'} />

  const avgConfidence = decisions.reduce((s, d) => s + d['MLConfidence(%)'], 0) / decisions.length
  const avgRisk = decisions.reduce((s, d) => s + d.FinalRiskScore, 0) / decisions.length
  const recoveryRate = (decisions.filter((d) => d.RecoverySuccessful).length / decisions.length) * 100

  return (
    <>
      <PageHeader
        title="AI Decision Engine"
        description="Risk scoring and routing recommendations from ml_ai_route_decisions.csv or computed live."
      >
        <div className="flex gap-2">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((level) => (
            <button
              key={level}
              onClick={() => setRiskFilter(level)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                riskFilter === level
                  ? 'bg-brand-600 text-white'
                  : 'border border-slate-300 bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </PageHeader>

      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="card p-5">
            <p className="text-sm text-slate-500">Avg ML Confidence</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{avgConfidence.toFixed(1)}%</p>
          </div>
          <div className="card p-5">
            <p className="text-sm text-slate-500">Avg Risk Score</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{avgRisk.toFixed(1)}</p>
          </div>
          <div className="card p-5">
            <p className="text-sm text-slate-500">Recovery Success</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{recoveryRate.toFixed(0)}%</p>
          </div>
        </div>

        <div className="space-y-4">
          {decisions.map((d) => (
            <div key={d.DisruptionID} className="card p-6">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`badge ${riskColor(d.FinalRiskLevel)}`}>{d.FinalRiskLevel}</span>
                    <span className="badge border-slate-200 bg-slate-50 text-slate-700">{decisionLabel(d.AI_Decision)}</span>
                    <span className="font-mono text-xs text-slate-500">{shortRouteId(d.RouteID)}</span>
                  </div>
                  <p className="mt-3 text-sm text-slate-700">{d.AI_Explanation}</p>
                  <p className="mt-2 text-sm font-medium text-brand-700">{d.Recommendation}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-semibold text-slate-900">{d.PriorityScore}</p>
                  <p className="text-xs text-slate-500">Priority</p>
                </div>
              </div>
              <div className="mt-4 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-3 lg:grid-cols-6">
                {[
                  ['ML Risk', d.MLRisk],
                  ['Confidence', `${d['MLConfidence(%)']}%`],
                  ['Stops Lost', d.StopsLost],
                  ['Recovery', `${d['RecoveryEfficiency(%)']}%`],
                  ['Time Δ', `${d['TimeChange(Hours)']} h`],
                  ['Distance Δ', `${d['DistanceChange(KM)']} km`],
                ].map(([label, value]) => (
                  <div key={label as string}>
                    <p className="text-xs text-slate-500">{label}</p>
                    <p className="text-sm font-medium text-slate-900">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
