import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
from lipidmaps.data.data_manager import DataManager

# ---------------------- BOOTSTRAP ----------------------
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

st.set_page_config(
    page_title="LIPID MAPS Quantitative Data Demo",
    page_icon="LM",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("Quantitative Data Demo")
st.markdown("""
Use the sidebar to select a file or upload your CSV.  
Process the file to see standardized lipid annotations.
""")

# ---------------------- SESSION DEFAULTS ----------------------
defaults = {
    "file_to_use": None,
    "dataset": None,
    "processed": False,
    "validation_issues": [],
    "validation_passed": None,
    "has_validation_report": False,
    "show_all_issues": False,
    "show_validation_section": True,
    "reactions": [],              # persistent reactions
}

for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------------- SIDEBAR ----------------------
process = False
generic_lm_id_button = False
fetch_reactions_button = False
validate_data = False

with st.sidebar:
    st.title("LIPID MAPS Processing")

    # ---- FILE selection ----
    with st.expander("File", expanded=True):
        test_data_dir = os.path.abspath(os.path.join(dir_path, '../tests/data/inputs/demo'))
        try:
            test_files = [f for f in os.listdir(test_data_dir)
                          if f.endswith((".tsv", ".csv"))]
        except:
            test_files = []
            st.warning(f"Test data directory not found: {test_data_dir}")

        selected_file = st.selectbox("Select test data", ["(none)"] + test_files)
        uploaded_file = st.file_uploader("Or upload CSV", type=["csv"])

        file_to_use = None
        if uploaded_file:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.read())
                file_to_use = tmp.name
        elif selected_file != "(none)":
            file_to_use = os.path.join(test_data_dir, selected_file)

        st.session_state["file_to_use"] = file_to_use

    # ---- OPTIONS ----
    with st.expander("Options", expanded=True):
        file_chosen = bool(st.session_state["file_to_use"])
        verification = st.selectbox(
            "Data Verification",
            ["With Verification", "Without Verification"],
            index=0,
            disabled=not file_chosen,
        )
        validate_data = (verification == "With Verification") if file_chosen else False

        process = st.button("Standardize with Refmet", disabled=not file_chosen)

    # ---- TOOLS ----
    with st.expander("Tools", expanded=True):
        processed_flag = bool(st.session_state["processed"])

        generic_lm_id_button = st.button("Assign Generic LMIDs",
                                         disabled=not processed_flag)

        fetch_reactions_button = st.button("Fetch reactions by LM ID",
                                          disabled=not processed_flag)

    # ---- VIEW ----
    with st.expander("View", expanded=True):
        st.session_state["show_validation_section"] = st.checkbox(
            "Show Validation Report",
            value=st.session_state["show_validation_section"]
        )

# ---------------------- TABS ----------------------
tab_labels = ["Preview", "Processed", "Reactions", "Validation"]
tabs = st.tabs(tab_labels)
tab_index = {name.lower(): i for i, name in enumerate(tab_labels)}

# --------------------------------------------------------------
# PREVIEW TAB
# --------------------------------------------------------------
with tabs[tab_index["preview"]]:
    if not st.session_state["file_to_use"]:
        st.info("Please select or upload a file to preview.")
    else:
        st.subheader("Preview of Selected Data")

        fp = st.session_state["file_to_use"]
        try:
            _, ext = os.path.splitext(fp)
            if ext.lower() in [".tsv", ".txt"]:
                try:
                    df = pd.read_csv(fp, sep="\t")
                except pd.errors.ParserError:
                    df = pd.read_csv(fp, sep="\t", skiprows=[1])
            else:
                try:
                    df = pd.read_csv(fp)
                except pd.errors.ParserError:
                    df = pd.read_csv(fp, skiprows=[1])

            st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error reading file: {e}")

# --------------------------------------------------------------
# PROCESSING ACTION
# --------------------------------------------------------------
if process and st.session_state["file_to_use"]:
    try:
        fp = st.session_state["file_to_use"]

        if validate_data:
            mgr = DataManager(validate_data=True)
            dataset = mgr.process_csv(fp)
        else:
            from lipidmaps import process_csv
            dataset = process_csv(fp)

        st.session_state["dataset"] = dataset
        st.session_state["processed"] = True
        st.session_state["reactions"] = []  # clear old reactions

        if validate_data and getattr(mgr, "validation_report", None):
            vr = mgr.validation_report
            st.session_state["validation_passed"] = vr.passed
            st.session_state["validation_issues"] = vr.issues or []
            st.session_state["has_validation_report"] = True
        else:
            st.session_state["has_validation_report"] = False
            st.session_state["validation_issues"] = []

        st.rerun()   # important

    except Exception as e:
        st.error(f"Error processing file: {e}")

