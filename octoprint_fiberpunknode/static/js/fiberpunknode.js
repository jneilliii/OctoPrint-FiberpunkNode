/*
 * View model for Fiberpunk Node
 *
 * Author: jneilliii
 * License: AGPLv3
 */
$(function() {
    function FiberpunknodeViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        // TODO: Implement your plugin's view model here.
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: FiberpunknodeViewModel,
        dependencies: [ "settingsViewModel" ],
        elements: [ "#settings_plugin_fiberpunknode" ]
    });
});
