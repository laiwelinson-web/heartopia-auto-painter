"""
GUI Application - Tkinter-based interface for Heartopia Auto-Painter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import logging

from src.image_processor import ImageProcessor
from src.heartopia_adapter import HeartopiaAdapter
from src.painter_bot import PainterBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HeartopiaAutopainterGUI:
    """
    Tkinter GUI for Heartopia Auto-Painter.
    """
    
    def __init__(self, root):
        """
        Initialize GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Heartopia Auto-Painter")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.input_image_path = tk.StringVar()
        self.output_image_path = tk.StringVar()
        self.canvas_size = tk.IntVar(value=512)
        self.click_speed = tk.DoubleVar(value=0.05)
        self.is_processing = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """
        Create GUI widgets.
        """
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame,
            text="Heartopia Auto-Painter 🎨",
            font=("Arial", 18, "bold")
        )
        title_label.pack()
        
        # Input section
        input_frame = ttk.LabelFrame(self.root, text="Image Processing", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Input Image:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_image_path, width=40).grid(
            row=0, column=1, sticky=tk.EW, padx=5
        )
        ttk.Button(
            input_frame,
            text="Browse...",
            command=self.browse_input_image
        ).grid(row=0, column=2, padx=5)
        
        ttk.Label(input_frame, text="Output Image:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.output_image_path, width=40).grid(
            row=1, column=1, sticky=tk.EW, padx=5
        )
        ttk.Button(
            input_frame,
            text="Browse...",
            command=self.browse_output_image
        ).grid(row=1, column=2, padx=5)
        
        ttk.Label(input_frame, text="Canvas Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        canvas_combo = ttk.Combobox(
            input_frame,
            textvariable=self.canvas_size,
            values=[512, 1024],
            state="readonly",
            width=10
        )
        canvas_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Processing buttons
        process_frame = ttk.Frame(self.root)
        process_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            process_frame,
            text="Extract Line Art",
            command=self.extract_line_art
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            process_frame,
            text="Preview Output",
            command=self.preview_output
        ).pack(side=tk.LEFT, padx=5)
        
        # Automation section
        automation_frame = ttk.LabelFrame(self.root, text="Automation Settings", padding=10)
        automation_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(automation_frame, text="Click Speed (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(automation_frame, textvariable=self.click_speed, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )
        ttk.Label(automation_frame, text="(0.01 = fast, 0.1 = slow)", font=("Arial", 8)).grid(
            row=0, column=2, sticky=tk.W, padx=5
        )
        
        # Automation buttons
        automation_btn_frame = ttk.Frame(self.root)
        automation_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            automation_btn_frame,
            text="Start Painting",
            command=self.start_painting
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            automation_btn_frame,
            text="Stop Painting",
            command=self.stop_painting
        ).pack(side=tk.LEFT, padx=5)
        
        # Status/Log section
        log_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def log_message(self, message: str):
        """
        Add message to log.
        
        Args:
            message: Message to log
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def browse_input_image(self):
        """
        Browse for input image.
        """
        path = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if path:
            self.input_image_path.set(path)
            self.log_message(f"Selected input: {path}")
    
    def browse_output_image(self):
        """
        Browse for output image.
        """
        path = filedialog.asksaveasfilename(
            title="Save Output Image",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
            defaultextension=".png"
        )
        if path:
            self.output_image_path.set(path)
            self.log_message(f"Selected output: {path}")
    
    def extract_line_art(self):
        """
        Extract line art from image.
        """
        if not self.input_image_path.get():
            messagebox.showerror("Error", "Please select an input image")
            return
        
        if not self.output_image_path.get():
            messagebox.showerror("Error", "Please specify an output path")
            return
        
        def process():
            try:
                self.is_processing = True
                self.log_message("Starting image processing...")
                
                processor = ImageProcessor(canvas_size=self.canvas_size.get())
                line_art = processor.extract_line_art(self.input_image_path.get())
                
                adapter = HeartopiaAdapter(canvas_size=self.canvas_size.get())
                adapted = adapter.adapt_for_heartopia(line_art)
                
                processor.save_image(adapted, self.output_image_path.get())
                
                self.log_message("✓ Image processing completed successfully!")
                messagebox.showinfo("Success", "Image processed successfully!")
                
            except Exception as e:
                self.log_message(f"✗ Error: {e}")
                messagebox.showerror("Error", f"Processing failed: {e}")
            finally:
                self.is_processing = False
        
        thread = threading.Thread(target=process)
        thread.start()
    
    def preview_output(self):
        """
        Preview output image.
        """
        if not self.output_image_path.get():
            messagebox.showerror("Error", "No output image to preview")
            return
        
        output_path = Path(self.output_image_path.get())
        if not output_path.exists():
            messagebox.showerror("Error", "Output file not found. Process image first.")
            return
        
        self.log_message(f"Preview: {output_path}")
        # Note: You can implement image preview here using PIL/Tkinter
    
    def start_painting(self):
        """
        Start automated painting.
        """
        if not self.output_image_path.get():
            messagebox.showerror("Error", "Please process an image first")
            return
        
        output_path = Path(self.output_image_path.get())
        if not output_path.exists():
            messagebox.showerror("Error", "Output image file not found")
            return
        
        def paint():
            try:
                self.is_processing = True
                self.log_message("Initializing painter bot...")
                
                bot = PainterBot(
                    click_speed=self.click_speed.get(),
                    safe_mode=True,
                    verify_clicks=True
                )
                
                self.log_message("Setting up game window...")
                if not bot.setup_game_window():
                    self.log_message("Warning: Could not detect game window")
                
                self.log_message("Starting in 5 seconds...")
                bot.countdown(5)
                
                self.log_message("Painting...")
                bot.paint_image(
                    str(output_path),
                    canvas_start_x=0,
                    canvas_start_y=0,
                    canvas_size=self.canvas_size.get()
                )
                
                self.log_message("✓ Painting completed!")
                messagebox.showinfo("Success", "Painting completed successfully!")
                
            except Exception as e:
                self.log_message(f"✗ Error: {e}")
                messagebox.showerror("Error", f"Painting failed: {e}")
            finally:
                self.is_processing = False
        
        thread = threading.Thread(target=paint)
        thread.start()
    
    def stop_painting(self):
        """
        Stop painting.
        """
        self.log_message("Stopping painting...")
        # Implement stop logic here


def main():
    """
    Main entry point.
    """
    root = tk.Tk()
    app = HeartopiaAutopainterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
