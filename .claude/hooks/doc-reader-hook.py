#!/usr/bin/env python3
"""
Claude Code hook that shows relevant documentation once before writing.
Works for any code by extracting keywords and finding relevant docs.
"""

import json
import sys
import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timedelta

# Configuration
DOCS_DIRECTORY = "./research"  # Directory containing documentation
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}  # File types to consider
MAX_FILES_TO_READ = 5  # Limit to prevent overwhelming Claude
MAX_FILE_SIZE = 50000  # Max file size in bytes (50KB)
CACHE_DIR = "/tmp/.claude-hook-cache"  # Directory to track shown docs
CACHE_EXPIRY_MINUTES = 30  # How long to remember we've shown docs

def ensure_cache_dir():
    """Ensure cache directory exists."""
    Path(CACHE_DIR).mkdir(exist_ok=True)

def get_operation_hash(tool_input: Dict) -> str:
    """Create a hash of the operation to track if we've shown docs for it."""
    # Create a unique identifier for this operation
    content = tool_input.get("content", "")
    file_path = tool_input.get("file_path", "")
    old_string = tool_input.get("old_string", "")
    
    # Combine relevant parts to create a hash
    operation_str = f"{file_path}:{content[:500]}:{old_string[:500]}"
    return hashlib.md5(operation_str.encode()).hexdigest()

def has_shown_docs(operation_hash: str) -> bool:
    """Check if we've already shown docs for this operation."""
    cache_file = Path(CACHE_DIR) / f"{operation_hash}.shown"
    
    if cache_file.exists():
        # Check if cache is still valid
        mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mod_time < timedelta(minutes=CACHE_EXPIRY_MINUTES):
            return True
        else:
            # Cache expired, remove it
            cache_file.unlink()
    
    return False

def mark_docs_shown(operation_hash: str):
    """Mark that we've shown docs for this operation."""
    ensure_cache_dir()
    cache_file = Path(CACHE_DIR) / f"{operation_hash}.shown"
    cache_file.touch()

def extract_keywords_from_tool_input(tool_input: Dict) -> Set[str]:
    """Extract relevant keywords from any code."""
    keywords = set()
    
    # Extract from file path
    file_path = tool_input.get("file_path", "")
    if file_path:
        path_obj = Path(file_path)
        # Add filename parts
        name_parts = path_obj.stem.replace('-', '_').replace('.', '_').split('_')
        keywords.update(part.lower() for part in name_parts if len(part) > 2)
    
    # Extract from content (for Write operations)
    content = tool_input.get("content", "")
    if content:
        # Look for import/require statements (works for Python, JS, Go, etc.)
        imports = re.findall(r'(?:from|import|require|use|using|include)\s+["\']?(\w+)', content, re.IGNORECASE)
        keywords.update(word.lower() for word in imports)
        
        # Look for package names in various formats
        # e.g., openai.OpenAI, pydantic_ai.Agent, @shopify/polaris
        packages = re.findall(r'(?:[\w-]+)[./:](?:[\w-]+)', content)
        for pkg in packages[:20]:  # Limit to avoid noise
            parts = re.split(r'[./:]', pkg)
            keywords.update(part.lower() for part in parts if len(part) > 2)
        
        # Extract class/function definitions
        definitions = re.findall(r'(?:class|function|def|func|interface|struct|type)\s+(\w+)', content, re.IGNORECASE)
        keywords.update(word.lower() for word in definitions[:10])
        
        # Look for API-specific patterns
        api_patterns = re.findall(r'(\w+)(?:Client|API|Service|Agent|Model)', content, re.IGNORECASE)
        keywords.update(word.lower() for word in api_patterns[:10])
    
    # Extract from old_string (for Edit operations)
    old_string = tool_input.get("old_string", "")
    if old_string:
        imports = re.findall(r'(?:from|import|require|use|using)\s+["\']?(\w+)', old_string, re.IGNORECASE)
        keywords.update(word.lower() for word in imports)
    
    # Remove common words that aren't helpful
    noise_words = {
        "the", "and", "or", "in", "to", "from", "import", "def", "class", 
        "return", "if", "else", "for", "while", "true", "false", "none",
        "self", "this", "new", "var", "let", "const", "function", "async",
        "await", "try", "catch", "except", "finally", "with", "as", "is"
    }
    keywords = keywords - noise_words
    
    # Filter out very short keywords
    keywords = {k for k in keywords if len(k) > 2}
    
    return keywords

