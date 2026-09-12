/**
 * PlanRail Prototype Authentication & Role Management
 * ====================================================
 * Manages local session roles: CONTROLLER, MAINTENANCE, ADMIN.
 */

export type UserRole = "CONTROLLER" | "MAINTENANCE" | "ADMIN";

export interface RoleConfig {
  role: UserRole;
  title: string;
  subtitle: string;
  description: string;
  defaultUsername: string;
  dashboardPath: string;
  allowedRoutes: string[];
  badgeLabel: string;
  badgeTone: "blue" | "amber" | "green";
  avatarCode: string;
}

export const ROLE_CONFIGS: Record<UserRole, RoleConfig> = {
  CONTROLLER: {
    role: "CONTROLLER",
    title: "Controller",
    subtitle: "Sectional / Chief Train Controller",
    description: "Plan possessions, review AI risk, optimize blocks and run What-If scenarios.",
    defaultUsername: "controller.delhi",
    dashboardPath: "/dashboard",
    allowedRoutes: ["/dashboard", "/network", "/maintenance", "/trains", "/blocks", "/insights"],
    badgeLabel: "CONTROLLER · SHIFT A",
    badgeTone: "blue",
    avatarCode: "CT",
  },
  MAINTENANCE: {
    role: "MAINTENANCE",
    title: "Maintenance Crew",
    subtitle: "Department / Field Engineer",
    description: "Manage maintenance work, inspect assets, track tasks and review risks.",
    defaultUsername: "engineer.pway",
    dashboardPath: "/maintenance-dashboard",
    allowedRoutes: ["/maintenance-dashboard", "/maintenance", "/network", "/trains", "/insights"],
    badgeLabel: "MAINTENANCE CREW",
    badgeTone: "amber",
    avatarCode: "MC",
  },
  ADMIN: {
    role: "ADMIN",
    title: "Admin",
    subtitle: "Division / System Administrator",
    description: "Manage corridor configuration, operational parameters and system health.",
    defaultUsername: "admin.nr_hq",
    dashboardPath: "/admin-dashboard",
    allowedRoutes: ["/admin-dashboard", "/network", "/maintenance", "/trains", "/insights"],
    badgeLabel: "SYSTEM ADMIN",
    badgeTone: "green",
    avatarCode: "AD",
  },
};

export function getSessionRole(): UserRole {
  if (typeof window === "undefined") return "CONTROLLER";
  const stored = sessionStorage.getItem("planrail-role");
  if (stored === "MAINTENANCE" || stored === "ADMIN" || stored === "CONTROLLER") {
    return stored;
  }
  return "CONTROLLER";
}

export function getSessionUsername(): string {
  if (typeof window === "undefined") return "controller.delhi";
  const stored = sessionStorage.getItem("planrail-username");
  return stored || ROLE_CONFIGS[getSessionRole()].defaultUsername;
}

export function isSessionActive(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem("planrail-demo-session") === "active";
}

export function setSession(role: UserRole, username: string): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem("planrail-demo-session", "active");
  sessionStorage.setItem("planrail-role", role);
  sessionStorage.setItem("planrail-username", username || ROLE_CONFIGS[role].defaultUsername);
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem("planrail-demo-session");
  sessionStorage.removeItem("planrail-role");
  sessionStorage.removeItem("planrail-username");
}

export function isRouteAllowed(pathname: string, role: UserRole): boolean {
  const config = ROLE_CONFIGS[role];
  if (!config) return true;
  return config.allowedRoutes.some((route) => pathname === route || pathname.startsWith(`${route}/`));
}
