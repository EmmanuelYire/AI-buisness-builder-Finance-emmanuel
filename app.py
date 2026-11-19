import json
import math
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Career Venture Lab — Team Business (Calculus | Financial Services)",
    page_icon="📊",
    layout="wide",
)

# -----------------------------------------------------------------------------
# DEFAULT SNAPSHOT FIXTURE (Team Business — Custom FIN-1 + Sample Ledger)
# -----------------------------------------------------------------------------
DEFAULT_SNAPSHOT = {
    "team_id": "Team Business",
    "course": "Calculus",
    "pathway": "FIN-1",
    "challenge_level": "Advanced",
    "state_version": 1,
    "simulation_date": "2026-12-31",
    "currency": "USD",
    "offering": {
        "offering_id": "financial_plan",
        "name": "Financial Plan",
        "price": 10000.00,
    },
    "demand": {
        "D0": 3,
        "demand_mode": "Manual",
    },
    "capacity": {
        "staff_hours": 3.0,
        "hours_per_unit": 1.50,
        "equipment_slots": 3,
        "compliance_minutes_available": 120.0,
        "compliance_minutes_per_job": 60.0,
    },
    "costs": {
        "unit_variable_cost": 1500.00,
        "monthly_fixed_cost": 4000.00,
        "advertising_spend": 0.00,
    },
    "startup_ledger_sample": {
        "owner_contribution": 8000.00,
        "equipment_assets": 4200.00,
        "preopening_setup": 800.00,
        "opening_cash": 3000.00,
        "cash_reserve_floor": 600.00,
    },
    "assumptions": {
        "no_backlog": True,
        "working_days_per_month": 20,
    },
}

st.title("📊 Career Venture Lab — Team Business Dashboard")
st.caption("Course: Calculus | Pathway: FIN-1 (Financial Plan Service) | Level: Advanced")

# -----------------------------------------------------------------------------
# SIDEBAR: MODE & GOVERNANCE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Simulator Controls")
    mode = st.radio(
        "Dashboard Mode",
        [
            "Normal (Operations & Finance)",
            "Calculus Optimization Lab",
            "Seasonal (Advanced Mode)",
            "Snapshot & Governance",
        ],
    )
    st.info(
        "**No-Backlog Rule:** Unfilled client requests cannot carry over to next month—they are permanently lost.\n\n"
        "**Startup Ledger Source:** Sample Fixture ($3,000.00 opening cash)."
    )

# -----------------------------------------------------------------------------
# SHARED INPUTS (PERSISTENT ACROSS MODES)
# -----------------------------------------------------------------------------
if "price" not in st.session_state:
    st.session_state.price = DEFAULT_SNAPSHOT["offering"]["price"]
    st.session_state.D0 = DEFAULT_SNAPSHOT["demand"]["D0"]
    st.session_state.staff_hours = DEFAULT_SNAPSHOT["capacity"]["staff_hours"]
    st.session_state.hours_per_unit = DEFAULT_SNAPSHOT["capacity"]["hours_per_unit"]
    st.session_state.equipment_slots = DEFAULT_SNAPSHOT["capacity"]["equipment_slots"]
    st.session_state.comp_mins = DEFAULT_SNAPSHOT["capacity"]["compliance_minutes_available"]
    st.session_state.comp_per_job = DEFAULT_SNAPSHOT["capacity"]["compliance_minutes_per_job"]
    st.session_state.var_cost = DEFAULT_SNAPSHOT["costs"]["unit_variable_cost"]
    st.session_state.fixed_cost = DEFAULT_SNAPSHOT["costs"]["monthly_fixed_cost"]
    st.session_state.ad_spend = DEFAULT_SNAPSHOT["costs"]["advertising_spend"]

# Capacity calculations
staff_cap = math.floor(st.session_state.staff_hours / st.session_state.hours_per_unit) if st.session_state.hours_per_unit > 0 else 0
equip_cap = int(st.session_state.equipment_slots)
comp_cap = math.floor(st.session_state.comp_mins / st.session_state.comp_per_job) if st.session_state.comp_per_job > 0 else 0
q_max = min(staff_cap, equip_cap, comp_cap)

