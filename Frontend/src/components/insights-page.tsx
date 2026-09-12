import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  BrainCircuit,
  CircleDot,
  RefreshCw,
  Sparkles,
  ShieldAlert,
  Train,
  CheckCircle2,
  TrendingUp,
  Activity,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  api,
  apiErrorMessage,
  asRecords,
  isRecord,
  readText,
  type JsonRecord,
} from "@/lib/api";
import type { AIHighAttentionTask, AIInsightsResponse, AIPredictResponse } from "@/lib/types";
import { cn } from "@/lib/utils";
import { EmptyState, PageIntro, PlanRailShell } from "@/components/planrail";

// Semantic color tokens for Recharts
const CHART_BLUE = "oklch(0.52 0.19 260)";
const CHART_GREEN = "oklch(0.59 0.14 157)";
const CHART_AMBER = "oklch(0.66 0.14 67)";
const CHART_RED = "oklch(0.58 0.17 35)";
const CHART_PURPLE = "oklch(0.55 0.18 300)";
const CHART_INK_SOFT = "oklch(0.18 0.015 270 / 0.45)";

type Slice = { name: string; value: number };

function categoryColor(category: string): string {
  const tone = category.toUpperCase();
  if (tone === "CRITICAL") return CHART_RED;
  if (tone === "HIGH") return CHART_AMBER;
  if (tone === "MEDIUM") return CHART_BLUE;
  if (tone === "LOW") return CHART_GREEN;
  return CHART_BLUE;
}

