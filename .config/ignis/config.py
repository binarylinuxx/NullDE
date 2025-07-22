import datetime
import asyncio
from ignis.widgets import Widget
from ignis.utils import Utils
from ignis.app import IgnisApp
from ignis.services.audio import AudioService
from ignis.services.system_tray import SystemTrayService, SystemTrayItem
from ignis.services.niri import NiriService, NiriWorkspace
from ignis.services.notifications import NotificationService
from ignis.services.mpris import MprisService, MprisPlayer

app = IgnisApp.get_default()

app.apply_css(f"{Utils.get_current_dir()}/style.scss")


audio = AudioService.get_default()
system_tray = SystemTrayService.get_default()
niri = NiriService.get_default()
notifications = NotificationService.get_default()
mpris = MprisService.get_default()


def niri_workspace_button(workspace: NiriWorkspace) -> Widget.Button:
    widget = Widget.Button(
        css_classes=["workspace"],
        on_click=lambda x: workspace.switch_to(),
        child=Widget.Label(label=str(workspace.idx)),
    )
    if workspace.is_active:
        widget.add_css_class("active")

    return widget


def niri_scroll_workspaces(monitor_name: str, direction: str) -> None:
    current = list(
        filter(lambda w: w.is_active and w.output == monitor_name, niri.workspaces)
    )[0].idx
    if direction == "up":
        target = current + 1
        niri.switch_to_workspace(target)
    else:
        target = current - 1
        niri.switch_to_workspace(target)


def niri_workspaces(monitor_name: str) -> Widget.EventBox:
    return Widget.EventBox(
        on_scroll_up=lambda x: niri_scroll_workspaces(monitor_name, "up"),
        on_scroll_down=lambda x: niri_scroll_workspaces(monitor_name, "down"),
        css_classes=["workspaces"],
        spacing=5,
        child=niri.bind(
            "workspaces",
            transform=lambda value: [
                niri_workspace_button(i) for i in value if i.output == monitor_name
            ],
        ),
    )


def mpris_title(player: MprisPlayer) -> Widget.Box:
    return Widget.Box(
        spacing=10,
        setup=lambda self: player.connect(
            "closed",
            lambda x: self.unparent(),  # remove widget when player is closed
        ),
        child=[
            Widget.Icon(image="audio-x-generic-symbolic"),
            Widget.Label(
                ellipsize="end",
                max_width_chars=20,
                label=player.bind("title"),
            ),
        ],
    )


def media() -> Widget.Box:
    return Widget.Box(
        spacing=0,
        child=[
            Widget.Label(
                label="No media players",
                visible=mpris.bind("players", lambda value: len(value) == 0),
            )
        ],
        setup=lambda self: mpris.connect(
            "player-added", lambda x, player: self.append(mpris_title(player))
        ),
    )


def niri_client_title(monitor_name) -> Widget.Label:
    return Widget.Label(
        css_classes=["fw"],
        ellipsize="end",
        max_width_chars=40,
        visible=niri.bind("active_output", lambda output: output == monitor_name),
        label=niri.active_window.bind("title"),
    )


def current_notification() -> Widget.Label:
    return Widget.Label(
        ellipsize="end",
        max_width_chars=50,
        label=notifications.bind(
            "notifications", lambda value: value[-1].summary if len(value) > 0 else None
        ),
    )


def clock() -> Widget.Label:
    # poll for current time every second
    return Widget.Label(
        css_classes=["clock"],
        label=Utils.Poll(
            1_000, lambda self: datetime.datetime.now().strftime("%I:%M%p")
        ).bind("output"),
    )


def speaker_volume() -> Widget.Box:
    return Widget.Box(
    css_classes=["volume"],
        child=[
            Widget.Icon(
                image=audio.speaker.bind("icon_name")
            ),
            Widget.Label(
                label=audio.speaker.bind("volume", transform=lambda value: str(value))
            ),
        ]
    )


def niri_keyboard_layout() -> Widget.EventBox:
    layout_map = {
        "russian": "RU",
        "english (us)": "US",
        "german": "DE",
        "french": "FR",
        # Add more mappings as needed
    }
    
    return Widget.EventBox(
        css_classes=["lang"],
        on_click=lambda self: niri.switch_kb_layout(),
        child=[
            Widget.Label(
                label=niri.keyboard_layouts.bind(
                    "current_name",
                    transform=lambda name: (
                        layout_map.get(name.lower(), name[:2].upper())
                    )
                )
            )
        ],
    )


def tray_item(item: SystemTrayItem) -> Widget.Button:
    if item.menu:
        menu = item.menu.copy()
    else:
        menu = None

    return Widget.Button(
        child=Widget.Box(
            child=[
                Widget.Icon(image=item.bind("icon"), pixel_size=24),
                menu,
            ]
        ),
        setup=lambda self: item.connect("removed", lambda x: self.unparent()),
        tooltip_text=item.bind("tooltip"),
        on_click=lambda x: menu.popup() if menu else None,
        on_right_click=lambda x: menu.popup() if menu else None,
        css_classes=["tray-item"],
    )


def tray():
    return Widget.Box(
        setup=lambda self: system_tray.connect(
            "added", lambda x, item: self.append(tray_item(item))
        ),
        spacing=10,
    )