def score_document_relevance(doc_path: Path, keywords: Set[str]) -> float:
    """Score how relevant a document is based on keywords."""
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read(MAX_FILE_SIZE).lower()
        
        score = 0.0
        path_str = str(doc_path).lower()
        
        # Check each keyword
        for keyword in keywords:
            # High score for path/filename matches
            if keyword in path_str:
                score += 5.0
            
            # Lower score for content matches
            if keyword in content:
                # Count occurrences with diminishing returns
                count = min(content.count(keyword), 10)
                score += count * 0.2
        
        return score
    except Exception:
        return 0

def find_relevant_docs(docs_dir: str, keywords: Set[str]) -> List[Path]:
    """Find and rank documentation files by relevance."""
    docs_path = Path(docs_dir)
    if not docs_path.exists() or not keywords:
        return []
    
    doc_files = []
    for ext in DOC_EXTENSIONS:
        doc_files.extend(docs_path.rglob(f"*{ext}"))
    
    # Score and sort documents
    scored_docs = []
    for doc_path in doc_files:
        try:
            if doc_path.stat().st_size <= MAX_FILE_SIZE:
                score = score_document_relevance(doc_path, keywords)
                if score > 0.5:  # Minimum threshold
                    scored_docs.append((score, doc_path))
        except:
            continue
    
    # Sort by score (highest first) and return top files
    scored_docs.sort(reverse=True)
    return [doc_path for _, doc_path in scored_docs[:MAX_FILES_TO_READ]]

def format_documentation_feedback(doc_paths: List[Path], keywords: Set[str]) -> str:
    """Format documentation as helpful feedback for Claude."""
    if not doc_paths:
        return ""
    
    output = [f"📚 Found relevant documentation for keywords: {', '.join(sorted(keywords)[:8])}\n"]
    
    for i, doc_path in enumerate(doc_paths, 1):
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read(MAX_FILE_SIZE)
            
            # Show first part of the document
            preview = content[:1500]
            if len(content) > 1500:
                preview += "\n... (truncated)"
            
            output.append(f"\n### {i}. {doc_path.relative_to('.')}")
            output.append(preview)
            
        except Exception as e:
            continue
    
    output.append("\n💡 Review this documentation before implementing. This message will only appear once.")
    return "\n".join(output)

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Only process coding-related tools
        coding_tools = {"Write", "Edit", "MultiEdit", "Task"}
        if tool_name not in coding_tools:
            sys.exit(0)
        
        # Get operation hash to check if we've shown docs
        operation_hash = get_operation_hash(tool_input)
        
        # If we've already shown docs for this operation, let it proceed
        if has_shown_docs(operation_hash):
            sys.exit(0)
        
        # Extract keywords from the tool input
        keywords = extract_keywords_from_tool_input(tool_input)
        if not keywords:
            sys.exit(0)
        
        # Find relevant documentation
        relevant_docs = find_relevant_docs(DOCS_DIRECTORY, keywords)
        
        if relevant_docs:
            # Mark that we're showing docs for this operation
            mark_docs_shown(operation_hash)
            
            # Format documentation as feedback
            feedback = format_documentation_feedback(relevant_docs, keywords)
            
            # Print feedback to stderr so Claude sees it
            print(feedback, file=sys.stderr)
            
            # Exit with code 2 to block this first attempt
            sys.exit(2)
        else:
            # No relevant docs found, proceed normally
            sys.exit(0)
            
    except json.JSONDecodeError:
        # Invalid JSON, proceed normally
        sys.exit(0)
    except Exception as e:
        # Log error but don't block operation
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()