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


def record_screen_start(filename="pluto_ot_full.mp4", display=":0.0", fps=25):
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
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


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
        "pluto_ot_full.mp4",
        "-t",
        "23",
        "-vf",
        "crop=1180:750:40:47",
        "-c:a",
        "copy",
        "pluto_ot_gui.mp4",
    ]
    print("Running postprocess crop + trim...")
    subprocess.run(cmd, check=True)


def copy_to_static(
    source_video="pluto_ot_gui.mp4", static_dir="../source/_static"
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
    window.setWindowTitle("pyPLUTO")
    window.show()

    recorder = record_screen_start("pyPLUTO")

    def click_select_file():
        print("Step 1: Clicking 'Select File' button")
        getattr(window, "Select File").animateClick()
        QTimer.singleShot(1000, wait_for_dialog)

    def wait_for_dialog(retries=20):
        dialog = getattr(window, "_file_dialog", None)
        if dialog is not None:
            test_path = pyPLUTO.find_example("")
            QTimer.singleShot(1000, lambda: go_to_mhd(test_path, dialog))
        elif retries > 0:
            QTimer.singleShot(500, lambda: wait_for_dialog(retries - 1))
        else:
            print("ERROR: QFileDialog did not appear.")

    def go_to_mhd(base_path, dialog):
        mhd_path = base_path / "MHD"
        dialog.setDirectory(str(mhd_path))
        print(f"→ Moved to: {mhd_path}")
        QTimer.singleShot(1000, lambda: go_to_orszag(mhd_path, dialog))

    def go_to_orszag(mhd_path, dialog):
        ot_path = mhd_path / "Orszag_Tang"
        dialog.setDirectory(str(ot_path))
        print(f"→ Entered folder: {ot_path}")
        QTimer.singleShot(1000, lambda: close_and_load(ot_path, dialog))

    def close_and_load(folder, dialog):
        dialog.close()
        print("→ Dialog closed.")
        QTimer.singleShot(0, lambda: load_file(folder))

    def load_file(folder):
        print("Step 2: Loading data file...")
        file_path = folder / "data.0001.dbl"
        window.folder_path = str(folder)
        window.datatype = "dbl"
        window.nout = 1
        window.load_data()
        QTimer.singleShot(1000, set_variable_to_prs)

    def set_variable_to_prs():
        print("Step: Selecting 'prs' variable")
        idx = window.var_selector.findText("prs")
        if idx != -1:
            window.var_selector.setFocus()
            window.var_selector.showPopup()
            QTimer.singleShot(1000, lambda: select_prs_index(idx))
        else:
            print("ERROR: 'prs' not found in var_selector")

    def select_prs_index(idx):
        window.var_selector.setCurrentIndex(idx)
        window.var_selector.repaint()
        print("→ 'prs' selected")
        QTimer.singleShot(1000, window.var_selector.hidePopup)
        QTimer.singleShot(2000, set_log_scale)

    def set_log_scale():
        print("Step: Setting vscale to 'log'")
        idx = window.vscale_selector.findText("log")
        if idx != -1:
            window.vscale_selector.setFocus()
            window.vscale_selector.showPopup()
            QTimer.singleShot(1000, lambda: select_log_scale(idx))
        else:
            print("ERROR: 'log' scale not found in vscale_selector")

    def select_log_scale(idx):
        window.vscale_selector.setCurrentIndex(idx)
        window.vscale_selector.repaint()
        QTimer.singleShot(1000, window.vscale_selector.hidePopup)
        print("→ 'log' scale selected")
        QTimer.singleShot(1000, set_vrange_limits)

    def set_vrange_limits():
        print("Step: Setting vmin and vmax")
        time.sleep(1)  # Wait for UI to settle
        window.vrange_min.setText("1.0")
        window.vrange_max.setText("10")
        QTimer.singleShot(
            1000, lambda: plot_variable("prs", open_cmap_mode_dropdown)
        )

    def plot_variable(varname, next_step=None):
        print(f"→ Plotting '{varname}'")
        window.Plot.animateClick()
        QTimer.singleShot(100, window.plot_data)
        if next_step:
            QTimer.singleShot(1000, next_step)

    def open_cmap_mode_dropdown():
        print("Step: Opening colormap mode dropdown (left)")
        idx = window.typecmap_selector.findText("Diverging")
        if idx != -1:
            window.typecmap_selector.setFocus()
            window.typecmap_selector.showPopup()

            # Visually navigate to the item without committing to it
            QTimer.singleShot(1000, lambda: visually_hover_cmap_mode(idx))
        else:
            print("ERROR: 'Diverging' not found in typecmap_selector")

    def visually_hover_cmap_mode(idx):
        # Show the user what we’re about to select
        view = window.typecmap_selector.view()
        model_index = window.typecmap_selector.model().index(idx, 0)
        view.setCurrentIndex(model_index)
        window.typecmap_selector.repaint()

        # Wait 1 second, then actually select & close the dropdown
        QTimer.singleShot(1000, lambda: finalize_cmap_mode(idx))

    def finalize_cmap_mode(idx):
        window.typecmap_selector.hidePopup()
        window.typecmap_selector.setCurrentIndex(idx)
        print("→ 'Diverging' selected")

        QTimer.singleShot(1000, open_colormap_dropdown)  # continue

    def open_colormap_dropdown():
        print("Step: Opening colormap (center) dropdown")
        idx = window.cmap_selector.findText("RdYlBu")
        if idx != -1:
            window.cmap_selector.setFocus()
            window.cmap_selector.showPopup()
            QTimer.singleShot(1000, lambda: select_colormap(idx))
        else:
            print("ERROR: 'RdBu' not found in cmap_selector")

    def select_colormap(idx):
        window.cmap_selector.setCurrentIndex(idx)
        window.cmap_selector.repaint()
        QTimer.singleShot(1000, window.cmap_selector.hidePopup)
        print("→ 'RdBu' selected")
        QTimer.singleShot(1000, check_reverse_cmap)

    def check_reverse_cmap():
        time.sleep(1)
        print("Step: Checking 'reversed' box")
        window.reverse_checkbox.setChecked(True)
        window.reverse_checkbox.repaint()
        QTimer.singleShot(1000, click_reload_canvas)

    def click_reload_canvas():
        print("Step: Clicking 'Reload Canvas'")
        getattr(window, "Update plot").animateClick()
        QTimer.singleShot(3000, close_window)

    def close_window():
        print("✅ Done. Closing window.")
        window.close()

    QTimer.singleShot(1000, click_select_file)
    return app


if __name__ == "__main__":
    recorder = record_screen_start()

    try:
        app = automate_gui()
        app.exec()  # now this runs properly
    finally:
        time.sleep(2)
        record_screen_stop(recorder)
        out, err = recorder.communicate(timeout=5)
        print("ffmpeg stdout:", out.decode())
        print("ffmpeg stderr:", err.decode())
        print("Recording stopped. Processing video...")
        postprocess_video()
        copy_to_static()
