from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

try:
    import yaml
    from yaml.loader import SafeLoader
except ImportError:
    yaml = None
    SafeLoader = None

try:
    from .data_types import ScanContext
except ImportError:
    # When running directly, use absolute imports
    import sys
    from pathlib import Path
    # scanner package is under codes directory, so need to add codes directory to sys.path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from scanner.data_types import ScanContext


# ============================================================================
# Constant definitions
# ============================================================================

# Long text threshold: print content exceeding this length will be extracted and replaced
LONG_TEXT_THRESHOLD = 100

# File encoding attempt order
FILE_ENCODINGS = ["utf-8", "gbk", "gb2312", "latin-1", "iso-8859-1"]


# ============================================================================
# Configuration management
# ============================================================================

class ConfigManager:
    """Configuration manager, responsible for loading and managing input resolver configuration."""
    
    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize configuration manager.
        
        Args:
            config_path: Config file path, if None then use default path
        """
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent 
                / "configs" / "default.yaml"
            )
        
        self._config_path = config_path
        self._config = self._load_config()
        self._code_extensions = set(self._config.get("code_extensions", []))
        self._ignore_dirs = set(self._config.get("ignore_dirs", []))
        self._print_patterns = self._parse_print_patterns()
        self._comment_patterns = self._parse_comment_patterns()
        self._extension_language_map = self._parse_extension_language_map()
    
    def _load_config(self) -> dict[str, Any]:
        """Load configuration file."""
        if not self._config_path.exists():
            raise FileNotFoundError(f"Config file does not exist: {self._config_path}")
        
        if yaml is None or SafeLoader is None:
            raise ImportError("PyYAML library required: pip install pyyaml")
        
        assert SafeLoader is not None  # Type check
        with open(self._config_path, "r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=SafeLoader)
        
        return config.get("input_resolver", {})
    
    def _parse_print_patterns(self) -> dict[str, list[str]]:
        """Parse print function pattern configuration."""
        patterns: dict[str, list[str]] = {}
        for lang, pattern_list in self._config.get("print_patterns", {}).items():
            patterns[lang] = pattern_list if isinstance(pattern_list, list) else []
        return patterns
    
    def _parse_comment_patterns(self) -> dict[str, dict[str, str | None]]:
        """Parse comment pattern configuration."""
        patterns: dict[str, dict[str, str | None]] = {}
        for lang, pattern_dict in self._config.get("comment_patterns", {}).items():
            patterns[lang] = pattern_dict if isinstance(pattern_dict, dict) else {}
        return patterns
    
    def _parse_extension_language_map(self) -> Mapping[str, tuple[str, ...]]:
        """Parse extension to language mapping configuration."""
        mapping: dict[str, tuple[str, ...]] = {}
        for ext, langs in self._config.get("extension_language_map", {}).items():
            if isinstance(langs, list):
                mapping[ext] = tuple(langs)
            else:
                mapping[ext] = (langs,)
        return mapping
    
    @property
    def code_extensions(self) -> set[str]:
        """Supported code file extensions."""
        return self._code_extensions
    
    @property
    def ignore_dirs(self) -> set[str]:
        """Directories to skip."""
        return self._ignore_dirs
    
    def get_print_patterns(self, language: str) -> list[str]:
        """Get print function pattern list for specified language."""
        return self._print_patterns.get(language, [])
    
    def get_comment_patterns(self, language: str) -> dict[str, str | None]:
        """Get comment patterns for specified language."""
        return self._comment_patterns.get(language, {})
    
    @property
    def extension_language_map(self) -> Mapping[str, tuple[str, ...]]:
        """Extension to language mapping."""
        return self._extension_language_map
    
    def get_language_from_extension(self, ext: str) -> str:
        """
        Determine language type from file extension (for filtering operations).
        
        Prefer mapping from config file, if not exists then use built-in mapping.
        
        Args:
            ext: File extension (including dot, e.g., ".py")
            
        Returns:
            Language type string, returns "unknown" if cannot be identified
        """
        ext_lower = ext.lower()
        
        # Prefer mapping from config file
        languages = self._extension_language_map.get(ext_lower, ())
        if languages:
            # Return first language as filter language
            return languages[0]
        
        # Use built-in mapping as fallback
        builtin_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript",
            ".java": "java",
            ".cpp": "c_cpp",
            ".c": "c_cpp",
            ".cc": "c_cpp",
            ".cxx": "c_cpp",
            ".h": "c_cpp",
            ".hpp": "c_cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "shell",
            ".bash": "shell",
            ".zsh": "shell",
            ".html": "html",
            ".css": "css",
            ".scss": "css",
            ".less": "css",
        }
        return builtin_map.get(ext_lower, "unknown")


# Global configuration manager instance
_config_manager = ConfigManager()

# Backward compatible global variables
_CODE_EXTENSIONS = _config_manager.code_extensions
_IGNORE_DIRS = _config_manager.ignore_dirs
_EXTENSION_LANGUAGE_MAP = _config_manager.extension_language_map


# ============================================================================
# Utility functions
# ============================================================================

def _ensure_existing_path(path: str | Path) -> Path:
    """
    Ensure path exists and is a directory.
    
    Args:
        path: Input path
        
    Returns:
        Resolved path object
        
    Raises:
        FileNotFoundError: Path does not exist
        NotADirectoryError: Path is not a directory
    """
    candidate = Path(path).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"Input path does not exist: {candidate}")
    if not candidate.is_dir():
        raise NotADirectoryError(f"Input path must be a directory: {candidate}")
    return candidate.resolve()


def _read_file_with_encoding(file_path: Path, encodings: Sequence[str] | None = None) -> str | None:
    """
    Attempt to read file content using multiple encodings.
    
    Args:
        file_path: File path
        encodings: Encoding list, if None then use default encoding list
        
    Returns:
        File content, returns None if cannot be read
    """
    if encodings is None:
        encodings = FILE_ENCODINGS
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return None


# ============================================================================
# Nested comment handling
# ============================================================================

def _find_outer_comment_pairs(content: str, start_pattern: str, end_pattern: str) -> list[tuple[int, int]]:
    """
    Find outermost comment pairs (handles nested comments).
    
    Args:
        content: File content
        start_pattern: Regex pattern for comment start
        end_pattern: Regex pattern for comment end
        
    Returns:
        List of comment pairs, each tuple contains (start position, end position)
    """
    starts = [m.start() for m in re.finditer(start_pattern, content)]
    ends = [m.end() for m in re.finditer(end_pattern, content)]
    
    outer_comments: list[tuple[int, int]] = []
    i, j = 0, 0
    depth = 0
    start_pos: int | None = None
    
    while i < len(starts) or j < len(ends):
        if j >= len(ends) or (i < len(starts) and starts[i] < ends[j]):
            if depth == 0:
                start_pos = starts[i]
            depth += 1
            i += 1
        else:
            depth -= 1
            if depth == 0 and start_pos is not None:
                outer_comments.append((start_pos, ends[j]))
                start_pos = None
            j += 1
    
    return outer_comments


# ============================================================================
# Comment processing module
# ============================================================================

def _clean_comment_content(comment_text: str, language: str, is_multi: bool = False) -> str:
    """
    Clean comment content, remove comment markers.
    
    Args:
        comment_text: Original comment text (including comment markers)
        language: Language type
        is_multi: Whether it's a multi-line comment
        
    Returns:
        Cleaned comment content
    """
    if is_multi:
        if language == "python":
            return re.sub(r'^"""|"""$|^\'\'\'|\'\'\'$', '', comment_text, flags=re.MULTILINE).strip()
        elif language == "ruby":
            return re.sub(r'^=begin|=end$', '', comment_text, flags=re.MULTILINE).strip()
        elif language == "html":
            return re.sub(r'^<!--|-->$', '', comment_text, flags=re.MULTILINE).strip()
        else:
            return re.sub(r'^/\*|\*/$', '', comment_text, flags=re.MULTILINE).strip()
    else:
        # Single-line comment
        if language in ("python", "ruby", "shell"):
            return re.sub(r'^#+', '', comment_text).strip()
        elif language in ("javascript", "typescript", "java", "c_cpp", "go", "rust"):
            return re.sub(r'^//+', '', comment_text).strip()
        elif language == "php":
            return re.sub(r'^//+|^#+', '', comment_text).strip()
        else:
            return comment_text.strip()


def _extract_comments_regex(content: str, file_path: Path, language: str) -> list[dict[str, Any]]:
    """
    Extract comments using regex.
    
    Args:
        content: File content
        file_path: File path
        language: Language type
        
    Returns:
        List of comments, each element contains type, file_path, line_number, content
    """
    comments: list[dict[str, Any]] = []
    patterns = _config_manager.get_comment_patterns(language)
    
    if not patterns:
        return comments
    
    # Extract multi-line comments (process first to avoid conflicts with single-line comments)
    multi_pattern = patterns.get("multi")
    if multi_pattern:
        if "/*" in multi_pattern:
            # Handle nested comments
            outer_pairs = _find_outer_comment_pairs(content, r'/\*', r'\*/')
            for start, end in outer_pairs:
                comment_text = content[start:end]
                comment_content = _clean_comment_content(comment_text, language, is_multi=True)
                if comment_content:
                    line_num = content[:start].count("\n") + 1
                    comments.append({
                        "type": "comment",
                        "file_path": str(file_path),
                        "line_number": line_num,
                        "content": comment_content
                    })
        else:
            # Other types of multi-line comments (Python, Ruby, HTML, etc.)
            for match in re.finditer(multi_pattern, content, re.DOTALL):
                comment_text = match.group(0)
                comment_content = _clean_comment_content(comment_text, language, is_multi=True)
                if comment_content:
                    line_num = content[:match.start()].count("\n") + 1
                    comments.append({
                        "type": "comment",
                        "file_path": str(file_path),
                        "line_number": line_num,
                        "content": comment_content
                    })
    
    # Extract single-line comments
    single_pattern = patterns.get("single")
    if single_pattern:
        for match in re.finditer(single_pattern, content, re.MULTILINE):
            comment_text = match.group(0)
            comment_content = _clean_comment_content(comment_text, language, is_multi=False)
            if comment_content:
                line_num = content[:match.start()].count("\n") + 1
                comments.append({
                    "type": "comment",
                    "file_path": str(file_path),
                    "line_number": line_num,
                    "content": comment_content
                })
    
    return comments


def _replace_comments_regex(content: str, language: str) -> str:
    """
    Replace comment content with spaces using regex, preserving comment markers.
    
    Args:
        content: File content
        language: Language type
        
    Returns:
        Processed content
    """
    patterns = _config_manager.get_comment_patterns(language)
    
    if not patterns:
        return content
    
    result = content
    
    # Process multi-line comments first (avoid conflicts with single-line comments)
    multi_pattern = patterns.get("multi")
    if multi_pattern:
        if "/*" in multi_pattern:
            # Handle nested comments
            outer_pairs = _find_outer_comment_pairs(result, r'/\*', r'\*/')
            # Replace from back to front to avoid position offset
            for start, end in reversed(outer_pairs):
                content_start = start + 2  # Length of /*
                content_end = end - 2  # Length of */
                if content_end > content_start:
                    result = result[:content_start] + " " + result[content_end:]
        elif '"""' in multi_pattern or "'''" in multi_pattern:
            # Python multi-line comments
            def replace_python_comment(match: re.Match[str]) -> str:
                matched_text = match.group(0)
                quote = '"""' if matched_text.startswith('"""') else "'''"
                quote_len = len(quote)
                if len(matched_text) > quote_len * 2:
                    return quote + " " + quote
                return matched_text
            result = re.sub(multi_pattern, replace_python_comment, result, flags=re.DOTALL)
        elif '<!--' in multi_pattern:
            # HTML comments
            def replace_html_comment(match: re.Match[str]) -> str:
                matched_text = match.group(0)
                if len(matched_text) > 7:  # Minimum length of <!-- -->
                    return "<!-- -->"
                return matched_text
            result = re.sub(multi_pattern, replace_html_comment, result, flags=re.DOTALL)
        elif '=begin' in multi_pattern:
            # Ruby comments
            def replace_ruby_comment(match: re.Match[str]) -> str:
                matched_text = match.group(0)
                if len(matched_text) > 12:  # Minimum length of =begin =end
                    return "=begin =end"
                return matched_text
            result = re.sub(multi_pattern, replace_ruby_comment, result, flags=re.DOTALL)
        else:
            # Other types of multi-line comments (e.g., CSS /* */)
            def replace_css_comment(match: re.Match[str]) -> str:
                matched_text = match.group(0)
                if len(matched_text) > 4:  # Minimum length of /* */
                    return "/* */"
                return matched_text
            result = re.sub(multi_pattern, replace_css_comment, result, flags=re.DOTALL)
    
    # Then process single-line comments
    single_pattern = patterns.get("single")
    if single_pattern:
        def replace_single_comment(match: re.Match[str]) -> str:
            matched_text = match.group(0)
            if language in ("python", "ruby", "shell"):
                if matched_text.startswith('#'):
                    return '# '
            elif language in ("javascript", "java", "c_cpp", "go", "rust"):
                if matched_text.startswith('//'):
                    return '// '
            elif language == "php":
                if matched_text.startswith('//'):
                    return '// '
                elif matched_text.startswith('#'):
                    return '# '
            return matched_text
        result = re.sub(single_pattern, replace_single_comment, result, flags=re.MULTILINE)
    
    return result


