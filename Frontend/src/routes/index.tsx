import { createFileRoute } from "@tanstack/react-router";

import { DemoLogin } from "@/components/planrail";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PlanRail — Demo Access" },
      { name: "description", content: "Enter the PlanRail demo dashboard for Delhi–Agra corridor operations." },
      { property: "og:title", content: "PlanRail — Demo Access" },
      { property: "og:description", content: "Enter the PlanRail demo dashboard for Delhi–Agra corridor operations." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: DemoLogin,
});