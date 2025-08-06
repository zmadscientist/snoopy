// snoopy.cpp - C++ version of snoopy dependency scanner for C/C++ projects

#include <iostream>
#include <fstream>
#include <filesystem>
#include <regex>
#include <set>
#include <string>
#include <vector>

namespace fs = std::filesystem;

const std::set<std::string> standard_headers = {
    "iostream", "vector", "map", "set", "string", "cmath",
    "cstdio", "cstdlib", "cstring", "cassert", "algorithm"
};

std::string classify_include(const std::string& header) {
    if (standard_headers.count(header)) return "Standard Library";
    if (header.find("/") != std::string::npos ||
        header.ends_with(".h") || header.ends_with(".hpp")) {
        return "Local or Third-Party";
    }
    return "Unknown";
}

std::set<std::string> extract_includes(const fs::path& file) {
    std::ifstream f(file);
    std::string line;
    std::regex include_re(R"(#include\s*[<\"]([^">]+)[">])");
    std::smatch match;
    std::set<std::string> includes;

    while (std::getline(f, line)) {
        if (std::regex_search(line, match, include_re)) {
            includes.insert(match[1]);
        }
    }
    return includes;
}

void print_makefile_suggestion(const std::vector<std::string>& cpp_files) {
    std::cout << "\n\U0001F6E0 Suggested Makefile:\n";
    std::cout << "-------------------------\n";
    std::cout << "CXX = g++\n";
    std::cout << "CXXFLAGS = -std=c++17 -Wall -O2\n\n";
    std::cout << "TARGET = main\n";
    std::cout << "SRCS =";
    for (const auto& file : cpp_files)
        std::cout << " " << file;
    std::cout << "\n";
    std::cout << "OBJS = $(SRCS:.cpp=.o)\n\n";
    std::cout << "all: $(TARGET)\n\n";
    std::cout << "$(TARGET): $(OBJS)\n\t$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)\n\n";
    std::cout << "clean:\n\trm -f $(TARGET) $(OBJS)\n";
    std::cout << "-------------------------\n";
}

void scan_file(const fs::path& file, std::set<std::string>& std_deps,
               std::set<std::string>& local_deps) {
    auto includes = extract_includes(file);
    std::cout << "\n\xF0\x9F\x93\x84 File: " << file << "\n";
    for (const auto& inc : includes) {
        auto category = classify_include(inc);
        std::cout << "  " << inc << std::string(25 - inc.length(), ' ') << " → " << category << "\n";
        if (category == "Standard Library") std_deps.insert(inc);
        else local_deps.insert(inc);
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: snoopy <path-to-file-or-folder>\n";
        return 1;
    }

    fs::path input_path(argv[1]);
    if (!fs::exists(input_path)) {
        std::cerr << "Error: path does not exist.\n";
        return 1;
    }

    std::set<std::string> std_deps;
    std::set<std::string> local_deps;
    std::vector<std::string> cpp_files;

    if (fs::is_regular_file(input_path)) {
        if (input_path.extension() == ".cpp" || input_path.extension() == ".c") {
            cpp_files.push_back(input_path.filename().string());
            scan_file(input_path, std_deps, local_deps);
        }
    } else {
        for (auto& entry : fs::recursive_directory_iterator(input_path)) {
            if (entry.path().extension() == ".cpp" || entry.path().extension() == ".c") {
                cpp_files.push_back(entry.path().filename().string());
                scan_file(entry.path(), std_deps, local_deps);
            }
        }
    }

    if (!std_deps.empty() || !local_deps.empty()) {
        std::cout << "\n=== \U0001F4BB C/C++ Dependency Summary ===\n";
        if (!std_deps.empty()) {
            std::cout << "Standard Library:\n";
            for (const auto& d : std_deps) std::cout << "  - " << d << "\n";
        }
        if (!local_deps.empty()) {
            std::cout << "Local or Third-Party:\n";
            for (const auto& d : local_deps) std::cout << "  - " << d << "\n";
        }
    }

    if (!cpp_files.empty()) {
        print_makefile_suggestion(cpp_files);
    }

    return 0;
}
