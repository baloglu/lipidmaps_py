import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
from lipidmaps.data.data_manager import DataManager

# Add src/ to sys.path to import package modules
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


st.header("LIPID MAPS Quantitative Data Demo")
st.markdown("""
Select a file from the test data directory or upload your own CSV file. Preview the file, then process it to see standardized lipid annotations.
""")

# List files in tests/data/inputs
test_data_dir = os.path.abspath(os.path.join(dir_path, '../tests/data/inputs'))
test_files = [f for f in os.listdir(test_data_dir) if f.endswith('.tsv') or f.endswith('.csv')]

st.subheader("Choose a test file or upload your own")
selected_file = st.selectbox("Select a test CSV file", ["(none)"] + test_files)
uploaded_file = st.file_uploader("Or upload a CSV file", type=["csv"])

file_to_use = None
if uploaded_file is not None:
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        file_to_use = tmp.name
elif selected_file and selected_file != "(none)":
    file_to_use = os.path.join(test_data_dir, selected_file)

if file_to_use:

    st.write("Preview of selected data:")
    try:
        _, ext = os.path.splitext(file_to_use)
        # Try reading with skiprows=1 to handle metadata in line 2
        if ext.lower() in [".tsv", ".txt"]:
            try:
                df = pd.read_csv(file_to_use, sep="\t")
            except pd.errors.ParserError:
                df = pd.read_csv(file_to_use, sep="\t", skiprows=[1])
        else:
            try:
                df = pd.read_csv(file_to_use)
            except pd.errors.ParserError:
                df = pd.read_csv(file_to_use, skiprows=[1])
        st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error reading file: {e}")

    if "dataset" not in st.session_state:
        st.session_state["dataset"] = None

    col1, col2 = st.columns(2)
    process_with_ver = col1.button("Process with verification")
    process_without_ver = col2.button("Process without verification")

    if process_with_ver or process_without_ver:
        try:
            if process_with_ver:
                mgr = DataManager(validate_data=True)
                dataset = mgr.process_csv(file_to_use)
                st.session_state["dataset"] = dataset
                # Build results table
                result_rows = []
                for lipid in dataset.lipids:
                    result_rows.append({
                        "input_name": getattr(lipid, "input_name", None),
                        "standardized_name": getattr(lipid, "standardized_name", None),
                        "lm_id": getattr(lipid, "lm_id", None),
                        "generic_lm_id": getattr(lipid, "generic_lm_id", None),
                        "refmet": getattr(lipid, "refmet_id", None),
                        "main_class": getattr(lipid, "main_class", None),
                        "sub_class": getattr(lipid, "sub_class", None),
                    })
                result_df = pd.DataFrame(result_rows)
                st.subheader("Processed Lipid Annotations")
                st.write(f"Rows: {result_df.shape[0]}, Columns: {result_df.shape[1]}")
                st.write(f"Number of LM ID's: {result_df['lm_id'].notna().sum()}")
                st.dataframe(result_df)
                
                # Display pie chart for main_classes
                if "main_class" in result_df.columns:
                    main_class_counts = result_df["main_class"].value_counts()
                    if len(main_class_counts) > 0:
                        st.subheader("Main Class Distribution")
                        fig = px.pie(values=main_class_counts.values, names=main_class_counts.index)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display pie chart for found lm_ids
                if "lm_id" in result_df.columns:
                    lm_id_counts = result_df["lm_id"].notna().value_counts()
                    if len(lm_id_counts) > 0:
                        st.subheader("LM ID Found Distribution")
                        fig = px.pie(values=lm_id_counts.values, names=["LM ID Found" if x else "LM ID Not Found" for x in lm_id_counts.index])
                        st.plotly_chart(fig, use_container_width=True)
                
                # Validation info
                if mgr.validation_report:
                    st.subheader("Validation Report (Processed)")
                    st.write(f"Passed: {mgr.validation_report.passed}")
                    st.write(f"Issues: {len(mgr.validation_report.issues)}")
                    if mgr.validation_report.issues:
                        for issue in mgr.validation_report.issues:
                            st.write(f"\t- {issue.message}")
                        # st.write(mgr.validation_report.issues)
            else:
                try:
                    from lipidmaps import process_csv
                except ImportError:
                    st.error("Could not import process_csv. Please check your package structure.")
                    st.stop()
                dataset = process_csv(file_to_use)
                st.session_state["dataset"] = dataset
                result_rows = []
                for lipid in dataset.lipids:
                    result_rows.append({
                        "input_name": getattr(lipid, "input_name", None),
                        "standardized_name": getattr(lipid, "standardized_name", None),
                        "lm_id": getattr(lipid, "lm_id", None),
                        "generic_lm_id": getattr(lipid, "generic_lm_id", None),
                        "refmet": getattr(lipid, "refmet_id", None),
                        "main_class": getattr(lipid, "main_class", None),
                        "sub_class": getattr(lipid, "sub_class", None),
                    })
                result_df = pd.DataFrame(result_rows)
                st.subheader("Processed Lipid Annotations")
                st.write(f"Rows: {result_df.shape[0]}, Columns: {result_df.shape[1]}")
                st.dataframe(result_df)
                
                # Display pie chart for main_classes
                if "main_class" in result_df.columns:
                    main_class_counts = result_df["main_class"].value_counts()
                    if len(main_class_counts) > 0:
                        st.subheader("Main Class Distribution")
                        fig = px.pie(values=main_class_counts.values, names=main_class_counts.index)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display pie chart for found lm_ids
                if "lm_id" in result_df.columns:
                    lm_id_counts = result_df["lm_id"].notna().value_counts()
                    if len(lm_id_counts) > 0:
                        st.subheader("LM ID Found Distribution")
                        fig = px.pie(values=lm_id_counts.values, names=["LM ID Found" if x else "LM ID Not Found" for x in lm_id_counts.index])
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing file: {e}")

    # Button to use headgroups for missing lm_ids
    if st.session_state.get("dataset") is not None:
        if st.button("Use headgroups for Generic LMIDs"):
            updated = st.session_state["dataset"].fill_missing_lm_ids_from_headgroups()
            st.success(f"Updated {updated} lipids using headgroup mapping.")
            # Re-display the table
            result_rows = []
            for lipid in st.session_state["dataset"].lipids:
                result_rows.append({
                    "input_name": getattr(lipid, "input_name", None),
                    "standardized_name": getattr(lipid, "standardized_name", None),
                    "lm_id": getattr(lipid, "lm_id", None),
                    "generic_lm_id": getattr(lipid, "generic_lm_id", None),
                    "refmet": getattr(lipid, "refmet_id", None),
                    "main_class": getattr(lipid, "main_class", None),
                    "sub_class": getattr(lipid, "sub_class", None),
                })
            result_df = pd.DataFrame(result_rows)
            st.subheader("Lipid Annotations After Headgroup Mapping")
            st.write(f"Rows: {result_df.shape[0]}, Columns: {result_df.shape[1]}")
            st.dataframe(result_df)
            
            # Display pie chart for main_classes
            if "main_class" in result_df.columns:
                main_class_counts = result_df["main_class"].value_counts()
                if len(main_class_counts) > 0:
                    st.subheader("Main Class Distribution")
                    fig = px.pie(values=main_class_counts.values, names=main_class_counts.index)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Display pie chart for found lm_ids
            if "lm_id" in result_df.columns:
                lm_id_counts = result_df["lm_id"].notna().value_counts()
                if len(lm_id_counts) > 0:
                    st.subheader("LM ID Found Distribution")
                    fig = px.pie(values=lm_id_counts.values, names=["LM ID Found" if x else "LM ID Not Found" for x in lm_id_counts.index])
                    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload a CSV file to begin.")
