import streamlit as st

import os
import sys

# Add src/ to sys.path to import package modules
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import DataManager from lipidmaps
try:
    from lipidmaps.data.data_manager import DataManager
except ImportError:
    st.error("Could not import DataManager. Please check your package structure.")
    st.stop()

st.title("LIPID MAPS Quantitative Data Demo")

st.markdown("""
Upload a quantitative CSV file to explore and process it using the LIPID MAPS package.
""")


uploaded_file = st.file_uploader("Upload quantitative CSV file", type=["csv"])

if uploaded_file:
    try:
        # Save uploaded file to a temporary location
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        st.write("Preview of uploaded data:")
        import pandas as pd
        df = pd.read_csv(tmp_path)
        st.dataframe(df.head())

        st.subheader("LIPID MAPS DataManager Demo")
        mgr = DataManager()
        dataset = mgr.process_csv(tmp_path)


        # List samples
        if st.checkbox("List samples"):
            st.write(dataset.list_samples())

        # List lipids
        if st.checkbox("List lipids"):
            st.write(dataset.list_lipids())

        # List lipids with LMID
        if st.checkbox("List lipids with LMID"):
            st.write(dataset.list_lipids_with_lmid())

        # List lipids with reactions
        if st.checkbox("List lipids with reactions"):
            st.write(dataset.list_lipids_with_reactions())

        # Show lipids with reactions (full objects)
        if st.checkbox("Show lipids with reactions (details)"):
            lipids = dataset.get_lipids_with_reactions()
            for l in lipids:
                st.markdown("---")
                st.write({
                    "Input name": l.input_name,
                    "LM ID": l.lm_id,
                    "Reactions": [r.reaction_name for r in (l.reactions or [])],
                    "Values": l.values
                })

        # Lipid info search (find_lipids)
        search = st.text_input("Search lipid info (name or substring)")
        if search:
            matches = dataset.find_lipids(search)
            if not matches:
                st.warning(f"No lipids matching '{search}' found.")
            else:
                for m in matches:
                    st.markdown("---")
                    st.write({
                        "Input name": m.input_name,
                        "Recognized": bool(m.standardized_name or m.lm_id),
                        "Standardized name": m.standardized_name,
                        "LM ID": m.lm_id,
                        "Values": m.values
                    })

        # Get value for a specific lipid/sample
        with st.expander("Get value for lipid/sample"):
            lipid_id = st.text_input("Lipid LMID for value lookup", key="lipid_id_lookup")
            sample_id = st.text_input("Sample ID for value lookup", key="sample_id_lookup")
            if lipid_id and sample_id:
                value = dataset.get_value(lipid_id, sample_id)
                st.write(f"Value for lipid {lipid_id} in sample {sample_id}: {value}")

        # Show grouped data
        if st.checkbox("Show grouped data (by sample group)"):
            grouped = dataset.get_grouped_data()
            for group, lipids in grouped.items():
                st.markdown(f"### Group: {group}")
                for l in lipids:
                    st.write({"Input name": l.input_name, "Values": l.values})

        # Show lipid x sample table
        if st.checkbox("Show lipid x sample table"):
            samples = dataset.list_samples()
            table = []
            for lipid in dataset.lipids:
                row = {"Lipid": lipid.input_name}
                for s in samples:
                    v = lipid.values.get(s)
                    row[s] = v if v is not None else ""
                table.append(row)
            st.dataframe(pd.DataFrame(table))

        # Clean up temp file
        os.remove(tmp_path)
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV file to begin.")
