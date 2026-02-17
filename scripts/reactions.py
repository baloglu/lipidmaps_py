import streamlit as st
from lipidmaps.data.models import reaction
from lipidmaps.config import LMSD_REACTIONS_BASE_URL


# @st.cache_data(ttl=60 * 60 * 2)
def fetch_all_reactions():
	"""Fetch all reactions and cache result for 2 hours."""
	reaction_checker = reaction.ReactionChecker(base_url=LMSD_REACTIONS_BASE_URL)
	return reaction_checker.check_reactions(lm_ids="all")


all_reactions = fetch_all_reactions()
st.write(all_reactions)