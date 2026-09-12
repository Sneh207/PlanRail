import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Boxes,
  BrainCircuit,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Clock3,
  Filter,
  Gauge,
  Layers,
  Search,
  ShieldAlert,
  Sparkles,
  Wrench,
} from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { cn } from "@/lib/utils";
import { EmptyState, PageIntro, PlanRailShell } from "@/components/planrail";

export function MaintenanceDashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ["planrail", "dashboard"],
    queryFn: api.dashboard,
  });

  const maintenanceQuery = useQuery({
    queryKey: ["planrail", "maintenance", "all_crew"],
    queryFn: () => api.maintenance({ page_size: 150 }),
  });

  const assetsQuery = useQuery({
    queryKey: ["planrail", "assets", "all_crew"],
    queryFn: () => api.assets({ page_size: 100 }),
  });

  const dashboardData = dashboardQuery.data;
  const maintenanceRecords = asRecords(maintenanceQuery.data);
  const assetRecords = asRecords(assetsQuery.data);

  const [department, setDepartment] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);

  // Filter options
  const departments = useMemo(() => {
    const set = new Set<string>();
    for (const r of maintenanceRecords) {
      const d = readText(r, ["department"]);
      if (d) set.add(d);
    }
    return Array.from(set).sort();
  }, [maintenanceRecords]);

  // Filtered maintenance queue
  const filteredRecords = useMemo(() => {
    return maintenanceRecords.filter((r) => {
      const d = readText(r, ["department"]);
      const s = readText(r, ["status"]);
      const sev = readNumber(r, ["severity"]) ?? 0;

      if (department !== "all" && d !== department) return false;
      if (status !== "all" && s !== status) return false;
      if (severity === "critical" && sev < 80) return false;
      if (severity === "high" && (sev < 70 || sev >= 80)) return false;
      if (severity === "medium" && (sev < 40 || sev >= 70)) return false;
      if (severity === "low" && sev >= 40) return false;

      return true;
    });
  }, [maintenanceRecords, department, severity, status]);

  // Selected request record for detail drawer
  const selectedRecord = useMemo(() => {
    if (!selectedRequestId) return maintenanceRecords[0] ?? null;
    return (
      maintenanceRecords.find(
        (r) => readText(r, ["request_id", "id", "task_id"]) === selectedRequestId,
      ) ?? null
    );
  }, [maintenanceRecords, selectedRequestId]);

  const activeReqId = selectedRecord
    ? (readText(selectedRecord, ["request_id", "id", "task_id"]) ?? "")
    : "";

  // AI Prediction for the selected request
  const aiQuery = useQuery({
    queryKey: ["planrail", "ai", "predict", activeReqId],
    queryFn: () => api.predict({ request_id: activeReqId }),
    enabled: Boolean(activeReqId),
    retry: false,
  });

  const aiData = aiQuery.data?.status === 200 ? aiQuery.data.data : null;

  const kpis = [
    {
      label: "Total Requests",
      value: dashboardData?.total_maintenance_requests ?? maintenanceRecords.length,
      tone: "blue",
      icon: ClipboardList,
    },
    {
      label: "Pending Work",
      value: dashboardData?.pending_requests ?? maintenanceRecords.filter((r) => readText(r, ["status"]) === "PENDING").length,
      tone: "amber",
      icon: Wrench,
    },
    {
      label: "Critical / High",
      value: dashboardData?.critical_high_requests ?? maintenanceRecords.filter((r) => (readNumber(r, ["severity"]) ?? 0) >= 70).length,
      tone: "red",
      icon: ShieldAlert,
    },
    {
      label: "Overdue Tasks",
      value: dashboardData?.overdue_requests ?? maintenanceRecords.filter((r) => (readNumber(r, ["overdue_days"]) ?? 0) > 0).length,
      tone: "red",
      icon: AlertTriangle,
    },
    {
      label: "Feasible Windows",
      value: dashboardData?.available_maintenance_windows ?? 408,
      tone: "green",
      icon: Gauge,
    },
    {
      label: "Asset Fleet",
      value: assetRecords.length || 85,
      tone: "ink",
      icon: Layers,
    },
  ];

  const loading = maintenanceQuery.isPending || dashboardQuery.isPending;
  const error = maintenanceQuery.error || dashboardQuery.error;

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="FIELD WORKLOAD & ASSET HEALTH — DELHI–AGRA"
          title="Maintenance Operations"
          description="Field maintenance workload, asset condition inspections, and block execution readiness."
        />

        {error ? (
          <div className="rounded-md border border-rail-red/20 bg-rail-red/5 p-4 text-xs text-rail-red">
            {apiErrorMessage(error, "Failed to load maintenance telemetry")}
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <section className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
              {kpis.map((kpi) => (
                <div
                  key={kpi.label}
                  className="relative rounded-[10px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 transition-transform duration-200 hover:-translate-y-0.5"
                >
                  <span
                    className={cn(
                      "absolute bottom-3.5 left-0 top-3.5 w-[3px] rounded-full",
                      kpi.tone === "amber" && "bg-rail-amber",
                      kpi.tone === "red" && "bg-rail-red",
                      kpi.tone === "green" && "bg-rail-green",
                      kpi.tone === "ink" && "bg-rail-ink/30",
                      kpi.tone === "blue" && "bg-rail-blue",
                    )}
                  />
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-mono text-[10px] tracking-[0.12em] text-rail-ink/45">
                      {kpi.label}
                    </div>
                    <kpi.icon className="size-4 text-rail-ink/25" />
                  </div>
                  {loading ? (
                    <Skeleton className="mt-2 h-9 w-20 bg-rail-ink/8" />
                  ) : (
                    <div className="mt-2 text-3xl font-extrabold tracking-tight">
                      {kpi.value}
                    </div>
                  )}
                  <div className="mt-2 font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
                    FIELD TELEMETRY
                  </div>
                </div>
              ))}
            </section>

            {/* Main Work Area: Queue + Inspection Drawer */}
            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
              {/* Maintenance Work Queue */}
              <section className="min-w-0 rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 p-4">
                  <div className="flex items-center gap-2">
                    <Wrench className="size-4 text-rail-amber" />
                    <span className="text-sm font-semibold">Active Work Queue</span>
                    <span className="font-mono text-[10px] text-rail-ink/40">
                      ({filteredRecords.length} TASKS)
                    </span>
                  </div>

                  {/* Filters */}
                  <div className="flex flex-wrap items-center gap-2">
                    <Select value={department} onValueChange={setDepartment}>
                      <SelectTrigger className="h-8 w-36 bg-rail-paper text-xs">
                        <SelectValue placeholder="Department" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Departments</SelectItem>
                        {departments.map((d) => (
                          <SelectItem key={d} value={d}>
                            {d}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>

                    <Select value={severity} onValueChange={setSeverity}>
                      <SelectTrigger className="h-8 w-32 bg-rail-paper text-xs">
                        <SelectValue placeholder="Severity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Severity</SelectItem>
                        <SelectItem value="critical">Critical (≥80)</SelectItem>
                        <SelectItem value="high">High (70-79)</SelectItem>
                        <SelectItem value="medium">Medium (40-69)</SelectItem>
                        <SelectItem value="low">Low (&lt;40)</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={status} onValueChange={setStatus}>
                      <SelectTrigger className="h-8 w-28 bg-rail-paper text-xs">
                        <SelectValue placeholder="Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="PENDING">PENDING</SelectItem>
                        <SelectItem value="SCHEDULED">SCHEDULED</SelectItem>
                        <SelectItem value="COMPLETED">COMPLETED</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[700px] text-left text-xs">
                    <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                      <tr>
                        <th className="px-4 py-3 font-medium">TASK ID</th>
                        <th className="px-4 py-3 font-medium">DEPARTMENT</th>
                        <th className="px-4 py-3 font-medium">SECTION / ASSET</th>
                        <th className="px-4 py-3 font-medium">SEVERITY</th>
                        <th className="px-4 py-3 font-medium">DUE DATE</th>
                        <th className="px-4 py-3 font-medium">OVERDUE</th>
                        <th className="px-4 py-3 font-medium">STATUS</th>
                        <th className="px-4 py-3 text-right font-medium">ACTION</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-rail-ink/8">
                      {filteredRecords.map((record) => {
                        const id = readText(record, ["request_id", "id", "task_id"]) ?? "—";
                        const dept = readText(record, ["department"]) ?? "—";
                        const sec = readText(record, ["section_id", "section"]) ?? "—";
                        const asset = readText(record, ["asset_type", "asset_id"]) ?? "Asset";
                        const sev = readNumber(record, ["severity"]) ?? 0;
                        const due = readText(record, ["due_date", "dueDate"]) ?? "—";
                        const overdueDays = readNumber(record, ["overdue_days"]) ?? 0;
                        const stat = readText(record, ["status"]) ?? "PENDING";
                        const isSelected = id === activeReqId;

                        return (
                          <tr
                            key={id}
                            onClick={() => setSelectedRequestId(id)}
                            className={cn(
                              "cursor-pointer transition-colors hover:bg-rail-blue/[0.04]",
                              isSelected && "bg-rail-blue/[0.08]",
                            )}
                          >
                            <td className="px-4 py-3 font-mono text-[11px] font-bold text-rail-blue">
                              {id}
                            </td>
                            <td className="px-4 py-3 font-semibold">{dept}</td>
                            <td className="px-4 py-3">
                              <span className="font-mono text-[11px]">{sec}</span>
                              <span className="ml-1.5 text-rail-ink/50">({asset})</span>
                            </td>
                            <td className="px-4 py-3">
                              <Badge
                                variant="outline"
                                className={cn(
                                  "font-mono text-[10px]",
                                  sev >= 80
                                    ? "border-rail-red/30 bg-rail-red/10 text-rail-red"
                                    : sev >= 70
                                      ? "border-rail-amber/30 bg-rail-amber/10 text-rail-amber"
                                      : "border-rail-blue/30 bg-rail-blue/10 text-rail-blue",
                                )}
                              >
                                {sev.toFixed(0)} / 100
                              </Badge>
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-rail-ink/70">
                              {due}
                            </td>
                            <td className="px-4 py-3">
                              {overdueDays > 0 ? (
                                <span className="font-mono text-[11px] font-semibold text-rail-red">
                                  +{overdueDays} d
                                </span>
                              ) : (
                                <span className="font-mono text-[11px] text-rail-green">
                                  On schedule
                                </span>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <span className="font-mono text-[10px] tracking-wider text-rail-ink/70 uppercase">
                                {stat}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 px-2 text-[11px] font-mono text-rail-blue"
                              >
                                Inspect &rarr;
                              </Button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {filteredRecords.length === 0 && (
                  <EmptyState label="No maintenance tasks match the selected filters." compact />
                )}
              </section>

              {/* Inspection & Readiness Drawer */}
              <aside className="space-y-4 rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
                <div>
                  <div className="flex items-center gap-1.5 font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                    <ClipboardList className="size-3.5 text-rail-blue" />
                    <span>TASK INSPECTION &amp; READINESS</span>
                  </div>
                  <div className="mt-1 text-sm font-bold">
                    {activeReqId ? `Task ${activeReqId}` : "Select a task"}
                  </div>
                </div>

                {selectedRecord ? (
                  <div className="space-y-4">
                    {/* Live AI Decision Support Box */}
                    <div className="rounded-lg border border-rail-blue/30 bg-rail-blue/[0.04] p-3.5 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 font-mono text-[10px] font-bold tracking-[0.1em] text-rail-blue">
                          <BrainCircuit className="size-3.5" /> AI PREDICTIVE RISK &amp; PRIORITY
                        </div>
                        {aiData?.model_status && (
                          <Badge
                            variant="outline"
                            className="border-rail-blue/30 font-mono text-[9px] text-rail-blue"
                          >
                            {aiData.model_status}
                          </Badge>
                        )}
                      </div>

                      {aiQuery.isPending ? (
                        <div className="space-y-2 py-1">
                          <Skeleton className="h-6 bg-rail-ink/8" />
                          <Skeleton className="h-10 bg-rail-ink/8" />
                        </div>
                      ) : aiData ? (
                        <div className="space-y-2.5">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="rounded border border-rail-ink/8 bg-rail-paper p-2">
                              <div className="font-mono text-[9px] text-rail-ink/45">FAILURE RISK</div>
                              <div className="mt-0.5 text-sm font-bold text-rail-amber">
                                {aiData.risk_score.toFixed(1)}{" "}
                                <span className="text-[10px] font-normal text-rail-ink/40">
                                  ({aiData.risk_category})
                                </span>
                              </div>
                            </div>
                            <div className="rounded border border-rail-ink/8 bg-rail-paper p-2">
                              <div className="font-mono text-[9px] text-rail-ink/45">PRIORITY SCORE</div>
                              <div className="mt-0.5 text-sm font-bold text-rail-blue">
                                {aiData.priority_score.toFixed(1)}{" "}
                                <span className="text-[10px] font-normal text-rail-ink/40">
                                  ({aiData.priority_category})
                                </span>
                              </div>
                            </div>
                          </div>

                          {aiData.risk_contributing_factors &&
                            aiData.risk_contributing_factors.length > 0 && (
                              <div className="space-y-1">
                                <div className="font-mono text-[9px] font-semibold text-rail-ink/50">
                                  PRIMARY RISK DRIVERS:
                                </div>
                                {aiData.risk_contributing_factors.slice(0, 2).map((factor, idx) => (
                                  <div
                                    key={idx}
                                    className="flex items-start gap-1.5 text-[11px] text-rail-ink/75"
                                  >
                                    <ShieldAlert className="mt-0.5 size-3 shrink-0 text-rail-amber" />
                                    <span className="leading-tight">{factor}</span>
                                  </div>
                                ))}
                              </div>
                            )}

                          {aiData.explanation && (
                            <p className="border-t border-rail-ink/8 pt-2 text-[11px] leading-relaxed text-rail-ink/70">
                              {aiData.explanation}
                            </p>
                          )}
                        </div>
                      ) : (
                        <div className="text-xs text-rail-ink/50">
                          AI evaluation available in AI Insights view.
                        </div>
                      )}
                    </div>

                    {/* Task Attributes */}
                    <div className="space-y-2 border-t border-rail-ink/8 pt-3 text-xs">
                      <div className="font-mono text-[10px] font-semibold tracking-[0.1em] text-rail-ink/40">
                        TASK SPECIFICATIONS
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="rounded bg-rail-paper p-2">
                          <div className="font-mono text-[9px] text-rail-ink/45">DEPARTMENT</div>
                          <div className="font-semibold text-rail-ink/80">
                            {readText(selectedRecord, ["department"])}
                          </div>
                        </div>
                        <div className="rounded bg-rail-paper p-2">
                          <div className="font-mono text-[9px] text-rail-ink/45">SECTION</div>
                          <div className="font-mono font-semibold text-rail-ink/80">
                            {readText(selectedRecord, ["section_id", "section"])}
                          </div>
                        </div>
                        <div className="rounded bg-rail-paper p-2">
                          <div className="font-mono text-[9px] text-rail-ink/45">WORK DURATION</div>
                          <div className="font-semibold text-rail-ink/80">
                            {readNumber(selectedRecord, ["duration_hours"])} hrs
                          </div>
                        </div>
                        <div className="rounded bg-rail-paper p-2">
                          <div className="font-mono text-[9px] text-rail-ink/45">DUE DATE</div>
                          <div className="font-semibold text-rail-ink/80">
                            {readText(selectedRecord, ["due_date", "dueDate"])}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <EmptyState label="Select a task from the queue to inspect readiness." compact />
                )}
              </aside>
            </div>

            {/* Asset Fleet Health Overview */}
            <section className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
              <div className="flex items-center justify-between border-b border-rail-ink/8 pb-3">
                <div className="flex items-center gap-2">
                  <Layers className="size-4 text-rail-blue" />
                  <span className="text-sm font-semibold">Corridor Asset Condition Overview</span>
                </div>
                <span className="font-mono text-[10px] text-rail-ink/40">
                  {assetRecords.length} REGISTERED ASSETS
                </span>
              </div>

              <div className="mt-3 overflow-x-auto">
                <table className="w-full min-w-[650px] text-left text-xs">
                  <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                    <tr>
                      <th className="px-3 py-2 font-medium">ASSET ID</th>
                      <th className="px-3 py-2 font-medium">TYPE</th>
                      <th className="px-3 py-2 font-medium">SECTION</th>
                      <th className="px-3 py-2 font-medium">INSTALLED</th>
                      <th className="px-3 py-2 font-medium">CONDITION SCORE</th>
                      <th className="px-3 py-2 font-medium">CRITICALITY</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rail-ink/8">
                    {assetRecords.slice(0, 10).map((asset) => {
                      const id = readText(asset, ["asset_id", "id"]) ?? "—";
                      const type = readText(asset, ["asset_type"]) ?? "—";
                      const sec = readText(asset, ["section_id"]) ?? "—";
                      const year = readNumber(asset, ["installation_year"]) ?? 2015;
                      const cond = readNumber(asset, ["condition_score"]) ?? 75;
                      const crit = readText(asset, ["criticality"]) ?? "MEDIUM";

                      return (
                        <tr key={id} className="hover:bg-rail-blue/[0.02]">
                          <td className="px-3 py-2 font-mono font-semibold text-rail-blue">
                            {id}
                          </td>
                          <td className="px-3 py-2">{type}</td>
                          <td className="px-3 py-2 font-mono text-[11px]">{sec}</td>
                          <td className="px-3 py-2 font-mono">{year}</td>
                          <td className="px-3 py-2">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-semibold">{cond.toFixed(0)}</span>
                              <div className="h-1.5 w-16 overflow-hidden rounded-full bg-rail-ink/10">
                                <div
                                  className={cn(
                                    "h-full rounded-full",
                                    cond >= 75 ? "bg-rail-green" : cond >= 50 ? "bg-rail-amber" : "bg-rail-red",
                                  )}
                                  style={{ width: `${cond}%` }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="px-3 py-2">
                            <Badge
                              variant="outline"
                              className={cn(
                                "font-mono text-[9px]",
                                crit === "HIGH"
                                  ? "border-rail-red/30 text-rail-red"
                                  : "border-rail-ink/20 text-rail-ink/60",
                              )}
                            >
                              {crit}
                            </Badge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </div>
    </PlanRailShell>
  );
}
