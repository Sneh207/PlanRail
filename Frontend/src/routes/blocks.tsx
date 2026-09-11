import { createFileRoute } from "@tanstack/react-router";
import { BlockPlanningPage } from "@/components/operations-pages";

export const Route = createFileRoute("/blocks")({
  head: () => ({
    meta: [
      { title: "PlanRail — Block Planning" },
      {
        name: "description",
        content:
          "Review existing railway blocks and planning windows across the Delhi–Agra corridor.",
      },
      { property: "og:title", content: "PlanRail — Block Planning" },
      {
        property: "og:description",
        content:
          "Review existing railway blocks and planning windows across the Delhi–Agra corridor.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: BlockPlanningPage,
});
