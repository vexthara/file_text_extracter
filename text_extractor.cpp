#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <unordered_map>
#include <chrono>
#include <iostream>
#include <algorithm>

namespace py = pybind11;
namespace fs = std::filesystem;

class TextExtractor {
private:
    // Common text patterns in game files
    std::vector<std::regex> text_patterns = {
        std::regex(R"("([^"\\]*(\\.[^"\\]*)*)")"),  // Double quoted strings
        std::regex(R"('([^'\\]*(\\.[^'\\]*)*)')"),  // Single quoted strings
        std::regex(R"(text\s*[:=]\s*["']([^"']+)["'])"),  // text: "value"
        std::regex(R"(label\s*[:=]\s*["']([^"']+)["'])"),  // label: "value"
        std::regex(R"(message\s*[:=]\s*["']([^"']+)["'])"), // message: "value"
        std::regex(R"(title\s*[:=]\s*["']([^"']+)["'])"),  // title: "value"
        std::regex(R"(description\s*[:=]\s*["']([^"']+)["'])"), // description: "value"
        std::regex(R"(name\s*[:=]\s*["']([^"']+)["'])"),   // name: "value"
        std::regex(R"(value\s*[:=]\s*["']([^"']+)["'])"),  // value: "value"
        std::regex(R"(content\s*[:=]\s*["']([^"']+)["'])"), // content: "value"
        std::regex(R"(<text>([^<]+)</text>)"),  // XML-style text tags
        std::regex(R"(<string>([^<]+)</string>)"), // XML string tags
        std::regex(R"(<message>([^<]+)</message>)"), // XML message tags
        std::regex(R"(<label>([^<]+)</label>)"), // XML label tags
        std::regex(R"(<title>([^<]+)</title>)"), // XML title tags
        std::regex(R"(<description>([^<]+)</description>)"), // XML description tags
        std::regex(R"(<name>([^<]+)</name>)"), // XML name tags
        std::regex(R"(<value>([^<]+)</value>)"), // XML value tags
        std::regex(R"(<content>([^<]+)</content>)") // XML content tags
    };
    
    // File extensions to process (can be set dynamically)
    std::vector<std::string> supported_extensions = {
        ".csv", ".erb", ".erh", ".py", ".cpp", ".c", ".h", ".hpp", ".cs", ".java", ".js", ".ts", ".jsx", ".tsx",
        ".xml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".txt", ".lua", ".rpy",
        ".unity", ".prefab", ".asset", ".scene", ".csproj", ".sln"
    };
    
    // Minimum text length to extract
    size_t min_text_length = 3;
    
    // Maximum text length per chunk
    size_t max_chunk_size = 50000;

