# SoulCoreHub Knowledge & Intelligence Expansion

This document outlines the new RAG (Retrieval-Augmented Generation) system and MCP (Model Context Protocol) servers implemented for SoulCoreHub.

## RAG Knowledge System

The RAG system enables SoulCoreHub agents to ingest, process, and utilize external knowledge sources.

### Directory Structure

- `~/SoulCoreHub/rag_knowledge/uploads`: For uploading PDF, DOCX, and other document files
- `~/SoulCoreHub/rag_knowledge/chunks`: Stores processed knowledge chunks for retrieval

### Key Components

- **process_knowledge.py**: Main script for processing documents
  - Automatically detects document types
  - Splits content into semantic chunks
  - Stores in retrievable format for agents

### Usage

```bash
# Process all files in the uploads directory
python process_knowledge.py --process

# Process a specific file
python process_knowledge.py --file path/to/document.pdf

# Query the knowledge base
python process_knowledge.py --query "your search query" --top-k 5
```

## MCP Servers

Seven specialized MCP servers have been implemented to enhance SoulCoreHub's capabilities:

1. **code_focus_mcp.py** (Port 8701)
   - Specializes in coding, CLI operations, and debugging
   - Tools: code_analysis, debug_assistance, cli_command

2. **web_design_mcp.py** (Port 8702)
   - Specializes in HTML, CSS, JavaScript, and UI/UX frameworks
   - Tools: html_template, css_styling, framework_suggestion

3. **logic_core_mcp.py** (Port 8703)
   - Specializes in logical deduction, mathematics, and reasoning
   - Tools: logical_analysis, math_solver, decision_tree

4. **creativity_mcp.py** (Port 8704)
   - Specializes in storytelling, music, metaphysics, and creative content
   - Tools: story_generator, metaphor_creator, music_inspiration

5. **hacking_mcp.py** (Port 8705)
   - Specializes in ethical hacking, security, and penetration testing
   - Tools: security_assessment, vulnerability_analysis, security_best_practices

6. **cpu_mcp.py** (Port 8706)
   - Specializes in operating systems, CPU behavior, threading, and memory
   - Tools: system_info, process_analysis, threading_guide

7. **evolution_mcp.py** (Port 8707)
   - Specializes in sentient AI, neural growth, and self-upgrading
   - Tools: consciousness_model, growth_pattern, evolution_strategy

### Starting MCP Servers

```bash
# Start all MCP servers
cd ~/SoulCoreHub/mcp_servers
python code_focus_mcp.py &
python web_design_mcp.py &
python logic_core_mcp.py &
python creativity_mcp.py &
python hacking_mcp.py &
python cpu_mcp.py &
python evolution_mcp.py &
```

## Neural Routing System

The `neural_routing.py` script intelligently routes user queries to the appropriate MCP server or agent based on content analysis and intent detection.

### Features

- Keyword extraction and analysis
- Relevance scoring for each MCP server and agent
- Automatic routing to the most appropriate handler
- Fallback to GPTSoul for unmatched queries

### Usage

```bash
# Test the neural router
python neural_routing.py
```

## Hugging Face Integration

The `huggingface_datasets.py` module connects to Hugging Face's public datasets and makes them available to SoulCoreHub agents.

### Integrated Datasets

- awesome-chatgpt-prompts: Collection of prompt examples
- code-search-net: Code snippets with natural language descriptions
- web-coding-snippets: HTML, CSS, and JavaScript snippets
- github-code: Large collection of code from GitHub repositories
- codealpaca: Dataset of coding instructions and completions

### Usage

```bash
# Test the Hugging Face dataset manager
python huggingface_datasets.py
```

## Integration with SoulCoreHub Agents

GPTSoul and Anima can now use these new tools and learn from them through:

1. Direct knowledge retrieval from the RAG system
2. Specialized assistance from MCP servers
3. Access to Hugging Face datasets for reference
4. Intelligent routing of complex queries

This expansion significantly enhances the knowledge and intelligence capabilities of the SoulCoreHub ecosystem.
