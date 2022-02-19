data "grafana_synthetic_monitoring_probes" "main" {}

provider "grafana" {
  url             = "https://reddeeralbertastake.grafana.net/"
  auth            = var.grafana_auth
  sm_url          = "https://synthetic-monitoring-api.grafana.net"
  sm_access_token = var.grafana_sm_access_token
}
