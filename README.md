# Grafana

Automation and tooling to provide monitoring of the Red Deer Alberta Stake building internet connections.

This repo provides scripts that manage the [stake Grafana instance](https://reddeeralbertastake.grafana.net).

A Docker image can be built and run which will poll [TM](http://tm.churchofjesuschrist.org) every 10 minutes and apply the [Terraform](https://app.terraform.io/app/RedDeerAlbertaStake) scripts to update the external IP's for each building in the stake.

Alerts are setup in Grafana which will notify [PagerDuty](https://reddeeralbertastake.pagerduty.com) if the connection goes offline for more than a few minutes.  Those PagerDuty alerts will be sent to the [#alerts](https://reddeeralbertastake.slack.com/archives/C033XU241FE) channel in Slack.

## Building

```shell
docker-compose build
```

## Running

### Save your LDS credentials to `.env`

```shell
TM_DATA_USERNAME="<username>"
TM_DATA_PASSWORD="<password>"
```

### Save your Terraform Cloud API Token to `.terraformrc`

```shell
credentials "app.terraform.io" {
  token = "<token>"
}
```

### Start the container

```shell
docker-compose up -d
```

As the church doesn't provide public API access, I had to work around it by using the browser testing framework [Selenium](https://www.selenium.dev) to simulate a login on TM, retrieve the API token from session storage and use that to log into the API to retrieve the firewall's public IP.  The script expects that Two-Step (MFA) Verification is setup on your LDS account and that you have the *Okta Verify App* option setup for it.  On startup, it will login with your credentials and trigger Okta Verify.  It will remember your session for 30 days, so as long as the script isn't stopped and restarted, you shouldn't need to accept the login with Okta Verify again until it expires.
