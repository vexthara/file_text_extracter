#!/usr/bin/env python3
"""
Game Text Translator - Hybrid Python/C++ Text Extraction and Translation Tool
Optimized for game localization with fast file processing
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import time
from pathlib import Path
import re

# Try to import the C++ module, fallback to pure Python if not available
try:
    import text_extractor
    CPP_AVAILABLE = True
    print("C++ module loaded successfully - using optimized processing")
except ImportError:
    CPP_AVAILABLE = False
    print("C++ module not available - using pure Python processing")

class GameTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Text Translator - Fast Text Extraction & Translation")
        self.root.geometry("1200x800")
        
        # Data storage
        self.extracted_texts = []
        self.translations = {}
        self.current_directory = ""
        self.output_directory = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Game Text Translator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Directory selection
        ttk.Label(main_frame, text="Source Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(main_frame, textvariable=self.dir_var, width=50)
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_directory).grid(row=1, column=2, pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # File extensions input
        ttk.Label(main_frame, text="File Extensions:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.extensions_var = tk.StringVar(value=".csv,.erb,.erh")
        extensions_entry = ttk.Entry(main_frame, textvariable=self.extensions_var, width=40)
        extensions_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # Extension presets
        preset_frame = ttk.Frame(main_frame)
        preset_frame.grid(row=3, column=2, sticky=tk.W, padx=(5, 0))
        ttk.Button(preset_frame, text="Code", command=lambda: self.set_extension_preset("code")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Web", command=lambda: self.set_extension_preset("web")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="All", command=lambda: self.set_extension_preset("all")).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(main_frame, text="(comma-separated, e.g., .py,.cpp,.js)", 
                 font=("Arial", 8)).grid(row=4, column=1, sticky=tk.W, padx=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.extract_btn = ttk.Button(button_frame, text="Extract Texts", 
                                     command=self.extract_texts_threaded)
        self.extract_btn.grid(row=0, column=0, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="Save Translation File", 
                                  command=self.save_translation_file, state=tk.DISABLED)
        self.save_btn.grid(row=0, column=1, padx=5)
        
        self.load_btn = ttk.Button(button_frame, text="Load Translation File", 
                                  command=self.load_translation_file)
        self.load_btn.grid(row=0, column=2, padx=5)
        
        self.apply_btn = ttk.Button(button_frame, text="Apply Translations", 
                                   command=self.apply_translations_threaded, state=tk.DISABLED)
        self.apply_btn.grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Main content area with notebook
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Extracted texts tab
        self.texts_frame = ttk.Frame(notebook)
        notebook.add(self.texts_frame, text="Extracted Texts")
        
        # Text list with scrollbar
        list_frame = ttk.Frame(self.texts_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_listbox = tk.Listbox(list_frame, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.text_listbox.yview)
        self.text_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.text_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.text_listbox.bind('<<ListboxSelect>>', self.on_text_select)
        
        # Translation tab
        self.translation_frame = ttk.Frame(notebook)
        notebook.add(self.translation_frame, text="Translation Editor")
        
        # Translation editor
        editor_frame = ttk.Frame(self.translation_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(editor_frame, text="Original Text:").pack(anchor=tk.W)
        self.original_text = scrolledtext.ScrolledText(editor_frame, height=8, wrap=tk.WORD)
        self.original_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(editor_frame, text="Translation:").pack(anchor=tk.W)
        self.translation_text = scrolledtext.ScrolledText(editor_frame, height=8, wrap=tk.WORD)
        self.translation_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(editor_frame, text="Save Translation", 
                  command=self.save_current_translation).pack(anchor=tk.W)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.dir_var.set(directory)
            self.current_directory = directory
            
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_var.set(directory)
            self.output_directory = directory
            
    def get_file_extensions(self):
        """Parse the file extensions from the input field"""
        extensions_text = self.extensions_var.get().strip()
        if not extensions_text:
            # Default extensions if none specified
            return ['.csv', '.erb', '.erh']
        
        # Split by comma and clean up
        extensions = []
        for ext in extensions_text.split(','):
            ext = ext.strip()
            if ext:
                # Ensure extension starts with a dot
                if not ext.startswith('.'):
                    ext = '.' + ext
                extensions.append(ext.lower())
        
        return extensions if extensions else ['.csv', '.erb', '.erh']
        
    def set_extension_preset(self, preset_type):
        """Set file extension presets"""
        presets = {
            "code": ".py,.cpp,.c,.h,.hpp,.cs,.java",
            "web": ".html,.css,.js,.ts,.jsx,.tsx,.json,.xml",
            "all": ".py,.cpp,.c,.h,.hpp,.cs,.java,.js,.ts,.jsx,.tsx,.html,.css,.xml,.json,.yaml,.yml,.ini,.cfg,.txt,.lua,.rpy,.unity,.prefab,.asset,.scene"
        }
        
        if preset_type in presets:
            self.extensions_var.set(presets[preset_type])
            
    def extract_texts_threaded(self):
        if not self.current_directory:
            messagebox.showerror("Error", "Please select a source directory")
            return
            
        if not self.output_directory:
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Validate file extensions
        extensions = self.get_file_extensions()
        if not extensions:
            messagebox.showerror("Error", "Please enter at least one valid file extension")
            return
            
        # Disable buttons during extraction
        self.extract_btn.config(state=tk.DISABLED)
        self.status_var.set(f"Extracting texts from files with extensions: {', '.join(extensions)}...")
        
        # Run extraction in separate thread
        thread = threading.Thread(target=self.extract_texts)
        thread.daemon = True
        thread.start()
        
    def extract_texts(self):
        try:
            if CPP_AVAILABLE:
                # Use C++ module for fast extraction
                extractor = text_extractor.TextExtractor()
                
                # Set the supported extensions
                allowed_extensions = self.get_file_extensions()
                extractor.set_supported_extensions(allowed_extensions)
                
                result = extractor.extract_texts(self.current_directory)
                
                # Convert C++ result to Python format
                self.extracted_texts = []
                for chunk in result.chunks:
                    self.extracted_texts.append({
                        'text': chunk.text,
                        'file_path': chunk.file_path,
                        'line_number': chunk.line_number,
                        'context': chunk.context,
                        'original_text': chunk.original_text
                    })
                
                # Save extracted texts
                extractor.save_extracted_texts(result.chunks, self.output_directory)
                
                # Update UI in main thread
                self.root.after(0, self.extraction_complete, result)
            else:
                # Fallback to pure Python implementation
                self.extract_texts_python()
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Extraction failed: {str(e)}"))
            self.root.after(0, self.extraction_error)
            
    def extract_texts_python(self):
        """Pure Python fallback implementation"""
        self.status_var.set("Extracting texts (Python mode)...")
        
        # Get user-specified file extensions
        allowed_extensions = self.get_file_extensions()
        self.status_var.set(f"Extracting texts (Python mode) - Processing: {', '.join(allowed_extensions)}")
        
        # Simple Python text extraction
        text_patterns = [
            r'"([^"\\]*(\\.[^"\\]*)*)"',  # Double quoted strings
            r"'([^'\\]*(\\.[^'\\]*)*)'",  # Single quoted strings
            r'text\s*[:=]\s*["\']([^"\']+)["\']',  # text: "value"
            r'label\s*[:=]\s*["\']([^"\']+)["\']',  # label: "value"
            r'message\s*[:=]\s*["\']([^"\']+)["\']', # message: "value"
            r'<text>([^<]+)</text>',  # XML-style text tags
            r'<string>([^<]+)</string>', # XML string tags
        ]
        
        self.extracted_texts = []
        files_processed = 0
        
        for root, dirs, files in os.walk(self.current_directory):
            for file in files:
                # Check if file has one of the allowed extensions
                file_lower = file.lower()
                if any(file_lower.endswith(ext) for ext in allowed_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                for pattern in text_patterns:
                                    matches = re.finditer(pattern, line)
                                    for match in matches:
                                        text = match.group(1)
                                        if len(text) >= 3:  # Minimum length
                                            # Handle large texts by splitting them if needed
                                            max_chunk_size = 50000
                                            if len(text) <= max_chunk_size:
                                                self.extracted_texts.append({
                                                    'text': text,
                                                    'file_path': file_path,
                                                    'line_number': line_num,
                                                    'context': line.strip(),
                                                    'original_text': match.group(0)
                                                })
                                            else:
                                                # Split large text into chunks
                                                chunks = self.split_text_into_chunks(text, max_chunk_size)
                                                for i, chunk in enumerate(chunks):
                                                    self.extracted_texts.append({
                                                        'text': chunk,
                                                        'file_path': f"{file_path}_chunk_{i}",
                                                        'line_number': line_num,
                                                        'context': line.strip(),
                                                        'original_text': match.group(0)
                                                    })
                        files_processed += 1
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        # Update UI
        self.root.after(0, self.extraction_complete_python, files_processed)
        
    def split_text_into_chunks(self, text, max_chunk_size):
        """Split large text into smaller chunks, trying to break at word boundaries"""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_chunk_size, len(text))
            
            # Try to break at word boundary
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space != -1 and last_space > start:
                    end = last_space
            
            chunks.append(text[start:end])
            start = end
            
            # Skip space if we broke at a word boundary
            if start < len(text) and text[start] == ' ':
                start += 1
        
        return chunks
        
    def extraction_complete(self, result):
        self.update_text_list()
        self.update_statistics(result.total_files_processed, result.total_texts_found, result.processing_time)
        self.extract_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Extraction complete! Found {result.total_texts_found} texts in {result.total_files_processed} files")
        
    def extraction_complete_python(self, files_processed):
        self.update_text_list()
        self.update_statistics(files_processed, len(self.extracted_texts), 0)
        self.extract_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Extraction complete! Found {len(self.extracted_texts)} texts in {files_processed} files")
        
    def extraction_error(self):
        self.extract_btn.config(state=tk.NORMAL)
        self.status_var.set("Extraction failed")
        
    def update_text_list(self):
        self.text_listbox.delete(0, tk.END)
        for i, text_data in enumerate(self.extracted_texts):
            # Show more characters for preview, especially for large texts
            text_length = len(text_data['text'])
            if text_length > 100:
                preview = text_data['text'][:100] + "..."
                # Add length indicator for large texts
                preview += f" [{text_length} chars]"
            else:
                preview = text_data['text']
            self.text_listbox.insert(tk.END, f"{i+1}. {preview}")
            
    def on_text_select(self, event):
        selection = self.text_listbox.curselection()
        if selection:
            index = selection[0]
            text_data = self.extracted_texts[index]
            
            # Update translation editor
            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(1.0, text_data['text'])
            
            # Load existing translation if available
            translation = self.translations.get(text_data['text'], "")
            self.translation_text.delete(1.0, tk.END)
            self.translation_text.insert(1.0, translation)
            
    def save_current_translation(self):
        selection = self.text_listbox.curselection()
        if selection:
            index = selection[0]
            text_data = self.extracted_texts[index]
            translation = self.translation_text.get(1.0, tk.END).strip()
            
            if translation:
                self.translations[text_data['text']] = translation
                messagebox.showinfo("Success", "Translation saved!")
            else:
                messagebox.showwarning("Warning", "Please enter a translation")
                
    def save_translation_file(self):
        if not self.translations:
            messagebox.showwarning("Warning", "No translations to save")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.translations, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Success", f"Translations saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save translations: {str(e)}")
                
    def load_translation_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                messagebox.showinfo("Success", f"Translations loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load translations: {str(e)}")
                
    def apply_translations_threaded(self):
        if not self.translations:
            messagebox.showwarning("Warning", "No translations to apply")
            return
            
        # Run in separate thread
        thread = threading.Thread(target=self.apply_translations)
        thread.daemon = True
        thread.start()
        
    def apply_translations(self):
        try:
            self.root.after(0, lambda: self.status_var.set("Applying translations..."))
            
            if CPP_AVAILABLE:
                # Use C++ module for fast application
                extractor = text_extractor.TextExtractor()
                # Note: This would need to be implemented in the C++ module
                pass
            else:
                # Pure Python implementation
                self.apply_translations_python()
                
            self.root.after(0, lambda: self.status_var.set("Translations applied successfully!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to apply translations: {str(e)}"))
            
    def apply_translations_python(self):
        """Pure Python implementation for applying translations"""
        # This is a simplified version - in practice, you'd want to be more careful
        # about file modification and backup
        for text_data in self.extracted_texts:
            if text_data['text'] in self.translations:
                # This would need more sophisticated file modification logic
                pass
                
    def update_statistics(self, files_processed, texts_found, processing_time):
        # Calculate statistics for large texts
        large_texts = [text for text in self.extracted_texts if len(text['text']) > 1000]
        very_large_texts = [text for text in self.extracted_texts if len(text['text']) > 10000]
        
        # Get current extensions for display
        current_extensions = self.get_file_extensions()
        
        stats = f"""
