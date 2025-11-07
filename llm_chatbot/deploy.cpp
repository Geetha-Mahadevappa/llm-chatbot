#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {
struct Options {
    fs::path venv_path{".venv"};
    std::string python_exe{"python3"};
    bool skip_install{false};
};

std::string quote(const std::string& arg) {
    std::string quoted = "\"";
    for (char ch : arg) {
        if (ch == '"') {
            quoted += "\\\"";
        } else if (ch == '\\') {
            quoted += "\\\\";
        } else {
            quoted += ch;
        }
    }
    quoted += '"';
    return quoted;
}

std::string quote(const fs::path& path) {
    return quote(path.string());
}

void print_usage(const char* argv0) {
    std::cout << "Usage: " << argv0 << " [options]\n\n"
              << "Options:\n"
              << "  --venv-path <path>   Path where the virtual environment will be created (default: .venv)\n"
              << "  --python <executable>  Python executable to use for managing the virtual environment (default: python3)\n"
              << "  --skip-install       Skip dependency installation, just validate the environment\n"
              << "  -h, --help           Show this message and exit\n";
}

Options parse_arguments(int argc, char** argv) {
    Options opts;
    if (const char* env_python = std::getenv("PYTHON")) {
        opts.python_exe = env_python;
    }
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--venv-path" && i + 1 < argc) {
            opts.venv_path = argv[++i];
        } else if (arg == "--python" && i + 1 < argc) {
            opts.python_exe = argv[++i];
        } else if (arg == "--skip-install") {
            opts.skip_install = true;
        } else if (arg == "-h" || arg == "--help") {
            print_usage(argv[0]);
            std::exit(EXIT_SUCCESS);
        } else {
            throw std::invalid_argument("Unknown argument: " + arg);
        }
    }
    return opts;
}

int run_command(const std::string& command) {
    std::cout << "\n>>> " << command << '\n';
    int rc = std::system(command.c_str());
    if (rc != 0) {
        throw std::runtime_error("Command failed with exit code " + std::to_string(rc) + ": " + command);
    }
    return rc;
}

fs::path detect_repo_root() {
    fs::path current = fs::current_path();
    const fs::path marker = "llm_chatbot";
    fs::path candidate = current;
    while (!candidate.empty()) {
        if (fs::exists(candidate / marker / "requirements.txt")) {
            return candidate;
        }
        candidate = candidate.parent_path();
    }
    throw std::runtime_error("Could not locate the project root containing llm_chatbot/requirements.txt");
}

fs::path python_in_venv(const fs::path& venv_path) {
#ifdef _WIN32
    return venv_path / "Scripts" / "python.exe";
#else
    return venv_path / "bin" / "python";
#endif
}

void ensure_virtualenv(const Options& opts, const fs::path& repo_root) {
    fs::path venv = opts.venv_path;
    if (!venv.is_absolute()) {
        venv = repo_root / venv;
    }

    if (!fs::exists(venv)) {
        std::cout << "Creating virtual environment at " << venv << '\n';
        run_command(quote(opts.python_exe) + " -m venv " + quote(venv));
    } else {
        std::cout << "Reusing existing virtual environment at " << venv << '\n';
    }

    fs::path python = python_in_venv(venv);
    if (!fs::exists(python)) {
        throw std::runtime_error("Virtual environment appears to be corrupted: " + python.string() + " not found");
    }

    if (!opts.skip_install) {
        run_command(quote(python) + " -m pip install --upgrade pip");
        run_command(quote(python) + " -m pip install -r " + quote(repo_root / "llm_chatbot" / "requirements.txt"));
    }

    std::cout << "\nVirtual environment ready: " << python << '\n';
}

void validate_project_layout(const fs::path& repo_root) {
    const fs::path app_entry = repo_root / "llm_chatbot" / "app" / "ui_streamlit.py";
    if (!fs::exists(app_entry)) {
        throw std::runtime_error("Expected Streamlit entry point not found at " + app_entry.string());
    }
}

void print_success_message(const fs::path& repo_root, const fs::path& venv_path) {
    fs::path venv = venv_path;
    if (!venv.is_absolute()) {
        venv = repo_root / venv;
    }

    fs::path python = python_in_venv(venv);
    fs::path streamlit_entry = repo_root / "llm_chatbot" / "app" / "ui_streamlit.py";

    std::cout << "\nDeployment prerequisites satisfied!\n";
    std::cout << "Use the following command to launch the Streamlit UI from your shell:\n";
#ifdef _WIN32
    std::cout << "  " << venv.string() << "\\Scripts\\streamlit run " << streamlit_entry.string() << '\n';
#else
    std::cout << "  source " << venv.string() << "/bin/activate && streamlit run " << streamlit_entry.string() << '\n';
#endif
}
}

int main(int argc, char** argv) {
    try {
        Options opts = parse_arguments(argc, argv);
        const fs::path repo_root = detect_repo_root();
        validate_project_layout(repo_root);
        ensure_virtualenv(opts, repo_root);
        print_success_message(repo_root, opts.venv_path);
    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << '\n';
        std::cerr << "Use --help to see usage instructions." << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
