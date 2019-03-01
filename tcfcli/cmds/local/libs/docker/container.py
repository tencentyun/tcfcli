import docker
from .utils import to_posix_path
from .attach_api import attach


class Container(object):

    _STDOUT_FRAME_TYPE = 1
    _STDERR_FRAME_TYPE = 2

    def __init__(self, image,
                 cmd,
                 work_dir,
                 host_dir,
                 mem=None,
                 env_vars=None,
                 entrypoint=None,
                 ports=None,
                 docker_client=None,
                 network_id=None,
                 container_opts=None,
                 additional_volumes=None):

        self._image = image
        self._cmd = cmd
        self._memory = mem
        self._env_vars = env_vars
        self._working_dir = work_dir
        self._host_dir = host_dir
        self._ports = ports
        self._entrypoint = entrypoint
        self._network_id = network_id

        self._docker_client = docker_client or docker.from_env()
        self.id = None

    def create(self):
        if self.is_exist():
            raise Exception('container has been created, can not create again.')

        kwargs = {
            "command": self._cmd,
            "working_dir": self._working_dir,
            "volumes": {
                self._host_dir: {
                    "bind": self._working_dir,
                    "mode": "ro"
                }
            },
            "tty": False
        }

        kwargs["volumes"] = {to_posix_path(host_dir): mount for host_dir, mount in kwargs["volumes"].items()}

        if self._env_vars:
            kwargs["environment"] = self._env_vars

        if self._ports:
            kwargs["ports"] = self._ports

        if self._entrypoint:
            kwargs["entrypoint"] = self._entrypoint

        if self._memory:
            kwargs["mem_limit"] = "{}m".format(self._memory)

        container_instance = self._docker_client.containers.create(self._image, **kwargs)
        self.id = container_instance.id

        if self._network_id:
            network = self._docker_client.networks.get(self._network_id)
            network.connect(self.id)

        return self.id

    def start(self):
        container_instance = self._docker_client.containers.get(self.id)

        container_instance.start()

    def delete(self):
        if not self.is_exist():
            return

        try:
            self._docker_client.containers.get(self.id).remove(force=True)
        except docker.errors.NotFound:
            pass
        except docker.errors.APIError as e:
            err_msg = str(e)
            if err_msg.find('is already in progress') < 0 or err_msg.find('removal of container') < 0:
                raise e
        except docker.errors.DockerException as e:
            raise Exception('delete container %s failed, error: %s' % (self.id, str(e)))

        self.id = None

    def is_exist(self):
        return self.id is not None

    def get_logs(self, stdout=None, stderr=None):
        if not stdout and not stderr:
            return

        if not self.is_exist():
            raise Exception('can not get logs, container does not exist')

        container_instance = self._docker_client.containers.get(self.id)

        logs_itr = attach(self._docker_client,
                          container=container_instance,
                          stdout=True,
                          stderr=True,
                          logs=True)

        self._write_container_output(logs_itr, stdout=stdout, stderr=stderr)

    @staticmethod
    def _write_container_output(output_itr, stdout=None, stderr=None):
        for frame_type, data in output_itr:
            if frame_type == Container._STDOUT_FRAME_TYPE and stdout:
                stdout.write(data)
            elif frame_type == Container._STDERR_FRAME_TYPE and stderr:
                stderr.write(data)
            else:
                pass

    @property
    def image(self):
        return self._image
