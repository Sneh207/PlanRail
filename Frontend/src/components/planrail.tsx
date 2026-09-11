import { useQuery } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  Boxes,
  ChevronRight,
  CircleDot,
  ClipboardList,
  Gauge,
  LayoutDashboard,
  LogOut,
  Menu,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldAlert,
  TrainFront,
  Wrench,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState, type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { api, asRecords, readNumber, readText, type JsonRecord } from "@/lib/api";
import { cn } from "@/lib/utils";

export const dashboardQuery = { queryKey: ["planrail", "dashboard"], queryFn: api.dashboard };
export const sectionsQuery = { queryKey: ["planrail", "sections"], queryFn: () => api.sections({ page: 1, page_size: 100 }) };
export const stationsQuery = { queryKey: ["planrail", "stations"], queryFn: () => api.stations({ page: 1, page_size: 100 }) };
export const maintenanceFeedQuery = { queryKey: ["planrail", "maintenance", "all"], queryFn: () => api.maintenance({ page: 1, page_size: 150 }) };

type NavItem = { label: string; to: string; icon: typeof LayoutDashboard };

const navItems: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard },
  { label: "Railway Network", to: "/network", icon: Network },
  { label: "Maintenance", to: "/maintenance", icon: Wrench },
  { label: "Trains", to: "/trains", icon: TrainFront },
  { label: "Block Planning", to: "/blocks", icon: Boxes },
  { label: "AI Insights", to: "/insights", icon: BrainCircuit },
];

export function DemoLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("demo.operator");
  const [password, setPassword] = useState("");

  function enterDashboard(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sessionStorage.setItem("planrail-demo-session", "active");
    navigate({ to: "/dashboard" });
  }

  return (
    <main className="min-h-screen bg-rail-paper text-rail-ink">
      <section className="grid min-h-screen lg:grid-cols-[minmax(0,42%)_1fr]">
        <div className="relative flex min-h-[520px] flex-col justify-between overflow-hidden bg-rail-ink px-7 py-8 text-rail-paper sm:px-10 sm:py-10">
          <div className="flex items-center gap-3">
            <span className="size-2.5 rounded-full bg-rail-blue" />
            <span className="font-mono text-[11px] tracking-[0.22em] text-rail-paper/70">
              PLANRAIL // CONTROL
            </span>
          </div>
          <div className="relative mt-20 lg:mt-0">
            <div className="mb-4 font-mono text-[11px] tracking-[0.2em] text-rail-blue">
              SIGNAL BOX · FIRST LIGHT
            </div>
            <h1 className="max-w-xl text-5xl font-extrabold leading-[0.95] tracking-tight sm:text-6xl">
              Delhi —
              <br />
              Agra
              <br />
              Corridor
            </h1>
            <p className="mt-6 max-w-[34ch] text-sm leading-relaxed text-rail-paper/60">
              Corridor operations surface for the Delhi–Agra main line. Blocks, maintenance, and
              risk — read at a glance.
            </p>
          </div>
          <div className="mt-20 flex max-w-sm justify-between font-mono text-[10px] tracking-[0.18em] text-rail-paper/40">
            <span>DELHI</span>
            <span>AGRA</span>
            <span>PROTOTYPE</span>
          </div>
          <div className="absolute bottom-24 left-10 h-40 w-px bg-rail-blue/40" />
          <div className="rail-pulse absolute left-[10.42rem] top-1/2 size-2 rounded-full bg-rail-blue" />
        </div>

        <div className="flex items-center bg-rail-paper px-6 py-12 sm:px-12">
          <form className="mx-auto w-full max-w-sm" onSubmit={enterDashboard}>
            <div className="mb-2 font-mono text-[11px] tracking-[0.2em] text-rail-ink/45">
              AUTH · OPERATOR
            </div>
            <h2 className="text-2xl font-bold tracking-tight">Operator sign-in</h2>
            <p className="mt-2 text-sm text-rail-ink/55">
              Enter the PlanRail decision-support workspace.
            </p>
            <div className="mt-8 space-y-4">
              <label className="block">
                <span className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                  USERNAME
                </span>
                <Input
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  className="mt-1.5 h-11 border-rail-ink/10 bg-rail-panel text-rail-ink focus-visible:ring-rail-blue/40"
                  placeholder="username"
                />
              </label>
              <label className="block">
                <span className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                  PASSWORD
                </span>
                <Input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="mt-1.5 h-11 border-rail-ink/10 bg-rail-panel text-rail-ink focus-visible:ring-rail-blue/40"
                  placeholder="••••••••"
                />
              </label>
            </div>
            <Button
              type="submit"
              className="mt-7 h-12 w-full rounded-lg bg-rail-blue text-rail-paper hover:bg-rail-blue/90"
            >
              Enter Dashboard
              <span className="size-1.5 rounded-full bg-rail-paper/80" />
            </Button>
            <p className="mt-4 font-mono text-[10px] tracking-[0.12em] text-rail-ink/35">
              LOCAL PROTOTYPE · READ-ONLY DECISION SUPPORT
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}

