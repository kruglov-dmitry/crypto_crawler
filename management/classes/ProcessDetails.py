
class ProcessDetails():
    def __init__(self, cmd, pid):
        self.cmd = cmd
        self.pid = pid
        self.pair_id = self._parse_cmd(self.cmd)

    def get_pair_id(self):
        return self.pair_id

    def _parse_cmd(self, cmd):
        # FIXME NOTE parsing
        return ""