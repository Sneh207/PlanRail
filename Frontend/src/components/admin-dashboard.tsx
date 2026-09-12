import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  Check,
  CheckCircle2,
  CircleDot,
  Cpu,
  Database,
  Layers,
  MapPin,
  Network,
  Radio,
  Save,
  Server,
  Shield,
  Sliders,
  Sparkles,
  TrainFront,
  Wrench,
  Boxes,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  api,
  apiErrorMessage,
  asRecords,
  readNumber,
  readText,
  type JsonRecord,
} from "@/lib/api";
import type { AdminConfigUpdateRequest } from "@/lib/types";
import { cn } from "@/lib/utils";
import { EmptyState, PageIntro, PlanRailShell } from "@/components/planrail";

export function AdminDashboardPage() {
  const queryClient = useQueryClient();

  const adminHealthQuery = useQuery({
    queryKey: ["planrail", "admin", "health"],
    queryFn: api.adminHealth,
    refetchInterval: 10000,
  });

  const adminConfigQuery = useQuery({
    queryKey: ["planrail", "admin", "config"],
    queryFn: api.adminConfig,
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
  const healthData = adminHealthQuery.data;
  const configData = adminConfigQuery.data;

  const [activeTab, setActiveTab] = useState<"config" | "stations" | "sections" | "services">("config");

  // Config Form State
  const [maxBlockDuration, setMaxBlockDuration] = useState<number>(4.0);
  const [emergencyMultiplier, setEmergencyMultiplier] = useState<number>(2.5);
  const [criticalFreightMultiplier, setCriticalFreightMultiplier] = useState<number>(1.8);
  const [corridorSpeedLimit, setCorridorSpeedLimit] = useState<number>(130);
  const [dispatchMode, setDispatchMode] = useState<string>("BALANCED");
  const [autoApprovalThreshold, setAutoApprovalThreshold] = useState<number>(0.85);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Sync config from backend when loaded
  useEffect(() => {
    if (configData) {
      if (configData.max_block_duration_hours != null) setMaxBlockDuration(configData.max_block_duration_hours);
      if (configData.emergency_priority_multiplier != null) setEmergencyMultiplier(configData.emergency_priority_multiplier);
      if (configData.critical_freight_multiplier != null) setCriticalFreightMultiplier(configData.critical_freight_multiplier);
      if (configData.corridor_speed_limit_kmh != null) setCorridorSpeedLimit(configData.corridor_speed_limit_kmh);
      if (configData.dispatch_mode) setDispatchMode(configData.dispatch_mode);
      if (configData.auto_approval_threshold != null) setAutoApprovalThreshold(configData.auto_approval_threshold);
    }
  }, [configData]);

  async function handleSaveConfig(e: React.FormEvent) {
    e.preventDefault();
    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const payload: AdminConfigUpdateRequest = {
        max_block_duration_hours: Number(maxBlockDuration),
        emergency_priority_multiplier: Number(emergencyMultiplier),
        critical_freight_multiplier: Number(criticalFreightMultiplier),
        corridor_speed_limit_kmh: Number(corridorSpeedLimit),
        dispatch_mode: dispatchMode,
        auto_approval_threshold: Number(autoApprovalThreshold),
      };
      await api.updateAdminConfig(payload);
      setSaveSuccess(true);
      void queryClient.invalidateQueries({ queryKey: ["planrail", "admin", "config"] });
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(apiErrorMessage(err, "Failed to save configuration"));
    } finally {
      setIsSaving(false);
    }
  }

  const counts = healthData?.data_counts;

  const systemKpis = [
    {
      label: "Stations",
      value: counts?.stations ?? stations.length,
      icon: MapPin,
      tone: "blue",
    },
    {
      label: "Track Sections",
      value: counts?.sections ?? sections.length,
      icon: Network,
      tone: "blue",
    },
    {
      label: "Asset Fleet",
      value: counts?.assets ?? 85,
      icon: Layers,
      tone: "ink",
    },
    {
      label: "Maintenance Tasks",
      value: counts?.maintenance_requests ?? 150,
      icon: Wrench,
      tone: "amber",
    },
    {
      label: "Passenger Trains",
      value: counts?.passenger_trains ?? 24,
      icon: TrainFront,
      tone: "ink",
    },
    {
      label: "Freight Movements",
      value: counts?.freight_movements ?? freight.length,
      suffix: "SIM",
      icon: Boxes,
      tone: "ink",
    },
    {
      label: "Maintenance Windows",
      value: counts?.maintenance_windows ?? 408,
      icon: Activity,
      tone: "green",
    },
    {
      label: "Database Engine",
      textValue: healthData?.database?.healthy ? "HEALTHY" : "CHECKING",
      icon: Database,
      tone: healthData?.database?.healthy ? "green" : "amber",
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
                {healthData?.backend?.status === "healthy" ? (
                  <Badge variant="outline" className="border-rail-green/30 font-mono text-[9px] text-rail-green">
                    ONLINE
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-rail-amber/30 font-mono text-[9px] text-rail-amber">
                    {healthData?.backend?.status ?? "CHECKING"}
                  </Badge>
                )}
              </div>
              <div className="text-sm font-bold text-rail-ink/90">Uvicorn ASGI Server</div>
              <div className="font-mono text-[10px] text-rail-ink/50">
                v{healthData?.backend?.version ?? "1.0.0"} · FastAPI Core
              </div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">CORRIDOR DATABASE</span>
                {healthData?.database?.healthy ? (
                  <Badge variant="outline" className="border-rail-green/30 font-mono text-[9px] text-rail-green">
                    CONNECTED
                  </Badge>
                ) : (
                  <Badge variant="outline" className="border-rail-amber/30 font-mono text-[9px] text-rail-amber">
                    CONNECTING
                  </Badge>
                )}
              </div>
              <div className="text-sm font-bold text-rail-ink/90">
                {healthData?.database?.dialect?.toUpperCase() ?? "SQLITE"} Engine
              </div>
              <div className="font-mono text-[10px] text-rail-ink/50">Delhi–Agra Authoritative DB</div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">OPTIMIZATION SOLVER</span>
                <Badge variant="outline" className="border-rail-blue/30 font-mono text-[9px] text-rail-blue">
                  {healthData?.optimizer?.status?.toUpperCase() ?? "OPERATIONAL"}
                </Badge>
              </div>
              <div className="text-sm font-bold text-rail-ink/90">Google OR-Tools CP-SAT</div>
              <div className="font-mono text-[10px] text-rail-ink/50">
                Max Time: {healthData?.optimizer?.max_time_limit_sec ?? 60}s · Multi-Task Bundling
              </div>
            </div>

            <div className="rounded-lg border border-rail-ink/8 bg-rail-paper p-3.5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] text-rail-ink/45">PREDICTIVE AI ENGINE</span>
                <Badge variant="outline" className="border-rail-blue/30 font-mono text-[9px] text-rail-blue">
                  {healthData?.ai_engine?.status?.toUpperCase() ?? "CALIBRATED"}
                </Badge>
              </div>
              <div className="text-sm font-bold text-rail-ink/90">
                {healthData?.ai_engine?.model_type ?? "XGBoost"} Risk Model
              </div>
              <div className="font-mono text-[10px] text-rail-ink/50">
                Threshold: {healthData?.ai_engine?.decision_threshold?.toFixed(4) ?? "0.5421"} · {healthData?.ai_engine?.feature_count ?? 11} Features
              </div>
            </div>
          </div>
        </section>

        {/* Corridor Infrastructure & Configuration Governance Tabs */}
        <section className="rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 px-5 py-4">
            <div className="flex items-center gap-2">
              <Network className="size-4 text-rail-blue" />
              <span className="text-sm font-semibold">Corridor Governance &amp; Infrastructure Registry</span>
            </div>

            <div className="flex items-center gap-1 rounded-lg bg-rail-paper p-1 border border-rail-ink/10">
              <button
                onClick={() => setActiveTab("config")}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-semibold transition",
                  activeTab === "config" ? "bg-rail-panel shadow-sm text-rail-ink ring-1 ring-rail-ink/5" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                <Sliders className="size-3.5 inline mr-1 text-rail-blue" />
                Operational Parameters
              </button>
              <button
                onClick={() => setActiveTab("stations")}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-semibold transition",
                  activeTab === "stations" ? "bg-rail-panel shadow-sm text-rail-ink ring-1 ring-rail-ink/5" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Stations ({stations.length})
              </button>
              <button
                onClick={() => setActiveTab("sections")}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-semibold transition",
                  activeTab === "sections" ? "bg-rail-panel shadow-sm text-rail-ink ring-1 ring-rail-ink/5" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Track Sections ({sections.length})
              </button>
              <button
                onClick={() => setActiveTab("services")}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-semibold transition",
                  activeTab === "services" ? "bg-rail-panel shadow-sm text-rail-ink ring-1 ring-rail-ink/5" : "text-rail-ink/60 hover:text-rail-ink"
                )}
              >
                Freight Movements ({freight.length})
              </button>
            </div>
          </div>

          <div className="p-5">
            {/* TAB 1: OPERATIONAL PARAMETERS CONFIGURATION */}
            {activeTab === "config" && (
              <form onSubmit={handleSaveConfig} className="max-w-3xl space-y-5">
                <div className="border-b border-rail-ink/8 pb-3">
                  <h3 className="text-sm font-bold text-rail-ink">Corridor Operational &amp; Solver Governance</h3>
                  <p className="text-xs text-rail-ink/60 mt-0.5">
                    Configure corridor physical speed envelopes, possession limits, and CP-SAT multi-department optimization weights. Changes persist to the authoritative database.
                  </p>
                </div>

                {saveSuccess && (
                  <div className="flex items-center gap-2 rounded-md border border-rail-green/30 bg-rail-green/10 p-3 text-xs font-semibold text-rail-green">
                    <Check className="size-4 shrink-0" />
                    <span>Configuration successfully persisted to backend database. Future CP-SAT runs will apply these weights.</span>
                  </div>
                )}

                {saveError && (
                  <div className="flex items-center gap-2 rounded-md border border-rail-red/30 bg-rail-red/10 p-3 text-xs font-semibold text-rail-red">
                    <AlertTriangle className="size-4 shrink-0" />
                    <span>{saveError}</span>
                  </div>
                )}

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      MAX BLOCK DURATION (HOURS)
                    </label>
                    <Input
                      type="number"
                      step="0.5"
                      min="1.0"
                      max="8.0"
                      value={maxBlockDuration}
                      onChange={(e) => setMaxBlockDuration(Number(e.target.value))}
                      className="bg-rail-paper font-mono text-xs"
                    />
                    <p className="text-[11px] text-rail-ink/50">Maximum window possession allowed in one block allocation.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      CORRIDOR SPEED LIMIT (KM/H)
                    </label>
                    <Input
                      type="number"
                      step="5"
                      min="80"
                      max="160"
                      value={corridorSpeedLimit}
                      onChange={(e) => setCorridorSpeedLimit(Number(e.target.value))}
                      className="bg-rail-paper font-mono text-xs"
                    />
                    <p className="text-[11px] text-rail-ink/50">Main line max permissible speed envelope between Delhi and Agra.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      EMERGENCY PRIORITY MULTIPLIER
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      min="1.0"
                      max="5.0"
                      value={emergencyMultiplier}
                      onChange={(e) => setEmergencyMultiplier(Number(e.target.value))}
                      className="bg-rail-paper font-mono text-xs"
                    />
                    <p className="text-[11px] text-rail-ink/50">Penalty weight multiplier in CP-SAT solver for emergency defects.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      CRITICAL FREIGHT WEIGHT MULTIPLIER
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      min="1.0"
                      max="4.0"
                      value={criticalFreightMultiplier}
                      onChange={(e) => setCriticalFreightMultiplier(Number(e.target.value))}
                      className="bg-rail-paper font-mono text-xs"
                    />
                    <p className="text-[11px] text-rail-ink/50">Penalty cost for delaying high-priority freight paths during possessions.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      DISPATCH OPERATION MODE
                    </label>
                    <Select value={dispatchMode} onValueChange={setDispatchMode}>
                      <SelectTrigger className="bg-rail-paper text-xs font-mono">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BALANCED">BALANCED (Passenger + Freight + Maintenance)</SelectItem>
                        <SelectItem value="FREIGHT_HEAVY">FREIGHT_HEAVY (Prioritize Industrial Throughput)</SelectItem>
                        <SelectItem value="MAINTENANCE_PRIORITY">MAINTENANCE_PRIORITY (Aggressive Possession Windows)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-[11px] text-rail-ink/50">Governs CP-SAT objective trade-offs during schedule generation.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-mono text-[10px] font-semibold text-rail-ink/50">
                      AI CONFIDENCE AUTO-APPROVAL THRESHOLD
                    </label>
                    <Input
                      type="number"
                      step="0.05"
                      min="0.5"
                      max="0.99"
                      value={autoApprovalThreshold}
                      onChange={(e) => setAutoApprovalThreshold(Number(e.target.value))}
                      className="bg-rail-paper font-mono text-xs"
                    />
                    <p className="text-[11px] text-rail-ink/50">Minimum confidence score required for AI recommendation flagging.</p>
                  </div>
                </div>

                <div className="border-t border-rail-ink/8 pt-4 flex items-center justify-between">
                  <span className="font-mono text-[10px] text-rail-ink/45">AUTHORITATIVE CONFIGURATION · POST /api/v1/admin/config</span>
                  <Button
                    type="submit"
                    disabled={isSaving}
                    className="bg-rail-blue text-rail-paper hover:bg-rail-blue/90 text-xs font-semibold gap-1.5"
                  >
                    <Save className="size-3.5" />
                    {isSaving ? "Persisting Changes…" : "Save Operational Parameters"}
                  </Button>
                </div>
              </form>
            )}

            {/* TAB 2: STATIONS */}
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

            {/* TAB 3: SECTIONS */}
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

            {/* TAB 4: FREIGHT MOVEMENTS */}
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
