import tkinter as tk
import argparse
from tkinter import font

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry(f'{int(width)}x{int(height)}+{int(x)}+{int(y)}')

def main():
    parser = argparse.ArgumentParser(description="Show Aegis alert overlay.")
    parser.add_argument("--title", required=True, help="Alert Title")
    parser.add_argument("--message", required=True, help="Alert Message")
    args = parser.parse_args()

    root = tk.Tk()
    root.title(args.title)
    
    # Borderless window with transparent key to avoid DWM invis issues on Windows
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    bg_color = "#050806"
    
    # Determine border color based on title (heuristics)
    title_lower = args.title.lower()
    if 'network' in title_lower or 'tcp' in title_lower:
        border_color = "#06b6d4" # Cyan
        header_text = "AEGIS EDGE SHIELD"
    elif 'unauthorized' in title_lower or 'rate limit' in title_lower or 'throttle' in title_lower:
        border_color = "#f97316" # Orange
        header_text = "AEGIS SYSTEM OVERWATCH"
    else:
        border_color = "#ef4444" # Red
        header_text = "AEGIS THREAT VECTOR"

    # Configure size and position
    window_width = 800
    window_height = 400
    center_window(root, window_width, window_height)
    
    # Base container with transparent-safe approach if needed, but solid works best
    root.configure(bg=bg_color)
    
    # Main glowing frame effect
    outer_frame = tk.Frame(root, bg=border_color, bd=2)
    outer_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    inner_frame = tk.Frame(outer_frame, bg=bg_color, bd=0)
    inner_frame.pack(fill=tk.BOTH, expand=True)

    # Styling for text
    try:
        title_font = font.Font(family="Consolas", size=28, weight="bold")
        msg_font = font.Font(family="Consolas", size=16)
        header_font = font.Font(family="Consolas", size=12, weight="bold")
    except:
        title_font = font.Font(family="Courier New", size=28, weight="bold")
        msg_font = font.Font(family="Courier New", size=16)
        header_font = font.Font(family="Courier New", size=12, weight="bold")

    # Header
    header_container = tk.Frame(inner_frame, bg=bg_color)
    header_container.pack(fill=tk.X, padx=20, pady=(20, 0))
    
    header_label = tk.Label(header_container, text=f"[{header_text}]", font=header_font, fg=border_color, bg=bg_color)
    header_label.pack(anchor="w")
    
    separator = tk.Frame(inner_frame, bg=border_color, height=1)
    separator.pack(fill=tk.X, padx=20, pady=(5, 20))

    # Alert Content
    title_label = tk.Label(inner_frame, text=f"⚠ {args.title}", font=title_font, fg=border_color, bg=bg_color)
    title_label.pack(pady=(20, 10))

    msg_label = tk.Label(inner_frame, text=args.message, font=msg_font, fg="#e2e8f0", bg=bg_color, justify=tk.CENTER, wraplength=700)
    msg_label.pack(pady=10, padx=20)

    # Footer
    footer_label = tk.Label(inner_frame, text="SYSTEM LOCKED // AUTORESOLVING...", font=header_font, fg="#475569", bg=bg_color)
    footer_label.pack(side="bottom", pady=20)

    # Close logic: auto-close after 2000 ms (2 seconds as requested)
    root.bind("<Button-1>", lambda e: root.destroy())
    root.after(2000, root.destroy)
    
    root.mainloop()

if __name__ == "__main__":
    main()
