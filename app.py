import streamlit as st
import pandas as pd
import itertools

st.set_page_config(
    page_title="Algebraic Property Checker",
    page_icon="📐",
    layout="centered"
)
st.title("Algebraic Structure Property Evaluator")

# -------- Input Set --------
elements = st.text_input("Enter elements of Set L (comma separated)", "0,a,b")

if elements:
    L = [x.strip() for x in elements.split(",")]

    st.subheader("θ (Theta) Operation Table")
    theta_df = st.data_editor(
        pd.DataFrame("", index=L, columns=L),
        key="theta"
    )

    st.subheader("φ (Phi) Operation Table")
    phi_df = st.data_editor(
        pd.DataFrame("", index=L, columns=L),
        key="phi"
    )

    if st.button("Evaluate Properties"):

        # -------- Validation --------
        if theta_df.isnull().values.any() or phi_df.isnull().values.any() or (theta_df == "").values.any() or (phi_df == "").values.any():
            st.error("❌ Please fill all cells in both tables.")
            st.stop()

        theta = {}
        phi = {}

        for i in L:
            for j in L:
                theta[(i,j)] = theta_df.loc[i,j]
                phi[(i,j)] = phi_df.loc[i,j]

        # -------- Property Checks --------

        def check_property(name, condition_func):
            for x,y,z in itertools.product(L,L,L):
                valid, message = condition_func(x,y,z)
                if not valid:
                    st.error(f"❌ {name} Failed for (x={x}, y={y}, z={z})")
                    st.write("Details:", message)
                    return False
            st.success(f"✅ {name} Satisfied")
            return True

        # Property 1
        def prop1(x,y,z):
            if theta[(x,x)] != x or phi[(x,x)] != x:
                return False, f"x={x}, θ(x,x)={theta[(x,x)]}, φ(x,x)={phi[(x,x)]}"
            return True, ""

        # Property 2
        def prop2(x,y,z):
            left = theta[(x, phi[(y,z)])]
            right = phi[(theta[(x,y)], theta[(x,z)])]
            return (left == right, f"LHS={left}, RHS={right}")

        # Property 3 (Associativity θ)
        def prop3(x,y,z):
            left = theta[(x, theta[(y,z)])]
            right = theta[(theta[(x,y)], z)]
            return (left == right, f"LHS={left}, RHS={right}")

        # Property 4
        def prop4(x,y,z):
            left = phi[(x, theta[(y,z)])]
            right = theta[(phi[(x,y)], phi[(x,z)])]
            return (left == right, f"LHS={left}, RHS={right}")

        # Property 5
        def prop5(x,y,z):
            left = theta[(phi[(x,y)], z)]
            right = phi[(theta[(x,z)], theta[(y,z)])]
            return (left == right, f"LHS={left}, RHS={right}")

        st.subheader("Results")

        # Property 1 separately
        p1_ok = True
        for x in L:
            if theta[(x,x)] != x or phi[(x,x)] != x:
                st.error(f"❌ Property 1 Failed for x={x}")
                p1_ok = False
                break
        if p1_ok:
            st.success("✅ Property 1 Satisfied")

        check_property("Property 2", prop2)
        check_property("Property 3 (θ Associative)", prop3)
        check_property("Property 4", prop4)
        check_property("Property 5", prop5)