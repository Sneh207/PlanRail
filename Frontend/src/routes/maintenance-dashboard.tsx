import { createFileRoute } from "@tanstack/react-router";

import { MaintenanceDashboardPage } from "@/components/maintenance-dashboard";

export const Route = createFileRoute("/maintenance-dashboard")({
  head: () => ({
    meta: [
      { title: "PlanRail — Maintenance Operations" },
      { name: "description", content: "Field maintenance workload, asset condition inspections, and task readiness." },
      { property: "og:title", content: "PlanRail — Maintenance Operations" },
      { property: "og:description", content: "Field maintenance workload, asset condition inspections, and task readiness." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: MaintenanceDashboardPage,
});