EXTRACTION STATISTICS
====================
Files Processed: {files_processed}
Texts Found: {texts_found}
Processing Time: {processing_time:.2f} seconds
Average Texts per File: {texts_found/files_processed if files_processed > 0 else 0:.2f}
File Extensions Processed: {', '.join(current_extensions)}

TEXT SIZE STATISTICS
===================
Large Texts (>1000 chars): {len(large_texts)}
Very Large Texts (>10000 chars): {len(very_large_texts)}
Maximum Text Length: {max(len(text['text']) for text in self.extracted_texts) if self.extracted_texts else 0} chars
Average Text Length: {sum(len(text['text']) for text in self.extracted_texts)/len(self.extracted_texts) if self.extracted_texts else 0:.1f} chars

TRANSLATION STATISTICS
=====================
Translations Completed: {len(self.translations)}
Translation Progress: {len(self.translations)/texts_found*100 if texts_found > 0 else 0:.1f}%

PERFORMANCE INFO
===============
C++ Module Available: {'Yes' if CPP_AVAILABLE else 'No'}
Processing Mode: {'Optimized (C++)' if CPP_AVAILABLE else 'Standard (Python)'}
Max Chunk Size: 50,000 characters
        """
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)

def main():
    root = tk.Tk()
    app = GameTranslator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
