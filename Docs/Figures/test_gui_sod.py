import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

import pyPLUTO
from pyPLUTO.gui.main_window import PyPLUTOApp


def get_window_geometry(window_title="PyPLUTO GUI"):
    # Find window ID by title
    win_id = (
        subprocess.check_output(["xdotool", "search", "--name", window_title])
        .decode()
        .strip()
        .split("\n")[0]
    )

    # Get window geometry
    output = subprocess.check_output(["xwininfo", "-id", win_id]).decode()

    x = int(re.search(r"Absolute upper-left X:\s+(\d+)", output).group(1))
    y = int(re.search(r"Absolute upper-left Y:\s+(\d+)", output).group(1))
    width = int(re.search(r"Width:\s+(\d+)", output).group(1))
    height = int(re.search(r"Height:\s+(\d+)", output).group(1))

    return x, y, width, height


def record_screen_start(filename="pluto_sod_full.mp4", display=":0.0", fps=25):
    x, y, w, h = get_window_geometry("PyPLUTO")

    screen_width = 1920
    screen_height = 1080

    # Adjust width and x if necessary
    if x + w > screen_width:
        w = screen_width - x
    # Adjust height and y if necessary
    if y + h > screen_height:
        h = screen_height - y

    # Ensure even dimensions for x264
    w -= w % 2
    h -= h % 2
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "x11grab",
        "-framerate",
        str(fps),
        "-video_size",
        f"{w}x{h}",
        "-i",
        f"{display}+{x},{y}",
        "-vcodec",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
        filename,
    ]
    print(f"Recording {w}x{h} at ({x},{y}) → {filename}")
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def record_screen_stop(proc):
    if proc.poll() is not None:
        print("ffmpeg already exited.")
        return

    print("Stopping ffmpeg recording gracefully...")
    proc.stdin.write(b"q\n")
    proc.stdin.flush()
    try:
        proc.wait(timeout=10)
        print("ffmpeg exited cleanly.")
    except subprocess.TimeoutExpired:
        print("Timeout — killing ffmpeg.")
        proc.kill()


def postprocess_video():
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite without asking
        "-ss",
        "0.25",
        "-i",
        "pluto_sod_full.mp4",
        "-t",
        "18",
        "-vf",
        "crop=1180:750:40:47",
        "-c:a",
        "copy",
        "pluto_sod_gui.mp4",
    ]
    print("Running postprocess crop + trim...")
    subprocess.run(cmd, check=True)


def copy_to_static(
    source_video="pluto_sod_gui.mp4", static_dir="../source/_static"
):
    src = Path(source_video)
    dst_dir = Path(static_dir).resolve()
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name

    shutil.copy2(src, dst)
    print(f"✅ Copied {src} → {dst}")


def automate_gui():
    app = QApplication(sys.argv)
    window = PyPLUTOApp(code="PLUTO")
    window.resize(1150, 720)
    window.show()

    def click_select_file():
        getattr(window, "Select File").animateClick()
        QTimer.singleShot(1000, wait_for_dialog_to_appear)

    def wait_for_dialog_to_appear(retries=20):
        dialog = getattr(window, "_file_dialog", None)

        def go_to_test():
            test_path = pyPLUTO.find_example(".")
            dialog.setDirectory(str(test_path))

            QTimer.singleShot(1000, lambda: go_to_hd(test_path))

        def go_to_hd(test_path):
            hd_path = test_path / "HD"
            dialog.setDirectory(str(hd_path))

            QTimer.singleShot(1000, lambda: go_to_sod(hd_path))

        def go_to_sod(hd_path):
            sod_path = hd_path / "Sod"
            dialog.setDirectory(str(sod_path))

            QTimer.singleShot(1000, lambda: close_and_load(sod_path))

        def close_and_load(sod_path):
            dialog.close()
            QTimer.singleShot(0, lambda: load_file(sod_path))

        # Start after 1 second
        QTimer.singleShot(1000, go_to_test)

    def load_file(folder_path):

        window.folder_path = str(folder_path)
        window.datatype = "dbl"
        window.nout = 1
        window.load_data()
        QTimer.singleShot(1000, set_title)

    def set_title():
        window.plot_title.setText("rho (blue), vx1 (red),prs (green)")
        QTimer.singleShot(0, plot_rho)

    def plot_rho():
        idx = window.var_selector.findText("rho")
        if idx != -1:
            window.var_selector.setCurrentIndex(idx)
        window.overplot_checkbox.setChecked(False)
        QTimer.singleShot(1000, lambda: plot_variable("rho", select_vx1))

    def select_vx1():
        idx = window.var_selector.findText("vx1")
        if idx != -1:
            window.var_selector.setCurrentIndex(idx)  # Set index first
            window.var_selector.repaint()
            window.var_selector.setFocus()
            window.var_selector.showPopup()
            QTimer.singleShot(
                1000, lambda: hide_dropdown_and_overplot("vx1", select_prs)
            )

    def select_prs():
        idx = window.var_selector.findText("prs")
        if idx != -1:
            window.var_selector.setCurrentIndex(idx)  # Set index first
            window.var_selector.repaint()
            window.var_selector.setFocus()
            window.var_selector.showPopup()
            QTimer.singleShot(1000, lambda: hide_dropdown_and_plot("prs"))

    def hide_dropdown_and_overplot(varname, next_step):
        window.var_selector.hidePopup()
        if varname == "vx1":
            time.sleep(1)
            window.overplot_checkbox.setChecked(True)
            window.overplot_checkbox.repaint()
        QTimer.singleShot(1000, lambda: plot_variable(varname, next_step))

    def hide_dropdown_and_plot(varname):
        window.var_selector.hidePopup()
        QTimer.singleShot(1000, lambda: plot_variable(varname, close_window))

    def plot_variable(varname, next_step=None):
        window.Plot.animateClick()  # Let the button do the work
        if next_step:
            QTimer.singleShot(1000, next_step)

    def close_window():
        time.sleep(2)
        print("✅ Done. Closing window.")
        window.close()

    QTimer.singleShot(1000, click_select_file)
    return app
    # sys.exit(app.exec())


if __name__ == "__main__":
    recorder = record_screen_start()

    try:
        app = automate_gui()
        app.exec()  # ← this blocks until GUI exits
    finally:
        time.sleep(2)  # let buffers flush
        record_screen_stop(recorder)
        print("Recording stopped. Processing video...")
        postprocess_video()
        copy_to_static()
