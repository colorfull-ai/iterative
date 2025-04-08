# Iterative Project Manager

A VS Code extension for managing iterative projects with a standardized folder structure and workflow.

## Features

- **Project Structure Management**: Easily create and manage iterative projects with standardized folder structure
- **Quick CRUD API Creation**: Generate FastAPI endpoints with a single click
- **Model Generation**: Create Pydantic models with standard fields and validation
- **Focus Mode**: Quickly switch between iterative projects
- **Custom Icons**: Visual distinction for iterative project folders

## Commands

All commands are prefixed with "Iterative:" and can be accessed via the command palette (Ctrl/Cmd + Shift + P):

- `Iterative: Open Project Manager` - Open the project management interface
- `Iterative: Create New Project` - Create a new iterative project
- `Iterative: Convert to Project` - Convert an existing folder to an iterative project
- `Iterative: Create CRUD API` - Create a new API file with CRUD endpoints (in api folder)
- `Iterative: Create Model` - Create a new Pydantic model (in models folder)
- `Iterative: Focus Mode` - Focus on a specific iterative project

## Project Structure

An iterative project follows this structure:

```
your-project/
├── .iterative/        # Project configuration
├── api/              # FastAPI endpoints
├── service/          # Business logic
├── models/           # Data models
└── actions/          # Background tasks
```

## Context Menu Actions

Right-click actions available in the explorer:

- On folders: "Iterative: Convert to Project"
- In api folder: "Iterative: Create CRUD API"
- In models folder: "Iterative: Create Model"

## Requirements

- VS Code 1.85.0 or higher
- Python 3.8 or higher (for generated code)
- FastAPI (for API functionality)
- Pydantic (for models)

## Extension Settings

This extension contributes the following settings:

- `iterative.focusMode`: Enable/disable focus mode for iterative projects

## Known Issues

Please report issues at [GitHub Issues](https://github.com/colorfull-ai/vscode-iterative/issues)

## Release Notes

### 0.1.0

Initial release of Iterative Project Manager:
- Basic project structure management
- CRUD API generation
- Model generation
- Focus mode
- Custom folder icons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

---

**Enjoy!** 