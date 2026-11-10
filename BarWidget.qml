import QtQuick
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "io.github.serverbauer.taskmanager"

  readonly property color foreground: bar ? bar.foreground : Color.foreground
  readonly property string fontFamily: bar ? bar.fontFamily : Style.font.family
  readonly property bool isGerman: (Qt.locale().name.indexOf("de") === 0)

  function localPath(url) {
    var value = String(url || "")
    if (value.indexOf("file://") === 0) value = value.slice(7)
    return decodeURIComponent(value)
  }

  readonly property string scriptPath: localPath(Qt.resolvedUrl("omarchy-taskmanager.sh"))

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Process {
    id: launcher
    command: [root.scriptPath]
  }

  Process {
    id: killActive
    command: [root.scriptPath, "kill-active"]
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "⚡ Tasks"
    tooltipText: root.isGerman
      ? "Task Manager (Ctrl+Shift+Esc)\nRechtsklick: Aktives Fenster beenden"
      : "Task Manager (Ctrl+Shift+Esc)\nRight-click: Terminate focused window"
    horizontalMargin: 8

    onPressed: function(button) {
      if (button === Qt.RightButton) {
        killActive.running = false
        killActive.running = true
      } else {
        launcher.running = false
        launcher.running = true
      }
    }
  }
}
