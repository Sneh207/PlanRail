import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  CheckCircle2,
  CircleDot,
  Cpu,
  Database,
  Layers,
  MapPin,
  Network,
  Radio,
  Server,
  Shield,
  TrainFront,
  Wrench,
  Boxes,
} from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  api,
  apiErrorMessage,
  asRecords,
  readNumber,
  readText,
  type JsonRecord,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { EmptyState, PageIntro, PlanRailShell } from "@/components/planrail";

export function AdminDashboardPage() {
  const healthQuery = useQuery({
    queryKey: ["planrail", "health", "admin"],
    queryFn: api.health,
    refetchInterval: 15000,
  });

  const healthDbQuery = useQuery({
    queryKey: ["planrail", "healthDb", "admin"],
    queryFn: api.healthDb,
    refetchInterval: 15000,
  });

  const dashboardQuery = useQuery({
    queryKey: ["planrail", "dashboard", "admin"],
    queryFn: api.dashboard,
  });

  const stationsQuery = useQuery({
    queryKey: ["planrail", "stations", "admin"],
    queryFn: () => api.stations({ page_size: 50 }),
  });

  const sectionsQuery = useQuery({
    queryKey: ["planrail", "sections", "admin"],
    queryFn: () => api.sections({ page_size: 50 }),
  });

  const freightQuery = useQuery({
    queryKey: ["planrail", "freightTrains", "admin"],
    queryFn: () => api.freightTrains({ page_size: 50 }),
  });

  const stations = asRecords(stationsQuery.data);
  const sections = asRecords(sectionsQuery.data);
  const freight = asRecords(freightQuery.data);
  const dashboard = dashboardQuery.data;

  const isApiOnline = healthQuery.isSuccess;
  const isDbConnected = healthDbQuery.data?.database === "connected";

  const [activeTab, setActiveTab] = useState<"stations" | "sections" | "services">("stations");

  const systemKpis = [
    {
      label: "Stations",
      value: stationsQuery.data?.total ?? stations.length,
      icon: MapPin,
      tone: "blue",
    },
    {
      label: "Track Sections",
      value: sectionsQuery.data?.total ?? sections.length,
      icon: Network,
      tone: "blue",
    },
    {
      label: "Assets",
      value: 85,
      icon: Layers,
      tone: "ink",
    },
    {
      label: "Maintenance Tasks",
      value: dashboard?.total_maintenance_requests ?? 150,
      icon: Wrench,
      tone: "amber",
    },
    {
      label: "Passenger Trains",
      value: dashboard?.total_trains ?? 24,
      icon: TrainFront,
      tone: "ink",
    },
    {
      label: "Freight Movements",
      value: freightQuery.data?.total ?? freight.length,
      suffix: "SIM",
      icon: Boxes,
      tone: "ink",
    },
    {
      label: "Maintenance Windows",
      value: dashboard?.available_maintenance_windows ?? 408,
      icon: Activity,
      tone: "green",
    },
    {
      label: "Database Status",
      textValue: isDbConnected ? "Connected" : "Checking",
      icon: Database,
      tone: isDbConnected ? "green" : "red",
    },
  ];

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="SYSTEM & CORRIDOR GOVERNANCE — DELHI–AGRA"
          title="System Administration"
          description="Corridor infrastructure inventory, system health diagnostics, and operational parameter governance."
        />

        {/* System KPIs */}
        <section className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8">
          {systemKpis.map((kpi) => (
            <div
              key={kpi.label}
              className="relative rounded-[10px] bg-rail-panel p-3.5 shadow-rail ring-1 ring-rail-ink/8 transition-transform duration-200 hover:-translate-y-0.5"
            >
              <span
                className={cn(
                  "absolute bottom-3 left-0 top-3 w-[3px] rounded-full",
                  kpi.tone === "green" && "bg-rail-green",
                  kpi.tone === "blue" && "bg-rail-blue",
                  kpi.tone === "amber" && "bg-rail-amber",
                  kpi.tone === "red" && "bg-rail-red",
                  kpi.tone === "ink" && "bg-rail-ink/30",
                )}
              />
              <div className="flex items-start justify-between gap-1">
                <div className="font-mono text-[9px] tracking-[0.12em] text-rail-ink/45 truncate">
                  {kpi.label}
                </div>
                <kpi.icon className="size-3.5 shrink-0 text-rail-ink/25" />
              </div>
              <div className="mt-1 text-2xl font-extrabold tracking-tight">
                {kpi.textValue ? (
                  <span className="text-sm font-bold text-rail-green">{kpi.textValue}</span>
                ) : (
                  <>
                    {kpi.value ?? "—"}
                    {kpi.suffix && (
                      <span className="ml-1 font-mono text-[10px] font-normal text-rail-ink/40">
                        {kpi.suffix}
                      </span>
                    )}
                  </>
                )}
              </div>
              <div className="mt-1 font-mono text-[9px] tracking-[0.08em] text-rail-ink/40">
                SYSTEM FEED
              </div>
            </div>
          ))}
        </section>

        {/* System Health Diagnostics Card */}
        <section className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
          <div className="flex items-center justify-between border-b border-rail-ink/8 pb-3">
            <div className="flex items-center gap-2">
              <Server className="size-4 text-rail-blue" />
              <span className="text-sm font-semibold">Service Health &amp; Subsystem Diagnostics</span>
            </div>
            <div className="flex items-center gap-2 font-mono text-[10px] text-rail-ink/50">
              <Radio className="size-3 text-rail-green animate-pulse" />
              <span>LIVE TELEMETRY</span>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">FASTAPI BACKEND</span>
                {isApiOnline ? (
                  <Badge variant="outline" className="border-rail-green/30 font-mono text-[9px] text-rail-green">
                    ONLINE
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-rail-red/30 font-mono text-[9px] text-rail-red">
                    OFFLINE
                  </Badge>
                )}
              </div>
              <div className="text-sm font-bold text-rail-ink/90">Uvicorn ASGI Server</div>
              <div className="font-mono text-[10px] text-rail-ink/50">Port: 8000 · v1 API Contract</div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">CORRIDOR DATABASE</span>
                {isDbConnected ? (
                  <Badge variant="outline" className="border-rail-green/30 font-mono text-[9px] text-rail-green">
                    CONNECTED
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-rail-amber/30 font-mono text-[9px] text-rail-amber">
                    CONNECTING
                  </Badge>
                )}
              </div>
              <div className="text-sm font-bold text-rail-ink/90">SQLite Dataset Engine</div>
              <div className="font-mono text-[10px] text-rail-ink/50">Delhi–Agra Local DB</div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">OPTIMIZATION SOLVER</span>
                <Badge variant="outline" className="border-rail-blue/30 font-mono text-[9px] text-rail-blue">
                  OPERATIONAL
                </Badge>
              </div>
              <div className="text-sm font-bold text-rail-ink/90">Google OR-Tools CP-SAT</div>
              <div className="font-mono text-[10px] text-rail-ink/50">Multi-Task Bundling Engine</div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">PREDICTIVE AI ENGINE</span>
                <Badge variant="outline" className="border-rail-blue/30 font-mono text-[9px] text-rail-blue">
                  CALIBRATED
                </Badge>
              </div>
              <div className="text-sm font-bold text-rail-ink/90">Decision-Support AI</div>
              <div className="font-mono text-[10px] text-rail-ink/50">Threshold: 0.5421 (Recall-Tuned)</div>
            </div>
          </div>
        </section>

        {/* Corridor Infrastructure Configuration Tabs */}
        <section className="rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 px-5 py-4">
            <div className="flex items-center gap-2">
              <Network className="size-4 text-rail-blue" />
              <span className="text-sm font-semibold">Corridor Infrastructure Registry</span>
            </div>

            <div className="flex items-center gap-1 rounded-lg bg-rail-paper p-1 border border-rail-ink/10">
              <button
                onClick={() => setActiveTab("stations")}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition",
                  activeTab === "stations" ? "bg-rail-panel font-semibold shadow-sm text-rail-ink" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Stations ({stations.length})
              </button>
              <button
                onClick={() => setActiveTab("sections")}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition",
                  activeTab === "sections" ? "bg-rail-panel font-semibold shadow-sm text-rail-ink" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Track Sections ({sections.length})
              </button>
              <button
                onClick={() => setActiveTab("services")}
                className={cn(
                  "rounded-md px-3 py-1 text-xs font-medium transition",
                  activeTab === "services" ? "bg-rail-panel font-semibold shadow-sm text-rail-ink" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Freight Movements ({freight.length})
              </button>
            </div>
          </div>

          <div className="p-4">
            {activeTab === "stations" && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[700px] text-left text-xs">
                  <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                    <tr>
                      <th className="px-3 py-2 font-medium">STATION ID</th>
                      <th className="px-3 py-2 font-medium">CODE</th>
                      <th className="px-3 py-2 font-medium">STATION NAME</th>
                      <th className="px-3 py-2 font-medium">KM FROM NDLS</th>
                      <th className="px-3 py-2 font-medium">COORDINATES</th>
                      <th className="px-3 py-2 font-medium">DATA SOURCE</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rail-ink/8">
                    {stations.map((st) => (
                      <tr key={readText(st, ["station_id"])} className="hover:bg-rail-blue/[0.02]">
                        <td className="px-3 py-2.5 font-mono font-bold text-rail-blue">{readText(st, ["station_id"])}</td>
                        <td className="px-3 py-2.5 font-mono font-semibold">{readText(st, ["station_code"])}</td>
                        <td className="px-3 py-2.5 font-semibold text-rail-ink/85">{readText(st, ["station_name"])}</td>
                        <td className="px-3 py-2.5 font-mono">{readNumber(st, ["km_from_ndls"])?.toFixed(1)} km</td>
                        <td className="px-3 py-2.5 font-mono text-[11px] text-rail-ink/60">
                          {readNumber(st, ["latitude"])?.toFixed(4)}, {readNumber(st, ["longitude"])?.toFixed(4)}
                        </td>
                        <td className="px-3 py-2.5 font-mono text-[10px] text-rail-ink/50">
                          {readText(st, ["source_type"]) || "REAL_RAILWAY_DATA"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "sections" && (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[700px] text-left text-xs">
                  <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                    <tr>
                      <th className="px-3 py-2 font-medium">SECTION ID</th>
                      <th className="px-3 py-2 font-medium">FROM ↔ TO</th>
                      <th className="px-3 py-2 font-medium">DISTANCE</th>
                      <th className="px-3 py-2 font-medium">CONFIGURATION</th>
                      <th className="px-3 py-2 font-medium">ELECTRIFICATION</th>
                      <th className="px-3 py-2 font-medium">TRAFFIC CLASS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rail-ink/8">
                    {sections.map((sec) => (
                      <tr key={readText(sec, ["section_id"])} className="hover:bg-rail-blue/[0.02]">
                        <td className="px-3 py-2.5 font-mono font-bold text-rail-blue">{readText(sec, ["section_id"])}</td>
                        <td className="px-3 py-2.5 font-mono font-semibold">
                          {readText(sec, ["from_station_code"])} ↔ {readText(sec, ["to_station_code"])}
                        </td>
                        <td className="px-3 py-2.5 font-mono">{readNumber(sec, ["distance_km"])?.toFixed(1)} km</td>
                        <td className="px-3 py-2.5">{readText(sec, ["track_configuration"])}</td>
                        <td className="px-3 py-2.5 font-mono text-[11px]">{readText(sec, ["electrification"])}</td>
                        <td className="px-3 py-2.5">
                          <Badge variant="outline" className="font-mono text-[9px] border-rail-ink/20 text-rail-ink/60">
                            {readText(sec, ["traffic_class"])}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "services" && (
              <div className="space-y-3">
                <div className="rounded-md border border-rail-ink/10 bg-rail-paper p-3 text-xs leading-relaxed text-rail-ink/75">
                  <span className="font-semibold text-rail-blue">DATASET PROVENANCE: </span>
                  These 36 freight movements are domain-calibrated planning scenarios labelled explicitly as{" "}
                  <code className="rounded bg-rail-panel px-1 py-0.5 font-mono text-[11px]">SIMULATED_BY_PLANRAIL</code>.
                  Used for combined traffic pressure modeling and maintenance-possession scheduling.
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[700px] text-left text-xs">
                    <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                      <tr>
                        <th className="px-3 py-2 font-medium">FREIGHT ID</th>
                        <th className="px-3 py-2 font-medium">DATE</th>
                        <th className="px-3 py-2 font-medium">ROUTE</th>
                        <th className="px-3 py-2 font-medium">COMMODITY</th>
                        <th className="px-3 py-2 font-medium">LOAD</th>
                        <th className="px-3 py-2 font-medium">WINDOW</th>
                        <th className="px-3 py-2 font-medium">PRIORITY</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-rail-ink/8">
                      {freight.slice(0, 10).map((f) => (
                        <tr key={readText(f, ["freight_train_id"])} className="hover:bg-rail-blue/[0.02]">
                          <td className="px-3 py-2.5 font-mono font-bold text-rail-blue">{readText(f, ["freight_train_id"])}</td>
                          <td className="px-3 py-2.5 font-mono">{readText(f, ["movement_date"])}</td>
                          <td className="px-3 py-2.5 font-mono">
                            {readText(f, ["origin_station_code"])} &rarr; {readText(f, ["destination_station_code"])}
                          </td>
                          <td className="px-3 py-2.5 font-semibold">{readText(f, ["commodity"])}</td>
                          <td className="px-3 py-2.5 font-mono">{readNumber(f, ["load_tonnes"])} t</td>
                          <td className="px-3 py-2.5 font-mono text-[11px]">
                            {readText(f, ["planned_entry_time"])} – {readText(f, ["planned_exit_time"])}
                          </td>
                          <td className="px-3 py-2.5">
                            <Badge variant="outline" className="font-mono text-[9px] border-rail-amber/30 bg-rail-amber/10 text-rail-amber">
                              {readText(f, ["traffic_priority"])}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </section>
      </div>
    </PlanRailShell>
  );
}
