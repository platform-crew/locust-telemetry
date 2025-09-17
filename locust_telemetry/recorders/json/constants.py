# Hack: Grafana doesn't allow us to add buffer time to autolink. This adds
# some buffer to metrics timestamp so that on clicking a link in grafana
# will navigate us for the correct time window
TEST_STOP_BUFFER_FOR_GRAPHS = 1  # 1 seconds
