# FIXME NOTE: https://unix.stackexchange.com/questions/267478/getting-public-ip-address-of-ec2-instance-from-outside-using-aws-cli


class ServerDetails(object):
    def __init__(self, server_name, server_id):
        self.server_name = server_name
        self.server_id = server_id