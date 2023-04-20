from typing import Optional, Union, List

from airflow.models import BaseOperator
from airflow.operators.docker_operator import DockerOperator


class DockerOperatorWithExposedPorts(DockerOperator):


    template_fields = (*DockerOperator.template_fields,
        'mounts', 'port',)


    def __init__(self, *args, **kwargs):

        # Templating params for mounts
        mounts = kwargs.get('mounts', [])
        for mount in mounts:
            mount.template_fields = ('Source', 'Target', 'Type')
        kwargs['mounts'] = mounts

        # Port Binding
        self.port = kwargs.pop('port', None)

        super().__init__(*args, **kwargs)


    def _run_image_with_mounts(
        self,
        target_mounts,
        add_tmp_variable: bool
    ) -> Optional[Union[List[str], str]]:

        """
        NOTE: This method was copied entirely from the base class
        `DockerOperator`, for the capability of performing port publishing.
        """

        if add_tmp_variable:
            self.environment['AIRFLOW_TMP_DIR'] = self.tmp_dir
        else:
            self.environment.pop('AIRFLOW_TMP_DIR', None)

        if not self.cli:
            raise Exception("The 'cli' should be initialized before!")

        self.port_bindings = {int(self.port) : int(self.port)} if self.port else {}
        if self.port_bindings and self.network_mode == "host":
            self.port_bindings = {}
            raise Exception(
                "`port_bindings` is not supported in `host` network mode.")

        self.container = self.cli.create_container(
            command=self.format_command(self.command),
            name=self.container_name,
            environment={**self.environment, **self._private_environment},
            ports=list(self.port_bindings.keys()),
            host_config=self.cli.create_host_config(
                auto_remove=False,
                mounts=target_mounts,
                network_mode=self.network_mode,
                shm_size=self.shm_size,
                dns=self.dns,
                dns_search=self.dns_search,
                cpu_shares=int(round(self.cpus * 1024)),
                port_bindings=self.port_bindings,
                mem_limit=self.mem_limit,
                cap_add=self.cap_add,
                extra_hosts=self.extra_hosts,
                privileged=self.privileged,
            ),
            image=self.image,
            user=self.user,
            entrypoint=self.format_command(self.entrypoint),
            working_dir=self.working_dir,
            tty=self.tty,
        )

        logstream = self.cli.attach(
            container=self.container['Id'],
            stdout=True,
            stderr=True,
            stream=True
        )

        try:
            self.cli.start(self.container['Id'])

            log_lines = []
            for log_chunk in logstream:
                log_chunk = str(log_chunk)
                log_lines.append(log_chunk)
                self.log.info("%s", log_chunk)

            result = self.cli.wait(self.container['Id'])

            if result['StatusCode'] != 0:
                joined_log_lines = "\n".join(log_lines)
                raise AirflowException(
                    f'Docker container failed: {repr(result)} ' + \
                    f'lines {joined_log_lines}')

            if self.retrieve_output:
                return self._attempt_to_retrieve_result()
            elif self.do_xcom_push:
                if len(log_lines) == 0:
                    return None
                try:
                    if self.xcom_all:
                        return log_lines
                    else:
                        return log_lines[-1]
                except StopIteration:
                    # handle the case when there is not a single line
                    # to iterate on
                    return None
            return None
        finally:
            if self.auto_remove == "success":
                self.cli.remove_container(self.container['Id'])
            elif self.auto_remove == "force":
                self.cli.remove_container(self.container['Id'], force=True)
