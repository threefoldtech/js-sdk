from .base_component import VDCBaseComponent
from jumpscale.loader import j
import gevent
import tempfile


class VDCMonitoring(VDCBaseComponent):
    def deploy_stack(self):
        self.vdc_deployer.info("initializing monitoring stack")
        load_thread = gevent.spawn(self.vdc_instance.load_info)
        helm_update_thread = gevent.spawn(self.configure_repos)
        gevent.joinall([load_thread, helm_update_thread])
        if not helm_update_thread.value:
            self.vdc_deployer.error(f"failed to configure prometheus helm repo")
            return False

        external_config = self._get_external_scrape_configs()
        self.vdc_deployer.info(f"external scrape config {external_config}")
        secret_key = self._config_scrape_secret(external_config)
        self.vdc_deployer.info(f"additional scrape config key {secret_key}")
        command_args = self._get_install_args(secret_key)
        self.vdc_deployer.info(f"helm install extra args {command_args}")
        return self.vdc_deployer.vdc_k8s_manager.install_chart(
            "prometheusstack", "prometheus-community/kube-prometheus-stack", extra_config=command_args
        )

    def configure_repos(self):
        self.vdc_deployer.info(f"adding and updating prometheus helm repos")
        self.vdc_deployer.vdc_k8s_manager.add_helm_repo(
            "prometheus-community", "https://prometheus-community.github.io/helm-charts"
        )
        self.vdc_deployer.vdc_k8s_manager.add_helm_repo("stable", "https://charts.helm.sh/stable")
        self.vdc_deployer.vdc_k8s_manager.update_repos()
        self.vdc_deployer.info(f"helm repos updated")
        return True

    def _get_external_scrape_configs(self):
        if not self.vdc_instance.s3.minio.wid:
            return
        minio_ip = self.vdc_instance.s3.minio.ip_address
        job = [
            {
                "job_name": "minio",
                "metrics_path": "/minio/prometheus/metrics",
                "scheme": "http",
                "static_configs": [{"targets": [f"{minio_ip}:9000"]}],
            }
        ]
        return j.data.serializers.yaml.dumps(job)

    def _config_scrape_secret(self, scrape_config):
        self.vdc_deployer.info("creating additional scrape config secret")
        if not scrape_config:
            return
        with tempfile.NamedTemporaryFile("w") as scrape_config_file:
            scrape_config_file.write(scrape_config)
            scrape_config_file.flush()
            with tempfile.NamedTemporaryFile("w") as scrape_secret_def:
                self.vdc_deployer.vdc_k8s_manager.execute_native_cmd(
                    f"kubectl create secret generic additional-scrape-configs --from-file={scrape_config_file.name} --dry-run -o yaml > {scrape_secret_def.name}"
                )
                self.vdc_deployer.vdc_k8s_manager.execute_native_cmd(f"kubectl apply -f {scrape_secret_def.name}")
                return scrape_config_file.name.split("/")[-1]

    @staticmethod
    def _get_install_args(secret_key=None):
        conf = {
            "prometheus.ingress.enabled": "false",
            "prometheus.service.port": "80",
            "prometheusSpec.replicas": "1",
            "grafana.ingress.enabled": "false",
            "grafana.ingress.path": "/",
            "resources.limits.cpu": "200m",
            "resources.limits.memory": "200Mi",
            "resources.requests.cpu": "100m",
            "resources.requests.memory": "100Mi",
        }
        if secret_key:
            conf.update(
                {
                    "prometheus.prometheusSpec.additionalScrapeConfigsSecret.enabled": "true",
                    "prometheus.prometheusSpec.additionalScrapeConfigsSecret.name": "additional-scrape-configs",
                    "prometheus.prometheusSpec.additionalScrapeConfigsSecret.key": secret_key,
                }
            )
        return conf
