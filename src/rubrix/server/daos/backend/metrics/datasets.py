# All metrics related to the datasets index
from rubrix.server.daos.backend.metrics.base import TermsAggregation

METRICS = {
    "all_rubrix_workspaces": TermsAggregation(
        id="all_rubrix_workspaces", field="owner.keyword"
    )
}
