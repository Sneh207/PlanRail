import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { _ as useNavigate, g as Link, l as useLocation } from "../_libs/@tanstack/react-router+[...].mjs";
import { o as require_jsx_runtime, r as Slot } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { t as useQuery } from "../_libs/tanstack__react-query.mjs";
import { D as Boxes, E as BrainCircuit, O as Activity, _ as Gauge, b as CircleDot, d as PanelLeftClose, f as Network, g as LayoutDashboard, h as LogOut, i as TrainFront, n as Wrench, o as ShieldAlert, p as Menu, r as TriangleAlert, t as X, u as PanelLeftOpen, y as ClipboardList } from "../_libs/lucide-react.mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
import { t as axios } from "../_libs/axios+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/planrail-C-ZDaIgs.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium cursor-pointer transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0", {
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
			destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
			outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
			secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
			ghost: "hover:bg-accent hover:text-accent-foreground",
			link: "text-primary underline-offset-4 hover:underline"
		},
		size: {
			default: "h-9 px-4 py-2",
			sm: "h-8 rounded-md px-3 text-xs",
			lg: "h-10 rounded-md px-8",
			icon: "h-9 w-9"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		ref,
		...props
	});
});
Button.displayName = "Button";
function Skeleton({ className, ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: cn("animate-pulse rounded-md bg-primary/10", className),
		...props
	});
}
var RAW_BASE_URL = {
	"BASE_URL": "/",
	"DEV": false,
	"MODE": "production",
	"PROD": true,
	"SSR": true,
	"TSS_DEV_SERVER": "false",
	"TSS_DEV_SSR_STYLES_BASEPATH": "/",
	"TSS_DEV_SSR_STYLES_ENABLED": "true",
	"TSS_DISABLE_CSRF_MIDDLEWARE_WARNING": "false",
	"TSS_INLINE_CSS_ENABLED": "false",
	"TSS_ROUTER_BASEPATH": "",
	"TSS_SERVER_FN_BASE": "/_serverFn/",
	"VITE_API_BASE_URL": "http://localhost:8000"
}["VITE_API_BASE_URL"];
var BASE_URL = typeof RAW_BASE_URL === "string" ? RAW_BASE_URL.replace(/\/+$/, "") : "";
var apiClient = axios.create({
	baseURL: BASE_URL || "http://localhost:8000",
	headers: { Accept: "application/json" },
	timeout: 15e3
});
function apiErrorMessage$1(error, fallback) {
	if (axios.isAxiosError(error)) {
		const data = error.response?.data;
		if (data && typeof data === "object" && "message" in data && typeof data.message === "string") return data.message;
		if (data && typeof data === "object" && "detail" in data) {
			if (typeof data.detail === "string") return data.detail;
			if (typeof data.detail === "object" && data.detail !== null && "message" in data.detail) return String(data.detail.message);
		}
		const status = error.response?.status;
		if (status) return `${fallback} (HTTP ${status}).`;
		if (error.code === "ECONNABORTED") return `${fallback}: Connection timed out.`;
		if (error.request) return `${fallback}: Cannot reach backend at ${BASE_URL || "http://localhost:8000"}. Please check server status.`;
	}
	if (error instanceof Error && error.message) return error.message;
	return fallback;
}
async function getJson(path, params) {
	try {
		return (await apiClient.get(path, { params })).data;
	} catch (error) {
		throw error;
	}
}
async function postJson(path, body) {
	try {
		const response = await apiClient.post(path, body);
		return {
			status: response.status,
			data: response.data
		};
	} catch (error) {
		if (axios.isAxiosError(error) && error.response) return {
			status: error.response.status,
			data: error.response.data
		};
		throw error;
	}
}
var api = {
	health: () => getJson("/api/v1/health"),
	healthDb: () => getJson("/api/v1/health/db"),
	dashboard: () => getJson("/api/v1/dashboard"),
	sections: (params) => getJson("/api/v1/sections", params),
	section: (sectionId) => getJson(`/api/v1/sections/${encodeURIComponent(sectionId)}`),
	stations: (params) => getJson("/api/v1/stations", params),
	station: (stationId) => getJson(`/api/v1/stations/${encodeURIComponent(stationId)}`),
	assets: (params) => getJson("/api/v1/assets", params),
	asset: (assetId) => getJson(`/api/v1/assets/${encodeURIComponent(assetId)}`),
	maintenance: (params) => getJson("/api/v1/maintenance", params),
	maintenanceRequest: (requestId) => getJson(`/api/v1/maintenance/${encodeURIComponent(requestId)}`),
	trains: (params) => getJson("/api/v1/trains", params),
	train: (trainNumber) => getJson(`/api/v1/trains/${encodeURIComponent(trainNumber)}`),
	trainSchedule: (trainNumber) => getJson(`/api/v1/trains/${encodeURIComponent(trainNumber)}/schedule`),
	freightTrains: (params) => getJson("/api/v1/freight-trains", params),
	freightTrain: (freightTrainId) => getJson(`/api/v1/freight-trains/${encodeURIComponent(freightTrainId)}`),
	blocks: (params) => getJson("/api/v1/blocks", params),
	block: (blockId) => getJson(`/api/v1/blocks/${encodeURIComponent(blockId)}`),
	generateOptimization: (body) => postJson("/api/v1/optimization/generate", body),
	predict: (body) => postJson("/api/v1/ai/predict", body),
	aiInsights: () => getJson("/api/v1/ai/insights"),
	runSimulation: (body) => postJson("/api/v1/simulation/run", body)
};
function asRecords(value) {
	if (Array.isArray(value)) return value.filter(isRecord);
	if (!isRecord(value)) return [];
	for (const key of [
		"data",
		"items",
		"results",
		"sections",
		"stations",
		"assets",
		"maintenance",
		"requests",
		"trains",
		"schedule",
		"stops",
		"blocks",
		"tasks"
	]) {
		const nested = value[key];
		if (Array.isArray(nested)) return nested.filter(isRecord);
	}
	return [];
}
function isRecord(value) {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}
function readValue(record, keys) {
	if (!record) return void 0;
	for (const key of keys) if (key in record) return record[key];
}
function readNumber(record, keys) {
	const value = readValue(record, keys);
	if (typeof value === "number" && Number.isFinite(value)) return value;
	if (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))) return Number(value);
	return null;
}
function readText(record, keys) {
	const value = readValue(record, keys);
	return typeof value === "string" && value.trim() !== "" ? value : null;
}
var Input = import_react.forwardRef(({ className, type, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
		type,
		className: cn("flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", className),
		ref,
		...props
	});
});
Input.displayName = "Input";
var dashboardQuery = {
	queryKey: ["planrail", "dashboard"],
	queryFn: api.dashboard
};
var sectionsQuery = {
	queryKey: ["planrail", "sections"],
	queryFn: () => api.sections({
		page: 1,
		page_size: 100
	})
};
var stationsQuery = {
	queryKey: ["planrail", "stations"],
	queryFn: () => api.stations({
		page: 1,
		page_size: 100
	})
};
var maintenanceFeedQuery = {
	queryKey: [
		"planrail",
		"maintenance",
		"all"
	],
	queryFn: () => api.maintenance({
		page: 1,
		page_size: 150
	})
};
var navItems = [
	{
		label: "Dashboard",
		to: "/dashboard",
		icon: LayoutDashboard
	},
	{
		label: "Railway Network",
		to: "/network",
		icon: Network
	},
	{
		label: "Maintenance",
		to: "/maintenance",
		icon: Wrench
	},
	{
		label: "Trains",
		to: "/trains",
		icon: TrainFront
	},
	{
		label: "Block Planning",
		to: "/blocks",
		icon: Boxes
	},
	{
		label: "AI Insights",
		to: "/insights",
		icon: BrainCircuit
	}
];
function DemoLogin() {
	const navigate = useNavigate();
	const [username, setUsername] = (0, import_react.useState)("demo.operator");
	const [password, setPassword] = (0, import_react.useState)("");
	function enterDashboard(event) {
		event.preventDefault();
		sessionStorage.setItem("planrail-demo-session", "active");
		navigate({ to: "/dashboard" });
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
		className: "min-h-screen bg-rail-paper text-rail-ink",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
			className: "grid min-h-screen lg:grid-cols-[minmax(0,42%)_1fr]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "relative flex min-h-[520px] flex-col justify-between overflow-hidden bg-rail-ink px-7 py-8 text-rail-paper sm:px-10 sm:py-10",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2.5 rounded-full bg-rail-blue" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-[11px] tracking-[0.22em] text-rail-paper/70",
							children: "PLANRAIL // CONTROL"
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative mt-20 lg:mt-0",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mb-4 font-mono text-[11px] tracking-[0.2em] text-rail-blue",
								children: "SIGNAL BOX · FIRST LIGHT"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h1", {
								className: "max-w-xl text-5xl font-extrabold leading-[0.95] tracking-tight sm:text-6xl",
								children: [
									"Delhi —",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", {}),
									"Agra",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("br", {}),
									"Corridor"
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-6 max-w-[34ch] text-sm leading-relaxed text-rail-paper/60",
								children: "Corridor operations surface for the Delhi–Agra main line. Blocks, maintenance, and risk — read at a glance."
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-20 flex max-w-sm justify-between font-mono text-[10px] tracking-[0.18em] text-rail-paper/40",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "DELHI" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "AGRA" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "PROTOTYPE" })
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "absolute bottom-24 left-10 h-40 w-px bg-rail-blue/40" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "rail-pulse absolute left-[10.42rem] top-1/2 size-2 rounded-full bg-rail-blue" })
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex items-center bg-rail-paper px-6 py-12 sm:px-12",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
					className: "mx-auto w-full max-w-sm",
					onSubmit: enterDashboard,
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mb-2 font-mono text-[11px] tracking-[0.2em] text-rail-ink/45",
							children: "AUTH · OPERATOR"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "text-2xl font-bold tracking-tight",
							children: "Operator sign-in"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-sm text-rail-ink/55",
							children: "Enter the PlanRail decision-support workspace."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-8 space-y-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
								className: "block",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-[10px] tracking-[0.15em] text-rail-ink/45",
									children: "USERNAME"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									value: username,
									onChange: (event) => setUsername(event.target.value),
									className: "mt-1.5 h-11 border-rail-ink/10 bg-rail-panel text-rail-ink focus-visible:ring-rail-blue/40",
									placeholder: "username"
								})]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
								className: "block",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-[10px] tracking-[0.15em] text-rail-ink/45",
									children: "PASSWORD"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
									type: "password",
									value: password,
									onChange: (event) => setPassword(event.target.value),
									className: "mt-1.5 h-11 border-rail-ink/10 bg-rail-panel text-rail-ink focus-visible:ring-rail-blue/40",
									placeholder: "••••••••"
								})]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							type: "submit",
							className: "mt-7 h-12 w-full rounded-lg bg-rail-blue text-rail-paper hover:bg-rail-blue/90",
							children: ["Enter Dashboard", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-1.5 rounded-full bg-rail-paper/80" })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-4 font-mono text-[10px] tracking-[0.12em] text-rail-ink/35",
							children: "LOCAL PROTOTYPE · READ-ONLY DECISION SUPPORT"
						})
					]
				})
			})]
		})
	});
}
function PlanRailShell({ children }) {
	const location = useLocation();
	const navigate = useNavigate();
	const [railOpen, setRailOpen] = (0, import_react.useState)(false);
	const [railCollapsed, setRailCollapsed] = (0, import_react.useState)(false);
	const isOnline = useQuery({
		queryKey: ["planrail", "health"],
		queryFn: api.health,
		refetchInterval: 1e4,
		retry: 1
	}).isSuccess;
	function signOut() {
		sessionStorage.removeItem("planrail-demo-session");
		navigate({ to: "/" });
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "min-h-screen overflow-x-hidden bg-rail-paper text-rail-ink",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex min-h-screen",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
					className: cn("fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-rail-ink text-rail-paper transition-transform duration-200 lg:sticky lg:translate-x-0", railOpen ? "translate-x-0" : "-translate-x-full", railCollapsed && "lg:w-[76px]"),
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: cn("flex items-center border-b border-rail-paper/10 px-5 py-5", railCollapsed ? "justify-center" : "gap-2.5"),
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-2.5 shrink-0 rounded-full bg-rail-blue" }),
								!railCollapsed && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-sm font-bold tracking-tight",
									children: "PlanRail"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
									"aria-label": "Close navigation",
									className: "ml-auto lg:hidden",
									onClick: () => setRailOpen(false),
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "size-4" })
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
							className: "flex-1 space-y-1 px-3 py-4",
							children: navItems.map(({ label, to, icon: Icon }) => {
								const active = location.pathname === to;
								return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
									to,
									onClick: () => setRailOpen(false),
									title: railCollapsed ? label : void 0,
									className: cn("relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors", railCollapsed && "justify-center px-2", active ? "bg-rail-paper font-semibold text-rail-ink" : "text-rail-paper/55 hover:bg-rail-paper/10 hover:text-rail-paper"),
									children: [
										active && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "absolute bottom-1.5 left-0 top-1.5 w-[3px] rounded-full bg-rail-blue" }),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-4 shrink-0" }),
										!railCollapsed && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: label })
									]
								}, to);
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: cn("border-t border-rail-paper/10 p-4", railCollapsed && "px-3"),
							children: [!railCollapsed && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "rounded-md border border-rail-paper/10 p-3",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "font-mono text-[10px] tracking-[0.15em] text-rail-paper/45",
										children: "CORRIDOR"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "mt-1 text-sm font-semibold",
										children: "Delhi–Agra Main Line"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "mt-3 flex items-center gap-2 font-mono text-[10px] tracking-[0.12em] text-rail-paper/60",
										children: isOnline ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "rail-pulse size-1.5 rounded-full bg-rail-green" }), " BACKEND CONNECTED"] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-1.5 rounded-full bg-rail-red" }), " BACKEND OFFLINE"] })
									})
								]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
								variant: "ghost",
								size: "icon",
								onClick: signOut,
								title: "Exit session",
								className: "mt-3 w-full text-rail-paper/55 hover:bg-rail-paper/10 hover:text-rail-paper",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LogOut, {}), !railCollapsed && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-xs",
									children: "Exit session"
								})]
							})]
						})
					]
				}),
				railOpen && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					"aria-label": "Close navigation overlay",
					className: "fixed inset-0 z-30 bg-rail-ink/40 lg:hidden",
					onClick: () => setRailOpen(false)
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "min-w-0 flex-1",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
							className: "sticky top-0 z-20 flex min-h-16 items-center justify-between border-b border-rail-ink/10 bg-rail-panel/95 px-4 backdrop-blur sm:px-6",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-3",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										size: "icon",
										className: "lg:hidden",
										"aria-label": "Open navigation",
										onClick: () => setRailOpen(true),
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Menu, {})
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										size: "icon",
										className: "hidden lg:inline-flex",
										"aria-label": railCollapsed ? "Expand navigation" : "Collapse navigation",
										onClick: () => setRailCollapsed((value) => !value),
										children: railCollapsed ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PanelLeftOpen, {}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PanelLeftClose, {})
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "hidden items-center gap-3 sm:flex",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: "font-mono text-[10px] tracking-[0.18em] text-rail-ink/45",
												children: "OPERATIONS"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: "text-rail-ink/20",
												children: "/"
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: "hidden font-mono text-[10px] tracking-[0.1em] text-rail-ink/45 xl:inline",
												children: "DELHI–AGRA CORRIDOR"
											})
										]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "text-sm font-semibold",
										children: navItems.find((item) => item.to === location.pathname)?.label ?? "Operations"
									})
								]
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-3 sm:gap-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "hidden items-center gap-2 font-mono text-[10px] tracking-[0.1em] text-rail-ink/55 md:flex",
									children: isOnline ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "rail-pulse size-1.5 rounded-full bg-rail-green" }), " LOCAL BACKEND CONNECTED"] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-1.5 rounded-full bg-rail-red" }), " BACKEND OFFLINE"] })
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-2 border-l border-rail-ink/10 pl-3 sm:gap-2.5 sm:pl-4",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "grid size-8 place-items-center rounded-full bg-rail-blue/15 text-xs font-bold text-rail-blue",
										children: "OP"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "hidden leading-tight sm:block",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "text-xs font-semibold",
											children: "Controller"
										}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "font-mono text-[9px] tracking-[0.1em] text-rail-ink/40",
											children: "SHIFT A"
										})]
									})]
								})]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("main", {
							className: "mx-auto max-w-[1480px] p-4 sm:p-6",
							children
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("footer", {
							className: "mx-auto flex max-w-[1480px] flex-col gap-1 border-t border-rail-ink/8 px-4 py-5 font-mono text-[9px] leading-relaxed tracking-[0.08em] text-rail-ink/40 sm:flex-row sm:items-center sm:justify-between sm:px-6",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "PLANRAIL DECISION-SUPPORT SYSTEM — DELHI–AGRA CORRIDOR PROTOTYPE." }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "shrink-0 text-rail-ink/30",
								children: "OR-TOOLS CP-SAT + AI PREDICTIVE INTELLIGENCE"
							})]
						})
					]
				})
			]
		})
	});
}
function DashboardPage() {
	const dashboard = useQuery(dashboardQuery);
	const sections = useQuery(sectionsQuery);
	const stations = useQuery(stationsQuery);
	const maintenanceFeed = useQuery(maintenanceFeedQuery);
	const data = dashboard.data;
	const sectionRecords = asRecords(sections.data);
	const stationRecords = asRecords(stations.data);
	const maintenanceRecords = asRecords(maintenanceFeed.data);
	const departmentStats = (0, import_react.useMemo)(() => {
		const counts = {};
		for (const r of maintenanceRecords) {
			const dept = readText(r, ["department"]) ?? "Other";
			counts[dept] = (counts[dept] ?? 0) + 1;
		}
		return Object.entries(counts).map(([department, count]) => ({
			department,
			count
		}));
	}, [maintenanceRecords]);
	const riskStats = (0, import_react.useMemo)(() => {
		let critical = 0;
		let high = 0;
		let medium = 0;
		let low = 0;
		for (const r of maintenanceRecords) {
			const sev = readNumber(r, ["severity"]) ?? 0;
			if (sev >= 80) critical++;
			else if (sev >= 70) high++;
			else if (sev >= 40) medium++;
			else low++;
		}
		const total = maintenanceRecords.length || 1;
		return [
			{
				label: "Critical Severity (≥80)",
				percentage: Math.round(critical / total * 100),
				count: critical
			},
			{
				label: "High Severity (≥70)",
				percentage: Math.round(high / total * 100),
				count: high
			},
			{
				label: "Medium Severity (≥40)",
				percentage: Math.round(medium / total * 100),
				count: medium
			},
			{
				label: "Low Severity (<40)",
				percentage: Math.round(low / total * 100),
				count: low
			}
		];
	}, [maintenanceRecords]);
	const recommendationText = (0, import_react.useMemo)(() => {
		if (!data) return null;
		if (data.overdue_requests > 0) return `Attention: ${data.overdue_requests} maintenance requests are overdue on the Delhi–Agra corridor. ${data.critical_high_requests} tasks require high-priority blocks. There are ${data.available_maintenance_windows} feasible maintenance windows available. Run CP-SAT Optimization to generate multi-department bundled block allocations.`;
		return `All corridor maintenance requests are within schedule limits. ${data.available_maintenance_windows} maintenance windows available across ${data.total_trains} scheduled train paths.`;
	}, [data]);
	const kpis = [
		{
			label: "Total Requests",
			value: data ? data.total_maintenance_requests : null,
			tone: "blue",
			icon: ClipboardList
		},
		{
			label: "Pending Maintenance",
			value: data ? data.pending_requests : null,
			tone: "amber",
			icon: Wrench
		},
		{
			label: "Critical / High",
			value: data ? data.critical_high_requests : null,
			tone: "red",
			icon: ShieldAlert
		},
		{
			label: "Overdue Tasks",
			value: data ? data.overdue_requests : null,
			tone: "red",
			icon: TriangleAlert
		},
		{
			label: "Feasible Windows",
			value: data ? data.available_maintenance_windows : null,
			tone: "green",
			icon: Gauge
		},
		{
			label: "Corridor Trains",
			value: data ? data.total_trains : null,
			tone: "ink",
			icon: TrainFront
		}
	];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
			eyebrow: "CORRIDOR TELEMETRY — DELHI–AGRA",
			title: "Operations overview",
			description: "Corridor maintenance status, asset posture, and maintenance window availability."
		}), dashboard.isError ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ErrorState, {
			message: apiErrorMessage(dashboard.error, "The dashboard metrics could not be loaded"),
			onRetry: () => void dashboard.refetch()
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6",
				children: kpis.map((kpi) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
					label: kpi.label,
					value: kpi.value,
					tone: kpi.tone,
					icon: kpi.icon,
					loading: dashboard.isPending
				}, kpi.label))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "grid grid-cols-1 gap-4 lg:grid-cols-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(NetworkPreview, {
					sections: sectionRecords,
					stations: stationRecords,
					loading: sections.isPending || stations.isPending
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Recommendation, { text: recommendationText })]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "grid grid-cols-1 gap-4 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(MaintenanceChart, {
					departmentStats,
					loading: maintenanceFeed.isPending
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(RiskChart, {
					riskStats,
					loading: maintenanceFeed.isPending
				})]
			})
		] })]
	});
}
function KpiCard({ label, value, loading, tone, suffix, icon: Icon }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "relative rounded-[10px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 transition-transform duration-200 hover:-translate-y-0.5",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: cn("absolute bottom-3.5 left-0 top-3.5 w-[3px] rounded-full", tone === "amber" && "bg-rail-amber", tone === "red" && "bg-rail-red", tone === "green" && "bg-rail-green", tone === "ink" && "bg-rail-ink/30", tone === "blue" && "bg-rail-blue") }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-start justify-between gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "font-mono text-[10px] tracking-[0.12em] text-rail-ink/45",
					children: label
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: "size-4 text-rail-ink/25" })]
			}),
			loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "mt-2 h-9 w-20 bg-rail-ink/8" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-2 text-3xl font-extrabold tracking-tight",
				children: value === null ? "—" : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [value, suffix && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-lg text-rail-ink/50",
					children: suffix
				})] })
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-2 font-mono text-[10px] tracking-[0.08em] text-rail-ink/40",
				children: value === null && !loading ? "NO DATA" : "BACKEND DATA"
			})
		]
	});
}
function NetworkPreview({ sections, stations, loading }) {
	const points = stations.map((station, index) => ({
		label: readText(station, [
			"station_code",
			"code",
			"station_name",
			"name"
		]) ?? `Station ${index + 1}`,
		position: `${Math.max(6, Math.min(94, 6 + index * 88 / Math.max(stations.length - 1, 1)))}%`
	}));
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[14px] bg-rail-panel p-4 shadow-rail ring-1 ring-rail-ink/8 lg:col-span-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between gap-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "font-mono text-[10px] tracking-[0.15em] text-rail-ink/45",
				children: "RAILWAY NETWORK"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-0.5 text-sm font-semibold",
				children: "Corridor map topology"
			})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "hidden font-mono text-[10px] tracking-[0.1em] text-rail-ink/35 sm:block",
				children: "GET /api/v1/sections"
			})]
		}), loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "mt-3 aspect-[16/7] w-full bg-rail-ink/8" }) : sections.length === 0 && stations.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, { label: "No sections or stations were returned by the backend network feeds." }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "rail-map mt-3 aspect-[16/7] overflow-hidden rounded-lg border border-rail-ink/8 bg-rail-map p-5",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex h-full flex-col justify-between",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between font-mono text-[10px] tracking-[0.14em] text-rail-ink/40",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "NEW DELHI (NDLS)" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: sections.length ? `${sections.length} SECTIONS` : "SECTIONS" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "AGRA CANTT (AGC)" })
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "relative px-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-1 rounded-full bg-rail-blue/15",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "h-full w-full rounded-full bg-rail-blue" })
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "absolute inset-x-0 top-1/2 flex -translate-y-1/2 justify-between",
							children: (points.length ? points : [{
								label: "Corridor feed",
								position: "50%"
							}]).map((point) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "group relative",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "rail-pulse block size-3 rounded-full border-2 border-rail-map bg-rail-blue shadow-[0_0_0_3px_color-mix(in_oklab,var(--color-rail-blue)_18%,transparent)]" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "absolute left-1/2 top-5 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] text-rail-ink/55",
									children: point.label
								})]
							}, `${point.label}-${point.position}`))
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between font-mono text-[10px] text-rail-ink/35",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: stations.length ? `${stations.length} STATIONS` : "STATIONS" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "195 KM PROTOTYPE CORRIDOR" })]
					})
				]
			})
		})]
	});
}
function Recommendation({ text }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-blue/25",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "rail-pulse size-1.5 rounded-full bg-rail-blue" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-[11px] tracking-[0.15em] text-rail-ink/50",
				children: "AI RECOMMENDATION"
			})]
		}), text ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-4 text-sm leading-relaxed text-rail-ink/80",
			children: text
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "Corridor recommendation will appear when telemetry responds.",
			compact: true
		})]
	});
}
function MaintenanceChart({ departmentStats, loading }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartPanel, {
		title: "Maintenance by Department",
		meta: "PENDING TASKS",
		children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartSkeleton, {}) : departmentStats.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "space-y-4",
			children: departmentStats.map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProgressRow, {
				label: item.department,
				value: item.count
			}, item.department))
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "No department maintenance requests returned.",
			compact: true
		})
	});
}
function RiskChart({ riskStats, loading }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartPanel, {
		title: "Severity & Urgency Distribution",
		meta: "ACTIVE BACKLOG",
		children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChartSkeleton, {}) : riskStats.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "space-y-4",
			children: riskStats.map((item, index) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProgressRow, {
				label: `${item.label} (${item.count})`,
				value: item.percentage,
				danger: index === 0
			}, item.label))
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "No risk distribution records available.",
			compact: true
		})
	});
}
function ChartPanel({ title, meta, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mb-5 flex items-center justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "font-semibold",
				children: title
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-[10px] text-rail-ink/35",
				children: meta
			})]
		}), children]
	});
}
function ProgressRow({ label, value, danger = false }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex justify-between font-mono text-[10px] text-rail-ink/50",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: label }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: value === null ? "—" : `${value}%` })]
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "mt-1.5 h-2 rounded-full bg-rail-ink/8",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: cn("h-full rounded-full", danger ? "bg-rail-red" : "bg-rail-blue"),
			style: { width: `${Math.max(0, Math.min(value ?? 0, 100))}%` }
		})
	})] });
}
function ChartSkeleton() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: "space-y-4",
		children: [
			1,
			2,
			3,
			4
		].map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-7 bg-rail-ink/8" }, item))
	});
}
function EmptyState({ label, compact = false }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("flex items-center gap-3 rounded-lg border border-dashed border-rail-ink/15 text-sm text-rail-ink/50", compact ? "mt-4 p-4" : "mt-3 min-h-40 justify-center p-6 text-center"),
		children: [compact ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleDot, { className: "size-4 shrink-0 text-rail-ink/30" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "size-4 shrink-0 text-rail-amber" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: label })]
	});
}
function ErrorState({ message, onRetry }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex min-h-40 flex-col items-center justify-center gap-3 rounded-[14px] border border-dashed border-rail-red/30 bg-rail-panel p-6 text-center",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleDot, { className: "size-5 text-rail-red" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-rail-ink/60",
				children: message
			}),
			onRetry && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				variant: "outline",
				size: "sm",
				onClick: onRetry,
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "size-3.5" }), "Retry feed"]
			})
		]
	});
}
function PageIntro({ eyebrow, title, description }) {
	const isOnline = useQuery({
		queryKey: ["planrail", "health"],
		queryFn: api.health,
		refetchInterval: 1e4,
		retry: 1
	}).isSuccess;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex flex-col justify-between gap-3 sm:flex-row sm:items-end",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "font-mono text-[10px] tracking-[0.2em] text-rail-ink/40",
				children: eyebrow
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "mt-1 text-2xl font-bold tracking-tight",
				children: title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-sm text-rail-ink/55",
				children: description
			})
		] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex items-center gap-2 font-mono text-[10px] tracking-[0.12em] text-rail-ink/40",
			children: isOnline ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "rail-pulse size-1.5 rounded-full bg-rail-green" }), " BACKEND CONNECTED"] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { className: "size-1.5 rounded-full bg-rail-red" }), " BACKEND OFFLINE"] })
		})]
	});
}
//#endregion
export { PageIntro as a, api as c, cn as d, isRecord as f, readValue as h, EmptyState as i, apiErrorMessage$1 as l, readText as m, DashboardPage as n, PlanRailShell as o, readNumber as p, DemoLogin as r, Skeleton as s, Button as t, asRecords as u };
