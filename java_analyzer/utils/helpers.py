"""
Helper Functions
Utility functions for naming validation, line counting, and other common tasks
"""

import re
from typing import List


def validate_class_name(name: str) -> bool:
    """
    Validate that a class name follows PascalCase convention.
    
    Args:
        name: The class name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))


def validate_method_name(name: str) -> bool:
    """
    Validate that a method name follows camelCase convention.
    
    Args:
        name: The method name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))


def count_blank_lines(lines: List[str]) -> int:
    """
    Count the number of blank lines in source code.
    
    Args:
        lines: Source code split into lines
        
    Returns:
        Number of blank lines
    """
    return sum(1 for line in lines if line.strip() == '')


def count_comment_lines(lines: List[str]) -> int:
    """
    Count the number of comment lines (single-line and multi-line).
    
    Args:
        lines: Source code split into lines
        
    Returns:
        Number of comment lines
    """
    count = 0
    in_block_comment = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check for block comment start
        if '/*' in stripped:
            in_block_comment = True
        
        # Count line if in block comment or single-line comment
        if in_block_comment or stripped.startswith('//'):
            count += 1
        
        # Check for block comment end
        if '*/' in stripped:
            in_block_comment = False
    
    return count


def calculate_comment_ratio(total_lines: int, comment_lines: int) -> float:
    """
    Calculate the ratio of comment lines to total lines.
    
    Args:
        total_lines: Total number of lines
        comment_lines: Number of comment lines
        
    Returns:
        Comment ratio as a percentage (0-100)
    """
    if total_lines == 0:
        return 0.0
    return (comment_lines / total_lines) * 100


def calculate_quality_score(total_issues: int, critical_count: int) -> int:
    """
    Calculate an overall quality score based on issues found.
    
    Args:
        total_issues: Total number of issues detected
        critical_count: Number of critical issues
        
    Returns:
        Quality score (0-100)
    """
    score = 100 - (total_issues * 2) - (critical_count * 10)
    return max(0, score)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"