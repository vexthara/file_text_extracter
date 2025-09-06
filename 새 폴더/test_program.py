#!/usr/bin/env python3
"""
Comprehensive test script for Game Text Translator
Tests all major functionality including UI, file processing, and edge cases
"""

import os
import sys
import tempfile
import shutil
import tkinter as tk
from tkinter import ttk
import time
import json

# Add current directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from game_translator import GameTranslator
    print("✓ Successfully imported GameTranslator")
except ImportError as e:
    print(f"✗ Failed to import GameTranslator: {e}")
    sys.exit(1)

class ProgramTester:
    def __init__(self):
        self.test_dir = None
        self.output_dir = None
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name, passed, message=""):
        """Log test results"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✓ {test_name}: PASSED {message}")
        else:
            print(f"✗ {test_name}: FAILED {message}")
    
    def setup_test_environment(self):
        """Create test files and directories"""
        print("\n=== Setting up test environment ===")
        
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp(prefix="game_translator_test_")
        self.output_dir = tempfile.mkdtemp(prefix="game_translator_output_")
        
        print(f"Test directory: {self.test_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Create test files with different extensions
        test_files = {
            "test.csv": 'name,description,value\n"Player Name","Enter your name","Default Player"\n"Score","Your current score","0"',
            "test.erb": '<h1><%= "Welcome to the Game" %></h1>\n<p><%= "Click start to begin" %></p>',
            "test.erh": '# Game Header\nTITLE = "Amazing Game"\nVERSION = "1.0"\nAUTHOR = "Game Developer"',
            "test.py": 'print("Hello World")\nmessage = "This is a test message"\nprint(message)',
            "test.js": 'console.log("JavaScript test");\nconst message = "Hello from JS";',
            "test.xml": '<game><title>Test Game</title><description>A test game for validation</description></game>',
            "test.json": '{"title": "Game Config", "messages": {"welcome": "Welcome to our game!", "goodbye": "Thanks for playing!"}}',
            "large_text.csv": f'id,text\n1,"{"A" * 25000}"\n2,"{"B" * 30000}"',  # Test large text handling
        }
        
        for filename, content in test_files.items():
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Created {len(test_files)} test files")
        
    def test_ui_initialization(self):
        """Test UI initialization"""
        print("\n=== Testing UI Initialization ===")
        
        try:
            root = tk.Tk()
            root.withdraw()  # Hide window during testing
            
            translator = GameTranslator(root)
            
            # Test if all required attributes exist
            required_attrs = ['extracted_texts', 'translations', 'current_directory', 
                            'output_directory', 'dir_var', 'output_var', 'extensions_var']
            
            for attr in required_attrs:
                if hasattr(translator, attr):
                    self.log_test(f"UI Attribute {attr}", True)
                else:
                    self.log_test(f"UI Attribute {attr}", False, f"Missing attribute: {attr}")
            
            # Test default extensions
            default_extensions = translator.extensions_var.get()
            expected_default = ".csv,.erb,.erh"
            self.log_test("Default Extensions", default_extensions == expected_default, 
                         f"Got: {default_extensions}, Expected: {expected_default}")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("UI Initialization", False, f"Exception: {e}")
    
    def test_extension_parsing(self):
        """Test file extension parsing"""
        print("\n=== Testing Extension Parsing ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Test default extensions
            extensions = translator.get_file_extensions()
            expected = ['.csv', '.erb', '.erh']
            self.log_test("Default Extension Parsing", extensions == expected,
                         f"Got: {extensions}, Expected: {expected}")
            
            # Test custom extensions
            translator.extensions_var.set(".py,.js,.cpp")
            extensions = translator.get_file_extensions()
            expected = ['.py', '.js', '.cpp']
            self.log_test("Custom Extension Parsing", extensions == expected,
                         f"Got: {extensions}, Expected: {expected}")
            
            # Test extension normalization (without dots)
            translator.extensions_var.set("py,js,cpp")
            extensions = translator.get_file_extensions()
            expected = ['.py', '.js', '.cpp']
            self.log_test("Extension Normalization", extensions == expected,
                         f"Got: {extensions}, Expected: {expected}")
            
            # Test mixed case
            translator.extensions_var.set(".PY,.JS,.CPP")
            extensions = translator.get_file_extensions()
            expected = ['.py', '.js', '.cpp']
            self.log_test("Case Insensitive Extensions", extensions == expected,
                         f"Got: {extensions}, Expected: {expected}")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Extension Parsing", False, f"Exception: {e}")
    
    def test_preset_functionality(self):
        """Test extension preset buttons"""
        print("\n=== Testing Extension Presets ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Test code preset
            translator.set_extension_preset("code")
            extensions = translator.extensions_var.get()
            self.log_test("Code Preset", ".py" in extensions and ".cpp" in extensions,
                         f"Code preset: {extensions}")
            
            # Test web preset
            translator.set_extension_preset("web")
            extensions = translator.extensions_var.get()
            self.log_test("Web Preset", ".html" in extensions and ".js" in extensions,
                         f"Web preset: {extensions}")
            
            # Test all preset
            translator.set_extension_preset("all")
            extensions = translator.extensions_var.get()
            self.log_test("All Preset", len(extensions.split(',')) > 10,
                         f"All preset has {len(extensions.split(','))} extensions")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Extension Presets", False, f"Exception: {e}")
    
    def test_file_processing(self):
        """Test file processing with different extensions"""
        print("\n=== Testing File Processing ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Set test directories
            translator.current_directory = self.test_dir
            translator.output_directory = self.output_dir
            
            # Test default extensions (.csv,.erb,.erh)
            translator.extensions_var.set(".csv,.erb,.erh")
            translator.extract_texts_python()
            
            csv_erb_erh_count = len(translator.extracted_texts)
            self.log_test("Default Extensions Processing", csv_erb_erh_count > 0,
                         f"Found {csv_erb_erh_count} texts from .csv,.erb,.erh files")
            
            # Test all extensions
            translator.extensions_var.set(".csv,.erb,.erh,.py,.js,.xml,.json")
            translator.extract_texts_python()
            
            all_extensions_count = len(translator.extracted_texts)
            self.log_test("Multiple Extensions Processing", all_extensions_count > csv_erb_erh_count,
                         f"Found {all_extensions_count} texts from multiple extensions")
            
            # Test large text handling
            large_texts = [text for text in translator.extracted_texts if len(text['text']) > 10000]
            self.log_test("Large Text Detection", len(large_texts) > 0,
                         f"Found {len(large_texts)} texts larger than 10k characters")
            
            # Test 50k character limit
            very_large_texts = [text for text in translator.extracted_texts if len(text['text']) > 50000]
            self.log_test("50k Character Limit", len(very_large_texts) == 0,
                         f"No texts exceed 50k limit (found {len(very_large_texts)} oversized)")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("File Processing", False, f"Exception: {e}")
    
    def test_text_chunking(self):
        """Test text chunking functionality"""
        print("\n=== Testing Text Chunking ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Test chunking with exactly 50k characters
            test_text = "A" * 50000
            chunks = translator.split_text_into_chunks(test_text, 50000)
            self.log_test("50k Text No Chunking", len(chunks) == 1 and len(chunks[0]) == 50000,
                         f"50k text produced {len(chunks)} chunks")
            
            # Test chunking with 75k characters
            test_text = "A" * 75000
            chunks = translator.split_text_into_chunks(test_text, 50000)
            self.log_test("75k Text Chunking", len(chunks) == 2,
                         f"75k text produced {len(chunks)} chunks")
            
            # Test all chunks are within limit
            test_text = "A" * 125000
            chunks = translator.split_text_into_chunks(test_text, 50000)
            all_within_limit = all(len(chunk) <= 50000 for chunk in chunks)
            self.log_test("Chunk Size Limit", all_within_limit,
                         f"All {len(chunks)} chunks within 50k limit: {all_within_limit}")
            
            # Test word boundary splitting
            test_text = "word " * 12500  # 62500 characters with spaces
            chunks = translator.split_text_into_chunks(test_text, 50000)
            no_partial_words = all(not chunk.endswith("wor") for chunk in chunks)
            self.log_test("Word Boundary Splitting", no_partial_words,
                         f"No partial words in {len(chunks)} chunks")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Text Chunking", False, f"Exception: {e}")
    
    def test_translation_management(self):
        """Test translation save/load functionality"""
        print("\n=== Testing Translation Management ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Add some test translations
            test_translations = {
                "Hello World": "Hola Mundo",
                "Welcome": "Bienvenido",
                "Goodbye": "Adiós"
            }
            translator.translations = test_translations
            
            # Test translation count
            self.log_test("Translation Storage", len(translator.translations) == 3,
                         f"Stored {len(translator.translations)} translations")
            
            # Test translation file save (simulate)
            translation_file = os.path.join(self.output_dir, "test_translations.json")
            try:
                with open(translation_file, 'w', encoding='utf-8') as f:
                    json.dump(translator.translations, f, ensure_ascii=False, indent=2)
                self.log_test("Translation File Save", os.path.exists(translation_file),
                             "Translation file created successfully")
            except Exception as e:
                self.log_test("Translation File Save", False, f"Save failed: {e}")
            
            # Test translation file load (simulate)
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    loaded_translations = json.load(f)
                self.log_test("Translation File Load", loaded_translations == test_translations,
                             "Translations loaded correctly")
            except Exception as e:
                self.log_test("Translation File Load", False, f"Load failed: {e}")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Translation Management", False, f"Exception: {e}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n=== Testing Error Handling ===")
        
        try:
            root = tk.Tk()
            root.withdraw()
            translator = GameTranslator(root)
            
            # Test empty extensions
            translator.extensions_var.set("")
            extensions = translator.get_file_extensions()
            self.log_test("Empty Extensions Fallback", extensions == ['.csv', '.erb', '.erh'],
                         f"Empty input gave: {extensions}")
            
            # Test invalid directory
            translator.current_directory = "/nonexistent/directory"
            translator.output_directory = self.output_dir
            try:
                translator.extract_texts_python()
                # Should not crash, just find no files
                self.log_test("Invalid Directory Handling", True, "No crash on invalid directory")
            except Exception as e:
                self.log_test("Invalid Directory Handling", False, f"Crashed: {e}")
            
            # Test very long extension list
            long_extensions = ",".join([f".ext{i}" for i in range(100)])
            translator.extensions_var.set(long_extensions)
            extensions = translator.get_file_extensions()
            self.log_test("Long Extension List", len(extensions) == 100,
                         f"Handled {len(extensions)} extensions")
            
            root.destroy()
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {e}")
    
    def cleanup_test_environment(self):
        """Clean up test files and directories"""
        print("\n=== Cleaning up test environment ===")
        
        try:
            if self.test_dir and os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                print(f"Cleaned up test directory: {self.test_dir}")
            
            if self.output_dir and os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                print(f"Cleaned up output directory: {self.output_dir}")
                
        except Exception as e:
            print(f"Warning: Could not clean up test directories: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("Game Text Translator - Comprehensive Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            self.setup_test_environment()
            self.test_ui_initialization()
            self.test_extension_parsing()
            self.test_preset_functionality()
            self.test_file_processing()
            self.test_text_chunking()
            self.test_translation_management()
            self.test_error_handling()
            
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup_test_environment()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print(f"Test Duration: {duration:.2f} seconds")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! The program works perfectly!")
            return True
        else:
            failed_tests = self.total_tests - self.passed_tests
            print(f"\n⚠️  {failed_tests} test(s) failed. Review the issues above.")
            return False

def main():
    """Main test function"""
    tester = ProgramTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ PROGRAM VALIDATION: PASSED")
        print("The Game Text Translator is working perfectly!")
    else:
        print("\n❌ PROGRAM VALIDATION: FAILED")
        print("The Game Text Translator has some issues that need to be addressed.")
    
    return success

if __name__ == "__main__":
    main()
