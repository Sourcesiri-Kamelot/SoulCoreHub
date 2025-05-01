#!/usr/bin/env python3
"""
Programming Knowledge - Provides Anima with programming language knowledge
Enables access to programming language documentation, syntax, and best practices
"""

import os
import json
import logging
import requests
import re
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("programming_knowledge.log"),
        logging.StreamHandler()
    ]
)

class ProgrammingKnowledge:
    """Programming language knowledge provider"""
    
    def __init__(self):
        """Initialize the programming knowledge provider"""
        self.cache_dir = Path.home() / "SoulCoreHub" / "data" / "programming_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = 7 * 24  # Cache expiry in hours (7 days)
        self.language_info = self._load_language_info()
        logging.info("Programming knowledge provider initialized")
    
    def _load_language_info(self):
        """Load information about programming languages"""
        languages = {
            "python": {
                "name": "Python",
                "docs_url": "https://docs.python.org/3/",
                "api_url": "https://docs.python.org/3/library/",
                "extension": ".py",
                "versions": ["3.11", "3.10", "3.9", "3.8", "3.7", "2.7"],
                "paradigms": ["object-oriented", "imperative", "functional", "procedural", "reflective"]
            },
            "javascript": {
                "name": "JavaScript",
                "docs_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                "api_url": "https://developer.mozilla.org/en-US/docs/Web/API",
                "extension": ".js",
                "versions": ["ES2022", "ES2021", "ES2020", "ES2019", "ES2018", "ES2017", "ES2016", "ES2015", "ES5"],
                "paradigms": ["object-oriented", "imperative", "functional", "event-driven"]
            },
            "java": {
                "name": "Java",
                "docs_url": "https://docs.oracle.com/en/java/",
                "api_url": "https://docs.oracle.com/en/java/javase/17/docs/api/",
                "extension": ".java",
                "versions": ["17", "11", "8"],
                "paradigms": ["object-oriented", "imperative", "functional", "reflective"]
            },
            "csharp": {
                "name": "C#",
                "docs_url": "https://docs.microsoft.com/en-us/dotnet/csharp/",
                "api_url": "https://docs.microsoft.com/en-us/dotnet/api/",
                "extension": ".cs",
                "versions": ["10.0", "9.0", "8.0", "7.3", "7.2", "7.1", "7.0"],
                "paradigms": ["object-oriented", "imperative", "functional", "declarative", "component-oriented"]
            },
            "cpp": {
                "name": "C++",
                "docs_url": "https://en.cppreference.com/w/cpp",
                "api_url": "https://en.cppreference.com/w/cpp/header",
                "extension": ".cpp",
                "versions": ["C++20", "C++17", "C++14", "C++11", "C++03", "C++98"],
                "paradigms": ["object-oriented", "procedural", "functional", "generic"]
            },
            "go": {
                "name": "Go",
                "docs_url": "https://golang.org/doc/",
                "api_url": "https://pkg.go.dev/std",
                "extension": ".go",
                "versions": ["1.19", "1.18", "1.17", "1.16"],
                "paradigms": ["concurrent", "imperative", "structured"]
            },
            "rust": {
                "name": "Rust",
                "docs_url": "https://doc.rust-lang.org/",
                "api_url": "https://doc.rust-lang.org/std/",
                "extension": ".rs",
                "versions": ["1.65", "1.64", "1.63", "1.62"],
                "paradigms": ["concurrent", "functional", "imperative", "structured"]
            },
            "typescript": {
                "name": "TypeScript",
                "docs_url": "https://www.typescriptlang.org/docs/",
                "api_url": "https://www.typescriptlang.org/docs/handbook/",
                "extension": ".ts",
                "versions": ["4.9", "4.8", "4.7", "4.6", "4.5"],
                "paradigms": ["object-oriented", "imperative", "functional"]
            },
            "ruby": {
                "name": "Ruby",
                "docs_url": "https://ruby-doc.org/",
                "api_url": "https://ruby-doc.org/core/",
                "extension": ".rb",
                "versions": ["3.1", "3.0", "2.7", "2.6", "2.5"],
                "paradigms": ["object-oriented", "imperative", "functional", "reflective"]
            },
            "php": {
                "name": "PHP",
                "docs_url": "https://www.php.net/docs.php",
                "api_url": "https://www.php.net/manual/en/",
                "extension": ".php",
                "versions": ["8.1", "8.0", "7.4", "7.3", "7.2"],
                "paradigms": ["object-oriented", "imperative", "functional", "reflective"]
            },
            "swift": {
                "name": "Swift",
                "docs_url": "https://swift.org/documentation/",
                "api_url": "https://developer.apple.com/documentation/swift",
                "extension": ".swift",
                "versions": ["5.7", "5.6", "5.5", "5.4", "5.3"],
                "paradigms": ["object-oriented", "protocol-oriented", "functional", "imperative"]
            },
            "kotlin": {
                "name": "Kotlin",
                "docs_url": "https://kotlinlang.org/docs/",
                "api_url": "https://kotlinlang.org/api/latest/jvm/stdlib/",
                "extension": ".kt",
                "versions": ["1.7", "1.6", "1.5", "1.4", "1.3"],
                "paradigms": ["object-oriented", "functional", "imperative", "concurrent"]
            }
        }
        return languages
    
    def _get_cache_path(self, cache_key):
        """Get the path for a cached item"""
        # Create a safe filename from the cache key
        safe_key = "".join(c if c.isalnum() else "_" for c in cache_key)
        return self.cache_dir / f"{safe_key}.json"
    
    def _get_from_cache(self, cache_key):
        """
        Get an item from the cache
        
        Args:
            cache_key (str): Cache key
            
        Returns:
            dict: Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time > timedelta(hours=self.cache_expiry):
                return None
            
            return cached["data"]
        except Exception as e:
            logging.error(f"Error reading from cache: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_key, data):
        """
        Save an item to the cache
        
        Args:
            cache_key (str): Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                }, f)
        except Exception as e:
            logging.error(f"Error saving to cache: {str(e)}")
    
    def get_language_info(self, language):
        """
        Get information about a programming language
        
        Args:
            language (str): Programming language name
            
        Returns:
            dict: Language information
        """
        language = language.lower()
        
        # Handle common aliases
        aliases = {
            "js": "javascript",
            "py": "python",
            "ts": "typescript",
            "c#": "csharp",
            "c++": "cpp",
            "golang": "go"
        }
        
        if language in aliases:
            language = aliases[language]
        
        if language in self.language_info:
            return self.language_info[language]
        
        return None
    
    def get_all_languages(self):
        """
        Get information about all supported programming languages
        
        Returns:
            dict: Language information
        """
        return self.language_info
    
    def get_language_syntax(self, language, concept):
        """
        Get syntax information for a programming language concept
        
        Args:
            language (str): Programming language name
            concept (str): Programming concept (e.g., "for loop", "function", "class")
            
        Returns:
            dict: Syntax information
        """
        language = language.lower()
        
        # Handle common aliases
        aliases = {
            "js": "javascript",
            "py": "python",
            "ts": "typescript",
            "c#": "csharp",
            "c++": "cpp",
            "golang": "go"
        }
        
        if language in aliases:
            language = aliases[language]
        
        # Check cache first
        cache_key = f"syntax_{language}_{concept}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved syntax information from cache for '{language}/{concept}'")
            return cached
        
        # Define syntax examples for common concepts
        syntax_examples = {
            "python": {
                "for loop": {
                    "description": "Iterate over a sequence (list, tuple, string) or other iterable objects",
                    "examples": [
                        "for item in sequence:\n    # code block",
                        "for i in range(5):\n    print(i)",
                        "for index, value in enumerate(sequence):\n    print(index, value)"
                    ]
                },
                "function": {
                    "description": "Define a named block of reusable code",
                    "examples": [
                        "def function_name(parameters):\n    # code block\n    return value",
                        "def greet(name):\n    return f\"Hello, {name}!\"",
                        "def add(a, b=0):\n    return a + b"
                    ]
                },
                "class": {
                    "description": "Define a blueprint for creating objects",
                    "examples": [
                        "class ClassName:\n    def __init__(self, parameters):\n        # constructor\n    \n    def method_name(self, parameters):\n        # method body",
                        "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        return f\"Hello, my name is {self.name}\""
                    ]
                },
                "if statement": {
                    "description": "Conditional execution of code",
                    "examples": [
                        "if condition:\n    # code block\nelif another_condition:\n    # code block\nelse:\n    # code block",
                        "if x > 0:\n    print(\"Positive\")\nelif x < 0:\n    print(\"Negative\")\nelse:\n    print(\"Zero\")"
                    ]
                },
                "list comprehension": {
                    "description": "Create lists from existing sequences",
                    "examples": [
                        "[expression for item in iterable if condition]",
                        "[x**2 for x in range(10)]",
                        "[x for x in range(100) if x % 2 == 0]"
                    ]
                }
            },
            "javascript": {
                "for loop": {
                    "description": "Iterate over a sequence",
                    "examples": [
                        "for (let i = 0; i < array.length; i++) {\n    // code block\n}",
                        "for (const item of array) {\n    // code block\n}",
                        "array.forEach((item, index) => {\n    // code block\n});"
                    ]
                },
                "function": {
                    "description": "Define a named block of reusable code",
                    "examples": [
                        "function functionName(parameters) {\n    // code block\n    return value;\n}",
                        "const functionName = (parameters) => {\n    // code block\n    return value;\n}",
                        "function greet(name) {\n    return `Hello, ${name}!`;\n}"
                    ]
                },
                "class": {
                    "description": "Define a blueprint for creating objects",
                    "examples": [
                        "class ClassName {\n    constructor(parameters) {\n        // constructor\n    }\n    \n    methodName(parameters) {\n        // method body\n    }\n}",
                        "class Person {\n    constructor(name, age) {\n        this.name = name;\n        this.age = age;\n    }\n    \n    greet() {\n        return `Hello, my name is ${this.name}`;\n    }\n}"
                    ]
                },
                "if statement": {
                    "description": "Conditional execution of code",
                    "examples": [
                        "if (condition) {\n    // code block\n} else if (anotherCondition) {\n    // code block\n} else {\n    // code block\n}",
                        "if (x > 0) {\n    console.log(\"Positive\");\n} else if (x < 0) {\n    console.log(\"Negative\");\n} else {\n    console.log(\"Zero\");\n}"
                    ]
                },
                "array methods": {
                    "description": "Common array manipulation methods",
                    "examples": [
                        "array.map(item => /* transform item */)",
                        "array.filter(item => /* condition */)",
                        "array.reduce((accumulator, item) => /* combine items */, initialValue)"
                    ]
                }
            }
            # Add more languages as needed
        }
        
        # Get syntax for the requested language and concept
        if language in syntax_examples and concept in syntax_examples[language]:
            result = syntax_examples[language][concept]
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            return result
        
        return None
    
    def search_documentation(self, language, query):
        """
        Search for documentation on a programming language topic
        
        Args:
            language (str): Programming language name
            query (str): Search query
            
        Returns:
            list: Search results
        """
        language_info = self.get_language_info(language)
        if not language_info:
            return []
        
        # Check cache first
        cache_key = f"docs_{language}_{query}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved documentation search results from cache for '{language}/{query}'")
            return cached
        
        # For now, return links to relevant documentation
        # In a real implementation, this would search the actual documentation
        results = []
        
        # Add general documentation link
        results.append({
            "title": f"{language_info['name']} Documentation",
            "url": language_info['docs_url'],
            "description": f"Official documentation for {language_info['name']}"
        })
        
        # Add API documentation link
        results.append({
            "title": f"{language_info['name']} API Reference",
            "url": language_info['api_url'],
            "description": f"API reference for {language_info['name']}"
        })
        
        # Add search query link
        search_url = f"https://www.google.com/search?q={query}+{language_info['name']}+documentation"
        results.append({
            "title": f"Search for '{query}' in {language_info['name']}",
            "url": search_url,
            "description": f"Search results for '{query}' in {language_info['name']}"
        })
        
        # Cache the results
        self._save_to_cache(cache_key, results)
        
        return results
    
    def get_code_snippet(self, language, concept):
        """
        Get a code snippet for a programming concept
        
        Args:
            language (str): Programming language name
            concept (str): Programming concept
            
        Returns:
            dict: Code snippet
        """
        # Check cache first
        cache_key = f"snippet_{language}_{concept}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved code snippet from cache for '{language}/{concept}'")
            return cached
        
        # Get syntax information
        syntax = self.get_language_syntax(language, concept)
        if syntax and "examples" in syntax and len(syntax["examples"]) > 0:
            snippet = {
                "language": language,
                "concept": concept,
                "code": syntax["examples"][0],
                "description": syntax.get("description", "")
            }
            
            # Cache the snippet
            self._save_to_cache(cache_key, snippet)
            
            return snippet
        
        return None
    
    def detect_language(self, code):
        """
        Detect the programming language of a code snippet
        
        Args:
            code (str): Code snippet
            
        Returns:
            str: Detected language
        """
        # Simple language detection based on syntax patterns
        patterns = {
            "python": [
                r"def\s+\w+\s*\([^)]*\)\s*:",
                r"import\s+\w+",
                r"from\s+\w+\s+import",
                r"class\s+\w+\s*:",
                r"if\s+.+:",
                r"for\s+.+\s+in\s+.+:"
            ],
            "javascript": [
                r"function\s+\w+\s*\([^)]*\)\s*{",
                r"const\s+\w+\s*=",
                r"let\s+\w+\s*=",
                r"var\s+\w+\s*=",
                r"class\s+\w+\s*{",
                r"import\s+.*\s+from\s+"
            ],
            "java": [
                r"public\s+class\s+\w+",
                r"private\s+\w+\s+\w+\s*\(",
                r"public\s+\w+\s+\w+\s*\(",
                r"import\s+java\.",
                r"package\s+\w+"
            ],
            "csharp": [
                r"namespace\s+\w+",
                r"using\s+\w+;",
                r"public\s+class\s+\w+",
                r"private\s+\w+\s+\w+\s*\(",
                r"public\s+\w+\s+\w+\s*\("
            ],
            "cpp": [
                r"#include\s+<\w+>",
                r"using\s+namespace\s+std;",
                r"int\s+main\s*\(\s*\)",
                r"class\s+\w+\s*{",
                r"::\w+"
            ]
        }
        
        scores = {}
        for lang, patterns_list in patterns.items():
            score = 0
            for pattern in patterns_list:
                if re.search(pattern, code):
                    score += 1
            scores[lang] = score
        
        # Get the language with the highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                for lang, score in scores.items():
                    if score == max_score:
                        return lang
        
        return "unknown"
    
    def get_best_practices(self, language):
        """
        Get best practices for a programming language
        
        Args:
            language (str): Programming language name
            
        Returns:
            list: Best practices
        """
        language = language.lower()
        
        # Handle common aliases
        aliases = {
            "js": "javascript",
            "py": "python",
            "ts": "typescript",
            "c#": "csharp",
            "c++": "cpp",
            "golang": "go"
        }
        
        if language in aliases:
            language = aliases[language]
        
        # Check cache first
        cache_key = f"best_practices_{language}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logging.info(f"Retrieved best practices from cache for '{language}'")
            return cached
        
        # Define best practices for common languages
        best_practices = {
            "python": [
                "Follow PEP 8 style guide",
                "Use meaningful variable and function names",
                "Write docstrings for functions and classes",
                "Use list comprehensions when appropriate",
                "Handle exceptions properly",
                "Use context managers (with statement) for file operations",
                "Prefer 'is not' over 'not ... is'",
                "Use virtual environments for project dependencies",
                "Write unit tests using pytest or unittest",
                "Use type hints for better code readability and IDE support"
            ],
            "javascript": [
                "Use const and let instead of var",
                "Use strict equality (===) instead of loose equality (==)",
                "Use arrow functions for short callbacks",
                "Use template literals for string interpolation",
                "Use destructuring assignment",
                "Use async/await for asynchronous code",
                "Use ESLint to enforce code style",
                "Use modules to organize code",
                "Handle promises properly with .catch() or try/catch",
                "Use functional programming methods like map, filter, and reduce"
            ],
            "java": [
                "Follow Java naming conventions",
                "Use interfaces for abstraction",
                "Handle exceptions properly",
                "Use try-with-resources for automatic resource management",
                "Prefer composition over inheritance",
                "Use StringBuilder for string concatenation in loops",
                "Use the Collections framework appropriately",
                "Make fields private and provide getters/setters when needed",
                "Use @Override annotation when overriding methods",
                "Use streams for functional-style operations"
            ],
            "csharp": [
                "Follow C# naming conventions",
                "Use properties instead of public fields",
                "Use LINQ for querying collections",
                "Use async/await for asynchronous code",
                "Use using statements for IDisposable objects",
                "Use string interpolation for string formatting",
                "Use nullable reference types",
                "Use pattern matching where appropriate",
                "Use expression-bodied members for short methods",
                "Use dependency injection for better testability"
            ]
        }
        
        # Get best practices for the requested language
        if language in best_practices:
            result = best_practices[language]
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            return result
        
        return []

