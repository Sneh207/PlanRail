import { createFileRoute } from "@tanstack/react-router";

import { AdminDashboardPage } from "@/components/admin-dashboard";

export const Route = createFileRoute("/admin-dashboard")({
  head: () => ({
    meta: [
      { title: "PlanRail — System Administration" },
      { name: "description", content: "Corridor infrastructure inventory, operational parameters and system health." },
      { property: "og:title", content: "PlanRail — System Administration" },
      { property: "og:description", content: "Corridor infrastructure inventory, operational parameters and system health." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: AdminDashboardPage,
});
