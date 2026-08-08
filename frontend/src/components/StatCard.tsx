interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'blue' | 'green' | 'amber' | 'slate'
}

const accents = {
  blue: 'border-l-brand-600',
  green: 'border-l-emerald-500',
  amber: 'border-l-amber-500',
  slate: 'border-l-slate-400',
}

export default function StatCard({ label, value, sub, accent = 'blue' }: StatCardProps) {
  return (
    <div className={`card border-l-4 p-5 ${accents[accent]}`}>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  )
}