# ============================================================================
# Print statement processing module
# ============================================================================

def _extract_string_from_print(match_str: str, language: str) -> str:
    """
    Extract string content from print statement.
    
    Args:
        match_str: Matched print statement
        language: Language type (currently unused, kept for compatibility)
        
    Returns:
        Extracted string content
    """
    # Uniformly use regex to extract string literals
    # Match content in single or double quotes (supports escaping)
    patterns = [
        r'["\']((?:[^"\'\\]|\\.)*)["\']',  # Standard strings (with escaping support)
        r'["\']([^"\']*)["\']',  # Simple strings (no escaping)
    ]
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, match_str))
        if matches:
            # Return longest string content
            longest_match = max(matches, key=lambda m: len(m.group(1)))
            return longest_match.group(1)
    
    return ""


def _extract_print_statements(content: str, file_path: Path, language: str) -> list[dict[str, Any]]:
    """
    Extract print statement content exceeding threshold from file.
    
    Args:
        content: File content
        file_path: File path
        language: Language type
        
    Returns:
        List of print content, each element contains type, file_path, line_number, content
    """
    print_statements: list[dict[str, Any]] = []
    patterns = _config_manager.get_print_patterns(language)
    
    if not patterns:
        return print_statements
    
    # Uniformly use regex to match all print statements
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            match_str = match.group(0)
            extracted_text = _extract_string_from_print(match_str, language)
            
            # If extracted content exceeds threshold
            if len(extracted_text) >= LONG_TEXT_THRESHOLD:
                line_num = content[:match.start()].count("\n") + 1
                print_statements.append({
                    "type": "print",
                    "file_path": str(file_path),
                    "line_number": line_num,
                    "content": extracted_text
                })
    
    return print_statements