# Linear price-response model: q(p) = max(0, 2*D0 - (D0/p0)*p)
p0 = DEFAULT_SNAPSHOT["offering"]["price"]
D0_base = DEFAULT_SNAPSHOT["demand"]["D0"]
modeled_demand = max(0.0, 2 * D0_base - (D0_base / p0) * st.session_state.price)
if st.session_state.price == p0:
    modeled_demand = float(st.session_state.D0)

delivered_units = min(q_max, math.floor(modeled_demand))
lost_demand = max(0, math.floor(modeled_demand) - delivered_units)

revenue = st.session_state.price * delivered_units
total_var_cost = st.session_state.var_cost * delivered_units
total_fixed_cost = st.session_state.fixed_cost + st.session_state.ad_spend
total_cost = total_var_cost + total_fixed_cost
net_profit = revenue - total_cost
opening_cash = DEFAULT_SNAPSHOT["startup_ledger_sample"]["opening_cash"]
closing_cash = opening_cash + net_profit

# -----------------------------------------------------------------------------
# MODE 1: NORMAL (OPERATIONS & FINANCE)
# -----------------------------------------------------------------------------
if mode == "Normal (Operations & Finance)":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Operations & Capacity Module")
        st.session_state.D0 = st.number_input(
            "Requested Financial Plans (Baseline D0 at $10,000)",
            min_value=0,
            value=int(st.session_state.D0),
            step=1,
        )
        st.session_state.staff_hours = st.number_input(
            "Available Advisor Staff Hours / Month",
            min_value=0.0,
            value=float(st.session_state.staff_hours),
            step=0.5,
        )
        st.session_state.hours_per_unit = st.number_input(
            "Advisor Hours per Financial Plan",
            min_value=0.1,
            value=float(st.session_state.hours_per_unit),
            step=0.25,
        )
        st.session_state.equipment_slots = st.number_input(
            "Equipment / Software Terminal Slots / Month",
            min_value=0,
            value=int(st.session_state.equipment_slots),
            step=1,
        )
        st.session_state.comp_mins = st.number_input(
            "Compliance / Research Minutes Available / Month",
            min_value=0.0,
            value=float(st.session_state.comp_mins),
            step=15.0,
        )
        st.session_state.comp_per_job = st.number_input(
            "Compliance / Research Minutes per Plan",
            min_value=1.0,
            value=float(st.session_state.comp_per_job),
            step=5.0,
        )

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Staff Limit", f"{staff_cap} plans")
        c2.metric("Software Slots", f"{equip_cap} plans")
        c3.metric("Compliance Limit", f"{comp_cap} plans")
        st.success(f"**Max Deliverable Capacity (Q_max):** {q_max} plans/month | **Delivered:** {delivered_units} | **Lost Requests:** {lost_demand}")

    with col2:
        st.subheader("2. Finance & Pricing Module")
        st.session_state.price = st.number_input(
            "Price per Financial Plan ($ USD)",
            min_value=0.0,
            value=float(st.session_state.price),
            step=250.0,
        )
        st.session_state.var_cost = st.number_input(
            "Unit Variable Cost per Plan ($ USD)",
            min_value=0.0,
            value=float(st.session_state.var_cost),
            step=100.0,
        )
        st.session_state.fixed_cost = st.number_input(
            "Monthly Fixed Costs ($ USD)",
            min_value=0.0,
            value=float(st.session_state.fixed_cost),
            step=250.0,
        )
        st.session_state.ad_spend = st.number_input(
            "Monthly Advertising Spend ($ USD)",
            min_value=0.0,
            value=float(st.session_state.ad_spend),
            step=100.0,
        )

        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Monthly Revenue", f"${revenue:,.2f}")
        m2.metric("Total Operating Cost", f"${total_cost:,.2f}")
        m3, m4 = st.columns(2)
        m3.metric("Monthly Net Profit", f"${net_profit:,.2f}")
        m4.metric("Closing Cash (Sample Ledger)", f"${closing_cash:,.2f}")

