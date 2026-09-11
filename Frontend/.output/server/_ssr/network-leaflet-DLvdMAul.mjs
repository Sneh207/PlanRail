import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { t as require_leaflet_src } from "../_libs/leaflet.mjs";
import { a as useMap, i as CircleMarker, n as Popup, r as MapContainer, t as TileLayer } from "../_libs/react-leaflet.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/network-leaflet-DLvdMAul.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var import_leaflet_src = /* @__PURE__ */ __toESM(require_leaflet_src());
function MapBoundsFitter({ points }) {
	const map = useMap();
	(0, import_react.useEffect)(() => {
		if (points.length > 0) {
			const bounds = import_leaflet_src.default.latLngBounds(points);
			map.fitBounds(bounds, {
				padding: [24, 24],
				maxZoom: 12
			});
		}
	}, [map, points]);
	return null;
}
function NetworkLeaflet({ sections, stations, sectionPoints, stationPoints, onSectionSelect }) {
	const allPositions = [...stationPoints, ...sectionPoints].map((p) => p.position);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(MapContainer, {
		center: allPositions[0] ?? [28, 77.5],
		zoom: 8,
		scrollWheelZoom: false,
		className: "h-full w-full",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MapBoundsFitter, { points: allPositions }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TileLayer, {
				attribution: "© <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>",
				url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
			}),
			sectionPoints.map(({ record, position }, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleMarker, {
				center: position,
				pathOptions: {
					color: "var(--color-rail-blue, #2563eb)",
					fillColor: "var(--color-rail-blue, #2563eb)",
					fillOpacity: .7
				},
				radius: 7,
				eventHandlers: { click: () => onSectionSelect(record) },
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Popup, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-36 space-y-1 text-xs",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
							className: "block text-sm font-semibold",
							children: readLabel(record, [
								"section_id",
								"sectionId",
								"id"
							]) ?? "Section"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							readLabel(record, ["start_station", "startStation"]),
							" → ",
							readLabel(record, ["end_station", "endStation"])
						] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
							"Length: ",
							readLabel(record, [
								"distance",
								"distance_km",
								"distanceKm"
							]) ?? "—",
							" km"
						] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: ["Traffic: ", readLabel(record, [
							"traffic_level",
							"trafficLevel",
							"status"
						]) ?? "—"] })
					]
				}) })
			}, `section-${index}`)),
			stationPoints.map(({ record, position }, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleMarker, {
				center: position,
				pathOptions: {
					color: "var(--color-rail-green, #16a34a)",
					fillColor: "var(--color-rail-green, #16a34a)",
					fillOpacity: .9
				},
				radius: 6,
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Popup, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-32 space-y-1 text-xs",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("strong", {
							className: "block font-semibold",
							children: readLabel(record, [
								"name",
								"station_name",
								"stationName"
							]) ?? "Station"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "font-mono text-[10px] text-gray-500",
							children: ["Code: ", readLabel(record, [
								"code",
								"station_code",
								"stationCode",
								"station_id",
								"stationId"
							]) ?? "—"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: ["Lines: ", readLabel(record, ["total_lines", "totalLines"]) ?? "—"] })
					]
				}) })
			}, `station-${index}`)),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "sr-only",
				children: [
					sections.length,
					" sections and ",
					stations.length,
					" stations mapped."
				]
			})
		]
	});
}
function readLabel(record, keys) {
	for (const key of keys) {
		const value = record[key];
		if (typeof value === "string" && value.trim()) return value;
		if (typeof value === "number" || typeof value === "boolean") return String(value);
	}
	return null;
}
//#endregion
export { NetworkLeaflet };
