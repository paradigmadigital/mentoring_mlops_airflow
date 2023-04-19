from airflow.operators.docker_operator import DockerOperator


class DockerKillerOperator(DockerOperator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _run_image(self):

        try:
            self.cli.stop(self.container_name)
            self.cli.remove_container(self.container_name)
        except Exception as error:
            Exception(f'DockerKillerOperator cant kill container ' + \
                f'{self.container_name}. {error}')