export function AIInsightsPage() {
  const insightsQuery = useQuery({
    queryKey: ["planrail", "ai", "insights"],
    queryFn: api.aiInsights,
  });

  const maintenanceQuery = useQuery({
    queryKey: ["planrail", "maintenance", "all_for_picker"],
    queryFn: () => api.maintenance({ page_size: 150 }),
  });

  const insightsData: AIInsightsResponse | null = insightsQuery.data ?? null;
  const maintenanceRecords = asRecords(maintenanceQuery.data);

  // Transform distributions into Slice arrays for Recharts
  const riskSlices: Slice[] = useMemo(() => {
    if (!insightsData?.risk_distribution) return [];
    return Object.entries(insightsData.risk_distribution)
      .map(([name, value]) => ({ name, value }))
      .filter((s) => s.value > 0);
  }, [insightsData]);

  const prioritySlices: Slice[] = useMemo(() => {
    if (!insightsData?.priority_distribution) return [];
    return Object.entries(insightsData.priority_distribution)
      .map(([name, value]) => ({ name, value }))
      .filter((s) => s.value > 0);
  }, [insightsData]);

  const departmentSlices: Slice[] = useMemo(() => {
    if (!insightsData?.department_distribution) return [];
    return Object.entries(insightsData.department_distribution)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [insightsData]);

  const attentionTasks: AIHighAttentionTask[] = insightsData?.high_attention_tasks ?? [];

  const [selectedRequestId, setSelectedRequestId] = useState<string>("");
  const defaultRequestId =
    attentionTasks[0]?.request_id ||
    (maintenanceRecords[0]?.request_id as string) ||
    "MR0001";
  const effectiveRequestId = selectedRequestId || defaultRequestId;

  const predictQuery = useQuery({
    queryKey: ["planrail", "ai", "predict", effectiveRequestId],
    queryFn: () => api.predict({ request_id: effectiveRequestId }),
    enabled: Boolean(effectiveRequestId),
    retry: false,
  });

  const prediction: AIPredictResponse | null =
    predictQuery.data?.status === 200 ? predictQuery.data.data : null;

  const loading = insightsQuery.isPending;
  const feedError = insightsQuery.error;

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="DECISION SUPPORT & PREDICTIVE INTELLIGENCE — DELHI–AGRA"
          title="AI Insights"
          description="Traffic-aware failure risk scoring, multi-criteria priority harmonization, and auditable controller briefings."
        />

        {feedError ? (
          <InsightsError
            message={apiErrorMessage(feedError, "The AI insights analytics could not be loaded")}
            onRetry={() => void insightsQuery.refetch()}
          />
        ) : loading ? (
          <InsightsSkeleton />
        ) : (
          <>
            {/* Top Corridor Recommendation Banner */}
            {insightsData?.corridor_ai_recommendation && (
              <div className="rounded-[14px] border border-rail-blue/30 bg-gradient-to-r from-rail-blue/10 via-rail-panel to-rail-paper p-5 shadow-rail">
                <div className="flex items-start gap-3.5">
                  <div className="mt-0.5 rounded-full bg-rail-blue/15 p-2 text-rail-blue">
                    <Sparkles className="size-5" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 font-mono text-[11px] font-bold tracking-[0.15em] text-rail-blue">
                      <span>CORRIDOR DECISION-SUPPORT RECOMMENDATION</span>
                      <Badge variant="outline" className="border-rail-blue/30 font-mono text-[10px] text-rail-blue">
                        {insightsData.model_status}
                      </Badge>
                    </div>
                    <p className="text-sm font-medium leading-relaxed text-rail-ink/90">
                      {insightsData.corridor_ai_recommendation}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Request Analyzer Card */}
            <RequestAnalysisCard
              prediction={prediction}
              predictionPending={predictQuery.isPending}
              predictionError={predictQuery.error}
              maintenanceList={maintenanceRecords}
              selectedId={effectiveRequestId}
              onSelectId={setSelectedRequestId}
              totalAnalyzed={insightsData?.total_requests_analyzed ?? 0}
            />

            {/* Distribution Charts */}
            <div className="grid gap-4 lg:grid-cols-3">
              <DistributionPanel
                title="Asset Failure Risk"
                meta="PROBABILISTIC MODEL"
                slices={riskSlices}
              />
              <DistributionPanel
                title="Maintenance Priority"
                meta="MULTI-CRITERIA (30/25/20/15/10)"
                slices={prioritySlices}
              />
              <DepartmentPanel slices={departmentSlices} />
            </div>

            {/* High Priority & High Risk Tasks Queue */}
            <HighAttentionTasks
              tasks={attentionTasks}
              total={insightsData?.total_requests_analyzed ?? 0}
              onSelectTask={(id) => setSelectedRequestId(id)}
              activeTaskId={effectiveRequestId}
            />
          </>
        )}
      </div>
    </PlanRailShell>
  );
}

function RequestAnalysisCard({
  prediction,
  predictionPending,
  predictionError,
  maintenanceList,
  selectedId,
  onSelectId,
  totalAnalyzed,
}: {
  prediction: AIPredictResponse | null;
  predictionPending: boolean;
  predictionError: unknown;
  maintenanceList: JsonRecord[];
  selectedId: string;
  onSelectId: (id: string) => void;
  totalAnalyzed: number;
}) {
  const components = prediction?.priority_components;
  const factors = prediction?.risk_contributing_factors ?? [];

  return (
    <section className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-blue/25">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 pb-4">
        <div className="flex items-center gap-2">
          <BrainCircuit className="size-4 text-rail-blue" />
          <span className="font-mono text-[11px] font-bold tracking-[0.15em] text-rail-ink/75">
            REQUEST AI EVALUATION & EXPLAINABILITY
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[10px] tracking-[0.08em] text-rail-ink/50">ANALYZE TASK:</span>
          {maintenanceList.length > 0 ? (
            <Select value={selectedId} onValueChange={onSelectId}>
              <SelectTrigger className="h-8 w-48 bg-rail-paper font-mono text-xs">
                <SelectValue placeholder="Select request" />
              </SelectTrigger>
              <SelectContent className="max-h-60">
                {maintenanceList.map((m, i) => {
                  const id = (readText(m, ["request_id", "id", "task_id"]) ?? `REQ-${i}`) as string;
                  const dept = readText(m, ["department"]) ?? "";
                  return (
                    <SelectItem key={id} value={id} className="font-mono text-xs">
                      {id} ({dept})
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
          ) : (
            <span className="font-mono text-[10px] text-rail-ink/40">NO REQUESTS</span>
          )}
        </div>
      </div>

      {predictionPending ? (
        <div className="mt-4 space-y-3">
          <Skeleton className="h-16 bg-rail-ink/8" />
          <Skeleton className="h-24 bg-rail-ink/8" />
        </div>
      ) : predictionError ? (
        <div className="mt-4 rounded-md border border-rail-red/20 bg-rail-red/5 p-3 text-xs text-rail-red">
          {apiErrorMessage(predictionError, "Could not fetch AI prediction for selected request")}
        </div>
      ) : prediction ? (
        <div className="mt-4 space-y-4">
          {/* Key Metrics Grid */}
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] tracking-[0.14em] text-rail-ink/45">PREDICTED FAILURE RISK</span>
                <Badge
                  variant="outline"
                  className="font-mono text-[9px]"
                  style={{ color: categoryColor(prediction.risk_category), borderColor: categoryColor(prediction.risk_category) }}
                >
                  {prediction.risk_category}
                </Badge>
              </div>
              <div className="mt-1 text-xl font-bold" style={{ color: categoryColor(prediction.risk_category) }}>
                {prediction.risk_score.toFixed(1)} <span className="text-xs font-normal text-rail-ink/40">/ 100</span>
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-rail-ink/45">
                P(failure) = {(prediction.risk_probability ?? (prediction.risk_score / 100)).toFixed(4)}
              </div>
            </div>

            <div className="rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] tracking-[0.14em] text-rail-ink/45">OPERATIONAL TRAFFIC IMPACT</span>
                <Badge
                  variant="outline"
                  className="font-mono text-[9px]"
                  style={{ color: categoryColor(prediction.traffic_impact_category || "LOW") }}
                >
                  {prediction.traffic_impact_category || "LOW"}
                </Badge>
              </div>
              <div className="mt-1 text-xl font-bold text-rail-ink/85">
                {(prediction.traffic_impact_score ?? 0).toFixed(1)} <span className="text-xs font-normal text-rail-ink/40">/ 100</span>
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-rail-ink/45">
                Combined passenger + freight pressure
              </div>
            </div>

            <div className="rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[9px] tracking-[0.14em] text-rail-ink/45">MULTI-CRITERIA PRIORITY</span>
                <Badge
                  variant="outline"
                  className="font-mono text-[9px]"
                  style={{ color: categoryColor(prediction.priority_category || "MEDIUM") }}
                >
                  {prediction.priority_category || "MEDIUM"}
                </Badge>
              </div>
              <div className="mt-1 text-xl font-bold text-rail-blue">
                {prediction.priority_score.toFixed(1)} <span className="text-xs font-normal text-rail-ink/40">/ 100</span>
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-rail-ink/45">
                Harmonized scheduling score
              </div>
            </div>

            <div className="rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3">
              <div className="font-mono text-[9px] tracking-[0.14em] text-rail-ink/45">MODEL PROVENANCE</div>
              <div className="mt-1 truncate text-xs font-bold text-rail-ink/80">
                {prediction.model_status || "DOMAIN_CALIBRATED_MODEL"}
              </div>
              <div className="mt-0.5 font-mono text-[10px] text-rail-ink/45">
                Threshold: 0.5421 (Recall-Tuned)
              </div>
            </div>
          </div>

          {/* Priority Component Breakdown */}
          {components && (
            <div className="rounded-md border border-rail-ink/8 bg-rail-paper p-3.5">
              <div className="font-mono text-[10px] font-bold tracking-[0.1em] text-rail-ink/60">
                MULTI-CRITERIA HARMONIZATION BREAKDOWN (30% / 25% / 20% / 15% / 10%)
              </div>
              <div className="mt-2.5 grid grid-cols-2 gap-3 sm:grid-cols-5">
                <ComponentBar label="Severity (30%)" value={components.severity} />
                <ComponentBar label="Criticality (25%)" value={components.criticality} />
                <ComponentBar label="Overdue (20%)" value={components.overdue} />
                <ComponentBar label="Risk (15%)" value={components.risk} />
                <ComponentBar label="Traffic (10%)" value={components.traffic_impact} />
              </div>
            </div>
          )}

          {/* Local SHAP Feature Contributions */}
          {prediction.feature_contributions && prediction.feature_contributions.length > 0 && (
            <div className="rounded-md border border-rail-ink/8 bg-rail-paper p-3.5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="font-mono text-[10px] font-bold tracking-[0.1em] text-rail-ink/70">
                  LOCAL SHAP ATTRIBUTIONS (TREE-EXPLAINER FEATURE IMPACT)
                </div>
                <div className="flex items-center gap-3 text-[10px] font-mono text-rail-ink/50">
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-rail-red/80" /> Increases Risk
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="size-2 rounded-full bg-rail-green/80" /> Decreases Risk
                  </span>
                </div>
              </div>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {prediction.feature_contributions.map((fc) => {
                  const isPos = fc.contribution > 0.005;
                  const isNeg = fc.contribution < -0.005;
                  return (
                    <div
                      key={fc.feature}
                      className={cn(
                        "rounded border p-2.5 text-xs transition-colors",
                        isPos
                          ? "border-rail-red/20 bg-rail-red/[0.03]"
                          : isNeg
                            ? "border-rail-green/20 bg-rail-green/[0.03]"
                            : "border-rail-ink/8 bg-rail-paper"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-rail-ink/85 truncate">{fc.feature_name}</span>
                        <Badge
                          variant="outline"
                          className={cn(
                            "font-mono text-[9px] px-1.5 py-0 uppercase",
                            isPos
                              ? "border-rail-red/30 text-rail-red bg-rail-red/5"
                              : isNeg
                                ? "border-rail-green/30 text-rail-green bg-rail-green/5"
                                : "border-rail-ink/20 text-rail-ink/50"
                          )}
                        >
                          {isPos ? "+ RISK" : isNeg ? "- RISK" : "NEUTRAL"}
                        </Badge>
                      </div>
                      <div className="mt-1.5 flex items-center justify-between text-[11px]">
                        <span className="font-mono text-rail-ink/60">Value: {fc.feature_value}</span>
                        <span
                          className={cn(
                            "font-mono font-bold",
                            isPos ? "text-rail-red" : isNeg ? "text-rail-green" : "text-rail-ink/60"
                          )}
                        >
                          SHAP {fc.contribution > 0 ? `+${fc.contribution.toFixed(3)}` : fc.contribution.toFixed(3)}
                        </span>
                      </div>
                      {/* Visual impact bar */}
                      <div className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-rail-ink/10">
                        <div
                          className={cn(
                            "h-full rounded-full transition-all",
                            isPos ? "bg-rail-red" : isNeg ? "bg-rail-green" : "bg-rail-ink/30"
                          )}
                          style={{
                            width: `${Math.min(100, Math.max(10, Math.abs(fc.contribution) * 60))}%`,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Risk Factors and Natural Language Briefing */}
          <div className="grid gap-3 lg:grid-cols-2">
            <div className="rounded-md border border-rail-ink/8 bg-rail-paper p-3.5">
              <div className="font-mono text-[10px] font-bold tracking-[0.1em] text-rail-ink/60">
                PRIMARY SHAP RISK DRIVERS
              </div>
              <div className="mt-2 space-y-1.5">
                {factors.length > 0 ? (
                  factors.map((f, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-rail-ink/80">
                      <ShieldAlert className="mt-0.5 size-3.5 shrink-0 text-rail-amber" />
                      <span>{f}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-rail-ink/50">Operating within nominal risk boundaries.</div>
                )}
              </div>
            </div>

            <div className="rounded-md border border-rail-blue/20 bg-rail-blue/[0.05] p-3.5">
              <div className="flex items-center gap-1.5 font-mono text-[10px] font-bold tracking-[0.08em] text-rail-blue">
                <Sparkles className="size-3.5" /> CONTROLLER AUDIT BRIEFING
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-rail-ink/80">
                {prediction.explanation || "No explanation provided for this maintenance task."}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <EmptyState label="Select a maintenance request above to evaluate AI decision-support metrics." compact />
      )}
    </section>
  );
}

function ComponentBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[10px]">
        <span className="font-mono text-rail-ink/55 truncate">{label}</span>
        <span className="font-bold font-mono text-rail-ink/80">{value.toFixed(1)}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-rail-ink/10">
        <div
          className="h-full rounded-full bg-rail-blue transition-all"
          style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

function DistributionPanel({
  title,
  meta,
  slices,
}: {
  title: string;
  meta: string;
  slices: Slice[];
}) {
  return (
    <div className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">{title}</div>
        <span className="font-mono text-[10px] text-rail-ink/35">{meta}</span>
      </div>
      {slices.length ? (
        <>
          <div className="mt-2 h-44">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={slices}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={42}
                  outerRadius={68}
                  paddingAngle={2}
                  strokeWidth={0}
                >
                  {slices.map((slice) => (
                    <Cell key={slice.name} fill={categoryColor(slice.name)} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "oklch(0.985 0.006 95)",
                    border: "1px solid oklch(0.18 0.015 270 / 0.12)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-1.5">
            {slices.map((slice) => (
              <div key={slice.name} className="flex items-center gap-2 text-xs">
                <span
                  className="size-2 shrink-0 rounded-full"
                  style={{ background: categoryColor(slice.name) }}
                />
                <span className="min-w-0 flex-1 truncate text-rail-ink/70">{slice.name}</span>
                <span className="font-mono text-[10px] font-semibold text-rail-ink/75">{slice.value}</span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <EmptyState label="No values were returned for this distribution." compact />
      )}
    </div>
  );
}

function DepartmentPanel({ slices }: { slices: Slice[] }) {
  return (
    <div className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">Maintenance by Department</div>
        <span className="font-mono text-[10px] text-rail-ink/35">CORRIDOR REQS</span>
      </div>
      {slices.length ? (
        <div className="mt-2 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={slices} layout="vertical" margin={{ left: 8, right: 16 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={100}
                tick={{ fontSize: 10, fill: CHART_INK_SOFT }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  background: "oklch(0.985 0.006 95)",
                  border: "1px solid oklch(0.18 0.015 270 / 0.12)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {slices.map((slice) => (
                  <Cell key={slice.name} fill={CHART_BLUE} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <EmptyState label="No department values were returned." compact />
      )}
    </div>
  );
}

function HighAttentionTasks({
  tasks,
  total,
  onSelectTask,
  activeTaskId,
}: {
  tasks: AIHighAttentionTask[];
  total: number;
  onSelectTask: (id: string) => void;
  activeTaskId: string;
}) {
  return (
    <section className="rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
      <div className="flex items-center justify-between border-b border-rail-ink/8 px-4 py-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="size-4 text-rail-red" />
          <span className="text-sm font-semibold">High-Priority &amp; High-Risk Maintenance Queue</span>
        </div>
        <span className="font-mono text-[10px] text-rail-ink/40">
          {tasks.length} OF {total} REQUESTS FLAGGED
        </span>
      </div>
      {tasks.length ? (
        <div className="divide-y divide-rail-ink/8">
          {tasks.map((task) => {
            const isSelected = task.request_id === activeTaskId;
            return (
              <div
                key={task.request_id}
                onClick={() => onSelectTask(task.request_id)}
                className={cn(
                  "flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3 transition hover:bg-rail-ink/[0.02]",
                  isSelected && "bg-rail-blue/[0.04] ring-1 ring-inset ring-rail-blue/30"
                )}
              >
                <span className="font-mono text-[11px] font-bold text-rail-blue">
                  {task.request_id}
                </span>
                <span className="min-w-0 flex-1 truncate text-xs text-rail-ink/70">
                  <span className="font-semibold text-rail-ink/90">{task.department}</span>
                  {" · "}
                  <span>{task.asset_type}</span>
                  {" · "}
                  <span className="font-mono text-[11px]">{task.section_id}</span>
                  {task.top_drivers && task.top_drivers.length > 0 && (
                    <span className="ml-2 text-rail-ink/50 italic truncate hidden md:inline">
                      ({task.top_drivers[0]})
                    </span>
                  )}
                </span>
                <Badge
                  variant="outline"
                  className="font-mono text-[10px]"
                  style={{ color: categoryColor(task.priority_category), borderColor: categoryColor(task.priority_category) }}
                >
                  PRI: {task.priority_score.toFixed(0)} ({task.priority_category})
                </Badge>
                <Badge
                  variant="outline"
                  className="font-mono text-[10px]"
                  style={{ color: categoryColor(task.risk_category), borderColor: categoryColor(task.risk_category) }}
                >
                  RISK: {task.risk_score.toFixed(0)} ({task.risk_category})
                </Badge>
                <Button variant="ghost" size="sm" className="h-7 text-xs font-mono text-rail-blue">
                  Analyze &rarr;
                </Button>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState label="No high-priority or high-risk tasks were returned." compact />
      )}
    </section>
  );
}

function InsightsSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-20 bg-rail-ink/8" />
      <Skeleton className="h-44 bg-rail-ink/8" />
      <div className="grid gap-4 lg:grid-cols-3">
        {[1, 2, 3].map((item) => (
          <Skeleton key={item} className="h-72 bg-rail-ink/8" />
        ))}
      </div>
      <Skeleton className="h-56 bg-rail-ink/8" />
    </div>
  );
}

function InsightsError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-[14px] border border-dashed border-rail-red/30 bg-rail-panel p-6 text-center">
      <CircleDot className="size-5 text-rail-red" />
      <p className="text-sm text-rail-ink/60">{message}</p>
      <Button variant="outline" size="sm" onClick={onRetry}>
        <RefreshCw className="size-3.5" />
        Retry feeds
      </Button>
    </div>
  );
}
