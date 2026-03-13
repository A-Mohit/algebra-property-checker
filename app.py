import streamlit as st
import pandas as pd
import itertools

st.set_page_config(page_title="Algebraic Theorem Engine", page_icon="📐")

st.title("📐 Algebraic Theorem Verification Engine")

# -----------------------------
# Initialize Session Storage
# -----------------------------
if "custom_theorems" not in st.session_state:
    st.session_state.custom_theorems = []

# -----------------------------
# Preloaded Standard Theorems
# -----------------------------
STANDARD_THEOREMS = [
    {"name": "Idempotent Law",
     "vars": 1,
     "lhs": "theta(x,x)",
     "rhs": "x"},

    {"name": "Idempotent Law (phi)",
     "vars": 1,
     "lhs": "phi(x,x)",
     "rhs": "x"},

    {"name": "Commutativity of θ",
     "vars": 2,
     "lhs": "theta(x,y)",
     "rhs": "theta(y,x)"},

    {"name": "Commutativity of φ",
     "vars": 2,
     "lhs": "phi(x,y)",
     "rhs": "phi(y,x)"},

    {"name": "Associativity of θ",
     "vars": 3,
     "lhs": "theta(x,theta(y,z))",
     "rhs": "theta(theta(x,y),z)"},

    {"name": "Associativity of φ",
     "vars": 3,
     "lhs": "phi(x,phi(y,z))",
     "rhs": "phi(phi(x,y),z)"},

    {"name": "Left Distributive (θ over φ)",
     "vars": 3,
     "lhs": "theta(x,phi(y,z))",
     "rhs": "phi(theta(x,y),theta(x,z))"},

    {"name": "Right Distributive (θ over φ)",
     "vars": 3,
     "lhs": "theta(phi(x,y),z)",
     "rhs": "phi(theta(x,z),theta(y,z))"},

    {"name": "Absorption Law 1",
     "vars": 2,
     "lhs": "theta(x,phi(x,y))",
     "rhs": "x"},

    {"name": "Absorption Law 2",
     "vars": 2,
     "lhs": "phi(x,theta(x,y))",
     "rhs": "x"},
]

# -----------------------------
# Input Set
# -----------------------------
elements = st.text_input("Enter elements of Set L (comma separated)", "0,a,b")

if elements:
    L = [x.strip() for x in elements.split(",")]

    st.subheader("θ (Theta) Operation Table")
    theta_df = st.data_editor(pd.DataFrame("", index=L, columns=L), key="theta")

    st.subheader("φ (Phi) Operation Table")
    phi_df = st.data_editor(pd.DataFrame("", index=L, columns=L), key="phi")

    # -----------------------------
    # Add Custom Theorem
    # -----------------------------
    st.markdown("---")
    st.header("➕ Add Custom Theorem")

    name = st.text_input("Theorem Name")
    var_count = st.selectbox("Number of Variables", [1,2,3])
    lhs = st.text_input("LHS Expression (Example: theta(x,y))")
    rhs = st.text_input("RHS Expression (Example: theta(y,x))")

    if st.button("Add Custom Theorem"):
        if name and lhs and rhs:
            st.session_state.custom_theorems.append({
                "name": name,
                "vars": var_count,
                "lhs": lhs,
                "rhs": rhs
            })
            st.success("Custom Theorem Added!")

    # -----------------------------
    # Combine Theorems
    # -----------------------------
    ALL_THEOREMS = STANDARD_THEOREMS + st.session_state.custom_theorems

    st.markdown("---")
    st.header("📚 Select Theorems to Verify")

    selected_names = st.multiselect(
        "Choose Theorems",
        [th["name"] for th in ALL_THEOREMS]
    )

    selected_theorems = [th for th in ALL_THEOREMS if th["name"] in selected_names]

# helper functions
import re

def replace_expr(expr):
    expr = expr.replace("theta", "theta_func")
    expr = expr.replace("phi", "phi_func")
    return expr

def extract_ops(expr):
    pattern = r'(theta|phi)\(([^()]+)\)'
    return re.findall(pattern, expr)

def show_steps(expr, x=None, y=None, z=None):
    steps = []
    ops = extract_ops(expr)

    for op,args in ops:
        args = args.split(',')
        values = []

        for a in args:
            a=a.strip()
            if a=='x':
                values.append(x)
            elif a=='y':
                values.append(y)
            elif a=='z':
                values.append(z)
            else:
                values.append(a)

        if op=='theta':
            res = theta_func(values[0],values[1])
            steps.append(f"{op}({values[0]},{values[1]}) = {res}")
        else:
            res = phi_func(values[0],values[1])
            steps.append(f"{op}({values[0]},{values[1]}) = {res}")

    return steps
    # -----------------------------
    # Verification
    # -----------------------------
    if st.button("🔍 Verify Selected Theorems"):

        if (theta_df == "").values.any() or (phi_df == "").values.any():
            st.error("Please fill operation tables.")
            st.stop()

        theta = {(i,j): theta_df.loc[i,j] for i in L for j in L}
        phi   = {(i,j): phi_df.loc[i,j] for i in L for j in L}

        def theta_func(a,b):
            return theta[(a,b)]

        def phi_func(a,b):
            return phi[(a,b)]

        def evaluate(expr, x=None, y=None, z=None):
            expr = expr.replace("theta", "theta_func")
            expr = expr.replace("phi", "phi_func")
            return eval(expr)

        st.markdown("## 📊 Results")

