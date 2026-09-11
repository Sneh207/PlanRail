import { useEffect } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import type { JsonRecord } from "@/lib/api";

type NetworkPoint = {
  record: JsonRecord;
  position: [number, number];
};

function MapBoundsFitter({ points }: { points: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (points.length > 0) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [24, 24], maxZoom: 12 });
    }
  }, [map, points]);
  return null;
}

export function NetworkLeaflet({
  sections,
  stations,
  sectionPoints,
  stationPoints,
  onSectionSelect,
}: {
  sections: JsonRecord[];
  stations: JsonRecord[];
  sectionPoints: NetworkPoint[];
  stationPoints: NetworkPoint[];
  onSectionSelect: (section: JsonRecord) => void;
}) {
  const allPositions = [...stationPoints, ...sectionPoints].map((p) => p.position);
  const defaultCenter: [number, number] = [28.0, 77.5]; // Delhi-Agra corridor center

  return (
    <MapContainer
      center={allPositions[0] ?? defaultCenter}
      zoom={8}
      scrollWheelZoom={false}
      className="h-full w-full"
    >
      <MapBoundsFitter points={allPositions} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {sectionPoints.map(({ record, position }, index) => (
        <CircleMarker
          key={`section-${index}`}
          center={position}
          pathOptions={{ color: "var(--color-rail-blue, #2563eb)", fillColor: "var(--color-rail-blue, #2563eb)", fillOpacity: 0.7 }}
          radius={7}
          eventHandlers={{ click: () => onSectionSelect(record) }}
        >
          <Popup>
            <div className="min-w-36 space-y-1 text-xs">
              <strong className="block text-sm font-semibold">{readLabel(record, ["section_id", "sectionId", "id"]) ?? "Section"}</strong>
              <div>{readLabel(record, ["start_station", "startStation"])} → {readLabel(record, ["end_station", "endStation"])}</div>
              <div>Length: {readLabel(record, ["distance", "distance_km", "distanceKm"]) ?? "—"} km</div>
              <div>Traffic: {readLabel(record, ["traffic_level", "trafficLevel", "status"]) ?? "—"}</div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
      {stationPoints.map(({ record, position }, index) => (
        <CircleMarker
          key={`station-${index}`}
          center={position}
          pathOptions={{ color: "var(--color-rail-green, #16a34a)", fillColor: "var(--color-rail-green, #16a34a)", fillOpacity: 0.9 }}
          radius={6}
        >
          <Popup>
            <div className="min-w-32 space-y-1 text-xs">
              <strong className="block font-semibold">{readLabel(record, ["name", "station_name", "stationName"]) ?? "Station"}</strong>
              <div className="font-mono text-[10px] text-gray-500">Code: {readLabel(record, ["code", "station_code", "stationCode", "station_id", "stationId"]) ?? "—"}</div>
              <div>Lines: {readLabel(record, ["total_lines", "totalLines"]) ?? "—"}</div>
            </div>
          </Popup>
        </CircleMarker>
      ))}
      <div className="sr-only">
        {sections.length} sections and {stations.length} stations mapped.
      </div>
    </MapContainer>
  );
}

function readLabel(record: JsonRecord, keys: readonly string[]) {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" && value.trim()) return value;
    if (typeof value === "number" || typeof value === "boolean") return String(value);
  }
  return null;
}