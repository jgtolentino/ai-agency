# VS Code Extension Architecture: Odoo Development Automations

**Version**: 1.0
**Created**: 2025-11-01
**Sprint**: 4 (Track 1: PRD-INTEGRATION)

---

## Overview

Thin wrapper VS Code extension that exposes existing Cline CLI skills as VS Code commands. **No duplication** - all logic delegated to existing automation scripts.

**Design Principle**: Extension = UI layer only. All functionality implemented in `/scripts/` and `/skills/`.

---

## 1. Extension Manifest

**File**: `package.json`

```json
{
  "name": "odoo-dev-automations",
  "displayName": "Odoo Development Automations",
  "description": "OCA-compliant Odoo module development with AI assistance",
  "version": "0.1.0",
  "publisher": "odoo-expertise",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": [
    "Programming Languages",
    "Snippets",
    "Other"
  ],
  "keywords": [
    "odoo",
    "oca",
    "python",
    "xml",
    "erp"
  ],
  "activationEvents": [
    "onLanguage:python",
    "onLanguage:xml",
    "workspaceContains:**/__manifest__.py"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "odoo.scaffoldModule",
        "title": "Odoo: Scaffold Module",
        "category": "Odoo"
      },
      {
        "command": "odoo.newModel",
        "title": "Odoo: New Model",
        "category": "Odoo"
      },
      {
        "command": "odoo.extendModel",
        "title": "Odoo: Extend Existing Model",
        "category": "Odoo"
      },
      {
        "command": "odoo.generateMigration",
        "title": "Odoo: Generate Migration Script",
        "category": "Odoo"
      },
      {
        "command": "odoo.generateDocs",
        "title": "Odoo: Generate Documentation",
        "category": "Odoo"
      },
      {
        "command": "odoo.validateOCA",
        "title": "Odoo: Validate OCA Compliance",
        "category": "Odoo"
      },
      {
        "command": "odoo.deploy",
        "title": "Odoo: Deploy Module",
        "category": "Odoo"
      },
      {
        "command": "odoo.rollback",
        "title": "Odoo: Rollback Deployment",
        "category": "Odoo"
      }
    ],
    "configuration": {
      "title": "Odoo Development Automations",
      "properties": {
        "odoo.scriptsPath": {
          "type": "string",
          "default": "${workspaceFolder}/scripts",
          "description": "Path to odoo-expertise scripts directory"
        },
        "odoo.outputDirectory": {
          "type": "string",
          "default": "${workspaceFolder}/custom_addons",
          "description": "Output directory for generated modules"
        },
        "odoo.defaultAuthor": {
          "type": "string",
          "default": "Odoo Community Association (OCA)",
          "description": "Default module author"
        },
        "odoo.defaultWebsite": {
          "type": "string",
          "default": "https://github.com/OCA",
          "description": "Default author website"
        },
        "odoo.defaultVersion": {
          "type": "string",
          "default": "16.0.1.0.0",
          "description": "Default module version"
        }
      }
    },
    "menus": {
      "explorer/context": [
        {
          "when": "resourceExtname == .py && resourcePath =~ /models/",
          "command": "odoo.extendModel",
          "group": "odoo@1"
        }
      ],
      "commandPalette": [
        {
          "command": "odoo.scaffoldModule",
          "when": "workspaceContains:**/__manifest__.py || workspaceContains:custom_addons"
        },
        {
          "command": "odoo.newModel",
          "when": "workspaceContains:**/__manifest__.py"
        },
        {
          "command": "odoo.extendModel",
          "when": "resourceExtname == .py"
        },
        {
          "command": "odoo.generateMigration",
          "when": "workspaceContains:**/__manifest__.py"
        },
        {
          "command": "odoo.generateDocs",
          "when": "workspaceContains:**/__manifest__.py"
        },
        {
          "command": "odoo.validateOCA",
          "when": "workspaceContains:**/__manifest__.py"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "pretest": "npm run compile && npm run lint",
    "lint": "eslint src --ext ts",
    "test": "node ./out/test/runTest.js"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "@types/node": "20.x",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

---

## 2. Extension Entry Point

**File**: `src/extension.ts`

```typescript
import * as vscode from 'vscode';
import { scaffoldModule } from './commands/scaffoldModule';
import { newModel } from './commands/newModel';
import { extendModel } from './commands/extendModel';
import { generateMigration } from './commands/generateMigration';
import { generateDocs } from './commands/generateDocs';
import { validateOCA } from './commands/validateOCA';
import { deploy } from './commands/deploy';
import { rollback } from './commands/rollback';

