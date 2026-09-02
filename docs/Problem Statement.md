# PlanRail — Problem Statement

## 1. Official Problem

SIH26027 focuses on **AI-powered automatic block planning to maximize asset availability for train operations on Indian Railways**.

Indian Railways has maintenance activities across multiple departments such as:

* Engineering
* Traction/OHE
* Signalling & Telecommunication

Maintenance information and operational information exist across different systems. Planning maintenance blocks while considering train operations, maintenance priorities, available resources and departmental requirements is difficult when these activities are handled independently.

PlanRail aims to provide an intelligent decision-support system that coordinates these activities and generates optimized maintenance block plans.

---

## 2. Problem in Simple Language

Railway maintenance teams need time to temporarily restrict railway operations so that maintenance can safely happen.

Different departments may need maintenance at similar locations and times.

Instead of creating separate blocks for every department, PlanRail should determine:

> Which maintenance tasks should be done, when should they be done, which tasks can be combined, and which time causes the least disruption to railway operations?

---

## 3. Example

Suppose:

* Engineering needs 2 hours
* OHE needs 1 hour
* Signalling needs 1.5 hours

and all three tasks are near each other.

Instead of:

Engineering → 2 hours
OHE → 1 hour
Signalling → 1.5 hours

PlanRail may recommend:

One coordinated 2-hour block containing compatible activities.

This can reduce:

* Total block duration
* Train disruption
* Repeated resource deployment
* Maintenance coordination effort

---

## 4. Proposed Solution

PlanRail will act as an intelligent decision-support layer.

It will:

1. Collect railway network, train and maintenance data.
2. Calculate maintenance priority.
3. Predict maintenance risk.
4. Analyze train traffic and possible conflicts.
5. Identify compatible maintenance tasks.
6. Generate optimized maintenance blocks.
7. Explain why each block was recommended.
8. Allow a railway controller to modify or reject recommendations.
9. Provide what-if simulation for changed conditions.
10. Display the complete plan through a web dashboard.

---

## 5. Prototype Scope

The prototype will focus on the Delhi–Agra corridor.

The system will use:

* Public railway data
* Historical train-delay data
* Railway network/geospatial data
* Freight statistics
* Official railway maintenance guidelines
* Domain-calibrated synthetic maintenance data

Real TMS/SMMS/TDMS/COA integration will not be implemented in the prototype.

---

## 6. Important Principle

PlanRail is NOT an autonomous railway control system.

It is a:

> Human-in-the-loop railway maintenance decision-support system.

AI generates recommendations.

The railway controller makes the final decision.

---

## 7. Main Objective

Generate a maintenance plan that attempts to:

* Minimize block duration
* Minimize train conflicts
* Maximize high-priority maintenance completion
* Maximize asset availability
* Combine compatible maintenance tasks
* Respect operational constraints
* Provide explainable recommendations

---

## 8. Success Metrics

The prototype should calculate:

* Total blocks before optimization
* Total blocks after optimization
* Total block hours before/after
* Number of train conflicts
* Maintenance completion percentage
* Critical maintenance completion
* Estimated asset availability improvement

All improvement numbers must be calculated from the prototype data. Do not claim real Indian Railways operational improvements.