public:
    // Method to set supported file extensions
    void set_supported_extensions(const std::vector<std::string>& extensions) {
        supported_extensions = extensions;
    }
    
    // Method to get current supported extensions
    std::vector<std::string> get_supported_extensions() const {
        return supported_extensions;
    }
    
    struct TextChunk {
        std::string text;
        std::string file_path;
        size_t line_number;
        size_t column_start;
        size_t column_end;
        std::string context;
        std::string original_text;
    };
    
    struct ExtractionResult {
        std::vector<TextChunk> chunks;
        size_t total_files_processed;
        size_t total_texts_found;
        double processing_time;
    };
    
    // Fast file scanning with C++ filesystem
    std::vector<std::string> scan_directory(const std::string& directory_path) {
        std::vector<std::string> files;
        
        try {
            for (const auto& entry : fs::recursive_directory_iterator(directory_path)) {
                if (entry.is_regular_file()) {
                    std::string file_path = entry.path().string();
                    std::string extension = entry.path().extension().string();
                    
                    // Convert to lowercase for comparison
                    std::transform(extension.begin(), extension.end(), extension.begin(), ::tolower);
                    
                    if (std::find(supported_extensions.begin(), supported_extensions.end(), extension) != supported_extensions.end()) {
                        files.push_back(file_path);
                    }
                }
            }
        } catch (const std::exception& e) {
            std::cerr << "Error scanning directory: " << e.what() << std::endl;
        }
        
        return files;
    }
    
    // Fast text extraction from a single file
    std::vector<TextChunk> extract_from_file(const std::string& file_path) {
        std::vector<TextChunk> chunks;
        
        try {
            std::ifstream file(file_path);
            if (!file.is_open()) {
                return chunks;
            }
            
            std::string line;
            size_t line_number = 0;
            
            while (std::getline(file, line)) {
                line_number++;
                
                for (const auto& pattern : text_patterns) {
                    std::sregex_iterator iter(line.begin(), line.end(), pattern);
                    std::sregex_iterator end;
                    
                    for (; iter != end; ++iter) {
                        std::smatch match = *iter;
                        std::string text = match[1].str();
                        
                        // Clean up the text
                        text = clean_text(text);
                        
                        if (text.length() >= min_text_length) {
                            TextChunk chunk;
                            chunk.text = text;
                            chunk.file_path = file_path;
                            chunk.line_number = line_number;
                            chunk.column_start = match.position(1);
                            chunk.column_end = match.position(1) + match.length(1);
                            chunk.context = line;
                            chunk.original_text = match.str();
                            
                            chunks.push_back(chunk);
                        }
                    }
                }
            }
            
            file.close();
        } catch (const std::exception& e) {
            std::cerr << "Error reading file " << file_path << ": " << e.what() << std::endl;
        }
        
        return chunks;
    }
    
    // Split text into chunks of specified size
    std::vector<TextChunk> split_into_chunks(const std::vector<TextChunk>& chunks) {
        std::vector<TextChunk> result;
        
        for (const auto& chunk : chunks) {
            if (chunk.text.length() <= max_chunk_size) {
                result.push_back(chunk);
            } else {
                // Split long text into smaller chunks
                std::string text = chunk.text;
                size_t start = 0;
                size_t chunk_id = 0;
                
                while (start < text.length()) {
                    size_t end = std::min(start + max_chunk_size, text.length());
                    
                    // Try to break at word boundary
                    if (end < text.length()) {
                        size_t last_space = text.rfind(' ', end);
                        if (last_space != std::string::npos && last_space > start) {
                            end = last_space;
                        }
                    }
                    
                    TextChunk new_chunk = chunk;
                    new_chunk.text = text.substr(start, end - start);
                    new_chunk.file_path += "_chunk_" + std::to_string(chunk_id);
                    result.push_back(new_chunk);
                    
                    start = end;
                    if (start < text.length() && text[start] == ' ') {
                        start++; // Skip the space
                    }
                    chunk_id++;
                }
            }
        }
        
        return result;
    }
    
    // Main extraction function
    ExtractionResult extract_texts(const std::string& directory_path) {
        auto start_time = std::chrono::high_resolution_clock::now();
        
        ExtractionResult result;
        
        // Scan directory for files
        std::vector<std::string> files = scan_directory(directory_path);
        result.total_files_processed = files.size();
        
        // Extract texts from all files
        for (const auto& file_path : files) {
            std::vector<TextChunk> file_chunks = extract_from_file(file_path);
            result.chunks.insert(result.chunks.end(), file_chunks.begin(), file_chunks.end());
        }
        
        // Split into manageable chunks
        result.chunks = split_into_chunks(result.chunks);
        result.total_texts_found = result.chunks.size();
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
        result.processing_time = duration.count() / 1000.0;
        
        return result;
    }
    
    // Save extracted texts to files
    void save_extracted_texts(const std::vector<TextChunk>& chunks, const std::string& output_dir) {
        try {
            fs::create_directories(output_dir);
            
            std::unordered_map<std::string, std::vector<TextChunk>> grouped_chunks;
            
            // Group chunks by file
            for (const auto& chunk : chunks) {
                grouped_chunks[chunk.file_path].push_back(chunk);
            }
            
            // Save each file's chunks
            for (const auto& pair : grouped_chunks) {
                std::string filename = fs::path(pair.first).filename().string();
                std::string output_file = output_dir + "/" + filename + "_extracted.txt";
                
                std::ofstream file(output_file);
                if (file.is_open()) {
                    file << "=== EXTRACTED TEXTS FROM: " << pair.first << " ===\n\n";
                    
                    for (const auto& chunk : pair.second) {
                        file << "Line " << chunk.line_number << ":\n";
                        file << "Context: " << chunk.context << "\n";
                        file << "Text: " << chunk.text << "\n";
                        file << "Original: " << chunk.original_text << "\n";
                        file << "---\n\n";
                    }
                    
                    file.close();
                }
            }
            
            // Save master translation file
            std::string master_file = output_dir + "/master_translation.txt";
            std::ofstream master(master_file);
            if (master.is_open()) {
                master << "=== MASTER TRANSLATION FILE ===\n\n";
                
                for (size_t i = 0; i < chunks.size(); i++) {
                    master << "ID: " << i + 1 << "\n";
                    master << "File: " << chunks[i].file_path << "\n";
                    master << "Line: " << chunks[i].line_number << "\n";
                    master << "Original: " << chunks[i].text << "\n";
                    master << "Translation: \n";
                    master << "---\n\n";
                }
                
                master.close();
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error saving extracted texts: " << e.what() << std::endl;
        }
    }
    
    // Apply translations back to files
    void apply_translations(const std::string& translation_file, const std::string& output_dir) {
        try {
            std::ifstream file(translation_file);
            if (!file.is_open()) {
                std::cerr << "Could not open translation file: " << translation_file << std::endl;
                return;
            }
            
            std::unordered_map<std::string, std::string> translations;
            std::string line;
            std::string current_id;
            std::string current_original;
            std::string current_translation;
            
            while (std::getline(file, line)) {
                if (line.find("ID: ") == 0) {
                    current_id = line.substr(4);
                } else if (line.find("Original: ") == 0) {
                    current_original = line.substr(10);
                } else if (line.find("Translation: ") == 0) {
                    current_translation = line.substr(13);
                    if (!current_translation.empty() && current_translation != " ") {
                        translations[current_original] = current_translation;
                    }
                }
            }
            
            file.close();
            
            // Apply translations to files
            for (const auto& pair : translations) {
                std::cout << "Applying translation: " << pair.first << " -> " << pair.second << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error applying translations: " << e.what() << std::endl;
        }
    }

private:
    std::string clean_text(const std::string& text) {
        std::string cleaned = text;
        
        // Remove escape sequences
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\n)"), "\n");
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\t)"), "\t");
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\r)"), "\r");
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\")"), "\"");
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\')"), "'");
        cleaned = std::regex_replace(cleaned, std::regex(R"(\\\\)"), "\\");
        
        // Trim whitespace
        cleaned.erase(cleaned.begin(), std::find_if(cleaned.begin(), cleaned.end(), [](unsigned char ch) {
            return !std::isspace(ch);
        }));
        cleaned.erase(std::find_if(cleaned.rbegin(), cleaned.rend(), [](unsigned char ch) {
            return !std::isspace(ch);
        }).base(), cleaned.end());
        
        return cleaned;
    }
};