export function activate(context: vscode.ExtensionContext) {
    console.log('Odoo Development Automations extension activated');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('odoo.scaffoldModule', scaffoldModule),
        vscode.commands.registerCommand('odoo.newModel', newModel),
        vscode.commands.registerCommand('odoo.extendModel', extendModel),
        vscode.commands.registerCommand('odoo.generateMigration', generateMigration),
        vscode.commands.registerCommand('odoo.generateDocs', generateDocs),
        vscode.commands.registerCommand('odoo.validateOCA', validateOCA),
        vscode.commands.registerCommand('odoo.deploy', deploy),
        vscode.commands.registerCommand('odoo.rollback', rollback)
    );
}

export function deactivate() {
    console.log('Odoo Development Automations extension deactivated');
}
```

---

## 3. Command Implementations

### 3.1 Scaffold Module Command

**File**: `src/commands/scaffoldModule.ts`

```typescript
import * as vscode from 'vscode';
import { executeScript } from '../utils/scriptExecutor';

export async function scaffoldModule() {
    // Collect user input
    const moduleName = await vscode.window.showInputBox({
        prompt: 'Enter module technical name (lowercase, underscores)',
        placeHolder: 'expense_approval',
        validateInput: (value) => {
            if (!/^[a-z][a-z0-9_]*$/.test(value)) {
                return 'Module name must start with lowercase letter and contain only lowercase letters, digits, and underscores';
            }
            return null;
        }
    });

    if (!moduleName) {
        return; // User cancelled
    }

    const description = await vscode.window.showInputBox({
        prompt: 'Enter module description',
        placeHolder: 'Expense approval workflow'
    });

    if (!description) {
        return;
    }

    const modelsInput = await vscode.window.showInputBox({
        prompt: 'Enter models (format: model.name:field1,field2)',
        placeHolder: 'expense.approval:name,amount,state'
    });

    const models = modelsInput ? modelsInput.split(/\s+/) : [];

    const dependsInput = await vscode.window.showInputBox({
        prompt: 'Enter dependencies (space-separated)',
        placeHolder: 'base hr account',
        value: 'base'
    });

    const depends = dependsInput ? dependsInput.split(/\s+/) : ['base'];

    // Build command
    const args = [
        '--name', moduleName,
        '--description', description,
        ...models.flatMap(m => ['--models', m]),
        ...depends.flatMap(d => ['--depends', d])
    ];

    // Execute script
    await executeScript('new_module.py', args, `Scaffolding module ${moduleName}...`);
}
```

---

### 3.2 Validate OCA Command

**File**: `src/commands/validateOCA.ts`

```typescript
import * as vscode from 'vscode';
import { executeCommand } from '../utils/scriptExecutor';

export async function validateOCA() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
    }

    // Show progress
    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Running OCA validation...',
        cancellable: false
    }, async (progress) => {
        progress.report({ message: 'Running pre-commit hooks...' });

        // Execute pre-commit
        const result = await executeCommand('pre-commit', ['run', '--all-files'], workspaceFolder.uri.fsPath);

        if (result.exitCode === 0) {
            vscode.window.showInformationMessage('✅ OCA validation passed');
        } else {
            const outputChannel = vscode.window.createOutputChannel('OCA Validation');
            outputChannel.appendLine(result.stdout);
            outputChannel.appendLine(result.stderr);
            outputChannel.show();

            vscode.window.showErrorMessage('❌ OCA validation failed. See output for details.');
        }
    });
}
```

---

## 4. Utility Functions

### 4.1 Script Executor

**File**: `src/utils/scriptExecutor.ts`

```typescript
import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';

