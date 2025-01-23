from tkinter import *
from sidebar_operations import show_filter_sidebar, show_adjust_sidebar, sidebar_canvas, hide_adjust_sidebar, hide_filter_sidebar, adjustment_sidebar_canvas,d


# Toggle Filter sidebar
def toggle_sidebar():
    if sidebar_canvas.winfo_ismapped():
        hide_filter_sidebar()
    else:
        if adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        show_filter_sidebar()


#toggler of adjust
def toggle_adjust_sidebar():
    if adjustment_sidebar_canvas.winfo_ismapped():
        hide_adjust_sidebar()
    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif draw_sidebar_canvas.winfo_ismapped():
            hide_draw_sidebar()
        show_adjust_sidebar()

is_draw_tool_active = False
# Drawing Sidebar Toggle Function
def toggle_draw_sidebar():
    global is_draw_tool_active
    if draw_sidebar_canvas.winfo_ismapped():
        hide_draw_sidebar()
        is_draw_tool_active = False

    else:
        if sidebar_canvas.winfo_ismapped():
            hide_filter_sidebar()
        elif adjustment_sidebar_canvas.winfo_ismapped():
            hide_adjust_sidebar()
        show_draw_sidebar()
        is_draw_tool_active = True
