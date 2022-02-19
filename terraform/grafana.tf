module "synthetic" {
  source = "./modules/synthetic"

  grafana_auth            = var.grafana_auth
  grafana_sm_access_token = var.grafana_sm_access_token

  chapels = var.chapels
}