# Register programming knowledge tools with MCP server
def register_programming_tools(server):
    """
    Register programming knowledge tools with the MCP server
    
    Args:
        server: MCP server instance
    """
    knowledge = ProgrammingKnowledge()
    
    # Get language info tool
    async def get_language_info_tool(params, metadata=None):
        language = params.get("language", "")
        return knowledge.get_language_info(language)
    
    # Get all languages tool
    async def get_all_languages_tool(params, metadata=None):
        return knowledge.get_all_languages()
    
    # Get language syntax tool
    async def get_language_syntax_tool(params, metadata=None):
        language = params.get("language", "")
        concept = params.get("concept", "")
        return knowledge.get_language_syntax(language, concept)
    
    # Search documentation tool
    async def search_documentation_tool(params, metadata=None):
        language = params.get("language", "")
        query = params.get("query", "")
        return knowledge.search_documentation(language, query)
    
    # Get code snippet tool
    async def get_code_snippet_tool(params, metadata=None):
        language = params.get("language", "")
        concept = params.get("concept", "")
        return knowledge.get_code_snippet(language, concept)
    
    # Detect language tool
    async def detect_language_tool(params, metadata=None):
        code = params.get("code", "")
        return {"language": knowledge.detect_language(code)}
    
    # Get best practices tool
    async def get_best_practices_tool(params, metadata=None):
        language = params.get("language", "")
        return knowledge.get_best_practices(language)
    
    # Register the tools
    server.register_tool(
        "programming_get_language_info",
        get_language_info_tool,
        "Get information about a programming language",
        "informative"
    )
    
    server.register_tool(
        "programming_get_all_languages",
        get_all_languages_tool,
        "Get information about all supported programming languages",
        "informative"
    )
    
    server.register_tool(
        "programming_get_language_syntax",
        get_language_syntax_tool,
        "Get syntax information for a programming language concept",
        "helpful"
    )
    
    server.register_tool(
        "programming_search_documentation",
        search_documentation_tool,
        "Search for documentation on a programming language topic",
        "helpful"
    )
    
    server.register_tool(
        "programming_get_code_snippet",
        get_code_snippet_tool,
        "Get a code snippet for a programming concept",
        "helpful"
    )
    
    server.register_tool(
        "programming_detect_language",
        detect_language_tool,
        "Detect the programming language of a code snippet",
        "analytical"
    )
    
    server.register_tool(
        "programming_get_best_practices",
        get_best_practices_tool,
        "Get best practices for a programming language",
        "informative"
    )

# Example usage
if __name__ == "__main__":
    try:
        # Create programming knowledge provider
        knowledge = ProgrammingKnowledge()
        
        # Test getting language info
        print("Python language info:")
        info = knowledge.get_language_info("python")
        print(f"Name: {info['name']}")
        print(f"Docs URL: {info['docs_url']}")
        print(f"Versions: {', '.join(info['versions'])}")
        print(f"Paradigms: {', '.join(info['paradigms'])}")
        print()
        
        # Test getting syntax
        print("Python for loop syntax:")
        syntax = knowledge.get_language_syntax("python", "for loop")
        print(f"Description: {syntax['description']}")
        print("Examples:")
        for example in syntax['examples']:
            print(f"---\n{example}\n---")
        print()
        
        # Test getting best practices
        print("Python best practices:")
        practices = knowledge.get_best_practices("python")
        for i, practice in enumerate(practices, 1):
            print(f"{i}. {practice}")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