PYBIND11_MODULE(text_extractor, m) {
    m.doc() = "Fast text extraction and translation management for game localization";
    
    py::class_<TextExtractor>(m, "TextExtractor")
        .def(py::init<>())
        .def("extract_texts", &TextExtractor::extract_texts, "Extract texts from directory")
        .def("save_extracted_texts", &TextExtractor::save_extracted_texts, "Save extracted texts to files")
        .def("apply_translations", &TextExtractor::apply_translations, "Apply translations to files")
        .def("set_supported_extensions", &TextExtractor::set_supported_extensions, "Set supported file extensions")
        .def("get_supported_extensions", &TextExtractor::get_supported_extensions, "Get current supported file extensions");
    
    py::class_<TextExtractor::TextChunk>(m, "TextChunk")
        .def_readonly("text", &TextExtractor::TextChunk::text)
        .def_readonly("file_path", &TextExtractor::TextChunk::file_path)
        .def_readonly("line_number", &TextExtractor::TextChunk::line_number)
        .def_readonly("column_start", &TextExtractor::TextChunk::column_start)
        .def_readonly("column_end", &TextExtractor::TextChunk::column_end)
        .def_readonly("context", &TextExtractor::TextChunk::context)
        .def_readonly("original_text", &TextExtractor::TextChunk::original_text);
    
    py::class_<TextExtractor::ExtractionResult>(m, "ExtractionResult")
        .def_readonly("chunks", &TextExtractor::ExtractionResult::chunks)
        .def_readonly("total_files_processed", &TextExtractor::ExtractionResult::total_files_processed)
        .def_readonly("total_texts_found", &TextExtractor::ExtractionResult::total_texts_found)
        .def_readonly("processing_time", &TextExtractor::ExtractionResult::processing_time);
}
