import { o as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-collection+[...].mjs";
import { t as useQuery } from "../_libs/tanstack__react-query.mjs";
import { E as BrainCircuit, a as Sparkles, b as CircleDot, c as RefreshCw, o as ShieldAlert, r as TriangleAlert } from "../_libs/lucide-react.mjs";
import { a as PageIntro, c as api, d as cn, i as EmptyState, l as apiErrorMessage$1, m as readText, o as PlanRailShell, s as Skeleton, t as Button, u as asRecords } from "./planrail-C-ZDaIgs.mjs";
import { a as SelectTrigger, i as SelectItem, n as Select, o as SelectValue, r as SelectContent, t as Badge } from "./select-B2z5z-Oe.mjs";
import { a as Bar, c as ResponsiveContainer, i as XAxis, l as Tooltip, n as BarChart, o as Pie, r as YAxis, s as Cell, t as PieChart } from "../_libs/recharts+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/insights-wYxbLQTo.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var CHART_BLUE = "oklch(0.52 0.19 260)";
var CHART_GREEN = "oklch(0.59 0.14 157)";
var CHART_AMBER = "oklch(0.66 0.14 67)";
var CHART_RED = "oklch(0.58 0.17 35)";
var CHART_INK_SOFT = "oklch(0.18 0.015 270 / 0.45)";
function categoryColor(category) {
	const tone = category.toUpperCase();
	if (tone === "CRITICAL") return CHART_RED;
	if (tone === "HIGH") return CHART_AMBER;
	if (tone === "MEDIUM") return CHART_BLUE;
	if (tone === "LOW") return CHART_GREEN;
	return CHART_BLUE;
}
function AIInsightsPage() {
	const insightsQuery = useQuery({
		queryKey: [
			"planrail",
			"ai",
			"insights"
		],
		queryFn: api.aiInsights
	});
	const maintenanceQuery = useQuery({
		queryKey: [
			"planrail",
			"maintenance",
			"all_for_picker"
		],
		queryFn: () => api.maintenance({ page_size: 150 })
	});
	const insightsData = insightsQuery.data ?? null;
	const maintenanceRecords = asRecords(maintenanceQuery.data);
	const riskSlices = (0, import_react.useMemo)(() => {
		if (!insightsData?.risk_distribution) return [];
		return Object.entries(insightsData.risk_distribution).map(([name, value]) => ({
			name,
			value
		})).filter((s) => s.value > 0);
	}, [insightsData]);
	const prioritySlices = (0, import_react.useMemo)(() => {
		if (!insightsData?.priority_distribution) return [];
		return Object.entries(insightsData.priority_distribution).map(([name, value]) => ({
			name,
			value
		})).filter((s) => s.value > 0);
	}, [insightsData]);
	const departmentSlices = (0, import_react.useMemo)(() => {
		if (!insightsData?.department_distribution) return [];
		return Object.entries(insightsData.department_distribution).map(([name, value]) => ({
			name,
			value
		})).sort((a, b) => b.value - a.value);
	}, [insightsData]);
	const attentionTasks = insightsData?.high_attention_tasks ?? [];
	const [selectedRequestId, setSelectedRequestId] = (0, import_react.useState)("");
	const defaultRequestId = attentionTasks[0]?.request_id || maintenanceRecords[0]?.request_id || "MR0001";
	const effectiveRequestId = selectedRequestId || defaultRequestId;
	const predictQuery = useQuery({
		queryKey: [
			"planrail",
			"ai",
			"predict",
			effectiveRequestId
		],
		queryFn: () => api.predict({ request_id: effectiveRequestId }),
		enabled: Boolean(effectiveRequestId),
		retry: false
	});
	const prediction = predictQuery.data?.status === 200 ? predictQuery.data.data : null;
	const loading = insightsQuery.isPending;
	const feedError = insightsQuery.error;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PlanRailShell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PageIntro, {
			eyebrow: "DECISION SUPPORT & PREDICTIVE INTELLIGENCE — DELHI–AGRA",
			title: "AI Insights",
			description: "Traffic-aware failure risk scoring, multi-criteria priority harmonization, and auditable controller briefings."
		}), feedError ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(InsightsError, {
			message: apiErrorMessage$1(feedError, "The AI insights analytics could not be loaded"),
			onRetry: () => void insightsQuery.refetch()
		}) : loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(InsightsSkeleton, {}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
			insightsData?.corridor_ai_recommendation && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "rounded-[14px] border border-rail-blue/30 bg-gradient-to-r from-rail-blue/10 via-rail-panel to-rail-paper p-5 shadow-rail",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-start gap-3.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-0.5 rounded-full bg-rail-blue/15 p-2 text-rail-blue",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "size-5" })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2 font-mono text-[11px] font-bold tracking-[0.15em] text-rail-blue",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: "CORRIDOR DECISION-SUPPORT RECOMMENDATION" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
								variant: "outline",
								className: "border-rail-blue/30 font-mono text-[10px] text-rail-blue",
								children: insightsData.model_status
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-sm font-medium leading-relaxed text-rail-ink/90",
							children: insightsData.corridor_ai_recommendation
						})]
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RequestAnalysisCard, {
				prediction,
				predictionPending: predictQuery.isPending,
				predictionError: predictQuery.error,
				maintenanceList: maintenanceRecords,
				selectedId: effectiveRequestId,
				onSelectId: setSelectedRequestId,
				totalAnalyzed: insightsData?.total_requests_analyzed ?? 0
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DistributionPanel, {
						title: "Asset Failure Risk",
						meta: "PROBABILISTIC MODEL",
						slices: riskSlices
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DistributionPanel, {
						title: "Maintenance Priority",
						meta: "MULTI-CRITERIA (30/25/20/15/10)",
						slices: prioritySlices
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DepartmentPanel, { slices: departmentSlices })
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(HighAttentionTasks, {
				tasks: attentionTasks,
				total: insightsData?.total_requests_analyzed ?? 0,
				onSelectTask: (id) => setSelectedRequestId(id),
				activeTaskId: effectiveRequestId
			})
		] })]
	}) });
}
function RequestAnalysisCard({ prediction, predictionPending, predictionError, maintenanceList, selectedId, onSelectId, totalAnalyzed }) {
	const components = prediction?.priority_components;
	const factors = prediction?.risk_contributing_factors ?? [];
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-blue/25",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-wrap items-center justify-between gap-3 border-b border-rail-ink/8 pb-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(BrainCircuit, { className: "size-4 text-rail-blue" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-mono text-[11px] font-bold tracking-[0.15em] text-rail-ink/75",
					children: "REQUEST AI EVALUATION & EXPLAINABILITY"
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-mono text-[10px] tracking-[0.08em] text-rail-ink/50",
					children: "ANALYZE TASK:"
				}), maintenanceList.length > 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
					value: selectedId,
					onValueChange: onSelectId,
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
						className: "h-8 w-48 bg-rail-paper font-mono text-xs",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "Select request" })
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectContent, {
						className: "max-h-60",
						children: maintenanceList.map((m, i) => {
							const id = readText(m, [
								"request_id",
								"id",
								"task_id"
							]) ?? `REQ-${i}`;
							const dept = readText(m, ["department"]) ?? "";
							return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectItem, {
								value: id,
								className: "font-mono text-xs",
								children: [
									id,
									" (",
									dept,
									")"
								]
							}, id);
						})
					})]
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "font-mono text-[10px] text-rail-ink/40",
					children: "NO REQUESTS"
				})]
			})]
		}), predictionPending ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mt-4 space-y-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-16 bg-rail-ink/8" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-24 bg-rail-ink/8" })]
		}) : predictionError ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-4 rounded-md border border-rail-red/20 bg-rail-red/5 p-3 text-xs text-rail-red",
			children: apiErrorMessage$1(predictionError, "Could not fetch AI prediction for selected request")
		}) : prediction ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mt-4 space-y-4",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-3 sm:grid-cols-2 lg:grid-cols-4",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-between",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-[9px] tracking-[0.14em] text-rail-ink/45",
										children: "PREDICTED FAILURE RISK"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
										variant: "outline",
										className: "font-mono text-[9px]",
										style: {
											color: categoryColor(prediction.risk_category),
											borderColor: categoryColor(prediction.risk_category)
										},
										children: prediction.risk_category
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-1 text-xl font-bold",
									style: { color: categoryColor(prediction.risk_category) },
									children: [
										prediction.risk_score.toFixed(1),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-xs font-normal text-rail-ink/40",
											children: "/ 100"
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-0.5 font-mono text-[10px] text-rail-ink/45",
									children: ["P(failure) = ", (prediction.risk_probability ?? prediction.risk_score / 100).toFixed(4)]
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-between",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-[9px] tracking-[0.14em] text-rail-ink/45",
										children: "OPERATIONAL TRAFFIC IMPACT"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
										variant: "outline",
										className: "font-mono text-[9px]",
										style: { color: categoryColor(prediction.traffic_impact_category || "LOW") },
										children: prediction.traffic_impact_category || "LOW"
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-1 text-xl font-bold text-rail-ink/85",
									children: [
										(prediction.traffic_impact_score ?? 0).toFixed(1),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-xs font-normal text-rail-ink/40",
											children: "/ 100"
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "mt-0.5 font-mono text-[10px] text-rail-ink/45",
									children: "Combined passenger + freight pressure"
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-between",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "font-mono text-[9px] tracking-[0.14em] text-rail-ink/45",
										children: "MULTI-CRITERIA PRIORITY"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
										variant: "outline",
										className: "font-mono text-[9px]",
										style: { color: categoryColor(prediction.priority_category || "MEDIUM") },
										children: prediction.priority_category || "MEDIUM"
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mt-1 text-xl font-bold text-rail-blue",
									children: [
										prediction.priority_score.toFixed(1),
										" ",
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "text-xs font-normal text-rail-ink/40",
											children: "/ 100"
										})
									]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "mt-0.5 font-mono text-[10px] text-rail-ink/45",
									children: "Harmonized scheduling score"
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "rounded-md border border-rail-ink/8 bg-rail-paper px-3.5 py-3",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "font-mono text-[9px] tracking-[0.14em] text-rail-ink/45",
									children: "MODEL PROVENANCE"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "mt-1 truncate text-xs font-bold text-rail-ink/80",
									children: prediction.model_status || "DOMAIN_CALIBRATED_MODEL"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "mt-0.5 font-mono text-[10px] text-rail-ink/45",
									children: "Threshold: 0.5421 (Recall-Tuned)"
								})
							]
						})
					]
				}),
				components && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-md border border-rail-ink/8 bg-rail-paper p-3.5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "font-mono text-[10px] font-bold tracking-[0.1em] text-rail-ink/60",
						children: "MULTI-CRITERIA HARMONIZATION BREAKDOWN (30% / 25% / 20% / 15% / 10%)"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-2.5 grid grid-cols-2 gap-3 sm:grid-cols-5",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ComponentBar, {
								label: "Severity (30%)",
								value: components.severity
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ComponentBar, {
								label: "Criticality (25%)",
								value: components.criticality
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ComponentBar, {
								label: "Overdue (20%)",
								value: components.overdue
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ComponentBar, {
								label: "Risk (15%)",
								value: components.risk
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ComponentBar, {
								label: "Traffic (10%)",
								value: components.traffic_impact
							})
						]
					})]
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "grid gap-3 lg:grid-cols-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "rounded-md border border-rail-ink/8 bg-rail-paper p-3.5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "font-mono text-[10px] font-bold tracking-[0.1em] text-rail-ink/60",
							children: "IDENTIFIED RISK DRIVERS"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-2 space-y-1.5",
							children: factors.length > 0 ? factors.map((f, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-start gap-2 text-xs text-rail-ink/80",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldAlert, { className: "mt-0.5 size-3.5 shrink-0 text-rail-amber" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: f })]
							}, i)) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "text-xs text-rail-ink/50",
								children: "Operating within nominal risk boundaries."
							})
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "rounded-md border border-rail-blue/20 bg-rail-blue/[0.05] p-3.5",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-1.5 font-mono text-[10px] font-bold tracking-[0.08em] text-rail-blue",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "size-3.5" }), " CONTROLLER AUDIT BRIEFING"]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1.5 text-xs leading-relaxed text-rail-ink/80",
							children: prediction.explanation || "No explanation provided for this maintenance task."
						})]
					})]
				})
			]
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "Select a maintenance request above to evaluate AI decision-support metrics.",
			compact: true
		})]
	});
}
function ComponentBar({ label, value }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-1",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between text-[10px]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-rail-ink/55 truncate",
				children: label
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-bold font-mono text-rail-ink/80",
				children: value.toFixed(1)
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "h-1.5 w-full overflow-hidden rounded-full bg-rail-ink/10",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "h-full rounded-full bg-rail-blue transition-all",
				style: { width: `${Math.max(0, Math.min(100, value))}%` }
			})
		})]
	});
}
function DistributionPanel({ title, meta, slices }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-sm font-semibold",
				children: title
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-[10px] text-rail-ink/35",
				children: meta
			})]
		}), slices.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-2 h-44",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
				width: "100%",
				height: "100%",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(PieChart, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pie, {
					data: slices,
					dataKey: "value",
					nameKey: "name",
					innerRadius: 42,
					outerRadius: 68,
					paddingAngle: 2,
					strokeWidth: 0,
					children: slices.map((slice) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: categoryColor(slice.name) }, slice.name))
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
					background: "oklch(0.985 0.006 95)",
					border: "1px solid oklch(0.18 0.015 270 / 0.12)",
					borderRadius: 8,
					fontSize: 12
				} })] })
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-3 space-y-1.5",
			children: slices.map((slice) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2 text-xs",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "size-2 shrink-0 rounded-full",
						style: { background: categoryColor(slice.name) }
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "min-w-0 flex-1 truncate text-rail-ink/70",
						children: slice.name
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-[10px] font-semibold text-rail-ink/75",
						children: slice.value
					})
				]
			}, slice.name))
		})] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "No values were returned for this distribution.",
			compact: true
		})]
	});
}
function DepartmentPanel({ slices }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[14px] bg-rail-panel p-5 shadow-rail ring-1 ring-rail-ink/8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-sm font-semibold",
				children: "Maintenance by Department"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
				className: "font-mono text-[10px] text-rail-ink/35",
				children: "CORRIDOR REQS"
			})]
		}), slices.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-2 h-56",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
				width: "100%",
				height: "100%",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
					data: slices,
					layout: "vertical",
					margin: {
						left: 8,
						right: 16
					},
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
							type: "number",
							hide: true
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
							type: "category",
							dataKey: "name",
							width: 100,
							tick: {
								fontSize: 10,
								fill: CHART_INK_SOFT
							},
							tickLine: false,
							axisLine: false
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { contentStyle: {
							background: "oklch(0.985 0.006 95)",
							border: "1px solid oklch(0.18 0.015 270 / 0.12)",
							borderRadius: 8,
							fontSize: 12
						} }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
							dataKey: "value",
							radius: [
								0,
								4,
								4,
								0
							],
							children: slices.map((slice) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, { fill: CHART_BLUE }, slice.name))
						})
					]
				})
			})
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "No department values were returned.",
			compact: true
		})]
	});
}
function HighAttentionTasks({ tasks, total, onSelectTask, activeTaskId }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "rounded-[14px] bg-rail-panel shadow-rail ring-1 ring-rail-ink/8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center justify-between border-b border-rail-ink/8 px-4 py-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "size-4 text-rail-red" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
					className: "text-sm font-semibold",
					children: "High-Priority & High-Risk Maintenance Queue"
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
				className: "font-mono text-[10px] text-rail-ink/40",
				children: [
					tasks.length,
					" OF ",
					total,
					" REQUESTS FLAGGED"
				]
			})]
		}), tasks.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "divide-y divide-rail-ink/8",
			children: tasks.map((task) => {
				const isSelected = task.request_id === activeTaskId;
				return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					onClick: () => onSelectTask(task.request_id),
					className: cn("flex cursor-pointer flex-wrap items-center gap-3 px-4 py-3 transition hover:bg-rail-ink/[0.02]", isSelected && "bg-rail-blue/[0.04] ring-1 ring-inset ring-rail-blue/30"),
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-[11px] font-bold text-rail-blue",
							children: task.request_id
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "min-w-0 flex-1 truncate text-xs text-rail-ink/70",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-semibold text-rail-ink/90",
									children: task.department
								}),
								" · ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: task.asset_type }),
								" · ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-[11px]",
									children: task.section_id
								}),
								task.top_drivers && task.top_drivers.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
									className: "ml-2 text-rail-ink/50 italic truncate hidden md:inline",
									children: [
										"(",
										task.top_drivers[0],
										")"
									]
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
							variant: "outline",
							className: "font-mono text-[10px]",
							style: {
								color: categoryColor(task.priority_category),
								borderColor: categoryColor(task.priority_category)
							},
							children: [
								"PRI: ",
								task.priority_score.toFixed(0),
								" (",
								task.priority_category,
								")"
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
							variant: "outline",
							className: "font-mono text-[10px]",
							style: {
								color: categoryColor(task.risk_category),
								borderColor: categoryColor(task.risk_category)
							},
							children: [
								"RISK: ",
								task.risk_score.toFixed(0),
								" (",
								task.risk_category,
								")"
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "ghost",
							size: "sm",
							className: "h-7 text-xs font-mono text-rail-blue",
							children: "Analyze →"
						})
					]
				}, task.request_id);
			})
		}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(EmptyState, {
			label: "No high-priority or high-risk tasks were returned.",
			compact: true
		})]
	});
}
function InsightsSkeleton() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-20 bg-rail-ink/8" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-44 bg-rail-ink/8" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "grid gap-4 lg:grid-cols-3",
				children: [
					1,
					2,
					3
				].map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-72 bg-rail-ink/8" }, item))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-56 bg-rail-ink/8" })
		]
	});
}
function InsightsError({ message, onRetry }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex min-h-40 flex-col items-center justify-center gap-3 rounded-[14px] border border-dashed border-rail-red/30 bg-rail-panel p-6 text-center",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleDot, { className: "size-5 text-rail-red" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-rail-ink/60",
				children: message
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				variant: "outline",
				size: "sm",
				onClick: onRetry,
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RefreshCw, { className: "size-3.5" }), "Retry feeds"]
			})
		]
	});
}
var SplitComponent = AIInsightsPage;
//#endregion
export { SplitComponent as component };
