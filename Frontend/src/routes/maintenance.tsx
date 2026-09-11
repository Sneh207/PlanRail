import { createFileRoute } from "@tanstack/react-router";
import { MaintenancePage } from "@/components/operations-pages";

export const Route = createFileRoute("/maintenance")({
  head: () => ({ meta: [{ title: "PlanRail — Maintenance" }, { name: "description", content: "Review maintenance posture across the Delhi–Agra corridor." }, { property: "og:title", content: "PlanRail — Maintenance" }, { property: "og:description", content: "Review maintenance posture across the Delhi–Agra corridor." }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: MaintenancePage,
});