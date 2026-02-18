import streamlit as st
import pandas as pd
from math import ceil


from lipidmaps.data.models.reaction import ReactionChecker, ReactionData, CompoundComponent
from lipidmaps.config import LMSD_REACTIONS_BASE_URL



# ---- Example: Your ReactionData objects ----
# reaction_list = [ReactionData(...), ReactionData(...), ...]

def reaction_to_row(r):
    """Flatten reaction row for the table."""
    return {
        "reaction_id": r.reaction_id,
        "reaction_name": r.reaction_name,
        "num_reactants": len(r.reactants),
        "num_products": len(r.products),
        "num_proteins": len(r.proteins),
        "num_pathways": len(r.pathways),
    }


def display_compound_card(compound):
    """Display a single compound as a card."""
    with st.container(border=True):
        # Main info
        st.markdown(f"**{compound.compound_name}**")
        if compound.compound_lm_id:
            st.caption(f"LM ID: `{compound.compound_lm_id}`")
        
        # System name
        if compound.compound_sys_name:
            st.markdown(f"<small>*{compound.compound_sys_name}*</small>", unsafe_allow_html=True)
        
        # Additional details in expander
        with st.expander("Details", expanded=False):
            details = {
                "ID": compound.id,
                "Type": compound.compound_type,
                "Synonyms": compound.compound_synonyms or "—",
                "Generic ID": compound.compound_generic_id or "—",
                "Abbreviation": compound.compound_abbrev or "—",
                "Chains": compound.compound_abbrev_chains or "—",
                "Headgroup": compound.compound_headgroup or "—",
            }
            for key, value in details.items():
                st.text(f"{key}: {value}")


def show_full_reaction(r: "ReactionData"):
    st.subheader(f"Reaction {r.reaction_id}: {r.reaction_name}")

    # Display Reactants and Products side-by-side
    st.markdown("### Reactants & Products")
    reactant_col, product_col = st.columns(2)
    
    with reactant_col:
        st.markdown("#### Reactants")
        if r.reactants:
            for comp in r.reactants:
                display_compound_card(comp)
        else:
            st.info("No reactants")
    
    with product_col:
        st.markdown("#### Products")
        if r.products:
            for comp in r.products:
                display_compound_card(comp)
        else:
            st.info("No products")

    # Additional reaction details
    st.markdown("---")
    
    st.markdown("### Proteins")
    if r.proteins:
        st.json(r.proteins)
    else:
        st.info("No proteins")

    st.markdown("### Curations")
    if r.curations:
        st.json(r.curations)
    else:
        st.info("No curations")

    st.markdown("### Pathways")
    if r.pathways:
        st.json(r.pathways)
    else:
        st.info("No pathways")

# @st.cache_data(ttl=60 * 60 * 2)
def fetch_all_reactions():
	"""Fetch all reactions and cache result for 2 hours."""
	reaction_checker = ReactionChecker(base_url=LMSD_REACTIONS_BASE_URL)
	return reaction_checker.check_reactions(lm_ids="all")


# Read selection from main app via st.session_state (direct access option)
selected = st.session_state.get("selected_reaction", None)
reaction_list = []

if selected:
	st.write("Selected reaction from main app:", selected)
else:
	all_reactions = fetch_all_reactions()
	reaction_list = all_reactions.reactions
     
# ---- Build Table ----
rows = [reaction_to_row(r) for r in reaction_list]
df = pd.DataFrame(rows)

# ---- Pagination ----
PAGE_SIZE = 10
total_pages = ceil(len(df) / PAGE_SIZE)

if "page" not in st.session_state:
    st.session_state.page = 1

prev_col, next_col = st.columns(2)
with prev_col:
    if st.button("⬅ Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with next_col:
    if st.button("Next ➡") and st.session_state.page < total_pages:
        st.session_state.page += 1

start = (st.session_state.page - 1) * PAGE_SIZE
end = start + PAGE_SIZE
page_df = df.iloc[start:end]

st.dataframe(page_df, use_container_width=True)

# ---- Row selection ----
selected_id = st.selectbox(
    "Select a reaction to view full details",
    page_df["reaction_id"],
)

# ---- Display full reaction ----
selected_reaction = next(r for r in reaction_list if r.reaction_id == selected_id)
show_full_reaction(selected_reaction)
