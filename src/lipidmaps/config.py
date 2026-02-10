import os

# Base URL for the ReactionChecker / LMSD reactions service.
# Can be overridden with the environment variable `LMSD_REACTIONS_BASE_URL`.
LMSD_REACTIONS_BASE_URL = os.getenv(
	"LMSD_REACTIONS_BASE_URL", "https://dev.lipidmaps.org"
)