export function PlanRailShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [railOpen, setRailOpen] = useState(false);
  const [railCollapsed, setRailCollapsed] = useState(false);

  const healthQuery = useQuery({
    queryKey: ["planrail", "health"],
    queryFn: api.health,
    refetchInterval: 10000,
    retry: 1,
  });
  const isOnline = healthQuery.isSuccess;

  function signOut() {
    sessionStorage.removeItem("planrail-demo-session");
    navigate({ to: "/" });
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-rail-paper text-rail-ink">
      <div className="flex min-h-screen">
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-rail-ink text-rail-paper transition-transform duration-200 lg:sticky lg:translate-x-0",
            railOpen ? "translate-x-0" : "-translate-x-full",
            railCollapsed && "lg:w-[76px]",
          )}
        >
          <div
            className={cn(
              "flex items-center border-b border-rail-paper/10 px-5 py-5",
              railCollapsed ? "justify-center" : "gap-2.5",
            )}
          >
            <span className="size-2.5 shrink-0 rounded-full bg-rail-blue" />
            {!railCollapsed && <span className="text-sm font-bold tracking-tight">PlanRail</span>}
            <button
              aria-label="Close navigation"
              className="ml-auto lg:hidden"
              onClick={() => setRailOpen(false)}
            >
              <X className="size-4" />
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navItems.map(({ label, to, icon: Icon }) => {
              const active = location.pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  onClick={() => setRailOpen(false)}
                  title={railCollapsed ? label : undefined}
                  className={cn(
                    "relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors",
                    railCollapsed && "justify-center px-2",
                    active
                      ? "bg-rail-paper font-semibold text-rail-ink"
                      : "text-rail-paper/55 hover:bg-rail-paper/10 hover:text-rail-paper",
                  )}
                >
                  {active && (
                    <span className="absolute bottom-1.5 left-0 top-1.5 w-[3px] rounded-full bg-rail-blue" />
                  )}
                  <Icon className="size-4 shrink-0" />
                  {!railCollapsed && <span>{label}</span>}
                </Link>
              );
            })}
          </nav>
          <div className={cn("border-t border-rail-paper/10 p-4", railCollapsed && "px-3")}>
            {!railCollapsed && (
              <div className="rounded-md border border-rail-paper/10 p-3">
                <div className="font-mono text-[10px] tracking-[0.15em] text-rail-paper/45">
                  CORRIDOR
                </div>
                <div className="mt-1 text-sm font-semibold">Delhi–Agra Main Line</div>
                <div className="mt-3 flex items-center gap-2 font-mono text-[10px] tracking-[0.12em] text-rail-paper/60">
                  {isOnline ? (
                    <>
                      <span className="rail-pulse size-1.5 rounded-full bg-rail-green" /> BACKEND CONNECTED
                    </>
                  ) : (
                    <>
                      <span className="size-1.5 rounded-full bg-rail-red" /> BACKEND OFFLINE
                    </>
                  )}
                </div>
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={signOut}
              title="Exit session"
              className="mt-3 w-full text-rail-paper/55 hover:bg-rail-paper/10 hover:text-rail-paper"
            >
              <LogOut />
              {!railCollapsed && <span className="text-xs">Exit session</span>}
            </Button>
          </div>
        </aside>

        {railOpen && (
          <button
            aria-label="Close navigation overlay"
            className="fixed inset-0 z-30 bg-rail-ink/40 lg:hidden"
            onClick={() => setRailOpen(false)}
          />
        )}
        <div className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 flex min-h-16 items-center justify-between border-b border-rail-ink/10 bg-rail-panel/95 px-4 backdrop-blur sm:px-6">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                aria-label="Open navigation"
                onClick={() => setRailOpen(true)}
              >
                <Menu />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hidden lg:inline-flex"
                aria-label={railCollapsed ? "Expand navigation" : "Collapse navigation"}
                onClick={() => setRailCollapsed((value) => !value)}
              >
                {railCollapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
              </Button>
              <div className="hidden items-center gap-3 sm:flex">
                <span className="font-mono text-[10px] tracking-[0.18em] text-rail-ink/45">
                  OPERATIONS
                </span>
                <span className="text-rail-ink/20">/</span>
                <span className="hidden font-mono text-[10px] tracking-[0.1em] text-rail-ink/45 xl:inline">
                  DELHI–AGRA CORRIDOR
                </span>
              </div>
              <span className="text-sm font-semibold">
                {navItems.find((item) => item.to === location.pathname)?.label ?? "Operations"}
              </span>
            </div>
            <div className="flex items-center gap-3 sm:gap-4">
              <span className="hidden items-center gap-2 font-mono text-[10px] tracking-[0.1em] text-rail-ink/55 md:flex">
                {isOnline ? (
                  <>
                    <span className="rail-pulse size-1.5 rounded-full bg-rail-green" /> LOCAL BACKEND CONNECTED
                  </>
                ) : (
                  <>
                    <span className="size-1.5 rounded-full bg-rail-red" /> BACKEND OFFLINE
                  </>
                )}
              </span>
              <div className="flex items-center gap-2 border-l border-rail-ink/10 pl-3 sm:gap-2.5 sm:pl-4">
                <div className="grid size-8 place-items-center rounded-full bg-rail-blue/15 text-xs font-bold text-rail-blue">
                  OP
                </div>
                <div className="hidden leading-tight sm:block">
                  <div className="text-xs font-semibold">Controller</div>
                  <div className="font-mono text-[9px] tracking-[0.1em] text-rail-ink/40">
                    SHIFT A
                  </div>
                </div>
              </div>
            </div>
          </header>
          <main className="mx-auto max-w-[1480px] p-4 sm:p-6">{children}</main>
          <footer className="mx-auto flex max-w-[1480px] flex-col gap-1 border-t border-rail-ink/8 px-4 py-5 font-mono text-[9px] leading-relaxed tracking-[0.08em] text-rail-ink/40 sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <span>PLANRAIL DECISION-SUPPORT SYSTEM — DELHI–AGRA CORRIDOR PROTOTYPE.</span>
            <span className="shrink-0 text-rail-ink/30">OR-TOOLS CP-SAT + AI PREDICTIVE INTELLIGENCE</span>
          </footer>
        </div>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const dashboard = useQuery(dashboardQuery);
  const sections = useQuery(sectionsQuery);
  const stations = useQuery(stationsQuery);
  const maintenanceFeed = useQuery(maintenanceFeedQuery);

  const data = dashboard.data;
  const sectionRecords = asRecords(sections.data);
  const stationRecords = asRecords(stations.data);
  const maintenanceRecords = asRecords(maintenanceFeed.data);

  // Derive department breakdown from real maintenance records
  const departmentStats = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const r of maintenanceRecords) {
      const dept = readText(r, ["department"]) ?? "Other";
      counts[dept] = (counts[dept] ?? 0) + 1;
    }
    return Object.entries(counts).map(([department, count]) => ({
      department,
      count,
    }));
  }, [maintenanceRecords]);

  // Derive risk distribution from real maintenance records
  const riskStats = useMemo(() => {
    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;
    for (const r of maintenanceRecords) {
      const sev = readNumber(r, ["severity"]) ?? 0;
      if (sev >= 80) critical++;
      else if (sev >= 70) high++;
      else if (sev >= 40) medium++;
      else low++;
    }
    const total = maintenanceRecords.length || 1;
    return [
      { label: "Critical Severity (≥80)", percentage: Math.round((critical / total) * 100), count: critical },
      { label: "High Severity (≥70)", percentage: Math.round((high / total) * 100), count: high },
      { label: "Medium Severity (≥40)", percentage: Math.round((medium / total) * 100), count: medium },
      { label: "Low Severity (<40)", percentage: Math.round((low / total) * 100), count: low },
    ];
  }, [maintenanceRecords]);

  // Dynamic recommendation derived from actual backlog
  const recommendationText = useMemo(() => {
    if (!data) return null;
    if (data.overdue_requests > 0) {
      return `Attention: ${data.overdue_requests} maintenance requests are overdue on the Delhi–Agra corridor. ${data.critical_high_requests} tasks require high-priority blocks. There are ${data.available_maintenance_windows} feasible maintenance windows available. Run CP-SAT Optimization to generate multi-department bundled block allocations.`;
    }
    return `All corridor maintenance requests are within schedule limits. ${data.available_maintenance_windows} maintenance windows available across ${data.total_trains} scheduled train paths.`;
  }, [data]);

  const kpis = [
    {
      label: "Total Requests",
      value: data ? data.total_maintenance_requests : null,
      tone: "blue",
      icon: ClipboardList,
    },
    {
      label: "Pending Maintenance",
      value: data ? data.pending_requests : null,
      tone: "amber",
      icon: Wrench,
    },
    {
      label: "Critical / High",
      value: data ? data.critical_high_requests : null,
      tone: "red",
      icon: ShieldAlert,
    },
    {
      label: "Overdue Tasks",
      value: data ? data.overdue_requests : null,
      tone: "red",
      icon: AlertTriangle,
    },
    {
      label: "Feasible Windows",
      value: data ? data.available_maintenance_windows : null,
      tone: "green",
      icon: Gauge,
    },
    {
      label: "Corridor Trains",
      value: data ? data.total_trains : null,
      tone: "ink",
      icon: TrainFront,
    },
  ] as const;

  return (
    <div className="space-y-5">
      <PageIntro
        eyebrow="CORRIDOR TELEMETRY — DELHI–AGRA"
        title="Operations overview"
        description="Corridor maintenance status, asset posture, and maintenance window availability."
      />
      {dashboard.isError ? (
        <ErrorState
          message={apiErrorMessage(dashboard.error, "The dashboard metrics could not be loaded")}
          onRetry={() => void dashboard.refetch()}
        />
      ) : (
        <>
          <section className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
            {kpis.map((kpi) => (
              <KpiCard
                key={kpi.label}
                label={kpi.label}
                value={kpi.value}
                tone={kpi.tone}
                icon={kpi.icon}
                loading={dashboard.isPending}
              />
            ))}
          </section>
          <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <NetworkPreview
              sections={sectionRecords}
              stations={stationRecords}
              loading={sections.isPending || stations.isPending}
            />
            <Recommendation text={recommendationText} />
          </section>
          <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <MaintenanceChart departmentStats={departmentStats} loading={maintenanceFeed.isPending} />
            <RiskChart riskStats={riskStats} loading={maintenanceFeed.isPending} />
          </section>
        </>
      )}
    </div>
  );
}

