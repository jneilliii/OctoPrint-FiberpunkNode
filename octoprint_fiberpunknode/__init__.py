# coding=utf-8
from __future__ import absolute_import
import threading
import time
import requests
import octoprint.plugin


class FiberpunknodePlugin(octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin
                          ):

    # ~~ sdcardupload hook

    def nop_upload_to_sd(self, printer, filename, path, sd_upload_started, sd_upload_succeeded, sd_upload_failed, *args,
                         **kwargs):

        remote_name = "/{}".format(filename)
        self._logger.info("Starting Fiberpunk Node API upload from {} to {}".format(filename, remote_name))

        sd_upload_started(filename, remote_name)

        def process():
            tic = 0
            toc = 0
            try:
                tic = time.perf_counter()
                upload_url = self._settings.get(["node_url"])
                if upload_url.endswith("/") and upload_url.startswith("http"):
                    upload_url = "{}edit".format(self._settings.get(["node_url"]))
                else:
                    return
                self._logger.info("Sending file")
                files = {'data': (remote_name, open(path, 'rb').read(), "application/octet-stream")}
                response = requests.post(upload_url, files=files, timeout=180)
                toc = time.perf_counter()
                if response.status_code == 200:
                    self._logger.info("File upload success")
                    if self._settings.get_boolean(["delete_after_transfer"]):
                        self._logger.info("Deleting file {} after transfer".format(filename))
                        self._file_manager.remove_file("local", filename)
                    sd_upload_succeeded(filename, remote_name, toc-tic)
                else:
                    self._logger.info("File upload failure")
                    sd_upload_failed(filename, remote_name, toc-tic)

            except Exception as e:
                self._logger.info(e)
                sd_upload_failed(filename, remote_name, toc-tic)

        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

        return remote_name

    # ~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return {
            "node_url": "",
            "delete_after_transfer": False
        }

    # ~~ AssetPlugin mixin

    def get_assets(self):
        return {
            "css": ["css/fiberpunknode.css"],
            "js": ["js/fiberpunknode.js"]
        }

    # ~~ Softwareupdate hook

    def get_update_information(self):
        return {
            "fiberpunknode": {
                "displayName": "Fiberpunk Node",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "jneilliii",
                "repo": "OctoPrint-FiberpunkNode",
                "current": self._plugin_version,
                "pip": "https://github.com/jneilliii/OctoPrint-FiberpunkNode/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Fiberpunk Node"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FiberpunknodePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.printer.sdcardupload": __plugin_implementation__.nop_upload_to_sd,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
