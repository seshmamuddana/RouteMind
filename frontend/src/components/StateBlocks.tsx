export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
        <p className="mt-3 text-sm text-slate-500">{label}</p>
      </div>
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="card max-w-md p-6 text-center">
        <p className="font-medium text-red-600">Unable to load data</p>
        <p className="mt-2 text-sm text-slate-500">{message}</p>
        <p className="mt-3 text-xs text-slate-400">Ensure the API server is running on port 8000.</p>
      </div>
    </div>
  )
}
