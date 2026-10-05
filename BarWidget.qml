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

  Process {
    id: launcher
    command: ["omarchy-taskmanager.sh"]
  }

  Process {
    id: killActive
    command: ["omarchy-taskmanager.sh", "kill-active"]
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
