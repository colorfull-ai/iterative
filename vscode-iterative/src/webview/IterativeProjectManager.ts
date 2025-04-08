import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export class IterativeProjectManager {
    public static currentPanel: IterativeProjectManager | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;

        // Set the webview's initial html content
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'createProject':
                        await this._createProject(message.projectName);
                        return;
                    case 'addFolder':
                        await this._addFolder(message.projectPath, message.folderType);
                        return;
                    case 'getProjects':
                        await this._getProjects();
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public static render(extensionUri: vscode.Uri) {
        if (IterativeProjectManager.currentPanel) {
            // If we already have a panel, show it
            IterativeProjectManager.currentPanel._panel.reveal(vscode.ViewColumn.One);
        } else {
            // Otherwise, create a new panel
            const panel = vscode.window.createWebviewPanel(
                'iterativeProjectManager',
                'Iterative Project Manager',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [
                        vscode.Uri.joinPath(extensionUri, 'media')
                    ]
                }
            );

            IterativeProjectManager.currentPanel = new IterativeProjectManager(panel, extensionUri);
        }
    }

    private async _createProject(projectName: string) {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showErrorMessage('Please open a workspace first');
            return;
        }

        try {
            const workspaceFolder = vscode.workspace.workspaceFolders[0];
            const projectPath = path.join(workspaceFolder.uri.fsPath, projectName);
            const iterativePath = path.join(projectPath, '.iterative');

            fs.mkdirSync(projectPath, { recursive: true });
            fs.mkdirSync(iterativePath);

            await this._panel.webview.postMessage({ 
                command: 'projectCreated', 
                projectPath: projectPath 
            });

            vscode.window.showInformationMessage(`Created project: ${projectName}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create project: ${error}`);
        }
    }

    private async _addFolder(projectPath: string, folderType: string) {
        try {
            const folderPath = path.join(projectPath, folderType);
            fs.mkdirSync(folderPath, { recursive: true });

            await this._panel.webview.postMessage({ 
                command: 'folderAdded', 
                projectPath,
                folderType 
            });

            vscode.window.showInformationMessage(`Added ${folderType} folder`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to add folder: ${error}`);
        }
    }

    private async _getProjects() {
        if (!vscode.workspace.workspaceFolders) {
            return;
        }

        try {
            const projects = [];
            const workspaceFolders = [];

            // Get all workspace folders
            for (const folder of vscode.workspace.workspaceFolders) {
                workspaceFolders.push({
                    name: folder.name,
                    path: folder.uri.fsPath,
                    isIterative: fs.existsSync(path.join(folder.uri.fsPath, '.iterative'))
                });
            }

            // Get iterative projects
            for (const folder of vscode.workspace.workspaceFolders) {
                const items = fs.readdirSync(folder.uri.fsPath);
                for (const item of items) {
                    const itemPath = path.join(folder.uri.fsPath, item);
                    const iterativePath = path.join(itemPath, '.iterative');
                    if (fs.existsSync(iterativePath)) {
                        const folders = fs.readdirSync(itemPath);
                        const apiPath = path.join(itemPath, 'api');
                        let hasValidApiRouter = false;

                        if (fs.existsSync(apiPath)) {
                            const apiFiles = fs.readdirSync(apiPath);
                            hasValidApiRouter = apiFiles.some(file => {
                                if (!file.endsWith('.py')) return false;
                                const content = fs.readFileSync(path.join(apiPath, file), 'utf8');
                                return content.includes('router = APIRouter()') || 
                                       content.includes('router=APIRouter()');
                            });
                        }

                        projects.push({
                            name: item,
                            path: itemPath,
                            folders,
                            hasValidApiRouter
                        });
                    }
                }
            }

            await this._panel.webview.postMessage({ 
                command: 'projectsLoaded', 
                projects,
                workspaceFolders
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load projects: ${error}`);
        }
    }

    private _getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'style.css'));

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iterative Project Manager</title>
            <link href="${styleUri}" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <header class="app-header">
                    <h1>Iterative Project Manager</h1>
                    <div class="workspace-status">
                        <div class="workspace-info">
                            <span class="label">Workspace:</span>
                            <span id="currentWorkspace">No folder selected</span>
                        </div>
                        <div class="selected-folder">
                            <span class="label">Selected:</span>
                            <span id="selectedFolder">No folder selected</span>
                        </div>
                    </div>
                </header>

                <div class="tab-container">
                    <div class="tab-header">
                        <button class="tab-button active" data-tab="projects">Projects</button>
                        <button class="tab-button" data-tab="structure">Structure</button>
                        <button class="tab-button" data-tab="settings">Settings</button>
                    </div>

                    <div class="tab-content active" id="projects-tab">
                        <div class="projects-header">
                            <div class="projects-dropdown">
                                <select id="projectSelect">
                                    <option value="">Select an Iterative Project</option>
                                </select>
                            </div>
                            <button id="convertButton" style="display: none;">Convert to Iterative</button>
                        </div>

                        <div class="folder-status-grid">
                            <div class="folder-status-card" id="apiStatus">
                                <h3>API</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="serviceStatus">
                                <h3>Service</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="modelsStatus">
                                <h3>Models</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="actionsStatus">
                                <h3>Actions</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                        </div>

                        <div class="project-actions">
                            <button id="startServerBtn" disabled>Start Server</button>
                            <button id="openInEditorBtn" disabled>Open in Editor</button>
                        </div>
                    </div>

                    <div class="tab-content" id="structure-tab">
                        <div class="folder-types">
                            <div class="folder-card" onclick="addFolder('api')">
                                <h3>API</h3>
                                <p>REST API endpoints with FastAPI router (requires a Python file with 'router = APIRouter()')</p>
                                <span class="folder-status">Optional</span>
                            </div>
                            <div class="folder-card" onclick="addFolder('service')">
                                <h3>Service</h3>
                                <p>Business logic and service layer implementations</p>
                                <span class="folder-status">Optional</span>
                            </div>
                            <div class="folder-card" onclick="addFolder('models')">
                                <h3>Models</h3>
                                <p>Data models and database schemas</p>
                                <span class="folder-status">Optional</span>
                            </div>
                            <div class="folder-card" onclick="addFolder('actions')">
                                <h3>Actions</h3>
                                <p>Automated tasks and background jobs</p>
                                <span class="folder-status">Optional</span>
                            </div>
                        </div>
                    </div>

                    <div class="tab-content" id="settings-tab">
                        <div class="settings-form">
                            <div class="setting-group">
                                <h3>Project Settings</h3>
                                <label>
                                    <input type="checkbox" id="autoStartServer">
                                    Auto-start server on project open
                                </label>
                                <label>
                                    <input type="checkbox" id="validateApiRouter">
                                    Validate API router on save
                                </label>
                            </div>
                            <div class="setting-group">
                                <h3>Server Settings</h3>
                                <label>
                                    Port
                                    <input type="number" id="serverPort" value="8000">
                                </label>
                                <label>
                                    Host
                                    <input type="text" id="serverHost" value="127.0.0.1">
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="${scriptUri}"></script>
        </body>
        </html>`;
    }

    public dispose() {
        IterativeProjectManager.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
} 