def _replace_long_prints(content: str, file_path: Path, language: str) -> str:
    """
    Replace print content exceeding threshold with spaces.
    
    Args:
        content: File content
        file_path: File path (currently unused, kept for compatibility)
        language: Language type
        
    Returns:
        Processed content
    """
    patterns = _config_manager.get_print_patterns(language)
    
    if not patterns:
        return content
    
    result = content
    
    for pattern in patterns:
        def replace_match(match: re.Match[str]) -> str:
            match_str = match.group(0)
            extracted_text = _extract_string_from_print(match_str, language)
            
            # If extracted content exceeds threshold, replace with spaces
            if len(extracted_text) >= LONG_TEXT_THRESHOLD:
                # Find string literals (including quotes)
                string_patterns = [
                    r'(["\'"])((?:[^"\'\\]|\\.)*)\1',  # Strings with escaping support
                    r'(["\'"])([^"\']*)\1',  # Simple strings
                ]
                
                for str_pattern in string_patterns:
                    str_match = re.search(str_pattern, match_str)
                    if str_match and len(str_match.group(2)) >= LONG_TEXT_THRESHOLD:
                        quote_char = str_match.group(1)
                        str_content = str_match.group(2)
                        # Replace string content with spaces, preserve quotes
                        replacement = (
                            match_str[:str_match.start()] +
                            quote_char + " " * len(str_content) + quote_char +
                            match_str[str_match.end():]
                        )
                        return replacement
            
            return match_str
        
        result = re.sub(pattern, replace_match, result, flags=re.MULTILINE | re.DOTALL)
    
    return result


