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

def show_full_reaction(r: "ReactionData"):
    st.subheader(f"Reaction {r.reaction_id}: {r.reaction_name}")

    st.markdown("### Reactants")
    for comp in r.reactants:
        st.json(comp.__dict__)

    st.markdown("### Products")
    for comp in r.products:
        st.json(comp.__dict__)

    st.markdown("### Proteins")
    st.json(r.proteins)

    st.markdown("### Curations")
    st.json(r.curations)

    st.markdown("### Pathways")
    st.json(r.pathways)

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

prev, next = st.columns(2)
with prev:
    if st.button("⬅ Previous") and st.session_state.page > 1:
        st.session_state.page -= 1
with next:
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