function KpiCard({
  label,
  value,
  loading,
  tone,
  suffix,
  icon: Icon,
}: {
  label: string;
  value: number | null;
  loading: boolean;
  tone: string;
  suffix?: string;
  icon: typeof Activity;
}) {
  return (
    <div className="relative rounded-[10px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 transition-transform duration-200 hover:-translate-y-0.5">
      <span
        className={cn(
          "absolute bottom-3.5 left-0 top-3.5 w-[3px] rounded-full",
          tone === "amber" && "bg-rail-amber",
          tone === "red" && "bg-rail-red",
          tone === "green" && "bg-rail-green",
          tone === "ink" && "bg-rail-ink/30",
          tone === "blue" && "bg-rail-blue",
        )}
      />
      <div className="flex items-start justify-between gap-2">
        <div className="font-mono text-[10px] tracking-[0.12em] text-rail-ink/45">{label}</div>
        <Icon className="size-4 text-rail-ink/25" />
      </div>
      {loading ? (
        <Skeleton className="mt-2 h-9 w-20 bg-rail-ink/8" />
      ) : (
        <div className="mt-2 text-3xl font-extrabold tracking-tight">
          {value === null ? (
            "—"
          ) : (
            <>
              {value}
              {suffix && <span className="text-lg text-rail-ink/50">{suffix}</span>}
            </>
          )}
        </div>
      )}
      <div className="mt-2 font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
        {value === null && !loading ? "NO DATA" : "BACKEND DATA"}
      </div>
    </div>
  );
}

