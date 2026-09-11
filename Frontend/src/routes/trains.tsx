import { createFileRoute } from "@tanstack/react-router";
import { TrainsPage } from "@/components/operations-pages";

export const Route = createFileRoute("/trains")({
  head: () => ({
    meta: [
      { title: "PlanRail — Trains" },
      {
        name: "description",
        content: "Search train services and schedules across the Delhi–Agra corridor.",
      },
      { property: "og:title", content: "PlanRail — Trains" },
      {
        property: "og:description",
        content: "Search train services and schedules across the Delhi–Agra corridor.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: TrainsPage,
});
