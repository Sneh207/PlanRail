import { createFileRoute } from "@tanstack/react-router";
import { AIInsightsPage } from "@/components/insights-page";

export const Route = createFileRoute("/insights")({
  head: () => ({
    meta: [
      { title: "PlanRail — AI Insights" },
      {
        name: "description",
        content:
          "Review risk, priority, and department distributions plus AI recommendations for the Delhi–Agra corridor.",
      },
      { property: "og:title", content: "PlanRail — AI Insights" },
      {
        property: "og:description",
        content:
          "Review risk, priority, and department distributions plus AI recommendations for the Delhi–Agra corridor.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: AIInsightsPage,
});
