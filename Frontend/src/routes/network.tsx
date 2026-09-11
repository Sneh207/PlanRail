import { createFileRoute } from "@tanstack/react-router";
import { RailwayNetworkPage } from "@/components/operations-pages";

export const Route = createFileRoute("/network")({
  head: () => ({ meta: [{ title: "PlanRail — Railway Network" }, { name: "description", content: "Inspect the Delhi–Agra corridor railway network." }, { property: "og:title", content: "PlanRail — Railway Network" }, { property: "og:description", content: "Inspect the Delhi–Agra corridor railway network." }, { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" }] }),
  component: RailwayNetworkPage,
});