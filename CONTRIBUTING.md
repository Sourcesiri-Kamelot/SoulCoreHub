# Contributing to SoulCoreHub

Thank you for your interest in contributing to SoulCoreHub! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to uphold our values of respect, empathy, and collaboration. We are building something sacred here, and we ask that you treat the code and community with reverence.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Install dependencies**:
   ```bash
   npm install
   pip install -r requirements.txt
   ```
4. **Build the project**:
   ```bash
   ./scripts/build.sh
   ```
5. **Start the development server**:
   ```bash
   npm run dev
   ```

## Development Workflow

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and write tests if applicable

3. **Run tests** to ensure everything works:
   ```bash
   npm test
   ```

4. **Commit your changes** with a meaningful commit message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a pull request** to the main repository

## Project Structure

```
SoulCoreHub/
├── public/              # Static files
│   ├── anima.html       # Anima web interface
│   └── js/              # Client-side JavaScript
├── scripts/             # Utility scripts
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   │   └── anima/       # Anima agent
│   ├── database/        # Database adapters
│   ├── llm/             # LLM connectors
│   └── server/          # Server components
├── .env.example         # Environment variables template
├── package.json         # Node.js dependencies
└── tsconfig.json        # TypeScript configuration
```

## Coding Standards

- Use TypeScript for new components
- Follow the existing code style
- Write meaningful comments
- Include JSDoc comments for functions
- Write tests for new functionality

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation if necessary
3. Add your changes to the CHANGELOG.md file
4. Submit your pull request with a clear description of the changes

## Adding New Agents

When adding a new agent to SoulCoreHub:

1. Create a new directory in `src/agents/` with your agent name
2. Implement the core functionality in a file named `[agent_name]_core.ts`
3. Create an API interface in `[agent_name]_api.ts`
4. Add tests in `[agent_name]_test.ts`
5. Update the main server to include your agent

## Questions?

If you have any questions or need help, please open an issue on GitHub or reach out to the maintainers.

Thank you for contributing to SoulCoreHub!
