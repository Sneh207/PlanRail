import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { c as HeadContent, d as createRouter, f as Outlet, g as Link, h as createRootRouteWithContext, m as createFileRoute, p as lazyRouteComponent, s as Scripts, v as useRouter } from "../_libs/@tanstack/react-router+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { n as QueryClientProvider } from "../_libs/tanstack__react-query.mjs";
import { t as QueryClient } from "../_libs/tanstack__query-core.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/router-Dos_LVEm.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var styles_default = "/assets/styles-D2B2RA4K.css";
function reportLovableError(error, context = {}) {
	if (typeof window === "undefined") return;
	window.__lovableEvents?.captureException?.(error, {
		source: "react_error_boundary",
		route: window.location.pathname,
		...context
	}, {
		mechanism: "react_error_boundary",
		handled: false,
		severity: "error"
	});
	const message = error instanceof Response ? `Response ${error.status}${error.url ? ` at ${error.url}` : ""}` : error instanceof Error ? error.message : String(error);
	const stack = error instanceof Error ? error.stack : void 0;
	window.__lovableReportRuntimeError?.({
		message,
		...stack !== void 0 && { stack },
		filename: window.location.pathname
	});
}
function NotFoundComponent() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-7xl font-bold text-foreground",
					children: "404"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "mt-4 text-xl font-semibold text-foreground",
					children: "Page not found"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "The page you're looking for doesn't exist or has been moved."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-6",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/",
						className: "inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90",
						children: "Go home"
					})
				})
			]
		})
	});
}
function ErrorComponent({ error, reset }) {
	console.error(error);
	const router = useRouter();
	(0, import_react.useEffect)(() => {
		reportLovableError(error, { boundary: "tanstack_root_error_component" });
	}, [error]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "flex min-h-screen items-center justify-center bg-background px-4",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "max-w-md text-center",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "text-xl font-semibold tracking-tight text-foreground",
					children: "This page didn't load"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm text-muted-foreground",
					children: "Something went wrong on our end. You can try refreshing or head back home."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-6 flex flex-wrap justify-center gap-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						onClick: () => {
							router.invalidate();
							reset();
						},
						className: "inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90",
						children: "Try again"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
						href: "/",
						className: "inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent",
						children: "Go home"
					})]
				})
			]
		})
	});
}
var Route$7 = createRootRouteWithContext()({
	head: () => ({
		meta: [
			{ charSet: "utf-8" },
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1"
			},
			{ title: "PlanRail — Corridor Operations" },
			{
				name: "description",
				content: "PlanRail railway operations control center for the Delhi–Agra corridor."
			},
			{
				name: "author",
				content: "Lovable"
			},
			{
				property: "og:title",
				content: "PlanRail — Corridor Operations"
			},
			{
				property: "og:description",
				content: "PlanRail railway operations control center for the Delhi–Agra corridor."
			},
			{
				property: "og:type",
				content: "website"
			},
			{
				name: "twitter:card",
				content: "summary_large_image"
			},
			{
				name: "twitter:site",
				content: "@Lovable"
			}
		],
		links: [{
			rel: "stylesheet",
			href: styles_default
		}, {
			rel: "icon",
			href: "/favicon.ico",
			type: "image/x-icon"
		}]
	}),
	shellComponent: RootShell,
	component: RootComponent,
	notFoundComponent: NotFoundComponent,
	errorComponent: ErrorComponent
});
function RootShell({ children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("html", {
		lang: "en",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("head", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HeadContent, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("body", { children: [children, /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Scripts, {})] })]
	});
}
function RootComponent() {
	const { queryClient } = Route$7.useRouteContext();
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(QueryClientProvider, {
		client: queryClient,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {})
	});
}
var $$splitComponentImporter$6 = () => import("./routes-CawK7yin.mjs");
var Route$6 = createFileRoute("/")({
	head: () => ({ meta: [
		{ title: "PlanRail — Demo Access" },
		{
			name: "description",
			content: "Enter the PlanRail demo dashboard for Delhi–Agra corridor operations."
		},
		{
			property: "og:title",
			content: "PlanRail — Demo Access"
		},
		{
			property: "og:description",
			content: "Enter the PlanRail demo dashboard for Delhi–Agra corridor operations."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$6, "component")
});
var $$splitComponentImporter$5 = () => import("./blocks-NGN2Jz-d.mjs");
var Route$5 = createFileRoute("/blocks")({
	head: () => ({ meta: [
		{ title: "PlanRail — Block Planning" },
		{
			name: "description",
			content: "Review existing railway blocks and planning windows across the Delhi–Agra corridor."
		},
		{
			property: "og:title",
			content: "PlanRail — Block Planning"
		},
		{
			property: "og:description",
			content: "Review existing railway blocks and planning windows across the Delhi–Agra corridor."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$5, "component")
});
var $$splitComponentImporter$4 = () => import("./dashboard-CYgx0Er_.mjs");
var Route$4 = createFileRoute("/dashboard")({
	head: () => ({ meta: [
		{ title: "PlanRail — Dashboard" },
		{
			name: "description",
			content: "Live Delhi–Agra railway corridor operations dashboard."
		},
		{
			property: "og:title",
			content: "PlanRail — Dashboard"
		},
		{
			property: "og:description",
			content: "Live Delhi–Agra railway corridor operations dashboard."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$4, "component")
});
var $$splitComponentImporter$3 = () => import("./insights-wYxbLQTo.mjs");
var Route$3 = createFileRoute("/insights")({
	head: () => ({ meta: [
		{ title: "PlanRail — AI Insights" },
		{
			name: "description",
			content: "Review risk, priority, and department distributions plus AI recommendations for the Delhi–Agra corridor."
		},
		{
			property: "og:title",
			content: "PlanRail — AI Insights"
		},
		{
			property: "og:description",
			content: "Review risk, priority, and department distributions plus AI recommendations for the Delhi–Agra corridor."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$3, "component")
});
var $$splitComponentImporter$2 = () => import("./maintenance-DWylWlm2.mjs");
var Route$2 = createFileRoute("/maintenance")({
	head: () => ({ meta: [
		{ title: "PlanRail — Maintenance" },
		{
			name: "description",
			content: "Review maintenance posture across the Delhi–Agra corridor."
		},
		{
			property: "og:title",
			content: "PlanRail — Maintenance"
		},
		{
			property: "og:description",
			content: "Review maintenance posture across the Delhi–Agra corridor."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$2, "component")
});
var $$splitComponentImporter$1 = () => import("./network-zfZNKum2.mjs");
var Route$1 = createFileRoute("/network")({
	head: () => ({ meta: [
		{ title: "PlanRail — Railway Network" },
		{
			name: "description",
			content: "Inspect the Delhi–Agra corridor railway network."
		},
		{
			property: "og:title",
			content: "PlanRail — Railway Network"
		},
		{
			property: "og:description",
			content: "Inspect the Delhi–Agra corridor railway network."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter$1, "component")
});
var $$splitComponentImporter = () => import("./trains-BGwUUzJE.mjs");
var Route = createFileRoute("/trains")({
	head: () => ({ meta: [
		{ title: "PlanRail — Trains" },
		{
			name: "description",
			content: "Search train services and schedules across the Delhi–Agra corridor."
		},
		{
			property: "og:title",
			content: "PlanRail — Trains"
		},
		{
			property: "og:description",
			content: "Search train services and schedules across the Delhi–Agra corridor."
		},
		{
			property: "og:type",
			content: "website"
		},
		{
			name: "twitter:card",
			content: "summary_large_image"
		}
	] }),
	component: lazyRouteComponent($$splitComponentImporter, "component")
});
var rootRouteChildren = {
	IndexRoute: Route$6.update({
		id: "/",
		path: "/",
		getParentRoute: () => Route$7
	}),
	BlocksRoute: Route$5.update({
		id: "/blocks",
		path: "/blocks",
		getParentRoute: () => Route$7
	}),
	DashboardRoute: Route$4.update({
		id: "/dashboard",
		path: "/dashboard",
		getParentRoute: () => Route$7
	}),
	InsightsRoute: Route$3.update({
		id: "/insights",
		path: "/insights",
		getParentRoute: () => Route$7
	}),
	MaintenanceRoute: Route$2.update({
		id: "/maintenance",
		path: "/maintenance",
		getParentRoute: () => Route$7
	}),
	NetworkRoute: Route$1.update({
		id: "/network",
		path: "/network",
		getParentRoute: () => Route$7
	}),
	TrainsRoute: Route.update({
		id: "/trains",
		path: "/trains",
		getParentRoute: () => Route$7
	})
};
var routeTree = Route$7._addFileChildren(rootRouteChildren)._addFileTypes();
var getRouter = () => {
	const queryClient = new QueryClient();
	return createRouter({
		routeTree,
		context: { queryClient },
		scrollRestoration: true,
		defaultPreloadStaleTime: 0
	});
};
//#endregion
export { getRouter };
