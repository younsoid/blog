#!/usr/bin/env python3
"""
Script to process markdown files and update their categories based on title patterns.

For files with "#숫자" pattern in title (e.g., "RAG #1"):
  - Extract the keyword before #숫자
  - Add it to categories if not already present

For files without the pattern:
  - Add 'etc' to categories if not already present

Excludes _index.md files.
"""

import os
import re
from pathlib import Path


def extract_front_matter(content):
    """Extract front matter from markdown content."""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    return parts[1], parts[2]


def parse_front_matter(front_matter):
    """Parse YAML-like front matter into a dict."""
    lines = front_matter.strip().split('\n')
    data = {}
    current_key = None
    in_array = False

    for line in lines:
        line = line.rstrip()

        # Handle array continuation
        if in_array:
            if line.startswith(' ') or line.startswith('-'):
                continue
            else:
                in_array = False

        # Parse key-value pairs
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value.startswith('['):
                # Inline array
                data[key] = value
                if not value.endswith(']'):
                    in_array = True
            else:
                data[key] = value

            current_key = key
        elif current_key and line.startswith(' '):
            # Continuation of previous value
            if current_key in data:
                data[current_key] += ' ' + line.strip()

    return data


def serialize_front_matter(data):
    """Convert dict back to YAML-like front matter."""
    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return '\n'.join(lines)


def extract_keyword_from_title(title):
    """Extract keyword before #숫자 pattern from title."""
    # Pattern: word(s) followed by #숫자
    pattern = r'^(.+?)\s*#\d+\s'
    match = re.match(pattern, title)
    if match:
        keyword = match.group(1).strip()
        # Remove quotes if present
        keyword = keyword.strip('"').strip("'")
        return keyword
    return None


def parse_categories(categories_str):
    """Parse categories string into a list."""
    # Handle ['AI'] or ['AI', 'RAG'] format
    categories_str = categories_str.strip()

    # Remove outer brackets
    if categories_str.startswith('[') and categories_str.endswith(']'):
        categories_str = categories_str[1:-1]

    # Split by comma and clean
    categories = []
    for cat in categories_str.split(','):
        cat = cat.strip().strip("'").strip('"').strip()
        if cat:
            categories.append(cat)

    return categories


def serialize_categories(categories):
    """Convert categories list back to string format."""
    quoted_cats = [f"'{cat}'" for cat in categories]
    return '[' + ', '.join(quoted_cats) + ']'


def process_file(file_path):
    """Process a single markdown file."""
    # Skip _index.md files
    if file_path.name == '_index.md':
        return None

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract front matter
    front_matter_str, body = extract_front_matter(content)
    if front_matter_str is None:
        return f"Skipped (no front matter): {file_path}"

    # Parse front matter
    front_matter = parse_front_matter(front_matter_str)

    # Get title and categories
    title = front_matter.get('title', '').strip('"').strip("'")
    categories_str = front_matter.get('categories', '')

    if not title or not categories_str:
        return f"Skipped (missing title or categories): {file_path}"

    # Parse current categories
    categories = parse_categories(categories_str)

    # Extract keyword or determine if 'etc' should be added
    keyword = extract_keyword_from_title(title)

    # Determine what to add
    if keyword:
        # Add keyword if not already present
        if keyword not in categories:
            categories.append(keyword)
            action = f"Added '{keyword}'"
        else:
            return f"No change ('{keyword}' already present): {file_path}"
    else:
        # Add 'etc' if not already present
        if 'etc' not in categories:
            categories.append('etc')
            action = "Added 'etc'"
        else:
            return f"No change ('etc' already present): {file_path}"

    # Update front matter
    front_matter['categories'] = serialize_categories(categories)

    # Reconstruct content
    new_front_matter_str = serialize_front_matter(front_matter)
    new_content = f"---\n{new_front_matter_str}\n---{body}"

    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return f"{action}: {file_path}"


def main():
    """Main function to process all markdown files in specified directories."""
    base_dir = Path('/Users/yshmbid/Hugo/blog/blog/content/docs/study')

    directories = [
        base_dir / 'AI',
        base_dir / 'FE',
        base_dir / 'BE'
    ]

    results = []

    for directory in directories:
        if not directory.exists():
            results.append(f"Directory not found: {directory}")
            continue

        # Process all .md files in the directory
        for md_file in directory.glob('*.md'):
            result = process_file(md_file)
            if result:
                results.append(result)

    # Print results
    print("\n=== Processing Results ===\n")
    for result in results:
        print(result)

    print(f"\nTotal files processed: {len(results)}")


if __name__ == '__main__':
    main()
