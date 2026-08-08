import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Optimization from './pages/Optimization'
import RouteExplorer from './pages/RouteExplorer'
import Disruptions from './pages/Disruptions'
import AIDecisions from './pages/AIDecisions'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="optimization" element={<Optimization />} />
        <Route path="explorer" element={<RouteExplorer />} />
        <Route path="disruptions" element={<Disruptions />} />
        <Route path="ai-decisions" element={<AIDecisions />} />
      </Route>
    </Routes>
  )
}
