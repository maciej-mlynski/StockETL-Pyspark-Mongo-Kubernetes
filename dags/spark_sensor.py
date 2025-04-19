from airflow.sensors.base import BaseSensorOperator
from airflow.exceptions import AirflowException
from kubernetes import client, config


class SparkApplicationSensor(BaseSensorOperator):
    """
    Wait until SparkApp is completed -> failed or succeed
    """
    template_fields = ("application_name",)

    def __init__(self,
                 application_name: str,
                 namespace: str = "spark-jobs",
                 poke_interval: int = 60,
                 timeout: int = 60*60*2,
                 **kwargs):
        super().__init__(poke_interval=poke_interval,
                         timeout=timeout,
                         **kwargs)
        self.application_name = application_name
        self.namespace = namespace

    def poke(self, context):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        api = client.CustomObjectsApi()
        app = api.get_namespaced_custom_object(
            group="sparkoperator.k8s.io",
            version="v1beta2",
            namespace=self.namespace,
            plural="sparkapplications",
            name=self.application_name,
        )
        state = app.get("status", {}) \
                   .get("applicationState", {}) \
                   .get("state")
        self.log.info("SparkApplication %s is in %s", self.application_name, state)
        if state == "COMPLETED":
            return True
        if state in ("FAILED", "UNKNOWN"):
            raise AirflowException(f"Spark job failed, state={state}")
        return False


