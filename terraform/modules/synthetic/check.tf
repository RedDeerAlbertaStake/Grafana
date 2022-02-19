resource "grafana_synthetic_monitoring_check" "chapel" {
  for_each = var.chapels

  job                = each.key
  target             = each.value
  enabled            = true
  basic_metrics_only = false

  probes = [
    data.grafana_synthetic_monitoring_probes.main.probes.NorthCalifornia,
    data.grafana_synthetic_monitoring_probes.main.probes.Oregon,
  ]

  labels = {}

  settings {
    ping {
      ip_version    = "V4"
      dont_fragment = false
    }
  }
}