# ============================================================================
# File processing module
# ============================================================================

def _should_process_file(file_path: Path, config: ConfigManager) -> tuple[bool, bool]:
    """
    Determine if file should be processed.
    
    Args:
        file_path: File path
        config: Configuration manager
        
    Returns:
        (is_code_file, is_language_file)
    """
    # Skip files in ignored directories
    if any(ignore_dir in file_path.parts for ignore_dir in config.ignore_dirs):
        return False, False
    
    ext = file_path.suffix.lower()
    is_code_file = ext in config.code_extensions
    languages = config.extension_language_map.get(ext, ())
    is_language_file = bool(languages)
    
    return is_code_file, is_language_file


def _process_code_file(
    file_path: Path,
    root_path: Path,
    output_dir: Path,
    config: ConfigManager,
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Process single code file: extract comments and print content, filter content, save processed file.
    
    Args:
        file_path: File path
        root_path: Root path (for calculating relative path)
        output_dir: Output directory
        config: Configuration manager
        
    Returns:
        (detected language list, extracted content list)
    """
    discovered_languages: list[str] = []
    extracted_items: list[dict[str, Any]] = []
    
    try:
        # Calculate relative path
        try:
            rel_path = file_path.relative_to(root_path)
        except ValueError:
            rel_path = file_path
        
        # Read file content
        content = _read_file_with_encoding(file_path)
        if content is None:
            return discovered_languages, extracted_items
        
        # Determine language type (for filtering)
        filter_language = config.get_language_from_extension(file_path.suffix)
        if filter_language == "unknown":
            return discovered_languages, extracted_items
        
        # Record detected languages
        languages = config.extension_language_map.get(file_path.suffix.lower(), ())
        for language in languages:
            if language not in discovered_languages:
                discovered_languages.append(language)
        
        # Extract comments and print content
        comments = _extract_comments_regex(content, rel_path, filter_language)
        print_statements = _extract_print_statements(content, rel_path, filter_language)
        extracted_items = comments + print_statements
        
        # Process content: remove comments, replace long prints
        processed_content = _replace_comments_regex(content, filter_language)
        processed_content = _replace_long_prints(processed_content, rel_path, filter_language)
        
        # Save processed file to output directory
        output_file_path = output_dir / rel_path
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(processed_content)
        except Exception as e:
            print(f"Error saving processed file {output_file_path}: {e}")
    
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    
    return discovered_languages, extracted_items


def _inspect_languages_and_code_paths(
    root_path: Path,
    *,
    output_dir: Path,
    language_map: Mapping[str, Sequence[str]],
    max_files: int,
) -> tuple[tuple[str, ...], list[dict[str, Any]], list[str]]:
    """
    Inspect languages and perform filtering operations.
    
    Args:
        root_path: Input root path
        output_dir: Output directory for saving processed files
        language_map: Language mapping
        max_files: Maximum number of files
    
    Returns:
        (detected language tuple, extracted content list, code file path list)
    """
    discovered: set[str] = set()
    all_extracted: list[dict[str, Any]] = []
    process_files: list[str] = []
    inspected = 0
    
    try:
        for file_path in root_path.rglob("*"):
            if inspected >= max_files > 0:
                break
            if not file_path.is_file():
                continue
            
            # Determine if should process
            is_code_file, is_language_file = _should_process_file(file_path, _config_manager)
            
            if not is_code_file:
                continue
            
            # Calculate relative path and add to list
            try:
                rel_path = file_path.relative_to(root_path)
                process_files.append(str(rel_path))
            except ValueError:
                process_files.append(str(file_path))
            
            inspected += 1
            
            # Check language mapping (use provided language_map)
            languages = language_map.get(file_path.suffix.lower(), ())
            if languages:
                for language in languages:
                    discovered.add(language)
            
            # Process code file
            file_languages, extracted_items = _process_code_file(
                file_path, root_path, output_dir, _config_manager
            )
            discovered.update(file_languages)
            all_extracted.extend(extracted_items)
    
    except Exception as e:
        print(f"Error traversing files: {e}")
    
    return (
        tuple(sorted(discovered)),
        all_extracted,
        process_files,
    )


# ============================================================================
# Main functions and public API
# ============================================================================

def _normalize_language(value: str | None) -> str | None:
    """
    Normalize language name.
    
    Args:
        value: Language name
        
    Returns:
        Normalized language name, returns None if empty
    """
    if not value:
        return None
    normalized = value.strip().lower()
    return normalized or None


def _merge_languages(
    explicit: Sequence[str] | None,
    detected: Sequence[str] | None,
) -> tuple[str, ...]:
    """
    Merge explicitly specified languages and detected languages.
    
    Args:
        explicit: Explicitly specified language list
        detected: Detected language list
        
    Returns:
        Merged language tuple, preserving order and deduplicated
    """
    ordered: list[str] = []
    seen: set[str] = set()
    
    def _add_languages(items: Iterable[str] | None) -> None:
        if not items:
            return
        for item in items:
            normalized = _normalize_language(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
    
    _add_languages(explicit)
    _add_languages(detected)
    return tuple(ordered)


def _serialize_scan_methods(
    scan_methods: Mapping[str, object] | Sequence[str],
) -> str:
    """
    Serialize scan method configuration to JSON string.
    
    Args:
        scan_methods: Scan method mapping or sequence
        
    Returns:
        JSON string representation
    """
    try:
        return json.dumps(
            scan_methods,
            ensure_ascii=True,
            sort_keys=True,
            default=str,
        )
    except TypeError:
        return repr(scan_methods)


def _build_metadata(
    metadata: Mapping[str, str] | None,
    scan_methods: Mapping[str, object] | Sequence[str] | None,
    process_files: list[str] | None = None,
    text_output_path: Path | None = None,
) -> MutableMapping[str, str]:
    """
    Build metadata dictionary.
    
    Args:
        metadata: User-provided metadata
        scan_methods: Scan method configuration
        process_files: List of processed code file paths
        
    Returns:
        Metadata dictionary
    """
    payload: MutableMapping[str, str] = {}
    if metadata:
        payload.update({str(key): str(value) for key, value in metadata.items()})
    
    if scan_methods is not None:
        payload["scan_methods"] = _serialize_scan_methods(scan_methods)
    
    if process_files is not None:
        payload["process_file"] = process_files
    
    if text_output_path is not None:
        payload["text_output_path"] = text_output_path
    
    return payload


def resolve_scan_context(
    path: str | Path,
    *,
    explicit_languages: Sequence[str] | None = None,
    auto_detect_languages: bool = True,
    language_detection_limit: int = 5000,
    scan_methods: Mapping[str, object] | Sequence[str] | None = None,
    metadata: Mapping[str, str] | None = None,
    extension_language_map: Mapping[str, Sequence[str]] | None = None,
) -> ScanContext:
    """
    Parse input path into ScanContext.
    
    This is the main public API of the module, responsible for parsing input path and generating scan context.
    
    Args:
        path: Input path (directory)
        explicit_languages: Explicitly specified language list
        auto_detect_languages: Whether to auto-detect languages
        language_detection_limit: Maximum number of files for language detection
        scan_methods: Scan method configuration
        metadata: User metadata
        extension_language_map: Extension to language mapping (overrides default config)
        
    Returns:
        ScanContext object
    """
    root_path = _ensure_existing_path(path)
    language_map = extension_language_map or _EXTENSION_LANGUAGE_MAP
    
    # Create directory named after input path filename under work_dir
    work_dir = Path(__file__).parent.parent / "work_dir"
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Get input path filename (directory name)
    path_name = root_path.name + "_work"
    output_dir = work_dir / path_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    detected_languages: Sequence[str] = ()
    all_extracted: list[dict[str, Any]] = []
    process_files: list[str] = []
    
    if auto_detect_languages:
        detected_languages, all_extracted, process_files = _inspect_languages_and_code_paths(
            root_path,
            output_dir=output_dir,
            language_map=language_map,
            max_files=language_detection_limit,
        )
    # Save extracted content to output_dir
    text_output_path: Path | None = None
    if all_extracted:
        text_output_path = output_dir / "extracted_text.json"
        text_output_path.parent.mkdir(parents=True, exist_ok=True)
        result = {"text": all_extracted}
        with open(text_output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    languages = _merge_languages(explicit_languages, detected_languages)
    metadata_payload = _build_metadata(metadata, scan_methods, process_files,text_output_path)
    

    
    return ScanContext(
        root_path=root_path,
        languages=languages,
        scan_methods=scan_methods,
        metadata=metadata_payload,
        output_path=output_dir,
    )


# ============================================================================
# Backward compatibility: preserve old function names
# ============================================================================

def _get_language_from_extension(ext: str) -> str:
    """Backward compatible: get language type from extension."""
    return _config_manager.get_language_from_extension(ext)

# Preserve old global variable access methods (via attributes)
def _get_print_patterns(language: str) -> list[str]:
    """Backward compatible: get print patterns."""
    return _config_manager.get_print_patterns(language)

def _get_comment_patterns(language: str) -> dict[str, str | None]:
    """Backward compatible: get comment patterns."""
    return _config_manager.get_comment_patterns(language)

# For backward compatibility, we need to use these in functions
# But we already use _config_manager directly, so these may not be needed
# Preserved in case external code accesses them directly


if __name__ == "__main__":
    resolve_scan_context(
        "/Users/lijinqi13/Code/agent-safety/evals/bench/repos/advanced-reason-mcp-main"
    )
    print("done")