# -----------------------------------------------------------------------------
# MODE 2: CALCULUS OPTIMIZATION LAB
# -----------------------------------------------------------------------------
elif mode == "Calculus Optimization Lab":
    st.subheader("Calculus Optimization Lab — Marginal & Average Rate Analysis")
    st.write(
        f"Evaluating continuous functions over your feasible operations domain **$0 \\le q \\le {q_max}$** "
        f"(at Price = **${st.session_state.price:,.2f}**, Variable Cost = **${st.session_state.var_cost:,.2f}**, Fixed Cost = **${total_fixed_cost:,.2f}**)."
    )

    marginal_rev = st.session_state.price
    marginal_cost = st.session_state.var_cost
    marginal_profit = marginal_rev - marginal_cost
    avg_cost_at_max = (total_fixed_cost / q_max + marginal_cost) if q_max > 0 else 0.0
    d_avg_cost_at_max = (-total_fixed_cost / (q_max ** 2)) if q_max > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Marginal Revenue R'(q)", f"${marginal_rev:,.2f} / plan")
    k2.metric("Marginal Cost C'(q)", f"${marginal_cost:,.2f} / plan")
    k3.metric("Marginal Profit P'(q)", f"${marginal_profit:,.2f} / plan")
    k4.metric("Avg Cost at Q_max", f"${avg_cost_at_max:,.2f} / plan")

    if q_max > 0:
        q_vals = np.linspace(0.1, float(q_max), 50)
        df_calc = pd.DataFrame({
            "Quantity (q)": q_vals,
            "Total Revenue R(q)": st.session_state.price * q_vals,
            "Total Cost C(q)": total_fixed_cost + st.session_state.var_cost * q_vals,
            "Total Profit P(q)": (st.session_state.price - st.session_state.var_cost) * q_vals - total_fixed_cost,
        }).set_index("Quantity (q)")
        st.line_chart(df_calc)
        st.caption(
            f"Rate of change of Average Cost at q = {q_max}: d(C_bar)/dq = -F / q^2 = ${d_avg_cost_at_max:,.2f} per plan^2."
        )

# -----------------------------------------------------------------------------
# MODE 3: SEASONAL (ADVANCED MODE)
# -----------------------------------------------------------------------------
elif mode == "Seasonal (Advanced Mode)":
    st.subheader("Advanced Seasonal Trigonometric Demand Model")
    st.write("Models monthly demand swings: $D(t, p) = q(p) \\cdot (1 + 0.20 \\cdot \\sin(2\\pi(t - 1)/12))$ for month $t \\in \\{1, \\dots, 12\\}$.")

    rows = []
    for t in range(1, 13):
        seasonal_factor = 1.0 + 0.20 * math.sin(2 * math.pi * (t - 1) / 12)
        d_t = modeled_demand * seasonal_factor
        sold_t = min(q_max, math.floor(d_t))
        rev_t = st.session_state.price * sold_t
        cost_t = total_fixed_cost + st.session_state.var_cost * sold_t
        prof_t = rev_t - cost_t
        rows.append({
            "Month (t)": t,
            "Seasonal Demand D(t)": round(d_t, 2),
            "Capacity (Q_max)": q_max,
            "Delivered Plans": sold_t,
            "Monthly Profit ($)": round(prof_t, 2),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# -----------------------------------------------------------------------------
# MODE 4: SNAPSHOT & GOVERNANCE
# -----------------------------------------------------------------------------
elif mode == "Snapshot & Governance":
    st.subheader("Human-in-the-Loop Snapshot State (Pending Review)")
    current_state = {
        "team_id": "Team Business",
        "course": "Calculus",
        "pathway": "FIN-1",
        "challenge_level": "Advanced",
        "state_version": 1,
        "approval_status": "PENDING STUDENT REVIEW",
        "offering": {"offering_id": "financial_plan", "price": round(st.session_state.price, 2)},
        "demand": {"D0": int(st.session_state.D0), "modeled_demand": round(modeled_demand, 2)},
        "capacity": {
            "staff_hours": st.session_state.staff_hours,
            "hours_per_unit": st.session_state.hours_per_unit,
            "equipment_slots": int(st.session_state.equipment_slots),
            "compliance_minutes_available": st.session_state.comp_mins,
            "compliance_minutes_per_job": st.session_state.comp_per_job,
            "derived_q_max": q_max,
        },
        "costs": {
            "unit_variable_cost": round(st.session_state.var_cost, 2),
            "monthly_fixed_cost": round(st.session_state.fixed_cost, 2),
            "advertising_spend": round(st.session_state.ad_spend, 2),
        },
        "projected_month_1": {
            "delivered_plans": delivered_units,
            "lost_requests": lost_demand,
            "revenue": round(revenue, 2),
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "opening_cash_sample": opening_cash,
            "closing_cash_sample": round(closing_cash, 2),
        },
    }
    st.json(current_state)
