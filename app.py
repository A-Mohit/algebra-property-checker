import streamlit as st
import pandas as pd
import itertools
import re

st.set_page_config(page_title="Algebraic Theorem Engine", page_icon="📐")

st.title("📐 Algebraic Theorem Verification Engine")

# -----------------------------
# Session Storage
# -----------------------------
if "custom_theorems" not in st.session_state:
    st.session_state.custom_theorems = []

# -----------------------------
# Standard Theorems
# -----------------------------
STANDARD_THEOREMS = [
    {"name":"Commutativity of θ","vars":2,"lhs":"theta(x,y)","rhs":"theta(y,x)"},
    {"name":"Commutativity of φ","vars":2,"lhs":"phi(x,y)","rhs":"phi(y,x)"},
    {"name":"Associativity of θ","vars":3,"lhs":"theta(x,theta(y,z))","rhs":"theta(theta(x,y),z)"},
    {"name":"Associativity of φ","vars":3,"lhs":"phi(x,phi(y,z))","rhs":"phi(phi(x,y),z)"},
    {"name":"Left Distributive","vars":3,"lhs":"theta(x,phi(y,z))","rhs":"phi(theta(x,y),theta(x,z))"},
    {"name":"Right Distributive","vars":3,"lhs":"theta(phi(x,y),z)","rhs":"phi(theta(x,z),theta(y,z))"},
]

# -----------------------------
# Expression Helpers
# -----------------------------
def replace_expr(expr):
    expr = expr.replace("theta(", "theta_func(")
    expr = expr.replace("phi(", "phi_func(")
    return expr

def extract_operations(expr):
    pattern = r'(theta|phi)\(([^()]+)\)'
    return re.findall(pattern, expr)

def show_steps(expr,x,y,z):

    ops = extract_operations(expr)

    steps=[]

    for op,args in ops:

        a,b = [v.strip() for v in args.split(",")]

        va = {"x":x,"y":y,"z":z}.get(a,a)
        vb = {"x":x,"y":y,"z":z}.get(b,b)

        if op=="theta":
            res = theta_func(va,vb)
        else:
            res = phi_func(va,vb)

        steps.append(f"{op}({va},{vb}) = {res}")

    return steps

# -----------------------------
# Input Set
# -----------------------------
elements = st.text_input("Enter elements of Set L (comma separated)","a,b")

if elements:

    L=[e.strip() for e in elements.split(",")]

    st.subheader("θ (Theta) Operation Table")

    theta_df = st.data_editor(
        pd.DataFrame("", index=L, columns=L),
        key="theta_table"
    )


    st.subheader("φ (Phi) Operation Table")

    phi_df = st.data_editor(
        pd.DataFrame("", index=L, columns=L),
        key="phi_table"
    )


    # -----------------------------
    # Add Custom Theorem
    # -----------------------------
    st.markdown("---")
    st.header("➕ Add Custom Theorem")

    name = st.text_input("Theorem Name")

    vars_count = st.selectbox("Number of Variables",[2,3])

    lhs = st.text_input("LHS Expression (Example: theta(x,y))")

    rhs = st.text_input("RHS Expression (Example: theta(y,x))")

    if st.button("Add Custom Theorem"):

        if name and lhs and rhs:

            st.session_state.custom_theorems.append(
                {"name":name,"vars":vars_count,"lhs":lhs,"rhs":rhs}
            )

            st.success("Theorem Added")

    # -----------------------------
    # Combine Theorems
    # -----------------------------
    ALL_THEOREMS = STANDARD_THEOREMS + st.session_state.custom_theorems

    st.markdown("---")

    st.header("📚 Select Theorems to Verify")

    selected = st.multiselect(
        "Choose Theorems",
        [t["name"] for t in ALL_THEOREMS]
    )

    selected_theorems = [t for t in ALL_THEOREMS if t["name"] in selected]

    # -----------------------------
    # Verify
    # -----------------------------
    if st.button("🔍 Verify Selected Theorems"):

        if (theta_df=="").values.any() or (phi_df=="").values.any():
            st.error("Fill all operation tables")
            st.stop()

        theta={(i,j):theta_df.loc[i,j] for i in L for j in L}
        phi={(i,j):phi_df.loc[i,j] for i in L for j in L}

        def theta_func(a,b):
            return theta[(a,b)]

        def phi_func(a,b):
            return phi[(a,b)]

        st.markdown("## 📊 Results")

        for th in selected_theorems:

            st.markdown("---")

            st.subheader(th["name"])

            st.latex(f"{th['lhs']} = {th['rhs']}")

            failed=False

            if th["vars"]==2:
                combos=itertools.product(L,L)
            else:
                combos=itertools.product(L,L,L)

            for combo in combos:

                if th["vars"]==2:
                    x,y=combo
                    z=None
                else:
                    x,y,z=combo

                lhs_val = eval(
                    replace_expr(th["lhs"]),
                    {},
                    {"theta_func":theta_func,"phi_func":phi_func,"x":x,"y":y,"z":z}
                )

                rhs_val = eval(
                    replace_expr(th["rhs"]),
                    {},
                    {"theta_func":theta_func,"phi_func":phi_func,"x":x,"y":y,"z":z}
                )

                if lhs_val != rhs_val:

                    st.error(f"Failed at x={x}, y={y}, z={z}")

                    st.write("### Step-by-Step Solution")

                    st.write("LHS Steps")

                    for s in show_steps(th["lhs"],x,y,z):
                        st.latex(s)

                    st.write("RHS Steps")

                    for s in show_steps(th["rhs"],x,y,z):
                        st.latex(s)

                    st.latex(f"LHS = {lhs_val}")

                    st.latex(f"RHS = {rhs_val}")

                    st.latex(f"{lhs_val} \\neq {rhs_val}")

                    failed=True
                    break

            if not failed:
                st.success("✅ Verified")

        st.markdown("---")
        st.caption("Developed by Mohit Adhikari 🚀")

