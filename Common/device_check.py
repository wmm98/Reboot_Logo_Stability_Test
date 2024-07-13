import subprocess


class Shell:
    @staticmethod
    def invoke(cmd, runtime=120):
        try:
            output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE).communicate(
                timeout=runtime)
            o = output.decode("utf-8")
            return o
        except subprocess.TimeoutExpired as e:
            print(str(e))


class DeviceCheck:
    def __init__(self, device):
        self.shell = Shell()
        self.device_name = device

    def restart_adb(self):
        self.shell.invoke("adb kill-server")
        self.shell.invoke("adb start-server")

    def device_is_online(self):
        devices = self.shell.invoke("adb devices")
        print(devices)
        if self.device_name + "device" in devices.replace('\r', '').replace('\t', '').replace(' ', ''):
            return True
        else:
            return False

    def device_boot(self):
        boot_res = self.shell.invoke("adb -s %s shell getprop sys.boot_completed" % self.device_name)
        return boot_res