for th in selected_theorems:

    st.markdown("---")
    st.subheader(f"🧾 {th['name']}")
    st.latex(f"{th['lhs']} = {th['rhs']}")

    failed = False

    if th["vars"] == 2:
        combos = itertools.product(L,L)
    elif th["vars"] == 3:
        combos = itertools.product(L,L,L)
    else:
        combos = [(x,) for x in L]

    for combo in combos:

        if len(combo)==1:
            x=combo[0]; y=None; z=None
        elif len(combo)==2:
            x,y=combo; z=None
        else:
            x,y,z=combo

        lhs_val = eval(replace_expr(th["lhs"]))
        rhs_val = eval(replace_expr(th["rhs"]))

        if lhs_val != rhs_val:

            st.error(f"❌ Failed at x={x}, y={y}, z={z}")

            st.write("### Step-by-Step Solution")

            st.write("**LHS Steps**")
            for step in show_steps(th["lhs"],x,y,z):
                st.latex(step)

            st.write("**RHS Steps**")
            for step in show_steps(th["rhs"],x,y,z):
                st.latex(step)

            st.latex(f"LHS = {lhs_val}")
            st.latex(f"RHS = {rhs_val}")
            st.latex(f"{lhs_val} \\neq {rhs_val}")

            failed = True
            break

    if not failed:
        st.success("✅ Verified")

# import streamlit as st
# import pandas as pd
# import itertools

# st.set_page_config(
#     page_title="Algebraic Property Checker",
#     page_icon="📐",
#     layout="centered"
# )
# st.title("Algebraic Structure Property Evaluator")

# # -------- Input Set --------
# elements = st.text_input("Enter elements of Set L (comma separated)", "0,a,b")

# if elements:
#     L = [x.strip() for x in elements.split(",")]

#     st.subheader("θ (Theta) Operation Table")
#     theta_df = st.data_editor(
#         pd.DataFrame("", index=L, columns=L),
#         key="theta"
#     )

#     st.subheader("φ (Phi) Operation Table")
#     phi_df = st.data_editor(
#         pd.DataFrame("", index=L, columns=L),
#         key="phi"
#     )

#     if st.button("Evaluate Properties"):

#         # -------- Validation --------
#         if theta_df.isnull().values.any() or phi_df.isnull().values.any() or (theta_df == "").values.any() or (phi_df == "").values.any():
#             st.error("❌ Please fill all cells in both tables.")
#             st.stop()

#         theta = {}
#         phi = {}

#         for i in L:
#             for j in L:
#                 theta[(i,j)] = theta_df.loc[i,j]
#                 phi[(i,j)] = phi_df.loc[i,j]

#         # -------- Property Checks --------

#         def check_property(name, condition_func):
#             for x,y,z in itertools.product(L,L,L):
#                 valid, message = condition_func(x,y,z)
#                 if not valid:
#                     st.error(f"❌ {name} Failed for (x={x}, y={y}, z={z})")
#                     st.write("Details:", message)
#                     return False
#             st.success(f"✅ {name} Satisfied")
#             return True

#         # Property 1
#         def prop1(x,y,z):
#             if theta[(x,x)] != x or phi[(x,x)] != x:
#                 return False, f"x={x}, θ(x,x)={theta[(x,x)]}, φ(x,x)={phi[(x,x)]}"
#             return True, ""

#         # Property 2
#         def prop2(x,y,z):
#             left = theta[(x, phi[(y,z)])]
#             right = phi[(theta[(x,y)], theta[(x,z)])]
#             return (left == right, f"LHS={left}, RHS={right}")

#         # Property 3 (Associativity θ)
#         def prop3(x,y,z):
#             left = theta[(x, theta[(y,z)])]
#             right = theta[(theta[(x,y)], z)]
#             return (left == right, f"LHS={left}, RHS={right}")

#         # Property 4
#         def prop4(x,y,z):
#             left = phi[(x, theta[(y,z)])]
#             right = theta[(phi[(x,y)], phi[(x,z)])]
#             return (left == right, f"LHS={left}, RHS={right}")

#         # Property 5
#         def prop5(x,y,z):
#             left = theta[(phi[(x,y)], z)]
#             right = phi[(theta[(x,z)], theta[(y,z)])]
#             return (left == right, f"LHS={left}, RHS={right}")

#         st.subheader("Results")

#         # Property 1 separately
#         p1_ok = True
#         for x in L:
#             if theta[(x,x)] != x or phi[(x,x)] != x:
#                 st.error(f"❌ Property 1 Failed for x={x}")
#                 p1_ok = False
#                 break
#         if p1_ok:
#             st.success("✅ Property 1 Satisfied")

#         check_property("Property 2", prop2)
#         check_property("Property 3 (θ Associative)", prop3)
#         check_property("Property 4", prop4)

#         check_property("Property 5", prop5)

