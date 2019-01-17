import requests_unixsocket

from lib.utils.utils import Utils

u = Utils()


# https://docs.docker.com/engine/reference/api/docker_remote_api_v1.24/
class Process:

    def __init__(self, container_id, ps_args="ef"):

        self.container_id = container_id
        self.ps_args = ps_args

        self.base = "http+unix://%2Fvar%2Frun%2Fdocker.sock"
        self.url = "/containers/%s/top?ps_args=%s" % (self.container_id, self.ps_args)

        self.session = requests_unixsocket.Session()
        try:
            self.resp = self.session.get(self.base + self.url)
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

    def _get_respj(self):
        resp = self.resp
        url = self.url
        resp_status_code = resp.status_code
        u.check_resp(resp_status_code, url)

    def ps(self):
        self._get_respj()

        return self.resp.json()

    def processes(self):
        self._get_respj()

        respj = self.resp.json()
        return '{}'.format(respj["Processes"])

    def titles(self):
        self._get_respj()

        respj = self.resp.json()
        return '{}'.format(respj["Titles"])
