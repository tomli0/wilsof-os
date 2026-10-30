import QtQuick
import qs.Common
import qs.Widgets
import qs.Modules.Plugins
import "."

PluginComponent {
    id: root
    pillClickAction: () => ProfileState.openSelector()

    horizontalBarPill: Component {
        StyledText {
            text: ProfileState.label
            color: ProfileState.status.error ? Theme.error : Theme.surfaceText
            font.pixelSize: Theme.fontSizeMedium
            width: implicitWidth + Theme.spacingM * 2
            height: root.widgetThickness
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
    verticalBarPill: Component {
        StyledText {
            text: ProfileState.label
            color: ProfileState.status.error ? Theme.error : Theme.surfaceText
            font.pixelSize: Theme.fontSizeMedium
            width: root.widgetThickness
            height: implicitWidth + Theme.spacingM * 2
            rotation: 90
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
