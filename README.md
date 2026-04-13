# Sir Albert Knowledge Base

This repository serves as the persistent, structured knowledge base for **Sir Albert** (Gal's AI assistant). 

It is managed via the [LLM Wiki Agent](https://github.com/gal-Tab/agent_knowledgebase) plugin.

## Directory Structure

- `raw/`: Drop your raw source files here (PDFs, Markdown, text, etc.). The agent will automatically extract and compile them.
- `wiki/`: The compiled, structured knowledge base maintained by the agent. Includes sources, entities, concepts, and comparisons.
- `tools/`: Extraction scripts used by the agent to parse files in the `raw/` directory.
- `wiki-schema.md`: The domain rules and configuration. Update this to guide how the agent synthesizes information.
- `HANDOFF.md`: Session persistence state.

## Usage

1. Add files to the `raw/` directory.
2. The agent will process them during its next session and update the `wiki/` structure.
3. Ask Sir Albert questions, and it will use this structured memory to answer with citations.
