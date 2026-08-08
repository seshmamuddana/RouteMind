import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { RouteStop } from '../api/client'

interface RouteMapProps {
  stops: RouteStop[]
  height?: string
}

const stationIcon = L.divIcon({
  className: '',
  html: `<div style="background:#2563eb;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 1px 4px rgba(0,0,0,.25)"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
})

export default function RouteMap({ stops, height = '400px' }: RouteMapProps) {
  useEffect(() => {
    delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl
  }, [])

  if (!stops.length) return null

  const sorted = [...stops].sort((a, b) => a.ActualSequence - b.ActualSequence)
  const positions: [number, number][] = sorted.map((s) => [s.Latitude, s.Longitude])
  const center = positions[Math.floor(positions.length / 2)]

  return (
    <div style={{ height }} className="overflow-hidden rounded-xl border border-slate-200">
      <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={positions} pathOptions={{ color: '#2563eb', weight: 3, opacity: 0.75 }} />
        {sorted.map((stop) =>
          stop.StopType === 'Station' ? (
            <Marker key={stop.StopID} position={[stop.Latitude, stop.Longitude]} icon={stationIcon}>
              <Popup>
                <strong>Station {stop.StopID}</strong>
                <br />
                Sequence: {stop.ActualSequence}
              </Popup>
            </Marker>
          ) : (
            <CircleMarker
              key={stop.StopID}
              center={[stop.Latitude, stop.Longitude]}
              radius={4}
              pathOptions={{ color: '#059669', fillColor: '#10b981', fillOpacity: 0.85, weight: 1 }}
            >
              <Popup>
                <strong>{stop.StopID}</strong>
                <br />
                Zone: {stop.ZoneID ?? '—'}
                <br />
                Seq: {stop.ActualSequence}
              </Popup>
            </CircleMarker>
          )
        )}
      </MapContainer>
    </div>
  )
}
