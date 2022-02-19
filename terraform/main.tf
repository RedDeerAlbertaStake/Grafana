terraform {
  cloud {
    organization = "RedDeerAlbertaStake"

    workspaces {
      name = "grafana"
    }
  }
}
