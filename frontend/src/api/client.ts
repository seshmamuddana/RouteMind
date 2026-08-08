const BASE = '/api'

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  dashboard: () => request<DashboardSummary>('/dashboard/summary'),
  routes: () => request<RouteListItem[]>('/routes'),
  route: (id: string) => request<RouteDetail>(`/routes/${encodeURIComponent(id)}`),
  optimizer: (routeId?: string) =>
    request<OptimizerResult[]>(routeId ? `/optimizer?route_id=${encodeURIComponent(routeId)}` : '/optimizer'),
  disruptions: (routeId?: string) =>
    request<Disruption[]>(routeId ? `/disruptions?route_id=${encodeURIComponent(routeId)}` : '/disruptions'),
  aiDecisions: (params?: { routeId?: string; riskLevel?: string }) => {
    const q = new URLSearchParams()
    if (params?.routeId) q.set('route_id', params.routeId)
    if (params?.riskLevel) q.set('risk_level', params.riskLevel)
    const qs = q.toString()
    return request<AIDecision[]>(`/ai-decisions${qs ? `?${qs}` : ''}`)
  },
}

export interface RouteListItem {
  routeId: string
  totalStops: number
  totalDistance: number
  routeScore: string
  station: number
  departureHour: number
}

export interface RouteStop {
  StopID: string
  Latitude: number
  Longitude: number
  StopType: string
  ActualSequence: number
  ZoneID: string | null
}

export interface RouteDetail {
  routeId: string
  station: string
  date: string
  departureTime: string
  capacity: number
  routeScore: string
  totalStops: number
  stops: RouteStop[]
  features?: {
    totalDistance: number
    averageStopDistance: number
    vehicleCapacity: number
    departureHour: number
    dayOfWeek: number
    dropoffRatio: number
    stopsPerKM: number
    capacityUtilization: number
    routeScore: string
  }
}

export interface OptimizerResult {
  RouteID: string
  TotalStops: number
  NNOptimizedStops: number
  OptimizedStops: number
  UnservedStops: number
  'OriginalDistance(KM)': number
  'NNDistance(KM)': number
  'OptimizedDistance(KM)': number
  'OriginalTime(Hours)': number
  'OptimizedTime(Hours)': number
  'Improvement(%)': number
  'ImprovementVsNN(%)': number
  'BaselineConstrainedDistance(KM)': number
  'ImprovementVsConstrained(%)': number
  StopsConstraint: boolean
  TimeConstraint: boolean
  AllStopsServed: boolean
}

export interface Disruption {
  DisruptionID: string
  RouteID: string
  DisruptionType: string
  Severity: string
  StopID: string
  Latitude?: number
  Longitude?: number
  DelayMinutes: number
  CapacityReduction: number
  Description: string
}

export interface AIDecision {
  RouteID: string
  DisruptionID: string
  DisruptionType: string
  Severity: string
  DelayMinutes: number
  CapacityReduction: number
  TotalStops: number
  StopsLost: number
  'DistanceChange(KM)': number
  'TimeChange(Hours)': number
  'RecoveryEfficiency(%)': number
  RecoverySuccessful: boolean
  RiskScore?: number
  RiskLevel?: string
  PriorityScore: number
  AI_Decision: string
  Recommendation: string
  MLRisk: string
  'MLConfidence(%)': number
  FinalRiskScore: number
  FinalRiskLevel: string
  AI_Explanation: string
}

export interface DashboardSummary {
  totalRoutes: number
  totalStops: number
  avgImprovement: number
  allStopsServed: number
  highRiskAlerts: number
  riskDistribution: Record<string, number>
  topRoutes: { RouteID: string; 'Improvement(%)': number; 'OptimizedDistance(KM)': number; TotalStops: number }[]
  defaultRouteId: string
}