export async function executeScript(
    scriptName: string,
    args: string[],
    progressMessage: string
): Promise<void> {
    const config = vscode.workspace.getConfiguration('odoo');
    const scriptsPath = config.get<string>('scriptsPath');

    if (!scriptsPath) {
        vscode.window.showErrorMessage('Odoo scripts path not configured');
        return;
    }

    const scriptPath = path.join(scriptsPath, scriptName);

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: progressMessage,
        cancellable: false
    }, async (progress) => {
        return new Promise<void>((resolve, reject) => {
            const process = spawn('python3', [scriptPath, ...args], {
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath
            });

            const outputChannel = vscode.window.createOutputChannel('Odoo Scripts');
            outputChannel.show();

            process.stdout.on('data', (data) => {
                outputChannel.appendLine(data.toString());
            });

            process.stderr.on('data', (data) => {
                outputChannel.appendLine(`ERROR: ${data.toString()}`);
            });

            process.on('close', (code) => {
                if (code === 0) {
                    vscode.window.showInformationMessage(`✅ ${progressMessage} completed successfully`);
                    resolve();
                } else {
                    vscode.window.showErrorMessage(`❌ ${progressMessage} failed with code ${code}`);
                    reject(new Error(`Script exited with code ${code}`));
                }
            });
        });
    });
}

export async function executeCommand(
    command: string,
    args: string[],
    cwd: string
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
    return new Promise((resolve) => {
        const process = spawn(command, args, { cwd });

        let stdout = '';
        let stderr = '';

        process.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        process.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        process.on('close', (code) => {
            resolve({
                exitCode: code ?? 1,
                stdout,
                stderr
            });
        });
    });
}
```

---

## 5. Devcontainer Configuration

**File**: `.devcontainer/devcontainer.json`

```json
{
  "name": "Odoo Development",
  "image": "odoo:16.0",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    },
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.flake8",
        "redhat.vscode-xml",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/bin/python3",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "python.analysis.typeCheckingMode": "basic",
        "files.associations": {
          "*.xml": "xml"
        },
        "odoo.scriptsPath": "${containerWorkspaceFolder}/scripts",
        "odoo.outputDirectory": "${containerWorkspaceFolder}/custom_addons"
      }
    }
  },
  "forwardPorts": [8069, 5678],
  "postCreateCommand": "pip install -r requirements.txt && pre-commit install",
  "remoteUser": "odoo"
}
```

**Port Mapping**:
- `8069`: Odoo HTTP server
- `5678`: Python debugger (debugpy)

---

## 6. Command to Script Mapping

| VS Code Command | Script | Arguments | Model |
|----------------|--------|-----------|-------|
| `odoo.scaffoldModule` | `scripts/new_module.py` | `--name`, `--description`, `--models`, `--depends` | DeepSeek v3.1 |
| `odoo.newModel` | `scripts/new_module.py` | `--models` (existing module) | DeepSeek v3.1 |
| `odoo.extendModel` | `scripts/extend_module.py` | `--module`, `--add-field`, `--add-method` | DeepSeek v3.1 |
| `odoo.generateMigration` | `scripts/generate_migration.py` | `--module`, `--from-version`, `--to-version` | DeepSeek v3.1 |
| `odoo.generateDocs` | `scripts/generate_docs.py` | `--module`, `--include-api`, `--format` | DeepSeek v3.1 |
| `odoo.validateOCA` | `pre-commit` | `run --all-files` | N/A |
| `odoo.deploy` | `scripts/deploy.sh` | `--environment`, `--strategy` | Claude Code |
| `odoo.rollback` | `scripts/rollback_deployment.py` | `--to-version`, `--validate-first` | DeepSeek R1 + Claude Code |

---

## 7. Integration with Cline

**Strategy**: VS Code extension invokes scripts directly. Cline skills provide alternative CLI interface.

**Workflow**:
```
User Action (VS Code UI)
    ↓
