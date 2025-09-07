#!/usr/bin/env python3
"""
Game Text Translator Launcher
Automatically sets up and runs the program without needing terminal access
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class GameTranslatorLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game Text Translator - Setup & Launcher")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.check_environment()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Game Text Translator", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Setup Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.setup_btn = ttk.Button(button_frame, text="Setup & Install", 
                                   command=self.setup_environment, state=tk.DISABLED)
        self.setup_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.run_btn = ttk.Button(button_frame, text="Run Translator", 
                                 command=self.run_translator, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_btn = ttk.Button(button_frame, text="Exit", 
                                  command=self.root.quit)
        self.exit_btn.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Info label
        info_text = """
This launcher will:
1. Check if Python and required packages are available
2. Install missing dependencies automatically
3. Try to build the C++ optimization module (optional)
4. Launch the Game Text Translator

The program will work even if the C++ module can't be built - it will use pure Python mode.
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, 
                              font=("Arial", 9))
        info_label.pack(fill=tk.X)
        
    def log_message(self, message):
        """Add a message to the status text"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def check_environment(self):
        """Check the current environment and enable appropriate buttons"""
        self.log_message("Checking environment...")
        
        # Check Python version
        python_version = sys.version_info
        self.log_message(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version < (3, 6):
            self.log_message("ERROR: Python 3.6 or higher is required!")
            return
            
        # Check if required packages are available
        try:
            import tkinter
            self.log_message("✓ tkinter is available")
        except ImportError:
            self.log_message("ERROR: tkinter is not available!")
            return
            
        # Check if pybind11 is available
        try:
            import pybind11
            self.log_message("✓ pybind11 is available")
            pybind11_available = True
        except ImportError:
            self.log_message("⚠ pybind11 not found - will install it")
            pybind11_available = False
            
        # Check if C++ module is already built
        try:
            import text_extractor
            self.log_message("✓ C++ optimization module is available")
            cpp_available = True
        except ImportError:
            self.log_message("⚠ C++ module not found - will try to build it")
            cpp_available = False
            
        # Enable setup button
        self.setup_btn.config(state=tk.NORMAL)
        
        if pybind11_available and cpp_available:
            self.log_message("✓ Environment is ready!")
            self.run_btn.config(state=tk.NORMAL)
        else:
            self.log_message("⚠ Setup required - click 'Setup & Install' button")
            
    def setup_environment(self):
        """Setup the environment by installing dependencies and building modules"""
        self.setup_btn.config(state=tk.DISABLED)
        self.run_btn.config(state=tk.DISABLED)
        
        # Run setup in a separate thread
        thread = threading.Thread(target=self.setup_thread)
        thread.daemon = True
        thread.start()
        
    def setup_thread(self):
        """Setup thread that runs the actual installation"""
        try:
            self.log_message("\n=== Starting Setup ===")
            
            # Install requirements
            self.log_message("Installing requirements...")
            self.progress_var.set(20)
            
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.log_message("✓ Requirements installed successfully")
                else:
                    self.log_message(f"⚠ Warning installing requirements: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.log_message("⚠ Timeout installing requirements - continuing anyway")
            except Exception as e:
                self.log_message(f"⚠ Error installing requirements: {e}")
                
            self.progress_var.set(50)
            
            # Try to build C++ module
            self.log_message("Building C++ optimization module...")
            try:
                result = subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.log_message("✓ C++ module built successfully")
                else:
                    self.log_message(f"⚠ C++ module build failed: {result.stderr}")
                    self.log_message("Program will use Python-only mode")
            except subprocess.TimeoutExpired:
                self.log_message("⚠ Timeout building C++ module - using Python mode")
            except Exception as e:
                self.log_message(f"⚠ Error building C++ module: {e}")
                self.log_message("Program will use Python-only mode")
                
            self.progress_var.set(100)
            
            # Check final status
            try:
                import text_extractor
                self.log_message("✓ C++ optimization module is working!")
                cpp_working = True
            except ImportError:
                self.log_message("✓ Using Python-only mode (still fast!)")
                cpp_working = False
                
            self.log_message("\n=== Setup Complete ===")
            self.log_message("You can now run the Game Text Translator!")
            
            # Enable run button
            self.run_btn.config(state=tk.NORMAL)
            self.setup_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log_message(f"ERROR during setup: {e}")
            self.setup_btn.config(state=tk.NORMAL)
            
    def run_translator(self):
        """Run the main translator program"""
        try:
            self.log_message("Starting Game Text Translator...")
            
            # Import and run the main program
            import game_translator
            game_translator.main()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start translator: {e}")
            self.log_message(f"Error: {e}")
            
    def run(self):
        """Start the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        launcher = GameTranslatorLauncher()
        launcher.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
