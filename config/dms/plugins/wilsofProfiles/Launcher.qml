import QtQuick
import qs.Services
import "Profiles.js" as Profiles
import "."

Item {
    property var pluginService: null
    property string trigger: "profil"
    signal itemsChanged()

    function getItems(query) {
        return Profiles.items(query, ProfileState.status);
    }

    function executeItem(item) {
        if (item && Profiles.valid(item.action))
            ProfileState.apply(item.action);
    }

    Connections {
        target: ProfileState
        function onStatusChanged() { itemsChanged(); }
    }
}
