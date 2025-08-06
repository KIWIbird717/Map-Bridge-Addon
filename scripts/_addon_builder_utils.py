import subprocess
from pathlib import Path


class BuildError(Exception):
    """Build errors exception"""
    pass


class AddonBuilderUtils:
    def __init__(self):
        self.project_root = Path(__file__).parent / ".."

    def __log(self,  message: str, method: str | None = None):
        print(
            f"[AddonBuilderUtils] {f'[{method}]' if method else ''} {message}")

    def _run_command(self, command, cwd=None, check=True):
        """Run command and returns result"""
        self.__log(f"Running: {' '.join(command)}",
                   method=self._run_command.__name__)
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            if e.stderr:
                print(f"Ошибка: {e.stderr}")
            raise BuildError(
                f"Команда завершилась с ошибкой: {' '.join(command)}")


def overrides(interface_class):
    """
    Override method of extended class

    Example:
        class MySuperInterface(object):
            def my_method(self):
                print 'hello world!'


        class ConcreteImplementer(MySuperInterface):
            @overrides(MySuperInterface)
            def my_method(self):
                print 'hello kitty!'
    See Also:
        - https://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method
    """
    def overrider(method):
        assert (method.__name__ in dir(interface_class))
        return method
    return overrider