# --------------------------------------------------------------
# PROCESSED TAB — ALWAYS RENDER
# --------------------------------------------------------------
with tabs[tab_index["processed"]]:
    dataset = st.session_state.get("dataset")

    if not dataset:
        st.info("No processed dataset yet.")
    else:
        st.subheader("Processed Lipid Annotations")

        # Build DataFrame and keep mapping to lipid objects
        lipid_rows = []
        for idx, lipid in enumerate(dataset.lipids):
            lipid_rows.append({
                "index": idx,
                "input_name": getattr(lipid, "input_name", None),
                "standardized_name": getattr(lipid, "standardized_name", None),
                "lm_id": getattr(lipid, "lm_id", None),
                "generic_lm_id": getattr(lipid, "generic_lm_id", None),
                "refmet": getattr(lipid, "refmet_id", None),
                "main_class": getattr(lipid, "main_class", None),
                "sub_class": getattr(lipid, "sub_class", None),
            })
        df_proc = pd.DataFrame(lipid_rows)

        st.write(f"Rows: {df_proc.shape[0]}, Columns: {df_proc.shape[1]}")
        # Show the table (read-only) and provide a selection control underneath.
        st.dataframe(df_proc)

        # Simple per-sample listing using dataset helper
        st.subheader("Per-sample lipid values")
        sample_opts = [s.sample_id for s in dataset.samples] if getattr(dataset, 'samples', None) else []
        if sample_opts:
            sample_sel = st.selectbox("Select sample to list lipid values", sample_opts, key="sample_list_select")
            data = dataset.get_lipid_values_for_samples(sample_sel)
            # display array of objects as bar chart and table
            try:
                df_vals = pd.DataFrame([d for d in data if d.get("value") is not None])
            except Exception:
                df_vals = pd.DataFrame(data)

            if df_vals.empty:
                st.info(f"No lipid values for sample {sample_sel}.")
            else:
                fig = px.bar(df_vals, x="input_name", y="value", title=f"Lipid values for sample {sample_sel}")
                fig.update_layout(xaxis_title="Lipid", yaxis_title="Value", xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_vals)
        else:
            st.info("No samples available in dataset.")

        # Mean value per main class for selected sample
        if sample_opts:
            st.subheader("Mean value per Main Class")
            try:
                main_classes = df_proc["main_class"].dropna().unique().tolist()
            except Exception:
                main_classes = []

            class_rows = []
            for mc in main_classes:
                class_lipids = [l for l in dataset.lipids if getattr(l, "main_class", None) == mc]
                if not class_lipids:
                    continue
                mean_val = dataset.mean_value_for_lipids(sample_sel, class_lipids, skip_missing=True)
                class_rows.append({"main_class": mc, "mean_value": mean_val})

            if class_rows:
                df_class = pd.DataFrame(class_rows).sort_values(by="mean_value", ascending=False)
                fig = px.bar(df_class, x="main_class", y="mean_value", title=f"Mean per main class for sample {sample_sel}")
                fig.update_layout(xaxis_title="Main class", yaxis_title="Mean value", xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_class)
            else:
                st.info("No main class information available to compute means.")

        # Provide a stable selection UI (selectbox) for choosing a lipid to view sample values bar chart
        options = [f"{i}: {getattr(l, 'input_name', '')}" for i, l in enumerate(dataset.lipids)]
        if options:
            sel = st.selectbox("Select lipid to view sample values bar chart", options, key="lipid_select")
            try:
                selected_idx = int(sel.split(":", 1)[0])
            except Exception:
                selected_idx = None
            if selected_idx is not None:
                st.session_state["selected_lipid_idx"] = selected_idx
                lipid = dataset.lipids[selected_idx]
                st.subheader(f"Sample values bar chart for: {lipid.input_name}")

                # Build bar chart of quantitation values
                values = getattr(lipid, "values", {}) or {}
                if values:
                    try:
                        sample_order = [s.sample_id for s in dataset.samples]
                    except Exception:
                        sample_order = list(values.keys())

                    rows = []
                    for sid in sample_order:
                        if sid in values:
                            rows.append({"sample": sid, "value": values[sid]})
                    if not rows:
                        rows = [{"sample": k, "value": v} for k, v in values.items()]

                    df_vals = pd.DataFrame(rows)
                    fig = px.bar(df_vals, x="sample", y="value", title=f"Quantitation for {lipid.input_name}")
                    fig.update_layout(xaxis_title="Sample", yaxis_title="Value")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No quantitation values available for this lipid.")
        else:
            st.info("No lipids available to select.")

        # ---- Pie Charts ----

        # Main class
        if "main_class" in df_proc:
            counts = df_proc["main_class"].value_counts()
            if len(counts) > 0:
                st.subheader("Main Class Distribution")
                fig = px.pie(values=counts.values, names=counts.index)
                st.plotly_chart(fig, use_container_width=True)

        # LMID Found
        if "lm_id" in df_proc:
            lm_counts = df_proc["lm_id"].notna().value_counts()
            if len(lm_counts) > 0:
                st.subheader("LM ID Found Distribution")
                fig = px.pie(values=lm_counts.values,
                             names=["LM ID Found" if x else "Not Found" for x in lm_counts.index])
                st.plotly_chart(fig, use_container_width=True)

        # Generic LMID
        if "generic_lm_id" in df_proc:
            gen_counts = df_proc["generic_lm_id"].notna().value_counts()
            if len(gen_counts) > 0:
                st.subheader("Generic LM ID Found Distribution")
                fig = px.pie(values=gen_counts.values,
                             names=["Found" if x else "Not Found" for x in gen_counts.index])
                st.plotly_chart(fig, use_container_width=True)

        # Neither LMID nor Generic LMID
        if "lm_id" in df_proc and "generic_lm_id" in df_proc:
            neither = (~df_proc["lm_id"].notna()) & (~df_proc["generic_lm_id"].notna())
            neither_counts = neither.value_counts()
            if len(neither_counts) > 0:
                st.subheader("Neither LM ID nor Generic LM ID Found")
                fig = px.pie(values=neither_counts.values,
                             names=["Neither Found" if x else "At Least One Found"
                                    for x in neither_counts.index])
                st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------------------