def speaker_slider() -> Widget.Scale:
    return Widget.Scale(
        min=0,
        max=100,
        step=1,
        value=audio.speaker.bind("volume"),
        on_change=lambda x: audio.speaker.set_volume(x.value),
        css_classes=["volume-slider"],  # we will customize style in style.css
    )


def create_exec_task(cmd: str) -> None:
    # use create_task to run async function in a regular (sync) one
    asyncio.create_task(Utils.exec_sh_async(cmd))


def logout() -> None:
    create_exec_task("niri msg action quit")


def power_menu() -> Widget.Button:
    menu = Widget.PopoverMenu(
        items=[
            Widget.MenuItem(
                label="Lock",
                on_activate=lambda x: create_exec_task("swaylock"),
            ),
            Widget.Separator(),
            Widget.MenuItem(
                label="Suspend",
                on_activate=lambda x: create_exec_task("systemctl suspend"),
            ),
            Widget.MenuItem(
                label="Hibernate",
                on_activate=lambda x: create_exec_task("systemctl hibernate"),
            ),
            Widget.Separator(),
            Widget.MenuItem(
                label="Reboot",
                on_activate=lambda x: create_exec_task("systemctl reboot"),
            ),
            Widget.MenuItem(
                label="Shutdown",
                on_activate=lambda x: create_exec_task("systemctl poweroff"),
            ),
            Widget.Separator(),
            Widget.MenuItem(
                label="Logout",
                on_activate=lambda x: logout(),
            ),
        ]
    )
    return Widget.Button(
        child=Widget.Box(
            child=[Widget.Icon(image="system-shutdown-symbolic", pixel_size=20), menu]
        ),
        on_click=lambda x: menu.popup(),
    )


def left(monitor_name: str) -> Widget.Box:
    return Widget.Box(
        child=[niri_workspaces(monitor_name)], spacing=10
    )


def center(monitor_name: str) -> Widget.Box:  # Add monitor_name parameter
    return Widget.Box(
        child=[
            niri_client_title(monitor_name),  # Now this will work
        ],
        spacing=10,
    )


def right() -> Widget.Box:
    return Widget.Box(
        child=[
            tray(),
            niri_keyboard_layout(),
            speaker_volume(),
            clock(),
        ],
        spacing=4,
    )


def bar(monitor_id: int = 0) -> Widget.Window:
    monitor_name = Utils.get_monitor(monitor_id).get_connector()  # type: ignore
    return Widget.Window(
        namespace=f"ignis_bar_{monitor_id}",
        monitor=monitor_id,
        anchor=["bottom", "right", "left"],
        exclusivity="exclusive",
        child=Widget.CenterBox(
            css_classes=["bar"],
            start_widget=left(monitor_name),  
            center_widget=center(monitor_name),  
            end_widget=right(),
        ),
    )

# this will display bar on all monitors
for i in range(Utils.get_n_monitors()):
    bar(i)

CORNER_SIZE = 20
CORNER_RADIUS = CORNER_SIZE // 2  # 20px

def create_corner_widget(corner: str, monitor_id: int = 0) -> Widget.Window:
    """Создает виджет скругленного угла"""
    anchor_map = {
        "top_left": ["top", "left"],
        "top_right": ["top", "right"], 
        "bottom_left": ["bottom", "left"],
        "bottom_right": ["bottom", "right"]
    }
    
    window = Widget.Window(
        namespace=f"corner_{corner}_{monitor_id}",
        monitor=monitor_id,
        anchor=anchor_map[corner],
        layer="foreground",  # Используем overlay вместо foreground
        child=Widget.Box(
            css_classes=[f"corner-{corner}"],
            width_request=CORNER_SIZE,
            height_request=CORNER_SIZE,
        )
    )
    return window

def create_edge_frame(side: str, monitor_id: int = 0) -> Widget.Window:
    """Создает рамку для краев экрана"""
    monitor = Utils.get_monitor(monitor_id)
    
    if side in ["top", "bottom"]:
        width = monitor.width - (CORNER_SIZE * 2)  # Вычитаем углы
        height = CORNER_SIZE
        anchor = [side, "center"]
    else:  # left, right
        width = CORNER_SIZE
        height = monitor.height - (CORNER_SIZE * 2)  # Вычитаем углы
        anchor = [side, "center"]
    
    return Widget.Window(
        namespace=f"edge_{side}_{monitor_id}",
        monitor=monitor_id,
        anchor=anchor,
        layer="overlay",
        child=Widget.Box(
            css_classes=["frame"],
            width_request=width,
            height_request=height,
        )
    )

# Создаем углы и рамки для всех мониторов
corner_windows = []
edge_windows = []

for monitor_id in range(Utils.get_n_monitors()):
    # Создаем углы
    for corner in ["top_left", "top_right", "bottom_right", "bottom_left"]:
        window = create_corner_widget(corner, monitor_id)
        corner_windows.append(window)
    
    # Создаем рамки (опционально)
    for side in ["top", "bottom", "left", "right"]:
        window = create_edge_frame(side, monitor_id)
        edge_windows.append(window)

