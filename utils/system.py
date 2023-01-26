import subprocess

from .logger import init_logger
logger = init_logger("utils.system")


class SystemController:

    def __init__(self, main_process: str):
        self.main_process = main_process

    def find_command(self, name: str) -> str:
        which_process = subprocess.run(["which", name], capture_output=True)
        if which_process.returncode == 0:
            return which_process.stdout.strip().decode()
        else:
            logger.debug(f"Command not found: {name}")
            raise FileNotFoundError(f"Command not found: {name}")

    def kill(self):
        try:
            systemctl_path = self.find_command("systemctl")
            subprocess.run([systemctl_path, "stop", self.main_process])
        except FileNotFoundError:
            try:
                subprocess.run(['/usr/bin/systemctl', "stop", self.main_process])
            except Exception as err:
                logger.exception(err)
        except Exception as err:
            logger.exception(err)

    def restart(self):
        try:
            systemctl_path = self.find_command("systemctl")
            subprocess.run([systemctl_path, "restart", self.main_process])
        except FileNotFoundError:
            try:
                subprocess.run(['/usr/bin/systemctl', "restart", self.main_process])
            except Exception as err:
                logger.exception(err)
        except Exception as err:
            logger.exception(err)

    def reboot(self):
        try:
            reboot_path = self.find_command("reboot")
            subprocess.run([reboot_path])
        except FileNotFoundError:
            try:
                subprocess.run(['/usr/bin/systemctl', "reboot", self.main_process])
            except Exception as err:
                logger.exception(err)
        except Exception as err:
            logger.exception(err)
