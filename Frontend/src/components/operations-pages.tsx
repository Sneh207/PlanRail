import { useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  OptimizationGenerateResponse,
  SimulationRunRequest,
  SimulationRunResponse,
} from "@/lib/types";
import {
  AlertCircle,
  ArrowRight,
  CalendarClock,
  Check,
  ChevronRight,
  CircleDot,
  Clock3,
  MapPin,
  PanelRight,
  RefreshCw,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Sparkles,
  TrendingUp,
  Wrench,
  X,
  BrainCircuit,
  ShieldAlert,
} from "lucide-react";
import { lazy, Suspense, useMemo, useState } from "react";

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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  api,
  apiErrorMessage,
  asRecords,
  isRecord,
  readNumber,
  readText,
  readValue,
  type JsonRecord,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { EmptyState, PageIntro, PlanRailShell } from "@/components/planrail";

const NetworkLeaflet = lazy(() =>
  import("@/components/network-leaflet").then((module) => ({ default: module.NetworkLeaflet })),
);

export function RailwayNetworkPage() {
  const sectionsQuery = useQuery({
    queryKey: ["planrail", "sections", "network"],
    queryFn: api.sections,
  });
  const stationsQuery = useQuery({
    queryKey: ["planrail", "stations", "network"],
    queryFn: api.stations,
  });
  const assetsQuery = useQuery({ queryKey: ["planrail", "assets"], queryFn: api.assets });
  const sections = asRecords(sectionsQuery.data);
  const stations = asRecords(stationsQuery.data);
  const assets = asRecords(assetsQuery.data);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);

  const sectionEntries = useMemo(
    () =>
      sections.map((record, index) => ({
        record,
        key: recordKey(record, index),
        id: recordId(record),
      })),
    [sections],
  );
  const selectedEntry = sectionEntries.find((entry) => entry.key === selectedKey) ?? null;
  const selectedSection = selectedEntry?.record ?? null;
  const detailId = selectedEntry?.id ?? null;
  const detailQuery = useQuery({
    queryKey: ["planrail", "section", detailId],
    queryFn: () => api.section(detailId ?? ""),
    enabled: Boolean(detailId),
  });
  const detail = isRecord(detailQuery.data) ? detailQuery.data : selectedSection;
  const sectionPoints = sections.flatMap((record) => {
    const position = coordinates(record);
    return position ? [{ record, position }] : [];
  });
  const stationPoints = stations.flatMap((record) => {
    const position = coordinates(record);
    return position ? [{ record, position }] : [];
  });
  const hasMapData = sectionPoints.length > 0 || stationPoints.length > 0;
  const associatedAssets = detailId
    ? assets.filter((asset) => assetSectionId(asset) === detailId)
    : [];
  const networkLoading =
    sectionsQuery.isPending || stationsQuery.isPending || assetsQuery.isPending;
  const networkError = sectionsQuery.error || stationsQuery.error || assetsQuery.error;

  function selectSection(record: JsonRecord, index = sections.indexOf(record)) {
    setSelectedKey(recordKey(record, index));
  }

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="NETWORK CONTROL — DELHI–AGRA"
          title="Railway network"
          description="Inspect corridor sections, station topology, and associated assets from the live feeds."
        />
        {networkError ? (
          <ErrorState
            message={apiErrorMessage(networkError, "The network feeds could not be loaded")}
            onRetry={() =>
              void Promise.all([
                sectionsQuery.refetch(),
                stationsQuery.refetch(),
                assetsQuery.refetch(),
              ])
            }
          />
        ) : networkLoading ? (
          <NetworkSkeleton />
        ) : sections.length === 0 && stations.length === 0 ? (
          <EmptyState label="No sections or stations were returned by the network feeds." />
        ) : (
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <section className="min-w-0 space-y-4">
              <div className="rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                      LIVE TOPOLOGY
                    </div>
                    <div className="mt-1 flex items-center gap-2 text-sm font-semibold">
                      <MapPin className="size-4 text-rail-blue" />
                      {hasMapData ? "Geospatial network view" : "Structured network view"}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
                    <span>{sections.length} SECTIONS</span>
                    <span>{stations.length} STATIONS</span>
                  </div>
                </div>
                {hasMapData ? (
                  <div className="mt-4 h-[420px] overflow-hidden rounded-lg border border-rail-ink/10 bg-rail-map">
                    <Suspense fallback={<Skeleton className="h-full w-full bg-rail-ink/8" />}>
                      <NetworkLeaflet
                        sections={sections}
                        stations={stations}
                        sectionPoints={sectionPoints}
                        stationPoints={stationPoints}
                        onSectionSelect={selectSection}
                      />
                    </Suspense>
                  </div>
                ) : (
                  <div className="rail-map mt-4 rounded-lg border border-rail-ink/10 p-4">
                    <div className="relative flex min-h-44 items-center px-4">
                      <div className="absolute inset-x-8 h-1 rounded-full bg-rail-blue/15" />
                      <div className="relative flex w-full items-center justify-between gap-3">
                        {stations.length ? (
                          stations.map((station, index) => (
                            <NetworkNode
                              key={`${recordKey(station, index)}`}
                              label={
                                readLabel(station, [
                                  "code",
                                  "station_code",
                                  "name",
                                  "station_name",
                                ]) ?? `Station ${index + 1}`
                              }
                            />
                          ))
                        ) : (
                          <NetworkNode label="Station coordinates unavailable" muted />
                        )}
                      </div>
                    </div>
                    <p className="font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
                      COORDINATES NOT RETURNED · LIST MODE ACTIVE
                    </p>
                  </div>
                )}
              </div>
              <div className="rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
                <div className="border-b border-rail-ink/8 px-4 py-3">
                  <div className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                    SECTIONS
                  </div>
                  <div className="mt-1 text-sm font-semibold">
                    Select a section to inspect its live fields
                  </div>
                </div>
                <div className="divide-y divide-rail-ink/8">
                  {sections.map((section, index) => (
                    <SectionRow
                      key={recordKey(section, index)}
                      record={section}
                      selected={selectedKey === recordKey(section, index)}
                      onClick={() => selectSection(section, index)}
                    />
                  ))}
                </div>
              </div>
            </section>
            <NetworkDetailPanel
              section={detail}
              loading={detailQuery.isFetching}
              error={detailQuery.error}
              assets={associatedAssets}
              onClose={() => setSelectedKey(null)}
            />
          </div>
        )}
      </div>
    </PlanRailShell>
  );
}