Extension Command
    ↓
Script Execution (scripts/new_module.py)
    ↓
Template Rendering (Jinja2)
    ↓
File Generation
    ↓
OCA Validation (pre-commit)
    ↓
Success Notification
```

**Alternative Workflow** (Cline CLI):
```
User Input (Cline Chat)
    ↓
Cline Skill (odoo.scaffold)
    ↓
Script Execution (scripts/new_module.py)
    ↓
[Same as above]
```

**Key Insight**: Both workflows use the same automation scripts → **zero duplication**.

---

## 8. Development Workflow

### 8.1 Extension Development

```bash
# Clone repository
git clone https://github.com/your-org/odoo-dev-automations-vscode

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Run extension in debug mode
# Press F5 in VS Code

# Package extension
npx vsce package
```

### 8.2 Testing

```typescript
// src/test/suite/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Odoo Extension Test Suite', () => {
    test('Extension should be activated', async () => {
        const ext = vscode.extensions.getExtension('odoo-expertise.odoo-dev-automations');
        assert.ok(ext);
        await ext?.activate();
        assert.ok(ext?.isActive);
    });

    test('Scaffold Module command should be registered', async () => {
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes('odoo.scaffoldModule'));
    });
});
```

---

## 9. Deployment

### 9.1 VS Code Marketplace

```bash
# Install vsce
npm install -g @vscode/vsce

# Login to publisher account
vsce login odoo-expertise

# Publish extension
vsce publish
```

### 9.2 Private Distribution

```bash
# Package as VSIX
vsce package

# Distribute VSIX file
# Users install: code --install-extension odoo-dev-automations-0.1.0.vsix
```

---

## 10. Benefits of Thin Wrapper Approach

| Aspect | Benefit |
|--------|---------|
| **No Duplication** | All logic in scripts, extension is UI only |
| **Testability** | Scripts tested independently, extension tests minimal |
| **Maintainability** | Single source of truth for automation logic |
| **CLI + GUI** | Same scripts work in Cline CLI and VS Code |
| **Portability** | Scripts work standalone, no VS Code dependency |
| **Flexibility** | Easy to add new commands (just wrap new scripts) |
| **Performance** | Lightweight extension, heavy lifting in Python |

---

## 11. Future Enhancements

### Phase 2 (Optional):
- **IntelliSense**: Odoo model field autocompletion
- **Snippets**: Code snippets for common Odoo patterns
- **Diagnostics**: Real-time OCA validation in editor
- **Debugger**: Odoo debugging configuration
- **WebView**: Visual module builder UI

### Phase 3 (Optional):
- **Odoo.sh Integration**: Direct deployment to Odoo.sh
- **GitHub Integration**: PR creation for module updates
- **Monitoring**: Real-time deployment health in status bar

---

## 12. References

**Existing Assets**:
- `/scripts/new_module.py` - Module generator (Track 1 deliverable)
- `/templates/` - Jinja2 templates (Track 1 deliverable)
- `/.pre-commit-config.yaml` - OCA validation hooks
- `/skills/odoo-module-dev/` - Cline skill

**PRD**:
- Section 2.1: VS Code Extension Requirements
- Section 3.2: Developer Workflow Automation

**VS Code Extension API**:
- [Commands](https://code.visualstudio.com/api/extension-guides/command)
- [QuickPick](https://code.visualstudio.com/api/ux-guidelines/quick-picks)
- [Progress](https://code.visualstudio.com/api/references/vscode-api#Progress)

---

**Status**: Architecture Complete → Ready for Track 2 Implementation

