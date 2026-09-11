import { createFileRoute } from "@tanstack/react-router";

import { DashboardPage, PlanRailShell } from "@/components/planrail";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "PlanRail — Dashboard" }, { name: "description", content: "Live Delhi–Agra railway corridor operations dashboard." }, { property: "og:title", content: "PlanRail — Dashboard" }, { property: "og:description", content: "Live Delhi–Agra railway corridor operations dashboard." }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: () => <PlanRailShell><DashboardPage /></PlanRailShell>,
});