export function MaintenancePage() {
  const maintenanceQuery = useQuery({
    queryKey: ["planrail", "maintenance"],
    queryFn: api.maintenance,
  });
  const records = asRecords(maintenanceQuery.data);
  const [department, setDepartment] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const selectedEntry =
    records
      .map((record, index) => ({ record, key: recordKey(record, index), id: recordId(record) }))
      .find((entry) => entry.key === selectedKey) ?? null;
  const detailQuery = useQuery({
    queryKey: ["planrail", "maintenance", selectedEntry?.id],
    queryFn: () => api.maintenanceRequest(selectedEntry?.id ?? ""),
    enabled: Boolean(selectedEntry?.id),
  });
  const departments = filterValues(records, ["department", "department_name", "departmentName"]);
  const severities = filterValues(records, ["severity"]);
  const statuses = filterValues(records, ["status"]);
  const filtered = records.filter(
    (record) =>
      matches(record, ["department", "department_name", "departmentName"], department) &&
      matches(record, ["severity"], severity) &&
      matches(record, ["status"], status),
  );
  const error = maintenanceQuery.error;

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="MAINTENANCE CONTROL — DELHI–AGRA"
          title="Maintenance"
          description="Review returned work requests by department, severity, status, and risk."
        />
        {error ? (
          <ErrorState
            message={apiErrorMessage(error, "The maintenance feed could not be loaded")}
            onRetry={() => void maintenanceQuery.refetch()}
          />
        ) : maintenanceQuery.isPending ? (
          <MaintenanceSkeleton />
        ) : records.length === 0 ? (
          <EmptyState label="No maintenance requests were returned by the backend." />
        ) : (
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <section className="min-w-0 rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
              <div className="flex flex-wrap items-center gap-2 border-b border-rail-ink/8 p-4">
                <div className="relative min-w-48 flex-1">
                  <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-rail-ink/35" />
                  <input
                    aria-label="Search maintenance records"
                    placeholder="Search is available through filters"
                    disabled
                    className="h-9 w-full rounded-md border border-rail-ink/10 bg-rail-paper pl-9 pr-3 text-xs text-rail-ink/50"
                  />
                </div>
                <FilterSelect
                  label="Department"
                  value={department}
                  values={departments}
                  onValueChange={setDepartment}
                />
                <FilterSelect
                  label="Severity"
                  value={severity}
                  values={severities}
                  onValueChange={setSeverity}
                />
                <FilterSelect
                  label="Status"
                  value={status}
                  values={statuses}
                  onValueChange={setStatus}
                />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-xs">
                  <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                    <tr>
                      {[
                        "TASK ID",
                        "DEPARTMENT",
                        "SECTION",
                        "SEVERITY",
                        "PRIORITY",
                        "RISK",
                        "DUE DATE",
                        "STATUS",
                      ].map((heading) => (
                        <th key={heading} className="px-4 py-3 font-medium">
                          {heading}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rail-ink/8">
                    {filtered.map((record, index) => {
                      const key = recordKey(record, index);
                      return (
                        <MaintenanceRow
                          key={key}
                          record={record}
                          selected={selectedKey === key}
                          onClick={() => setSelectedKey(key)}
                        />
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {filtered.length === 0 && (
                <EmptyState label="No maintenance requests match the selected filters." compact />
              )}
              <div className="flex items-center justify-between border-t border-rail-ink/8 px-4 py-3 font-mono text-[10px] text-rail-ink/40">
                <span>
                  {filtered.length} OF {records.length} REQUESTS
                </span>
                <span>READ-ONLY FEED</span>
              </div>
            </section>
            <MaintenanceDetailPanel
              record={
                isRecord(detailQuery.data) ? detailQuery.data : (selectedEntry?.record ?? null)
              }
              loading={detailQuery.isFetching}
              error={detailQuery.error}
              onClose={() => setSelectedKey(null)}
            />
          </div>
        )}
      </div>
    </PlanRailShell>
  );
}

export function TrainsPage() {
  const [activeTab, setActiveTab] = useState<"passenger" | "freight">("passenger");

  // Passenger Trains Query
  const trainsQuery = useQuery({ queryKey: ["planrail", "trains"], queryFn: api.trains });
  const passengerRecords = asRecords(trainsQuery.data);

  // Freight Trains Query
  const freightQuery = useQuery({
    queryKey: ["planrail", "freight-trains"],
    queryFn: () => api.freightTrains({ page_size: 50 }),
  });
  const freightRecords = asRecords(freightQuery.data);

  const [search, setSearch] = useState("");
  const [selectedPassengerKey, setSelectedPassengerKey] = useState<string | null>(null);
  const [selectedFreightKey, setSelectedFreightKey] = useState<string | null>(null);

  // Filter passenger trains
  const passengerEntries = passengerRecords.map((record, index) => ({
    record,
    key: trainKey(record, index),
    number: readLabel(record, ["train_number", "trainNumber", "number", "id"]),
  }));
  const filteredPassenger = passengerEntries.filter(({ record }) => {
    const haystack = [
      readLabel(record, ["train_number", "trainNumber", "number", "id"]),
      readLabel(record, ["train_name", "trainName", "name"]),
      readLabel(record, ["train_type", "trainType", "type"]),
      readLabel(record, ["priority"]),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(search.trim().toLowerCase());
  });

  // Filter freight trains
  const freightEntries = freightRecords.map((record, index) => ({
    record,
    key: readLabel(record, ["freight_train_id", "id"]) ?? `freight-${index}`,
    id: readLabel(record, ["freight_train_id", "id"]),
  }));
  const filteredFreight = freightEntries.filter(({ record }) => {
    const haystack = [
      readLabel(record, ["freight_train_id", "id"]),
      readLabel(record, ["commodity"]),
      readLabel(record, ["origin_station_code"]),
      readLabel(record, ["destination_station_code"]),
      readLabel(record, ["traffic_priority"]),
      readLabel(record, ["movement_date"]),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(search.trim().toLowerCase());
  });

  // Selected Passenger Train
  const selectedPassenger = passengerEntries.find((entry) => entry.key === selectedPassengerKey) ?? null;
  const trainNumber = selectedPassenger?.number;
  const passengerDetailQuery = useQuery({
    queryKey: ["planrail", "train", trainNumber],
    queryFn: () => api.train(trainNumber ?? ""),
    enabled: Boolean(trainNumber) && activeTab === "passenger",
  });
  const scheduleQuery = useQuery({
    queryKey: ["planrail", "train", trainNumber, "schedule"],
    queryFn: () => api.trainSchedule(trainNumber ?? ""),
    enabled: Boolean(trainNumber) && activeTab === "passenger",
  });
  const passengerDetail = isRecord(passengerDetailQuery.data)
    ? passengerDetailQuery.data
    : (selectedPassenger?.record ?? null);
  const schedule = asRecords(scheduleQuery.data);

  // Selected Freight Train
  const selectedFreight = freightEntries.find((entry) => entry.key === selectedFreightKey) ?? null;
  const freightId = selectedFreight?.id;
  const freightDetailQuery = useQuery({
    queryKey: ["planrail", "freight-train", freightId],
    queryFn: () => api.freightTrain(freightId ?? ""),
    enabled: Boolean(freightId) && activeTab === "freight",
  });
  const freightDetail = isRecord(freightDetailQuery.data)
    ? freightDetailQuery.data
    : (selectedFreight?.record ?? null);

  const error = activeTab === "passenger" ? trainsQuery.error : freightQuery.error;
  const loading = activeTab === "passenger" ? trainsQuery.isPending : freightQuery.isPending;

  return (
    <PlanRailShell>
      <div className="space-y-5">
        <PageIntro
          eyebrow="TRAFFIC CONTROL — DELHI–AGRA"
          title="Corridor Traffic & Trains"
          description="Inspect passenger service timetables and synthetic freight planning scenarios on the Delhi–Agra corridor."
        />

        {/* Tab Selector */}
        <div className="flex flex-wrap items-center gap-3 border-b border-rail-ink/10 pb-3">
          <button
            type="button"
            onClick={() => {
              setActiveTab("passenger");
              setSearch("");
            }}
            className={cn(
              "rounded-lg px-4 py-2 text-xs font-semibold transition-colors",
              activeTab === "passenger"
                ? "bg-rail-blue text-rail-paper shadow-sm"
                : "bg-rail-panel text-rail-ink/60 hover:bg-rail-panel/80",
            )}
          >
            Passenger Services ({passengerRecords.length})
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("freight");
              setSearch("");
            }}
            className={cn(
              "flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition-colors",
              activeTab === "freight"
                ? "bg-rail-blue text-rail-paper shadow-sm"
                : "bg-rail-panel text-rail-ink/60 hover:bg-rail-panel/80",
            )}
          >
            <span>Freight Planning Movements ({freightRecords.length})</span>
            <Badge className="border-amber-500/30 bg-amber-500/15 text-[9px] uppercase text-amber-600">
              SYNTHETIC
            </Badge>
          </button>
        </div>

        {error ? (
          <ErrorState
            message={apiErrorMessage(error, "The traffic feed could not be loaded")}
            onRetry={() => void (activeTab === "passenger" ? trainsQuery.refetch() : freightQuery.refetch())}
          />
        ) : loading ? (
          <TableSkeleton />
        ) : activeTab === "passenger" ? (
          passengerRecords.length === 0 ? (
            <EmptyState label="No passenger trains were returned by the backend." />
          ) : (
            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
              <section className="min-w-0 rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 p-4">
                  <div className="relative min-w-56 flex-1">
                    <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-rail-ink/35" />
                    <input
                      aria-label="Search trains"
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                      placeholder="Search train number or name"
                      className="h-9 w-full rounded-md border border-rail-ink/10 bg-rail-paper pl-9 pr-3 text-xs outline-none placeholder:text-rail-ink/35 focus:border-rail-blue/50 focus:ring-2 focus:ring-rail-blue/10"
                    />
                  </div>
                  <span className="font-mono text-[10px] tracking-[0.1em] text-rail-ink/40">
                    {filteredPassenger.length} OF {passengerRecords.length} SERVICES
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[620px] text-left text-xs">
                    <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                      <tr>
                        {["TRAIN NUMBER", "TRAIN NAME", "TRAIN TYPE", "PRIORITY"].map((heading) => (
                          <th key={heading} className="px-4 py-3 font-medium">
                            {heading}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-rail-ink/8">
                      {filteredPassenger.map(({ record, key }) => (
                        <TrainRow
                          key={key}
                          record={record}
                          selected={selectedPassengerKey === key}
                          onClick={() => setSelectedPassengerKey(key)}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>
                {filteredPassenger.length === 0 && (
                  <EmptyState label="No trains match the current search." compact />
                )}
                <div className="flex items-center justify-between border-t border-rail-ink/8 px-4 py-3 font-mono text-[10px] text-rail-ink/40">
                  <span>READ-ONLY SCHEDULE FEED</span>
                  <span>GET /api/v1/trains</span>
                </div>
              </section>
              <TrainDetailPanel
                train={passengerDetail}
                schedule={schedule}
                loading={passengerDetailQuery.isFetching || scheduleQuery.isFetching}
                error={passengerDetailQuery.error || scheduleQuery.error}
                onClose={() => setSelectedPassengerKey(null)}
              />
            </div>
          )
        ) : (
          freightRecords.length === 0 ? (
            <EmptyState label="No freight planning movements were returned by the backend." />
          ) : (
            <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
              <section className="min-w-0 rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 p-4">
                  <div className="relative min-w-56 flex-1">
                    <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-rail-ink/35" />
                    <input
                      aria-label="Search freight movements"
                      value={search}
                      onChange={(event) => setSearch(event.target.value)}
                      placeholder="Search freight ID, commodity, priority, or date"
                      className="h-9 w-full rounded-md border border-rail-ink/10 bg-rail-paper pl-9 pr-3 text-xs outline-none placeholder:text-rail-ink/35 focus:border-rail-blue/50 focus:ring-2 focus:ring-rail-blue/10"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className="border-amber-500/30 bg-amber-500/10 font-mono text-[10px] text-amber-700">
                      SIMULATED_BY_PLANRAIL
                    </Badge>
                    <span className="font-mono text-[10px] tracking-[0.1em] text-rail-ink/40">
                      {filteredFreight.length} OF {freightRecords.length} RECORDS
                    </span>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[680px] text-left text-xs">
                    <thead className="bg-rail-ink/[0.03] font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">
                      <tr>
                        {[
                          "FREIGHT ID",
                          "DATE",
                          "ROUTE",
                          "COMMODITY",
                          "TONNAGE",
                          "ENTRY → EXIT",
                          "PRIORITY",
                        ].map((heading) => (
                          <th key={heading} className="px-4 py-3 font-medium">
                            {heading}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-rail-ink/8">
                      {filteredFreight.map(({ record, key }) => (
                        <FreightRow
                          key={key}
                          record={record}
                          selected={selectedFreightKey === key}
                          onClick={() => setSelectedFreightKey(key)}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>
                {filteredFreight.length === 0 && (
                  <EmptyState label="No freight records match the current search." compact />
                )}
                <div className="flex items-center justify-between border-t border-rail-ink/8 px-4 py-3 font-mono text-[10px] text-rail-ink/40">
                  <span>SYNTHETIC PLANNING SCENARIO · 2026-09-14 TO 2026-09-16</span>
                  <span>GET /api/v1/freight-trains</span>
                </div>
              </section>
              <FreightDetailPanel
                record={freightDetail}
                loading={freightDetailQuery.isFetching}
                error={freightDetailQuery.error}
                onClose={() => setSelectedFreightKey(null)}
              />
            </div>
          )
        )}
      </div>
    </PlanRailShell>
  );
}

export function BlockPlanningPage() {
  const queryClient = useQueryClient();
  const blocksQuery = useQuery({ queryKey: ["planrail", "blocks"], queryFn: api.blocks });
  const records = asRecords(blocksQuery.data);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [optimizationOpen, setOptimizationOpen] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationGenerateResponse | null>(null);
  const [optimizationError, setOptimizationError] = useState<string | null>(null);
  const [optimizationPending, setOptimizationPending] = useState(false);
  const [targetDate, setTargetDate] = useState(() => new Date().toISOString().slice(0, 10));

  // What-If Simulation State
  const [simulationScenario, setSimulationScenario] = useState<
    "TRAFFIC_PLUS_20" | "EMERGENCY_MAINTENANCE" | "REMOVE_MAINTENANCE_WINDOW"
  >("TRAFFIC_PLUS_20");
  const [simulationTargetDate, setSimulationTargetDate] = useState("2026-09-15");
  const [simulationRequestId, setSimulationRequestId] = useState("REQ00001");
  const [simulationWindowId, setSimulationWindowId] = useState("MW00001");
  const [simulationResult, setSimulationResult] = useState<SimulationRunResponse | null>(null);
  const [simulationPending, setSimulationPending] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  // Demo-only approval state: no approval API exists yet, so decisions are
  // kept locally and clearly labelled in the UI.
  const [demoDecisions, setDemoDecisions] = useState<Record<string, BlockDecision>>({});
  const entries = records.map((record, index) => ({
    record,
    key: blockKey(record, index),
    id: blockId(record),
  }));
  const selected = entries.find((entry) => entry.key === selectedKey) ?? null;
  const detailQuery = useQuery({
    queryKey: ["planrail", "block", selected?.id],
    queryFn: () => api.block(selected?.id ?? ""),
    enabled: Boolean(selected?.id),
  });
  const bounds = timelineBounds(records);
  const error = blocksQuery.error;

  async function generatePlan() {
    setOptimizationError(null);
    setOptimizationPending(true);
    try {
      const response = await api.generateOptimization({
        target_date: targetDate,
        selected_request_ids: null,
        max_block_duration_hours: 4.0,
      });
      if (response.status >= 200 && response.status < 300 && response.data) {
        setOptimizationResult(response.data);
        setOptimizationOpen(true);
        void queryClient.invalidateQueries({ queryKey: ["planrail", "blocks"] });
      } else {
        setOptimizationError(
          apiErrorMessage(response.data, "The optimization endpoint did not return an available plan."),
        );
      }
    } catch (requestError) {
      setOptimizationError(apiErrorMessage(requestError, "The optimization endpoint could not be reached"));
    } finally {
      setOptimizationPending(false);
    }
  }

  async function runWhatIfSimulation() {
    setSimulationError(null);
    setSimulationPending(true);
    try {
      const payload: SimulationRunRequest = {
        scenario_type: simulationScenario,
        target_date: simulationTargetDate,
        request_id: simulationScenario === "EMERGENCY_MAINTENANCE" ? simulationRequestId : null,
        window_id: simulationScenario === "REMOVE_MAINTENANCE_WINDOW" ? simulationWindowId : null,
      };
      const response = await api.runSimulation(payload);
      if (response.status >= 200 && response.status < 300 && response.data) {
        setSimulationResult(response.data);
      } else {
        setSimulationError(
          apiErrorMessage(response.data, "The simulation endpoint did not return valid metrics."),
        );
      }
    } catch (err) {
      setSimulationError(apiErrorMessage(err, "The What-If simulation service could not be reached"));
    } finally {
      setSimulationPending(false);
    }
  }

  return (
    <PlanRailShell>
      <div className="space-y-6">
        <PageIntro
          eyebrow="BLOCK CONTROL — DELHI–AGRA"
          title="Block planning & What-If simulation"
          description="Review corridor blocks, generate optimal maintenance possessions with CP-SAT, and simulate external operational shocks."
        />

        {/* Top Control Bar: Optimizer & Quick Actions */}
        <div className="flex flex-col gap-3 rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <div className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                CP-SAT OPTIMIZER
              </div>
              <div className="mt-0.5 text-sm text-rail-ink/70">
                Generate deconflicted maintenance blocks for selected target date
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[11px] text-rail-ink/50">Target Date:</span>
              <input
                type="date"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                className="h-8 rounded-md border border-rail-ink/10 bg-rail-paper px-2.5 text-xs font-mono text-rail-ink/80 outline-none focus:border-rail-blue/50"
              />
            </div>
          </div>
          <Button
            onClick={() => void generatePlan()}
            disabled={optimizationPending}
            className="w-full bg-rail-blue text-rail-paper hover:bg-rail-blue/90 sm:w-auto"
          >
            <Sparkles className="size-4" /> {optimizationPending ? "Solving CP-SAT Model…" : "Generate Optimal Plan"}
          </Button>
        </div>

        {optimizationError && <ErrorState message={optimizationError} />}

        {/* What-If Simulation Engine Section */}
        <section className="rounded-[14px] border border-rail-ink/10 bg-rail-panel p-5 shadow-rail">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 pb-4">
            <div>
              <div className="flex items-center gap-2 font-mono text-[10px] tracking-[0.15em] text-rail-blue">
                <SlidersHorizontal className="size-3.5" />
                WHAT-IF SIMULATION ENGINE
              </div>
              <h3 className="mt-1 text-base font-bold text-rail-ink">
                Scenario & Sensitivity Analysis
              </h3>
              <p className="mt-0.5 text-xs text-rail-ink/65">
                Non-destructive simulation of corridor disruptions and capacity adjustments.
              </p>
            </div>
            <div className="flex items-center gap-2">
              {simulationResult && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSimulationResult(null)}
                  className="h-8 gap-1.5 border-rail-ink/15 text-xs"
                >
                  <RotateCcw className="size-3.5" /> Reset to Baseline
                </Button>
              )}
              <Button
                size="sm"
                onClick={() => void runWhatIfSimulation()}
                disabled={simulationPending}
                className="h-8 gap-1.5 bg-rail-ink text-xs font-medium text-rail-paper hover:bg-rail-ink/90"
              >
                <TrendingUp className="size-3.5" />
                {simulationPending ? "Simulating Scenario…" : "Run Simulation"}
              </Button>
            </div>
          </div>

          {/* Scenario Selection Grid */}
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              {
                id: "TRAFFIC_PLUS_20" as const,
                title: "Traffic +20%",
                desc: "Simulate a 20% surge in train traffic density across the Delhi–Agra corridor.",
              },
              {
                id: "EMERGENCY_MAINTENANCE" as const,
                title: "Emergency Maintenance",
                desc: "Inject an urgent maintenance possession request and test dynamic reallocation.",
              },
              {
                id: "REMOVE_MAINTENANCE_WINDOW" as const,
                title: "Remove Maintenance Window",
                desc: "Withdraw an operational track window and evaluate optimizer reassignment.",
              },
            ].map((sc) => {
              const active = simulationScenario === sc.id;
              return (
                <div
                  key={sc.id}
                  onClick={() => setSimulationScenario(sc.id)}
                  className={cn(
                    "cursor-pointer rounded-xl border p-3 transition-all",
                    active
                      ? "border-rail-blue bg-rail-paper shadow-sm ring-2 ring-rail-blue/20"
                      : "border-rail-ink/10 bg-rail-paper/40 hover:bg-rail-paper/80",
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-rail-ink">{sc.title}</span>
                    <Badge
                      variant="outline"
                      className={cn(
                        "font-mono text-[9px]",
                        active ? "border-rail-blue text-rail-blue" : "border-rail-ink/20 text-rail-ink/40",
                      )}
                    >
                      {active ? "ACTIVE" : "SELECT"}
                    </Badge>
                  </div>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-rail-ink/65">{sc.desc}</p>
                </div>
              );
            })}
          </div>

          {/* Scenario Parameters */}
          <div className="mt-4 flex flex-wrap items-center gap-4 rounded-lg bg-rail-paper p-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] text-rail-ink/50">TARGET DATE:</span>
              <input
                type="date"
                value={simulationTargetDate}
                onChange={(e) => setSimulationTargetDate(e.target.value)}
                className="h-7 rounded border border-rail-ink/15 bg-rail-panel px-2 font-mono text-xs"
              />
            </div>
            {simulationScenario === "EMERGENCY_MAINTENANCE" && (
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-rail-ink/50">REQUEST ID:</span>
                <input
                  type="text"
                  value={simulationRequestId}
                  onChange={(e) => setSimulationRequestId(e.target.value)}
                  placeholder="e.g. REQ00001"
                  className="h-7 w-28 rounded border border-rail-ink/15 bg-rail-panel px-2 font-mono text-xs"
                />
              </div>
            )}
            {simulationScenario === "REMOVE_MAINTENANCE_WINDOW" && (
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-rail-ink/50">WINDOW ID:</span>
                <input
                  type="text"
                  value={simulationWindowId}
                  onChange={(e) => setSimulationWindowId(e.target.value)}
                  placeholder="e.g. MW00001"
                  className="h-7 w-28 rounded border border-rail-ink/15 bg-rail-panel px-2 font-mono text-xs"
                />
              </div>
            )}
          </div>

          {simulationError && (
            <div className="mt-3">
              <ErrorState message={simulationError} />
            </div>
          )}

          {/* Simulation Results Comparative Display */}
          {simulationResult && (
            <div className="mt-4 space-y-4 rounded-xl border border-rail-blue/20 bg-rail-paper p-4">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rail-ink/8 pb-3">
                <div className="flex items-center gap-2">
                  <span className="rail-pulse size-2 rounded-full bg-rail-blue" />
                  <span className="font-mono text-xs font-bold text-rail-blue">
                    {simulationResult.simulation_id}
                  </span>
                  <Badge variant="outline" className="font-mono text-[9px]">
                    {simulationResult.scenario_type}
                  </Badge>
                </div>
                <span className="font-mono text-[10px] text-rail-ink/40">
                  Target: {simulationResult.target_date}
                </span>
              </div>

              {/* Metrics Comparative Grid */}
              <div className="grid gap-3 sm:grid-cols-4">
                <div className="rounded-lg border border-rail-ink/8 bg-rail-panel p-3">
                  <div className="font-mono text-[9px] tracking-wider text-rail-ink/45">
                    SCHEDULED TASKS
                  </div>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-xl font-extrabold text-rail-ink">
                      {simulationResult.scenario.scheduled_tasks}
                    </span>
                    <span className="text-xs text-rail-ink/40">
                      vs {simulationResult.baseline.scheduled_tasks} baseline
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className={cn(
                      "mt-2 font-mono text-[9px]",
                      simulationResult.difference.scheduled_tasks_delta >= 0
                        ? "border-rail-green/30 text-rail-green"
                        : "border-rail-red/30 text-rail-red",
                    )}
                  >
                    {simulationResult.difference.scheduled_tasks_delta >= 0 ? "+" : ""}
                    {simulationResult.difference.scheduled_tasks_delta} delta
                  </Badge>
                </div>

                <div className="rounded-lg border border-rail-ink/8 bg-rail-panel p-3">
                  <div className="font-mono text-[9px] tracking-wider text-rail-ink/45">
                    TOTAL DURATION
                  </div>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-xl font-extrabold text-rail-ink">
                      {simulationResult.scenario.total_scheduled_duration_hours.toFixed(1)}h
                    </span>
                    <span className="text-xs text-rail-ink/40">
                      vs {simulationResult.baseline.total_scheduled_duration_hours.toFixed(1)}h
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className="mt-2 border-rail-ink/20 font-mono text-[9px] text-rail-ink/60"
                  >
                    {simulationResult.difference.scheduled_duration_delta_hours >= 0 ? "+" : ""}
                    {simulationResult.difference.scheduled_duration_delta_hours.toFixed(1)}h delta
                  </Badge>
                </div>

                <div className="rounded-lg border border-rail-ink/8 bg-rail-panel p-3">
                  <div className="font-mono text-[9px] tracking-wider text-rail-ink/45">
                    TRAIN EXPOSURE
                  </div>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-xl font-extrabold text-rail-ink">
                      {simulationResult.scenario.total_expected_train_exposure}
                    </span>
                    <span className="text-xs text-rail-ink/40">
                      vs {simulationResult.baseline.total_expected_train_exposure}
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className="mt-2 border-rail-ink/20 font-mono text-[9px] text-rail-ink/60"
                  >
                    {simulationResult.difference.train_exposure_delta >= 0 ? "+" : ""}
                    {simulationResult.difference.train_exposure_delta} exposure delta
                  </Badge>
                </div>

                <div className="rounded-lg border border-rail-ink/8 bg-rail-panel p-3">
                  <div className="font-mono text-[9px] tracking-wider text-rail-ink/45">
                    UNSCHEDULED TASKS
                  </div>
                  <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-xl font-extrabold text-rail-ink">
                      {simulationResult.scenario.unscheduled_tasks}
                    </span>
                    <span className="text-xs text-rail-ink/40">
                      vs {simulationResult.baseline.unscheduled_tasks}
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className={cn(
                      "mt-2 font-mono text-[9px]",
                      simulationResult.scenario.unscheduled_tasks === 0
                        ? "border-rail-green/30 text-rail-green"
                        : "border-rail-amber/30 text-rail-amber",
                    )}
                  >
                    {simulationResult.scenario.unscheduled_tasks === 0 ? "ALL ACCOMMODATED" : "CAPACITY CONSTRAINED"}
                  </Badge>
                </div>
              </div>

              {/* Task Reallocations & Unscheduled Chips */}
              {(simulationResult.moved_tasks.length > 0 ||
                simulationResult.unscheduled_tasks_after_simulation.length > 0 ||
                simulationResult.newly_scheduled_tasks.length > 0) && (
                <div className="flex flex-wrap gap-2 text-xs">
                  {simulationResult.newly_scheduled_tasks.map((id) => (
                    <Badge key={id} className="bg-rail-green/15 text-rail-green font-mono text-[10px]">
                      + NEW: {id}
                    </Badge>
                  ))}
                  {simulationResult.moved_tasks.map((id) => (
                    <Badge key={id} className="bg-rail-blue/15 text-rail-blue font-mono text-[10px]">
                      ↔ MOVED: {id}
                    </Badge>
                  ))}
                  {simulationResult.unscheduled_tasks_after_simulation.map((id) => (
                    <Badge key={id} className="bg-rail-red/15 text-rail-red font-mono text-[10px]">
                      ✕ UNSCHEDULED: {id}
                    </Badge>
                  ))}
                </div>
              )}

              {/* Explanation Note */}
              <div className="rounded-lg bg-rail-panel p-3 text-xs leading-relaxed text-rail-ink/80">
                <div className="font-mono text-[10px] tracking-wider text-rail-ink/40 mb-1">
                  EXPLANATION &amp; DECISION IMPACT
                </div>
                {simulationResult.explanation}
              </div>
            </div>
          )}
        </section>

        {/* Existing Blocks Feed */}
        {error ? (
          <ErrorState
            message={apiErrorMessage(error, "The block feed could not be loaded")}
            onRetry={() => void blocksQuery.refetch()}
          />
        ) : blocksQuery.isPending ? (
          <BlockSkeleton />
        ) : records.length === 0 ? (
          <EmptyState label="No existing blocks were returned by the backend." />
        ) : (
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
            <section className="min-w-0 rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
                    EXISTING BLOCKS
                  </div>
                  <div className="mt-1 text-sm font-semibold">Corridor occupation timeline</div>
                </div>
                <div className="font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
                  {records.length} BLOCKS
                </div>
              </div>
              <div className="mt-5 overflow-x-auto">
                <div className="min-w-[700px]">
                  <div className="ml-[170px] flex justify-between border-b border-rail-ink/10 pb-2 font-mono text-[10px] text-rail-ink/40">
                    <span>{bounds.labelStart}</span>
                    <span>{bounds.labelMid}</span>
                    <span>{bounds.labelEnd}</span>
                  </div>
                  <div className="divide-y divide-rail-ink/8">
                    {records.map((record, index) => (
                      <BlockTimelineRow
                        key={blockKey(record, index)}
                        record={record}
                        selected={selectedKey === blockKey(record, index)}
                        bounds={bounds}
                        onClick={() => setSelectedKey(blockKey(record, index))}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2 font-mono text-[10px] tracking-[0.08em] text-rail-ink/40">
                <CalendarClock className="size-3.5" /> TIMINGS AND STATUS REFLECT REAL BACKEND BLOCKS
              </div>
            </section>
            <BlockDetailPanel
              block={isRecord(detailQuery.data) ? detailQuery.data : (selected?.record ?? null)}
              loading={detailQuery.isFetching}
              error={detailQuery.error}
              decision={selected ? (demoDecisions[selected.key] ?? null) : null}
              onDecision={(decision) => {
                if (selected)
                  setDemoDecisions((current) => ({ ...current, [selected.key]: decision }));
              }}
              onClose={() => setSelectedKey(null)}
            />
          </div>
        )}
      </div>

      <Dialog open={optimizationOpen} onOpenChange={setOptimizationOpen}>
        <DialogContent className="border-rail-ink/10 bg-rail-panel text-rail-ink sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="size-5 text-rail-blue" />
              Optimization Plan Generated
            </DialogTitle>
            <DialogDescription className="pt-1 text-rail-ink/60">
              CP-SAT solver ran against corridor constraints for target date {targetDate}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div className="rounded-md border border-rail-ink/8 bg-rail-paper p-3">
                <div className="font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">BLOCKS GENERATED</div>
                <div className="mt-1 text-lg font-bold text-rail-blue">
                  {optimizationResult?.total_blocks_generated ?? 0}
                </div>
              </div>
              <div className="rounded-md border border-rail-ink/8 bg-rail-paper p-3">
                <div className="font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">TASKS SCHEDULED</div>
                <div className="mt-1 text-lg font-bold text-rail-green">
                  {optimizationResult?.total_tasks_scheduled ?? 0}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-2 border-b border-rail-ink/8 pb-2">
              <span className="text-rail-ink/45">Total Duration</span>
              <span className="font-mono font-medium">
                {optimizationResult?.total_duration_hours != null
                  ? `${optimizationResult.total_duration_hours.toFixed(1)} hrs`
                  : "—"}
              </span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-2 border-b border-rail-ink/8 pb-2">
              <span className="text-rail-ink/45">Solver Status</span>
              <span className="font-mono font-medium uppercase text-rail-green">
                {optimizationResult?.status ?? "OPTIMAL"}
              </span>
            </div>
            <div className="grid grid-cols-[120px_1fr] gap-2">
              <span className="text-rail-ink/45">Run ID</span>
              <span className="truncate font-mono text-[11px] text-rail-ink/60">
                {optimizationResult?.run_id ?? "—"}
              </span>
            </div>
            {optimizationResult?.message && (
              <p className="rounded-md bg-rail-paper p-2.5 text-rail-ink/70">
                {optimizationResult.message}
              </p>
            )}
          </div>
          <DialogFooter>
            <Button
              className="w-full bg-rail-blue text-rail-paper hover:bg-rail-blue/90"
              onClick={() => setOptimizationOpen(false)}
            >
              View Updated Corridor Blocks
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </PlanRailShell>
  );
}

function TrainRow({
  record,
  selected,
  onClick,
}: {
  record: JsonRecord;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <tr
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onClick();
      }}
      className={cn(
        "cursor-pointer transition-colors hover:bg-rail-blue/[0.04]",
        selected && "bg-rail-blue/[0.07]",
      )}
    >
      <td className="px-4 py-3 font-mono text-[11px] font-semibold">
        {readLabel(record, ["train_number", "trainNumber", "number", "id"]) ?? "—"}
      </td>
      <td className="px-4 py-3">{readLabel(record, ["train_name", "trainName", "name"]) ?? "—"}</td>
      <td className="px-4 py-3 text-rail-ink/60">
        {readLabel(record, ["train_type", "trainType", "type"]) ?? "—"}
      </td>
      <td className="px-4 py-3">
        <StatusBadge value={readLabel(record, ["priority"])} kind="priority" />
      </td>
    </tr>
  );
}

function TrainDetailPanel({
  train,
  schedule,
  loading,
  error,
  onClose,
}: {
  train: JsonRecord | null;
  schedule: JsonRecord[];
  loading: boolean;
  error: Error | null;
  onClose: () => void;
}) {
  const trainDelay = train
    ? readLabel(train, ["delay", "delay_minutes", "delayMinutes", "delay_status"])
    : null;
  return (
    <aside className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
      <PanelHeader
        eyebrow="TRAIN DETAIL"
        title={train ? "Selected service" : "Select a train"}
        onClose={train ? onClose : undefined}
      />
      {error ? (
        <ErrorState
          message={apiErrorMessage(error, "The train detail or schedule could not be loaded")}
        />
      ) : !train ? (
        <EmptyState label="Choose a train to inspect its returned schedule." compact />
      ) : loading ? (
        <DetailSkeleton />
      ) : (
        <div className="mt-5 space-y-5">
          <DetailFields record={train} />
          {trainDelay && (
            <div className="rounded-md border border-rail-amber/20 bg-rail-amber/10 p-3 text-xs text-rail-amber">
              <div className="font-mono text-[10px] tracking-[0.14em]">DELAY</div>
              <div className="mt-1 font-semibold">{trainDelay}</div>
            </div>
          )}
          <ScheduleTimeline schedule={schedule} />
        </div>
      )}
    </aside>
  );
}

function FreightRow({
  record,
  selected,
  onClick,
}: {
  record: JsonRecord;
  selected: boolean;
  onClick: () => void;
}) {
  const freightId = readLabel(record, ["freight_train_id", "id"]) ?? "—";
  const date = readLabel(record, ["movement_date"]) ?? "—";
  const origin = readLabel(record, ["origin_station_code"]) ?? "—";
  const dest = readLabel(record, ["destination_station_code"]) ?? "—";
  const commodity = readLabel(record, ["commodity"]) ?? "—";
  const tonnes = readLabel(record, ["load_tonnes"]);
  const entry = readLabel(record, ["planned_entry_time"]) ?? "—";
  const exit = readLabel(record, ["planned_exit_time"]) ?? "—";
  const priority = readLabel(record, ["traffic_priority"]) ?? "Medium";

  return (
    <tr
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onClick();
      }}
      className={cn(
        "cursor-pointer transition-colors hover:bg-rail-blue/[0.04]",
        selected && "bg-rail-blue/[0.07]",
      )}
    >
      <td className="px-4 py-3 font-mono text-[11px] font-semibold text-rail-blue">
        {freightId}
      </td>
      <td className="whitespace-nowrap px-4 py-3 font-mono text-[11px] text-rail-ink/60">
        {date}
      </td>
      <td className="px-4 py-3 font-mono text-[11px] font-medium">
        {origin} → {dest}
      </td>
      <td className="px-4 py-3">{commodity}</td>
      <td className="px-4 py-3 font-mono text-[11px] text-rail-ink/70">
        {tonnes ? `${Number(tonnes).toLocaleString()} T` : "—"}
      </td>
      <td className="whitespace-nowrap px-4 py-3 font-mono text-[11px] text-rail-ink/60">
        {entry} → {exit}
      </td>
      <td className="px-4 py-3">
        <StatusBadge value={priority} kind="priority" />
      </td>
    </tr>
  );
}

function FreightDetailPanel({
  record,
  loading,
  error,
  onClose,
}: {
  record: JsonRecord | null;
  loading: boolean;
  error: Error | null;
  onClose: () => void;
}) {
  return (
    <aside className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
      <PanelHeader
        eyebrow="FREIGHT PLANNING RECORD"
        title={record ? "Simulated Freight Movement" : "Select a freight train"}
        onClose={record ? onClose : undefined}
      />
      {error ? (
        <ErrorState message={apiErrorMessage(error, "The freight detail could not be loaded")} />
      ) : !record ? (
        <EmptyState
          label="Choose a freight movement from the list to inspect its planning parameters."
          compact
        />
      ) : loading ? (
        <DetailSkeleton />
      ) : (
        <div className="mt-5 space-y-4">
          <div className="rounded-md border border-amber-500/25 bg-amber-500/10 p-3 text-xs">
            <div className="font-mono text-[10px] font-bold tracking-[0.08em] text-amber-800">
              SYNTHETIC PLANNING SCENARIO
            </div>
            <p className="mt-1 text-amber-900/80">
              Domain-calibrated PlanRail planning scenario; not a real FOIS/NTES train record. Used for traffic pressure modeling & maintenance-block optimization.
            </p>
          </div>
          <DetailFields
            record={record}
            keys={[
              ["Freight Train ID", ["freight_train_id", "id"]],
              ["Movement Date", ["movement_date"]],
              ["Corridor", ["corridor"]],
              ["Origin Station", ["origin_station_code"]],
              ["Destination Station", ["destination_station_code"]],
              ["Commodity", ["commodity"]],
              ["Gross Tonnage", ["load_tonnes"]],
              ["Planned Entry", ["planned_entry_time"]],
              ["Planned Exit", ["planned_exit_time"]],
              ["Traffic Priority", ["traffic_priority"]],
              ["Data Status", ["data_status"]],
              ["Planning Use", ["planning_use"]],
              ["Source Basis", ["source_basis"]],
            ]}
          />
          {readLabel(record, ["simulation_note"]) && (
            <div className="rounded-md bg-rail-paper p-3 text-xs">
              <div className="font-mono text-[10px] tracking-[0.1em] text-rail-ink/45">SIMULATION NOTE</div>
              <p className="mt-1 text-rail-ink/75 leading-relaxed">{readLabel(record, ["simulation_note"])}</p>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}

function ScheduleTimeline({ schedule }: { schedule: JsonRecord[] }) {
  return (
    <div>
      <div className="flex items-center justify-between gap-3">
        <div className="font-mono text-[10px] tracking-[0.14em] text-rail-ink/45">SCHEDULE</div>
        <div className="font-mono text-[10px] text-rail-ink/35">
          {schedule.length ? `${schedule.length} STOPS` : "NO STOPS RETURNED"}
        </div>
      </div>
      {schedule.length ? (
        <div className="mt-3 space-y-0">
          {schedule.map((stop, index) => {
            const delay = readLabel(stop, [
              "delay",
              "delay_minutes",
              "delayMinutes",
              "delay_status",
            ]);
            return (
              <div
                key={`stop-${recordKey(stop, index)}`}
                className="relative flex gap-3 pb-4 last:pb-0"
              >
                <div className="flex w-4 shrink-0 flex-col items-center">
                  <span className="z-10 mt-1 size-2.5 rounded-full bg-rail-blue ring-4 ring-rail-blue/10" />
                  {index < schedule.length - 1 && (
                    <span className="absolute bottom-0 top-3 w-px bg-rail-blue/20" />
                  )}
                </div>
                <div className="min-w-0 flex-1 rounded-md border border-rail-ink/8 bg-rail-paper px-3 py-2 text-xs">
                  <div className="flex items-start justify-between gap-3">
                    <span className="font-semibold">
                      {readLabel(stop, [
                        "station",
                        "station_name",
                        "stationName",
                        "name",
                        "code",
                      ]) ?? "Stop"}
                    </span>
                    <span className="shrink-0 font-mono text-[10px] text-rail-ink/50">
                      {readLabel(stop, [
                        "arrival",
                        "arrival_time",
                        "arrivalTime",
                        "time",
                        "departure",
                        "departure_time",
                        "departureTime",
                      ]) ?? "—"}
                    </span>
                  </div>
                  {delay && (
                    <div className="mt-1 font-mono text-[10px] text-rail-amber">
                      DELAY · {delay}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState label="No schedule stops were returned for this train." compact />
      )}
    </div>
  );
}

function BlockTimelineRow({
  record,
  selected,
  bounds,
  onClick,
}: {
  record: JsonRecord;
  selected: boolean;
  bounds: TimelineBounds;
  onClick: () => void;
}) {
  const start = readLabel(record, ["start_time", "startTime", "start"]);
  const end = readLabel(record, ["end_time", "endTime", "end"]);
  const startDate = parseDate(start);
  const endDate = parseDate(end);
  const hasPosition = startDate !== null && endDate !== null && bounds.end > bounds.start;
  const left =
    hasPosition && startDate !== null
      ? Math.max(0, Math.min(100, ((startDate - bounds.start) / (bounds.end - bounds.start)) * 100))
      : 0;
  const width =
    hasPosition && startDate !== null && endDate !== null
      ? Math.max(
          4,
          Math.min(100 - left, ((endDate - startDate) / (bounds.end - bounds.start)) * 100),
        )
      : 0;
  const status = readLabel(record, ["status"]);
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "grid w-full grid-cols-[150px_minmax(0,1fr)] gap-5 px-2 py-3 text-left transition-colors hover:bg-rail-blue/[0.04]",
        selected && "bg-rail-blue/[0.07]",
      )}
    >
      <div className="min-w-0">
        <div className="truncate text-xs font-semibold">
          {readLabel(record, ["section", "section_id", "sectionId"]) ?? "Section unavailable"}
        </div>
        <div className="mt-1 flex items-center gap-1.5 font-mono text-[10px] text-rail-ink/45">
          <Clock3 className="size-3" />
          {start ?? "Start unavailable"}
        </div>
      </div>
      <div className="relative flex min-h-10 items-center rounded-sm bg-rail-ink/[0.04] px-2">
        {hasPosition ? (
          <span
            className={cn(
              "absolute inset-y-2 rounded-sm bg-rail-blue/80",
              toneClass(null, status).replace("bg-", "bg-"),
            )}
            style={{ left: `${left}%`, width: `${width}%` }}
          />
        ) : (
          <span className="font-mono text-[10px] text-rail-ink/35">TIMING UNAVAILABLE</span>
        )}
        <span className="relative ml-auto font-mono text-[10px] text-rail-ink/50">
          {end ?? "End unavailable"}
        </span>
      </div>
    </button>
  );
}

type BlockDecision = "approved" | "rejected";

function BlockDetailPanel({
  block,
  loading,
  error,
  decision,
  onDecision,
  onClose,
}: {
  block: JsonRecord | null;
  loading: boolean;
  error: Error | null;
  decision: BlockDecision | null;
  onDecision: (decision: BlockDecision) => void;
  onClose: () => void;
}) {
  const [pendingDecision, setPendingDecision] = useState<BlockDecision | null>(null);
  const tasks = block
    ? asRecords(readValue(block, ["tasks", "associated_tasks", "associatedTasks"]))
    : [];
  const id = block ? (blockId(block) ?? "Block ID unavailable") : null;
  const section = block
    ? readLabel(block, ["section", "section_id", "sectionId"])
    : null;
  const start = block ? readLabel(block, ["start_time", "startTime", "start"]) : null;
  const end = block ? readLabel(block, ["end_time", "endTime", "end"]) : null;
  const startMs = parseDate(start);
  const endMs = parseDate(end);
  const durationMinutes =
    startMs !== null && endMs !== null && endMs > startMs
      ? Math.round((endMs - startMs) / 60000)
      : null;
  const status = block ? readLabel(block, ["status"]) : null;
  const impactParts = [
    durationMinutes !== null
      ? `Occupies the section for ${durationMinutes} minute${durationMinutes === 1 ? "" : "s"}.`
      : null,
    tasks.length
      ? `${tasks.length} associated task${tasks.length === 1 ? "" : "s"} returned by the backend.`
      : null,
    status ? `Current status: ${status}.` : null,
  ].filter((part): part is string => part !== null);
  return (
    <aside className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
      <PanelHeader
        eyebrow="BLOCK DETAIL"
        title={block ? "Full API response" : "Select a block"}
        onClose={block ? onClose : undefined}
      />
      {error ? (
        <ErrorState message={apiErrorMessage(error, "The block detail could not be loaded")} />
      ) : !block ? (
        <EmptyState
          label="Choose a block to inspect its full response and returned tasks."
          compact
        />
      ) : loading ? (
        <DetailSkeleton />
      ) : (
        <div className="mt-5 space-y-5">
          <DetailFields record={block} />
          <div>
            <div className="font-mono text-[10px] tracking-[0.14em] text-rail-ink/45">
              ASSOCIATED TASKS
            </div>
            {tasks.length ? (
              <div className="mt-3 space-y-2">
                {tasks.map((task, index) => (
                  <div
                    key={recordKey(task, index)}
                    className="rounded-md border border-rail-ink/8 bg-rail-paper p-3 text-xs"
                  >
                    {readLabel(task, ["task_id", "taskId", "id", "name"]) ?? formatValue(task)}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState label="No associated tasks were returned for this block." compact />
            )}
          </div>
          <div className="rounded-md border border-rail-ink/10 bg-rail-paper p-3.5">
            <div className="flex items-center justify-between gap-3">
              <div className="font-mono text-[10px] tracking-[0.14em] text-rail-ink/45">
                BLOCK DECISION
              </div>
              <span className="font-mono text-[9px] tracking-[0.08em] text-rail-amber">
                DEMO · LOCAL ONLY
              </span>
            </div>
            {decision ? (
              <div
                className={cn(
                  "mt-3 flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-semibold",
                  decision === "approved"
                    ? "border-rail-green/25 bg-rail-green/10 text-rail-green"
                    : "border-rail-red/25 bg-rail-red/10 text-rail-red",
                )}
              >
                {decision === "approved" ? <Check className="size-4" /> : <X className="size-4" />}
                {decision === "approved" ? "Approved" : "Rejected"} — demo interaction, no approval
                API exists yet
              </div>
            ) : (
              <div className="mt-3 flex gap-2">
                <Button
                  size="sm"
                  className="flex-1 bg-rail-green text-rail-paper hover:bg-rail-green/90"
                  onClick={() => setPendingDecision("approved")}
                >
                  <Check /> Approve
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 border-rail-red/30 text-rail-red hover:bg-rail-red/10"
                  onClick={() => setPendingDecision("rejected")}
                >
                  <X /> Reject
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
      <Dialog
        open={pendingDecision !== null}
        onOpenChange={(open) => {
          if (!open) setPendingDecision(null);
        }}
      >
        <DialogContent className="border-rail-ink/10 bg-rail-panel text-rail-ink">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {pendingDecision === "approved" ? (
                <Check className="size-5 text-rail-green" />
              ) : (
                <X className="size-5 text-rail-red" />
              )}
              {pendingDecision === "approved" ? "Approve block" : "Reject block"}
            </DialogTitle>
            <DialogDescription className="pt-1 text-rail-ink/60">
              Demo interaction — no approval API currently exists. The status updates locally only.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2.5 text-xs">
            <div className="grid grid-cols-[110px_1fr] gap-3 border-b border-rail-ink/8 pb-2.5">
              <span className="text-rail-ink/45">Block ID</span>
              <span className="font-mono font-semibold">{id ?? "—"}</span>
            </div>
            <div className="grid grid-cols-[110px_1fr] gap-3 border-b border-rail-ink/8 pb-2.5">
              <span className="text-rail-ink/45">Section</span>
              <span className="font-medium">{section ?? "Section unavailable"}</span>
            </div>
            <div className="grid grid-cols-[110px_1fr] gap-3 border-b border-rail-ink/8 pb-2.5">
              <span className="text-rail-ink/45">Time window</span>
              <span className="font-medium">
                {start ?? "Start unavailable"} → {end ?? "End unavailable"}
              </span>
            </div>
            <div className="grid grid-cols-[110px_1fr] gap-3">
              <span className="text-rail-ink/45">Impact</span>
              <span className="font-medium leading-relaxed">
                {impactParts.length
                  ? impactParts.join(" ")
                  : "No impact fields were returned for this block."}
              </span>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPendingDecision(null)}>
              Cancel
            </Button>
            <Button
              className={cn(
                "text-rail-paper",
                pendingDecision === "approved"
                  ? "bg-rail-green hover:bg-rail-green/90"
                  : "bg-rail-red hover:bg-rail-red/90",
              )}
              onClick={() => {
                if (pendingDecision) onDecision(pendingDecision);
                setPendingDecision(null);
              }}
            >
              Confirm {pendingDecision === "approved" ? "approval" : "rejection"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </aside>
  );
}

type TimelineBounds = {
  start: number;
  end: number;
  labelStart: string;
  labelMid: string;
  labelEnd: string;
};

function timelineBounds(records: JsonRecord[]): TimelineBounds {
  const dates = records
    .flatMap((record) => [
      parseDate(readLabel(record, ["start_time", "startTime", "start"])),
      parseDate(readLabel(record, ["end_time", "endTime", "end"])),
    ])
    .filter((value): value is number => value !== null);
  if (!dates.length)
    return {
      start: 0,
      end: 1,
      labelStart: "Start time unavailable",
      labelMid: "—",
      labelEnd: "End time unavailable",
    };
  const start = Math.min(...dates);
  const end = Math.max(...dates, start + 60 * 60 * 1000);
  return {
    start,
    end,
    labelStart: formatDateTime(start),
    labelMid: formatDateTime(start + (end - start) / 2),
    labelEnd: formatDateTime(end),
  };
}

function parseDate(value: string | null): number | null {
  if (!value) return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatDateTime(value: number) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(value);
}

function trainKey(record: JsonRecord, index: number) {
  return readLabel(record, ["train_number", "trainNumber", "number", "id"]) ?? `train-${index}`;
}

function blockId(record: JsonRecord) {
  return readLabel(record, ["block_id", "blockId", "id"]);
}

function blockKey(record: JsonRecord, index: number) {
  return blockId(record) ?? `block-${index}`;
}

function TableSkeleton() {
  return (
    <div className="rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8">
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((item) => (
          <Skeleton key={item} className="h-12 bg-rail-ink/8" />
        ))}
      </div>
    </div>
  );
}

function BlockSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
      <Skeleton className="h-[500px] bg-rail-ink/8" />
      <Skeleton className="h-[420px] bg-rail-ink/8" />
    </div>
  );
}

function SectionRow({
  record,
  selected,
  onClick,
}: {
  record: JsonRecord;
  selected: boolean;
  onClick: () => void;
}) {
  const risk = readNumber(record, ["risk_score", "riskScore", "risk"]);
  const status = readText(record, [
    "status",
    "traffic_level",
    "trafficLevel",
    "risk_level",
    "riskLevel",
  ]);
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition-colors hover:bg-rail-blue/[0.04]",
        selected && "bg-rail-blue/[0.07]",
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <span className={cn("size-2 shrink-0 rounded-full", toneClass(risk, status))} />
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold">
            {readLabel(record, ["section_id", "sectionId", "id"]) ?? "Section ID unavailable"}
          </div>
          <div className="mt-0.5 truncate text-xs text-rail-ink/50">
            {readLabel(record, ["start_station", "startStation", "from"]) ??
              "Start station unavailable"}{" "}
            → {readLabel(record, ["end_station", "endStation", "to"]) ?? "End station unavailable"}
          </div>
        </div>
      </div>
      <ChevronRight
        className={cn("size-4 shrink-0 text-rail-ink/25", selected && "text-rail-blue")}
      />
    </button>
  );
}

function NetworkDetailPanel({
  section,
  loading,
  error,
  assets,
  onClose,
}: {
  section: JsonRecord | null;
  loading: boolean;
  error: Error | null;
  assets: JsonRecord[];
  onClose: () => void;
}) {
  return (
    <aside className="rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
      <PanelHeader
        eyebrow="SECTION DETAIL"
        title={section ? "Selected section" : "Select a section"}
        onClose={section ? onClose : undefined}
      />
      {error ? (
        <ErrorState message={apiErrorMessage(error, "The section detail could not be loaded")} />
      ) : !section ? (
        <EmptyState
          label="Choose a section from the list or map to inspect its returned fields."
          compact
        />
      ) : loading ? (
        <DetailSkeleton />
      ) : (
        <div className="mt-5 space-y-5">
          <DetailFields
            record={section}
            keys={[
              ["Section ID", ["section_id", "sectionId", "id"]],
              ["Start station", ["start_station", "startStation", "from"]],
              ["End station", ["end_station", "endStation", "to"]],
              ["Distance", ["distance", "distance_km", "distanceKm"]],
              ["Traffic level", ["traffic_level", "trafficLevel"]],
              ["Risk score", ["risk_score", "riskScore", "risk"]],
            ]}
          />
          <div>
            <div className="font-mono text-[10px] tracking-[0.14em] text-rail-ink/45">
              ASSOCIATED ASSETS
            </div>
            {assets.length ? (
              <div className="mt-3 space-y-2">
                {assets.map((asset, index) => (
                  <div
                    key={recordKey(asset, index)}
                    className="rounded-md border border-rail-ink/8 bg-rail-paper p-3 text-xs"
                  >
                    {readLabel(asset, ["asset_id", "assetId", "id", "name"]) ?? "Asset record"}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState label="No assets returned for this section." compact />
            )}
          </div>
        </div>
      )}
    </aside>
  );
}

function MaintenanceRow({
  record,
  selected,
  onClick,
}: {
  record: JsonRecord;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <tr
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onClick();
      }}
      className={cn(
        "cursor-pointer transition-colors hover:bg-rail-blue/[0.04]",
        selected && "bg-rail-blue/[0.07]",
      )}
    >
      <td className="px-4 py-3 font-mono text-[11px] font-semibold">
        {readLabel(record, ["task_id", "taskId", "request_id", "requestId", "id"]) ?? "—"}
      </td>
      <td className="px-4 py-3">
        {readLabel(record, ["department", "department_name", "departmentName"]) ?? "—"}
      </td>
      <td className="px-4 py-3">
        {readLabel(record, ["section", "section_id", "sectionId"]) ?? "—"}
      </td>
      <td className="px-4 py-3">
        <StatusBadge value={readLabel(record, ["severity"])} kind="severity" />
      </td>
      <td className="px-4 py-3">
        <StatusBadge value={readLabel(record, ["priority"])} kind="priority" />
      </td>
      <td className="px-4 py-3">
        <StatusBadge
          value={readLabel(record, ["risk", "risk_level", "riskLevel", "risk_score", "riskScore"])}
          kind="risk"
        />
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-rail-ink/60">
        {readLabel(record, ["due_date", "dueDate", "due"]) ?? "—"}
      </td>
      <td className="px-4 py-3">{readLabel(record, ["status"]) ?? "—"}</td>
    </tr>
  );
}

function MaintenanceDetailPanel({
  record,
  loading,
  error,
  onClose,
}: {
  record: JsonRecord | null;
  loading: boolean;
  error: Error | null;
  onClose: () => void;
}) {
  const reqId = record ? (readText(record, ["request_id", "id", "task_id"]) ?? "") : "";

  const aiQuery = useQuery({
    queryKey: ["planrail", "ai", "predict", reqId],
    queryFn: () => api.predict({ request_id: reqId }),
    enabled: Boolean(reqId),
    retry: false,
  });

  const aiData = aiQuery.data?.status === 200 ? aiQuery.data.data : null;

  return (
    <aside className="space-y-4 rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8 xl:sticky xl:top-20 xl:h-fit">
      <PanelHeader
        eyebrow="REQUEST DETAIL & AI EVALUATION"
        title={record ? `Request ${reqId}` : "Select a request"}
        onClose={record ? onClose : undefined}
      />
      {error ? (
        <ErrorState
          message={apiErrorMessage(error, "The maintenance detail could not be loaded")}
        />
      ) : !record ? (
        <EmptyState
          label="Select a maintenance row to inspect the full returned response."
          compact
        />
      ) : loading ? (
        <DetailSkeleton />
      ) : (
        <>
          {/* AI Decision Support Analysis */}
          {reqId && (
            <div className="rounded-lg border border-rail-blue/30 bg-rail-blue/[0.04] p-3.5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 font-mono text-[10px] font-bold tracking-[0.1em] text-rail-blue">
                  <BrainCircuit className="size-3.5" /> AI PREDICTION &amp; RISK
                </div>
                {aiData?.model_status && (
                  <Badge variant="outline" className="font-mono text-[9px] border-rail-blue/30 text-rail-blue">
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
                    <div className="rounded bg-rail-paper p-2 border border-rail-ink/8">
                      <div className="font-mono text-[9px] text-rail-ink/45">PREDICTED RISK</div>
                      <div className="mt-0.5 text-sm font-bold text-rail-amber">
                        {aiData.risk_score.toFixed(1)} <span className="text-[10px] font-normal text-rail-ink/40">({aiData.risk_category})</span>
                      </div>
                    </div>
                    <div className="rounded bg-rail-paper p-2 border border-rail-ink/8">
                      <div className="font-mono text-[9px] text-rail-ink/45">PRIORITY SCORE</div>
                      <div className="mt-0.5 text-sm font-bold text-rail-blue">
                        {aiData.priority_score.toFixed(1)} <span className="text-[10px] font-normal text-rail-ink/40">({aiData.priority_category})</span>
                      </div>
                    </div>
                  </div>

                  {aiData.risk_contributing_factors && aiData.risk_contributing_factors.length > 0 && (
                    <div className="space-y-1">
                      <div className="font-mono text-[9px] font-semibold text-rail-ink/50">TOP RISK DRIVERS:</div>
                      {aiData.risk_contributing_factors.slice(0, 2).map((factor, idx) => (
                        <div key={idx} className="flex items-start gap-1.5 text-[11px] text-rail-ink/75">
                          <ShieldAlert className="mt-0.5 size-3 shrink-0 text-rail-amber" />
                          <span className="leading-tight">{factor}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {aiData.explanation && (
                    <p className="text-[11px] leading-relaxed text-rail-ink/70 border-t border-rail-ink/8 pt-2">
                      {aiData.explanation}
                    </p>
                  )}
                </div>
              ) : (
                <div className="text-xs text-rail-ink/50">Click Analyze on AI Insights for full deep-dive.</div>
              )}
            </div>
          )}

          <div className="font-mono text-[10px] font-semibold tracking-[0.1em] text-rail-ink/40 pt-1">
            RECORD ATTRIBUTES
          </div>
          <DetailFields record={record} />
        </>
      )}
    </aside>
  );
}

function DetailFields({
  record,
  keys,
}: {
  record: JsonRecord;
  keys?: Array<[string, readonly string[]]>;
}) {
  const entries = keys
    ? keys
        .map(([label, fieldKeys]) => [label, scalar(record, fieldKeys)] as const)
        .filter(([, value]) => value !== null)
    : Object.entries(record).map(([key, value]) => [formatKey(key), formatValue(value)] as const);
  return entries.length ? (
    <div className="space-y-3">
      {entries.map(([label, value]) => (
        <div
          key={label}
          className="grid grid-cols-[minmax(0,42%)_1fr] gap-3 border-b border-rail-ink/8 pb-3 text-xs"
        >
          <dt className="text-rail-ink/45">{label}</dt>
          <dd className="break-words font-medium text-rail-ink/80">{value}</dd>
        </div>
      ))}
    </div>
  ) : (
    <EmptyState label="The response contained no displayable fields." compact />
  );
}

function PanelHeader({
  eyebrow,
  title,
  onClose,
}: {
  eyebrow: string;
  title: string;
  onClose?: (() => void) | undefined;
}) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div>
        <div className="flex items-center gap-2 font-mono text-[10px] tracking-[0.15em] text-rail-ink/45">
          <PanelRight className="size-3.5 text-rail-blue" />
          {eyebrow}
        </div>
        <div className="mt-1 text-sm font-semibold">{title}</div>
      </div>
      {onClose && (
        <Button variant="ghost" size="icon" aria-label="Close detail panel" onClick={onClose}>
          <ChevronRight className="rotate-180" />
        </Button>
      )}
    </div>
  );
}

function FilterSelect({
  label,
  value,
  values,
  onValueChange,
}: {
  label: string;
  value: string;
  values: string[];
  onValueChange: (value: string) => void;
}) {
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger
        aria-label={`Filter by ${label}`}
        className="w-auto min-w-28 bg-rail-paper text-xs"
      >
        <SelectValue placeholder={label} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All {label}</SelectItem>
        {values.map((item) => (
          <SelectItem key={item} value={item}>
            {item}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function StatusBadge({
  value,
  kind,
}: {
  value: string | null;
  kind: "severity" | "priority" | "risk";
}) {
  const tone = value?.toLowerCase() ?? "";
  const className =
    kind === "risk" || tone.includes("critical") || tone.includes("high")
      ? "border-rail-red/20 bg-rail-red/10 text-rail-red"
      : tone.includes("medium") || tone.includes("amber")
        ? "border-rail-amber/25 bg-rail-amber/10 text-rail-amber"
        : "border-rail-green/20 bg-rail-green/10 text-rail-green";
  return <Badge className={cn("border text-[10px] uppercase", className)}>{value ?? "—"}</Badge>;
}

function NetworkNode({ label, muted = false }: { label: string; muted?: boolean }) {
  return (
    <div className="relative z-10 flex max-w-28 flex-col items-center gap-2 text-center">
      <span
        className={cn(
          "size-3 rounded-full border-2 border-rail-map bg-rail-blue",
          muted && "bg-rail-ink/25",
        )}
      />
      <span className="font-mono text-[9px] text-rail-ink/55">{label}</span>
    </div>
  );
}
function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-[14px] border border-dashed border-rail-red/30 bg-rail-panel p-6 text-center">
      <CircleDot className="size-5 text-rail-red" />
      <p className="text-sm text-rail-ink/60">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="size-3.5" />
          Retry feed
        </Button>
      )}
    </div>
  );
}
function NetworkSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-4 rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8">
        <Skeleton className="h-8 w-48 bg-rail-ink/8" />
        <Skeleton className="h-[420px] w-full bg-rail-ink/8" />
        <div className="grid grid-cols-3 gap-2">
          {[1, 2, 3].map((item) => <Skeleton key={item} className="h-5 bg-rail-ink/8" />)}
        </div>
      </div>
      <div className="space-y-4 rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
        <Skeleton className="h-8 w-40 bg-rail-ink/8" />
        {[1, 2, 3, 4, 5].map((item) => <Skeleton key={item} className="h-8 bg-rail-ink/8" />)}
      </div>
    </div>
  );
}
function MaintenanceSkeleton() {
  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-3 rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8">
        <Skeleton className="h-9 w-full bg-rail-ink/8" />
        {[1, 2, 3, 4, 5, 6].map((item) => <Skeleton key={item} className="h-11 bg-rail-ink/8" />)}
      </div>
      <div className="space-y-4 rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8">
        <Skeleton className="h-8 w-40 bg-rail-ink/8" />
        {[1, 2, 3, 4].map((item) => <Skeleton key={item} className="h-8 bg-rail-ink/8" />)}
      </div>
    </div>
  );
}
function DetailSkeleton() {
  return (
    <div className="mt-5 space-y-4">
      {[1, 2, 3, 4, 5].map((item) => (
        <Skeleton key={item} className="h-8 bg-rail-ink/8" />
      ))}
    </div>
  );
}

function recordId(record: JsonRecord) {
  return readLabel(record, [
    "section_id",
    "sectionId",
    "request_id",
    "requestId",
    "task_id",
    "taskId",
    "id",
  ]);
}
function recordKey(record: JsonRecord, index: number) {
  return recordId(record) ?? `record-${index}`;
}
function readLabel(record: JsonRecord, keys: readonly string[]) {
  const value = scalar(record, keys);
  return value === null ? null : value;
}
function scalar(record: JsonRecord | null | undefined, keys: readonly string[]) {
  const value = readValue(record, keys);
  if (typeof value === "string" && value.trim()) return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return null;
}
function formatKey(key: string) {
  return key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
function coordinates(record: JsonRecord) {
  const lat = readNumber(record, ["latitude", "lat", "start_latitude", "startLatitude"]);
  const lng = readNumber(record, ["longitude", "lng", "lon", "start_longitude", "startLongitude"]);
  return lat !== null && lng !== null ? ([lat, lng] as [number, number]) : null;
}
function assetSectionId(record: JsonRecord) {
  const value = readValue(record, ["section_id", "sectionId", "section"]);
  if (isRecord(value)) return recordId(value);
  if (typeof value === "number" || typeof value === "string") return String(value);
  return null;
}
function toneClass(risk: number | null, status: string | null) {
  const text = status?.toLowerCase() ?? "";
  if ((risk !== null && risk >= 70) || text.includes("critical") || text.includes("high"))
    return "bg-rail-red";
  if ((risk !== null && risk >= 40) || text.includes("medium") || text.includes("amber"))
    return "bg-rail-amber";
  return "bg-rail-green";
}
function filterValues(records: JsonRecord[], keys: readonly string[]) {
  return [
    ...new Set(
      records
        .map((record) => readLabel(record, keys))
        .filter((value): value is string => value !== null),
    ),
  ].sort();
}
function matches(record: JsonRecord, keys: readonly string[], filter: string) {
  return filter === "all" || readLabel(record, keys) === filter;
}