# GENERIC LMID ASSIGNMENT
# --------------------------------------------------------------
if generic_lm_id_button and st.session_state["dataset"] is not None:
    ds = st.session_state["dataset"]
    updated = ds.fill_missing_lm_ids_from_headgroups()
    st.success(f"Updated {updated} lipids using headgroup mapping.")
    st.rerun()  # refresh processed page


# --------------------------------------------------------------
# REACTIONS TAB
# --------------------------------------------------------------
if fetch_reactions_button and st.session_state["dataset"] is not None:
    ds = st.session_state["dataset"]
    mgr = DataManager()

    try:
        reactions = mgr.fetch_reactions_for_lm_ids(ds, reaction_type="species-level")
        st.session_state["reactions"] = reactions

        # annotate dataset with reactions (optional)
        mgr.annotate_lipids_with_reactions(ds, reactions)

        st.success(f"Fetched {len(reactions)} reactions.")
        st.rerun()  # IMPORTANT: stable, never clears processed page
    except Exception as e:
        st.error(f"Error fetching reactions: {e}")

with tabs[tab_index["reactions"]]:
    st.subheader("Reactions for LM IDs")
    if not st.session_state["reactions"]:
        st.info("No reactions fetched yet. Use Tools → Fetch reactions by LM ID.")
    else:
        # Build reactions table, handling pathway dicts or objects
        rxn_df = pd.DataFrame([{
            "reaction_id": r.reaction_id,
            "reaction_name": r.reaction_name,
            "reactants": ", ".join(getattr(c, "compound_lm_id", "") for c in getattr(r, "reactants", [])),
            "products": ", ".join(getattr(c, "compound_lm_id", "") for c in getattr(r, "products", [])),
            "pathways": ", ".join(
                (p.get("name") if isinstance(p, dict) else getattr(p, "pathway_name", ""))
                for p in getattr(r, "pathways", [])
            ),
            "ec_number": ", ".join(
                (p.get("ec_number") if isinstance(p, dict) else getattr(p, "ec_number", ""))
                for p in getattr(r, "proteins", [])
            ),
        } for r in st.session_state["reactions"]])

        st.dataframe(rxn_df)

        # Show lipids annotated with reactions
        dataset = st.session_state.get("dataset")
        if dataset:
            lipids_with_rxn = dataset.get_lipids_with_reactions()
            if lipids_with_rxn:
                st.subheader("Lipids Annotated with Reactions")

                lip_df = pd.DataFrame([{
                    "input_name": getattr(lip, "input_name", None),
                    "lm_id": getattr(lip, "lm_id", None),
                    "reactions": ", ".join(getattr(r, "reaction_name", "") for r in (lip.reactions or [])),
                } for lip in lipids_with_rxn])

                st.dataframe(lip_df)
            else:
                st.info("No lipids in the dataset have reactions.")


# --------------------------------------------------------------
# VALIDATION TAB
# --------------------------------------------------------------
with tabs[tab_index["validation"]]:
    if not st.session_state["show_validation_section"]:
        st.info("Validation report is hidden.")
    elif not st.session_state["has_validation_report"]:
        st.info("Run processing with verification enabled.")
    else:
        st.subheader("Validation Report")
        st.write(f"Passed: {st.session_state['validation_passed']}")

        issues = st.session_state["validation_issues"]
        st.write(f"Issues: {len(issues)}")

        show_all = st.checkbox("Show all issues", key="show_all_issues")
        to_show = issues if show_all else issues[:5]

        for issue in to_show:
            st.write("-", getattr(issue, "message", str(issue)))

        if len(issues) > 5 and not show_all:
            st.write(f"...and {len(issues) - 5} more.")