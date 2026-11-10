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

  Process {
    id: launcher
    command: [root.scriptPath]
  }

  Process {
    id: killActive
    command: [root.scriptPath, "kill-active"]
  }

  BarButton {
    id: button
    bar: root.bar
    tooltip: root.isGerman
      ? "Task Manager (Ctrl+Shift+Esc)\nRechtsklick: Aktives Fenster beenden"
      : "Task Manager (Ctrl+Shift+Esc)\nRight-click: Terminate focused window"
    horizontalPadding: 8

    onClicked: {
      launcher.running = false
      launcher.running = true
    }

    MouseArea {
      anchors.fill: parent
      acceptedButtons: Qt.RightButton
      onClicked: {
        killActive.running = false
        killActive.running = true
      }
    }

    contentItem: Row {
      spacing: 6
      anchors.verticalCenter: parent.verticalCenter

      Text {
        text: "⚡"
        font.pixelSize: 13
        anchors.verticalCenter: parent.verticalCenter
      }

      Text {
        text: "Tasks"
        color: root.foreground
        font.family: root.fontFamily
        font.pixelSize: 12
        font.bold: true
        anchors.verticalCenter: parent.verticalCenter
      }
    }
  }
}