function NetworkPreview({
  sections,
  stations,
  loading,
}: {
  sections: JsonRecord[];
  stations: JsonRecord[];
  loading: boolean;
}) {
  const points = stations.map((station, index) => ({
    label:
      readText(station, ["station_code", "code", "station_name", "name"]) ?? `Station ${index + 1}`,
    position: `${Math.max(6, Math.min(94, 6 + (index * 88) / Math.max(stations.length - 1, 1)))}%`,
  }));
  return (
    <div className="rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 lg:col-span-2">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
            RAILWAY NETWORK
          </div>
          <div className="mt-0.5 text-sm font-semibold">Corridor map topology</div>
        </div>
        <span className="hidden font-mono text-[10px] tracking-[0.1em] text-rail-ink/35 sm:block">
          GET /api/v1/sections
        </span>
      </div>
      {loading ? (
        <Skeleton className="mt-3 aspect-[16/7] w-full bg-rail-ink/8" />
      ) : sections.length === 0 && stations.length === 0 ? (
        <EmptyState label="No sections or stations were returned by the backend network feeds." />
      ) : (
        <div className="rail-map mt-3 aspect-[16/7] overflow-hidden rounded-lg border border-rail-ink/8 bg-rail-map p-5">
          <div className="flex h-full flex-col justify-between">
            <div className="flex items-center justify-between font-mono text-[10px] tracking-[0.14em] text-rail-ink/40">
              <span>NEW DELHI (NDLS)</span>
              <span>{sections.length ? `${sections.length} SECTIONS` : "SECTIONS"}</span>
              <span>AGRA CANTT (AGC)</span>
            </div>
            <div className="relative px-2">
              <div className="h-1 rounded-full bg-rail-blue/15">
                <div className="h-full w-full rounded-full bg-rail-blue" />
              </div>
              <div className="absolute inset-x-0 top-1/2 flex -translate-y-1/2 justify-between">
                {(points.length ? points : [{ label: "Corridor feed", position: "50%" }]).map(
                  (point) => (
                    <div key={`${point.label}-${point.position}`} className="group relative">
                      <span className="rail-pulse block size-3 rounded-full border-2 border-rail-map bg-rail-blue shadow-[0_0_0_3px_color-mix(in_oklab,var(--color-rail-blue)_18%,transparent)]" />
                      <span className="absolute left-1/2 top-5 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] text-rail-ink/55">
                        {point.label}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </div>
            <div className="flex items-center justify-between font-mono text-[10px] text-rail-ink/35">
              <span>{stations.length ? `${stations.length} STATIONS` : "STATIONS"}</span>
              <span>195 KM PROTOTYPE CORRIDOR</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Recommendation({ text }: { text: string | null }) {
  return (
    <div className="flex flex-col rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-blue/25">
      <div className="flex items-center gap-2">
        <span className="rail-pulse size-1.5 rounded-full bg-rail-blue" />
        <span className="font-mono text-[11px] tracking-[0.15em] text-rail-ink/50">
          AI RECOMMENDATION
        </span>
      </div>
      {text ? (
        <p className="mt-4 text-sm leading-relaxed text-rail-ink/80">{text}</p>
      ) : (
        <EmptyState label="Corridor recommendation will appear when telemetry responds." compact />
      )}
    </div>
  );
}

function MaintenanceChart({
  departmentStats,
  loading,
}: {
  departmentStats: Array<{ department: string; count: number }>;
  loading: boolean;
}) {
  return (
    <ChartPanel title="Maintenance by Department" meta="PENDING TASKS">
      {loading ? (
        <ChartSkeleton />
      ) : departmentStats.length ? (
        <div className="space-y-4">
          {departmentStats.map((item) => (
            <ProgressRow
              key={item.department}
              label={item.department}
              value={item.count}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          label="No department maintenance requests returned."
          compact
        />
      )}
    </ChartPanel>
  );
}

function RiskChart({
  riskStats,
  loading,
}: {
  riskStats: Array<{ label: string; percentage: number; count: number }>;
  loading: boolean;
}) {
  return (
    <ChartPanel title="Severity & Urgency Distribution" meta="ACTIVE BACKLOG">
      {loading ? (
        <ChartSkeleton />
      ) : riskStats.length ? (
        <div className="space-y-4">
          {riskStats.map((item, index) => (
            <ProgressRow
              key={item.label}
              label={`${item.label} (${item.count})`}
              value={item.percentage}
              danger={index === 0}
            />
          ))}
        </div>
      ) : (
        <EmptyState label="No risk distribution records available." compact />
      )}
    </ChartPanel>
  );
}

function ChartPanel({
  title,
  meta,
  children,
}: {
  title: string;
  meta: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
      <div className="mb-5 flex items-center justify-between">
        <div className="font-semibold">{title}</div>
        <span className="font-mono text-[10px] text-rail-ink/35">{meta}</span>
      </div>
      {children}
    </div>
  );
}

function ProgressRow({
  label,
  value,
  danger = false,
}: {
  label: string;
  value: number | null;
  danger?: boolean;
}) {
  return (
    <div>
      <div className="flex justify-between font-mono text-[10px] text-rail-ink/50">
        <span>{label}</span>
        <span>{value === null ? "—" : `${value}%`}</span>
      </div>
      <div className="mt-1.5 h-2 rounded-full bg-rail-ink/8">
        <div
          className={cn("h-full rounded-full", danger ? "bg-rail-red" : "bg-rail-blue")}
          style={{ width: `${Math.max(0, Math.min(value ?? 0, 100))}%` }}
        />
      </div>
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4].map((item) => (
        <Skeleton key={item} className="h-7 bg-rail-ink/8" />
      ))}
    </div>
  );
}

export function EmptyState({ label, compact = false }: { label: string; compact?: boolean }) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border border-dashed border-rail-ink/15 text-sm text-rail-ink/50",
        compact ? "mt-4 p-4" : "mt-3 min-h-40 justify-center p-6 text-center",
      )}
    >
      {compact ? (
        <CircleDot className="size-4 shrink-0 text-rail-ink/30" />
      ) : (
        <AlertTriangle className="size-4 shrink-0 text-rail-amber" />
      )}
      <span>{label}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-[14px] border border-dashed border-rail-red/30 bg-rail-panel p-6 text-center">
      <CircleDot className="size-5 text-rail-red" />
      <p className="text-sm text-rail-ink/60">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <Activity className="size-3.5" />
          Retry feed
        </Button>
      )}
    </div>
  );
}

export function PageIntro({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  const healthQuery = useQuery({
    queryKey: ["planrail", "health"],
    queryFn: api.health,
    refetchInterval: 10000,
    retry: 1,
  });
  const isOnline = healthQuery.isSuccess;

  return (
    <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
      <div>
        <div className="font-mono text-[10px] tracking-[0.2em] text-rail-ink/40">{eyebrow}</div>
        <h1 className="mt-1 text-2xl font-bold tracking-tight">{title}</h1>
        <p className="mt-1 text-sm text-rail-ink/55">{description}</p>
      </div>
      <div className="flex items-center gap-2 font-mono text-[10px] tracking-[0.12em] text-rail-ink/40">
        {isOnline ? (
          <>
            <span className="rail-pulse size-1.5 rounded-full bg-rail-green" /> BACKEND CONNECTED
          </>
        ) : (
          <>
            <span className="size-1.5 rounded-full bg-rail-red" /> BACKEND OFFLINE
          </>
        )}
      </div>
    </div>
  );
}


export function OperationsPage({
  title,
  description,
  icon: Icon,
  endpoint,
  note,
}: {
  title: string;
  description: string;
  icon: typeof Network;
  endpoint: string;
  note: string;
}) {
  return (
    <div className="space-y-5">
      <PageIntro eyebrow="OPERATIONS MODULE" title={title} description={description} />
      <div className="grid min-h-[420px] place-items-center rounded-[14px] border border-dashed border-rail-ink/15 bg-rail-panel/60 p-8 text-center shadow-rail">
        <div className="max-w-md">
          <div className="mx-auto grid size-14 place-items-center rounded-xl bg-rail-blue/10 text-rail-blue">
            <Icon className="size-6" />
          </div>
          <h2 className="mt-5 text-lg font-semibold">{title} feed ready</h2>
          <p className="mt-2 text-sm leading-relaxed text-rail-ink/55">{note}</p>
          <div className="mt-5 inline-flex items-center gap-2 rounded-md bg-rail-ink/5 px-3 py-2 font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
            <Activity className="size-3" /> {endpoint}
          </div>
          <div className="mt-5 flex items-center justify-center gap-2 text-xs text-rail-ink/45">
            <ChevronRight className="size-4" /> Phase 1 foundation surface
          </div>
        </div>
      </div>
    </div>
  );
}

function isRecordLike(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function readRecords(record: JsonRecord | null | undefined, keys: string[]): JsonRecord[] {
  for (const key of keys) {
    const value = record?.[key];
    if (Array.isArray(value)) return value.filter(isRecordLike);
  }
  return [];
}
