# Hack: Grafana doesn't allow us to add buffer time to autolink. This adds
# some buffer to metrics timestamp so that on clicking a link in grafana
# will navigate us for the correct time window
TEST_STOP_BUFFER_FOR_GRAPHS = 1  # 1 seconds

REQUEST_STATS_TYPE_FINAL = "final"
REQUEST_STATS_TYPE_CURRENT = "current"
REQUEST_STATS_TYPE_ENDPOINT = "endpoint"
REQUEST_STATUS_SUCCESS = "success"
REQUEST_STATUS_ERROR = "error"
