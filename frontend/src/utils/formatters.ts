export function shortRouteId(id: string): string {
  return id.replace('RouteID_', '').slice(0, 8) + '…'
}

export function formatPercent(value: number, digits = 1): string {
  return `${value.toFixed(digits)}%`
}

export function formatKm(value: number): string {
  return `${value.toFixed(2)} km`
}

export function riskColor(level: string): string {
  switch (level.toUpperCase()) {
    case 'HIGH':
      return 'bg-red-50 text-red-700 border-red-200'
    case 'MEDIUM':
      return 'bg-amber-50 text-amber-800 border-amber-200'
    default:
      return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  }
}

export function disruptionLabel(type: string): string {
  return type.replace(/_/g, ' ')
}

export function decisionLabel(decision: string): string {
  return decision.replace(/_/g, ' ')
}
