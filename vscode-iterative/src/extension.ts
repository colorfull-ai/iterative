import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface IconTheme {
    iconDefinitions: { [key: string]: any };
    folderNames: { [key: string]: string };
    folderNamesExpanded: { [key: string]: string };
    light?: {
        folderNames: { [key: string]: string };
        folderNamesExpanded: { [key: string]: string };
    };
}

interface IterativeProject {
    parentPath: string;
    parentName: string;
    iterativePath: string;
}

function findIterativeProjects(workspaceFolders: readonly vscode.WorkspaceFolder[]): IterativeProject[] {
    const projects: IterativeProject[] = [];
    
    for (const folder of workspaceFolders) {
        const basePath = folder.uri.fsPath;
        try {
            const items = fs.readdirSync(basePath);
            for (const item of items) {
                const itemPath = path.join(basePath, item);
                const iterativePath = path.join(itemPath, '.iterative');
                if (fs.existsSync(iterativePath)) {
                    projects.push({
                        parentPath: itemPath,
                        parentName: item,
                        iterativePath: iterativePath
                    });
                }
            }
        } catch (err) {
            console.error(`Error reading directory ${basePath}:`, err);
        }
    }
    return projects;
}

async function updateIconThemeForProjects(projects: IterativeProject[]) {
    console.log('Starting icon theme update...');
    const iconThemePath = path.join(__dirname, '..', 'resources', 'iterative-icon-theme.json');
    console.log(`Icon theme path: ${iconThemePath}`);
    let iconTheme: IconTheme;
    
    try {
        console.log('Reading icon theme file...');
        const themeContent = fs.readFileSync(iconThemePath, 'utf8');
        iconTheme = JSON.parse(themeContent);

        // Reset to empty mappings
        console.log('Resetting folder mappings...');
        iconTheme.folderNames = {};
        iconTheme.folderNamesExpanded = {};
        if (iconTheme.light) {
            iconTheme.light.folderNames = {};
            iconTheme.light.folderNamesExpanded = {};
        }

        // Process each iterative project
        console.log(`Processing ${projects.length} iterative projects...`);
        for (const project of projects) {
            console.log(`Processing project: ${project.parentName}`);
            
            // Set parent folder icon
            iconTheme.folderNames[project.parentName] = "_iterative_project";
            iconTheme.folderNamesExpanded[project.parentName] = "_iterative_project";
            
            // Set standard folder icons within this project
            try {
                const items = fs.readdirSync(project.parentPath);
                for (const item of items) {
                    const fullPath = path.join(project.parentPath, item);
                    const relativePath = path.relative(project.parentPath, fullPath);
                    
                    if (item === 'api') {
                        iconTheme.folderNames[`${project.parentName}/api`] = "_api_folder";
                        iconTheme.folderNamesExpanded[`${project.parentName}/api`] = "_api_folder";
                    } else if (item === 'service' || item === 'services') {
                        iconTheme.folderNames[`${project.parentName}/${item}`] = "_service_folder";
                        iconTheme.folderNamesExpanded[`${project.parentName}/${item}`] = "_service_folder";
                    } else if (item === 'models') {
                        iconTheme.folderNames[`${project.parentName}/models`] = "_models_folder";
                        iconTheme.folderNamesExpanded[`${project.parentName}/models`] = "_models_folder";
                    } else if (item === '.iterative') {
                        iconTheme.folderNames[`${project.parentName}/.iterative`] = "_iterative_folder";
                        iconTheme.folderNamesExpanded[`${project.parentName}/.iterative`] = "_iterative_folder";
                    }
                }
            } catch (err) {
                console.error(`Error reading project directory ${project.parentPath}:`, err);
            }
        }

        // Apply the same mappings to light theme if it exists
        if (iconTheme.light) {
            iconTheme.light.folderNames = { ...iconTheme.folderNames };
            iconTheme.light.folderNamesExpanded = { ...iconTheme.folderNamesExpanded };
        }

        console.log('Final icon mappings:', iconTheme.folderNames);
        console.log('Writing updated theme back to disk...');
        fs.writeFileSync(iconThemePath, JSON.stringify(iconTheme, null, 2));
        console.log('Icon theme update complete');
    } catch (error) {
        console.error('Error updating icon theme:', error);
        if (error instanceof Error) {
            console.error('Error details:', error.message);
            console.error('Stack trace:', error.stack);
        }
    }
}

async function setIterativeIconTheme() {
    console.log('Setting iterative icon theme...');
    try {
        const config = vscode.workspace.getConfiguration();
        const currentTheme = config.get('workbench.iconTheme');
        console.log(`Current icon theme: ${currentTheme}`);
        
        if (currentTheme !== 'iterative-icons') {
            await config.update('workbench.iconTheme', 'iterative-icons', vscode.ConfigurationTarget.Workspace);
            console.log('Icon theme updated to iterative-icons');
            
            // Instead of forcing a reload, show a message with reload option
            const action = await vscode.window.showInformationMessage(
                'Icon theme updated. Reload window to apply changes?',
                'Reload Window'
            );
            
            if (action === 'Reload Window') {
                await vscode.commands.executeCommand('workbench.action.reloadWindow');
            }
        }
    } catch (error) {
        console.error('Error setting icon theme:', error);
        // Don't rethrow - allow the extension to continue working
    }
}

async function checkAndSetIconTheme() {
    if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
        console.log('No workspace folders open');
        return;
    }

    try {
        // Log workspace information
        console.log('Workspace folders:');
        vscode.workspace.workspaceFolders.forEach(folder => {
            console.log(`- ${folder.name}: ${folder.uri.fsPath}`);
        });

        // Find iterative projects using direct filesystem search
        const projects = findIterativeProjects(vscode.workspace.workspaceFolders);
        
        if (projects.length > 0) {
            console.log(`Found ${projects.length} iterative projects:`, 
                projects.map(p => `${p.parentName} (${p.parentPath})`));
            await updateIconThemeForProjects(projects);
            await setIterativeIconTheme();
        } else {
            console.log('No iterative projects found');
        }
    } catch (error) {
        console.error('Error checking for iterative projects:', error);
        if (error instanceof Error) {
            console.error('Error details:', error.message);
            console.error('Stack trace:', error.stack);
        }
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Iterative extension is now active!');
    console.log('Extension path:', context.extensionPath);

    // Track active file changes
    let activeEditor = vscode.window.activeTextEditor;
    let lastSelectedFolder: string | undefined;

    vscode.window.onDidChangeActiveTextEditor(editor => {
        activeEditor = editor;
        if (editor) {
            const filePath = editor.document.uri.fsPath;
            const folderPath = path.dirname(filePath);
            if (folderPath !== lastSelectedFolder) {
                lastSelectedFolder = folderPath;
                if (IterativeProjectManager.currentPanel) {
                    IterativeProjectManager.currentPanel.updateSelectedFolder(folderPath);
                }
            }
        }
    }, null, context.subscriptions);

    // Track explorer selection changes
    vscode.window.onDidChangeWindowState(e => {
        const selection = vscode.window.activeTextEditor?.document.uri;
        if (selection) {
            const folderPath = path.dirname(selection.fsPath);
            if (folderPath !== lastSelectedFolder) {
                lastSelectedFolder = folderPath;
                if (IterativeProjectManager.currentPanel) {
                    IterativeProjectManager.currentPanel.updateSelectedFolder(folderPath);
                }
            }
        }
    }, null, context.subscriptions);

    // Track workspace folder changes
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
        if (IterativeProjectManager.currentPanel) {
            IterativeProjectManager.currentPanel.refresh();
        }
    }, null, context.subscriptions);

    // Initial check for .iterative folders
    checkAndSetIconTheme();

    // Set up file system watcher for .iterative folders and related folders
    const iterativeWatcher = vscode.workspace.createFileSystemWatcher('**/.iterative');
    const apiWatcher = vscode.workspace.createFileSystemWatcher('**/api');
    const serviceWatcher = vscode.workspace.createFileSystemWatcher('**/service');
    const servicesWatcher = vscode.workspace.createFileSystemWatcher('**/services');
    const modelsWatcher = vscode.workspace.createFileSystemWatcher('**/models');
    
    // Register commands
    let openManager = vscode.commands.registerCommand('iterative.openManager', () => {
        IterativeProjectManager.render(context.extensionUri);
    });

    let createProject = vscode.commands.registerCommand('iterative.createProject', async () => {
        IterativeProjectManager.render(context.extensionUri);
    });

    // Handle the creation of .iterative folders
    iterativeWatcher.onDidCreate(async (uri) => {
        console.log('New .iterative folder detected:', uri.fsPath);
        const parentDir = path.dirname(uri.fsPath);
        const parentName = path.basename(parentDir);
        const projects = [{
            parentPath: parentDir,
            parentName: parentName,
            iterativePath: uri.fsPath
        }];
        await updateIconThemeForProjects(projects);
        await setIterativeIconTheme();
        vscode.window.showInformationMessage(`Iterative project detected in ${parentName}! Icons updated.`);
    });

    // Handle the deletion of .iterative folders
    iterativeWatcher.onDidDelete(async (uri) => {
        console.log('.iterative folder deleted:', uri.fsPath);
        if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
            return;
        }

        try {
            const projects = findIterativeProjects(vscode.workspace.workspaceFolders);
            console.log(`Remaining iterative projects: ${projects.length}`);
            if (projects.length === 0) {
                console.log('No more iterative projects, resetting icon theme');
                await vscode.workspace.getConfiguration().update('workbench.iconTheme', undefined, vscode.ConfigurationTarget.Workspace);
            } else {
                await updateIconThemeForProjects(projects);
            }
            await vscode.commands.executeCommand('workbench.action.reloadWindow');
        } catch (error) {
            console.error('Error handling .iterative folder deletion:', error);
        }
    });

    let manageProject = vscode.commands.registerCommand('vscode-iterative.manageProject', async () => {
        if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders[0];
        const iterativePath = path.join(workspaceFolder.uri.fsPath, '.iterative');
        if (!fs.existsSync(iterativePath)) {
            vscode.window.showErrorMessage('Not an iterative project');
            return;
        }

        // TODO: Implement project management features
        vscode.window.showInformationMessage('Managing iterative project...');
    });

    // Register the command to manually update icons
    let disposable = vscode.commands.registerCommand('iterative.updateIcons', async () => {
        if (!vscode.workspace.workspaceFolders || vscode.workspace.workspaceFolders.length === 0) {
            vscode.window.showWarningMessage('No workspace folders open.');
            return;
        }

        try {
            const projects = findIterativeProjects(vscode.workspace.workspaceFolders);
            await updateIconThemeForProjects(projects);
            await setIterativeIconTheme();
            vscode.window.showInformationMessage('Iterative project icons updated!');
        } catch (error) {
            console.error('Error updating icons:', error);
            vscode.window.showErrorMessage('Failed to update Iterative project icons.');
        }
    });

    // Register convert to iterative command
    let convertToIterative = vscode.commands.registerCommand('iterative.convertToIterative', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('Please select a folder to convert');
            return;
        }

        try {
            const iterativePath = path.join(uri.fsPath, '.iterative');
            if (fs.existsSync(iterativePath)) {
                vscode.window.showInformationMessage('This folder is already an Iterative project');
                return;
            }

            fs.mkdirSync(iterativePath);
            const projects = [{
                parentPath: uri.fsPath,
                parentName: path.basename(uri.fsPath),
                iterativePath: iterativePath
            }];
            await updateIconThemeForProjects(projects);
            await setIterativeIconTheme();
            vscode.window.showInformationMessage(`Successfully converted ${path.basename(uri.fsPath)} to an Iterative project`);

            if (IterativeProjectManager.currentPanel) {
                IterativeProjectManager.currentPanel.refresh();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to convert folder: ${error}`);
        }
    });

    // Register create API file command
    let createApiFile = vscode.commands.registerCommand('iterative.createApiFile', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('Please select an api folder');
            return;
        }

        try {
            // Get the name for the new API file
            const fileName = await vscode.window.showInputBox({
                prompt: 'Enter the name for your API resource (e.g., users, products)',
                placeHolder: 'resource_name'
            });

            if (!fileName) {
                return; // User cancelled
            }

            const apiFilePath = path.join(uri.fsPath, `${fileName}.py`);
            
            // Simple API endpoints template
            const apiTemplate = `from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.post("/${fileName}")
async def create_${fileName}(data: dict):
    return {"message": "Created ${fileName}", "data": data}

@router.get("/${fileName}")
async def read_${fileName}s():
    return {"message": "List all ${fileName}s"}

@router.get("/${fileName}/{${fileName}_id}")
async def read_${fileName}(${fileName}_id: int):
    return {"message": f"Get ${fileName} {${fileName}_id}"}

@router.put("/${fileName}/{${fileName}_id}")
async def update_${fileName}(${fileName}_id: int, data: dict):
    return {"message": f"Update ${fileName} {${fileName}_id}", "data": data}

@router.delete("/${fileName}/{${fileName}_id}")
async def delete_${fileName}(${fileName}_id: int):
    return {"message": f"Delete ${fileName} {${fileName}_id}"}
`;

            fs.writeFileSync(apiFilePath, apiTemplate);
            
            // Open the new file in the editor
            const document = await vscode.workspace.openTextDocument(apiFilePath);
            await vscode.window.showTextDocument(document);

            vscode.window.showInformationMessage(`Created new API file: ${fileName}.py`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create API file: ${error}`);
        }
    });

    // Register create model file command
    let createModelFile = vscode.commands.registerCommand('iterative.createModelFile', async (uri: vscode.Uri) => {
        if (!uri) {
            vscode.window.showErrorMessage('Please select a models folder');
            return;
        }

        try {
            // Get the name for the new model file
            const modelName = await vscode.window.showInputBox({
                prompt: 'Enter the name for your model (e.g., user, product)',
                placeHolder: 'model_name'
            });

            if (!modelName) {
                return; // User cancelled
            }

            const modelFilePath = path.join(uri.fsPath, `${modelName}.py`);
            
            // Simple model template
            const modelTemplate = `from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ${modelName.charAt(0).toUpperCase() + modelName.slice(1)}Base(BaseModel):
    """Base ${modelName} model with common fields."""
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

class ${modelName.charAt(0).toUpperCase() + modelName.slice(1)}Create(${modelName.charAt(0).toUpperCase() + modelName.slice(1)}Base):
    """${modelName} creation model."""
    pass

class ${modelName.charAt(0).toUpperCase() + modelName.slice(1)}(${modelName.charAt(0).toUpperCase() + modelName.slice(1)}Base):
    """${modelName} model with ID."""
    id: int

    class Config:
        orm_mode = True
`;

            fs.writeFileSync(modelFilePath, modelTemplate);
            
            // Open the new file in the editor
            const document = await vscode.workspace.openTextDocument(modelFilePath);
            await vscode.window.showTextDocument(document);

            vscode.window.showInformationMessage(`Created new model file: ${modelName}.py`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create model file: ${error}`);
        }
    });

    // Register focus mode command
    let focusMode = vscode.commands.registerCommand('iterative.focusMode', async () => {
        if (!vscode.workspace.workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folders open');
            return;
        }

        try {
            const projects = findIterativeProjects(vscode.workspace.workspaceFolders);
            if (projects.length === 0) {
                vscode.window.showInformationMessage('No Iterative projects found in workspace');
                return;
            }

            // Create QuickPick for project selection
            const quickPick = vscode.window.createQuickPick();
            quickPick.items = projects.map(project => ({
                label: project.parentName,
                description: project.parentPath
            }));
            quickPick.placeholder = 'Select an Iterative project to focus';

            quickPick.onDidChangeSelection(async ([item]) => {
                if (item && item.description) {
                    // Set workspace to only show the selected project
                    const uri = vscode.Uri.file(item.description);
                    await vscode.commands.executeCommand('vscode.openFolder', uri, {
                        forceNewWindow: false
                    });
                    vscode.window.showInformationMessage(`Focused on project: ${item.label}`);
                }
                quickPick.dispose();
            });

            quickPick.onDidHide(() => quickPick.dispose());
            quickPick.show();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to enter focus mode: ${error}`);
        }
    });

    context.subscriptions.push(
        createProject,
        openManager,
        manageProject,
        convertToIterative,
        createApiFile,
        createModelFile,
        focusMode,
        iterativeWatcher,
        apiWatcher,
        serviceWatcher,
        servicesWatcher,
        modelsWatcher,
        disposable
    );
}

export function deactivate() {} 

export class IterativeProjectManager {
    public static currentPanel: IterativeProjectManager | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

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

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;

        // Set the webview's initial html content
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);

        // Listen for when the panel is disposed
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
                    case 'checkFolder':
                        await this._checkFolder(message.projectPath, message.folderType);
                        return;
                    case 'startServer':
                        await this._startServer(message.projectPath);
                        return;
                    case 'openInEditor':
                        await this._openInEditor(message.projectPath);
                        return;
                    case 'updateSetting':
                        await this._updateSetting(message.settingName, message.value);
                        return;
                }
            },
            null,
            this._disposables
        );
    }

    public updateSelectedFolder(folderPath: string) {
        this._panel.webview.postMessage({
            command: 'selectedFolderChanged',
            folder: {
                name: path.basename(folderPath),
                path: folderPath,
                isIterative: fs.existsSync(path.join(folderPath, '.iterative'))
            }
        });
    }

    public refresh() {
        this._getProjects();
    }

    private async _checkFolder(projectPath: string, folderType: string) {
        try {
            const folderPath = path.join(projectPath, folderType);
            const exists = fs.existsSync(folderPath);
            let isValid = exists;

            if (exists && folderType === 'api') {
                const apiFiles = fs.readdirSync(folderPath);
                isValid = apiFiles.some(file => {
                    if (!file.endsWith('.py')) return false;
                    const content = fs.readFileSync(path.join(folderPath, file), 'utf8');
                    return content.includes('router = APIRouter()') || 
                           content.includes('router=APIRouter()');
                });
            }

            await this._panel.webview.postMessage({
                command: 'folderStatus',
                folder: folderType,
                exists,
                isValid
            });
        } catch (error) {
            console.error(`Error checking folder status: ${error}`);
        }
    }

    private async _startServer(projectPath: string) {
        try {
            // Implementation for starting the server
            vscode.window.showInformationMessage(`Starting server for ${projectPath}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start server: ${error}`);
        }
    }

    private async _openInEditor(projectPath: string) {
        try {
            const uri = vscode.Uri.file(projectPath);
            await vscode.commands.executeCommand('vscode.openFolder', uri);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open in editor: ${error}`);
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

    private async _updateSetting(settingName: string, value: any) {
        try {
            switch (settingName) {
                case 'hideNonIterativeFolders':
                    await vscode.workspace.getConfiguration('iterative').update('hideNonIterativeFolders', value, vscode.ConfigurationTarget.Global);
                    break;
                // Handle other settings here
                default:
                    console.log(`Setting ${settingName} not recognized`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update setting: ${error}`);
        }
    }

    private _getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'main.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'style.css'));
        const codiconsUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'codicon.css'));

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iterative Project Manager</title>
            <link href="${styleUri}" rel="stylesheet">
            <link href="${codiconsUri}" rel="stylesheet">
            <link href="https://unpkg.com/lucide-static@latest/font/lucide.css" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <header class="app-header">
                    <h1><i class="lucide-git-branch"></i> Iterative Project Manager</h1>
                    <div class="workspace-status">
                        <div class="workspace-info">
                            <i class="lucide-folder"></i>
                            <span class="label">Workspace:</span>
                            <span id="currentWorkspace">No folder selected</span>
                        </div>
                    </div>
                </header>

                <div class="tab-container">
                    <div class="tab-header">
                        <button class="tab-button active" data-tab="projects">
                            <i class="lucide-layers"></i> Projects
                        </button>
                        <button class="tab-button" data-tab="structure">
                            <i class="lucide-folder-tree"></i> Structure
                        </button>
                        <button class="tab-button" data-tab="settings">
                            <i class="lucide-settings"></i> Settings
                        </button>
                    </div>

                    <div class="tab-content active" id="projects-tab">
                        <div class="projects-header">
                            <div class="projects-dropdown">
                                <select id="projectSelect">
                                    <option value="">Select an Iterative Project</option>
                                </select>
                            </div>
                            <button id="convertButton" class="primary-button" style="display: none;">
                                <i class="lucide-plus-circle"></i> Convert to Iterative
                            </button>
                        </div>

                        <div class="folder-status-grid">
                            <div class="folder-status-card" id="apiStatus">
                                <i class="lucide-globe"></i>
                                <h3>API</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="serviceStatus">
                                <i class="lucide-settings"></i>
                                <h3>Service</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="modelsStatus">
                                <i class="lucide-database"></i>
                                <h3>Models</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                            <div class="folder-status-card" id="actionsStatus">
                                <i class="lucide-play"></i>
                                <h3>Actions</h3>
                                <div class="status-indicator"></div>
                                <p class="status-text">Not Found</p>
                            </div>
                        </div>

                        <div class="project-actions">
                            <button id="startServerBtn" disabled>
                                <i class="lucide-play"></i> Start Server
                            </button>
                            <button id="openInEditorBtn" disabled>
                                <i class="lucide-edit"></i> Open in Editor
                            </button>
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
                                <label>
                                    <input type="checkbox" id="hideNonIterativeFolders">
                                    Hide non-iterative folders in workspace
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
            <script>
                document.getElementById('hideNonIterativeFolders').addEventListener('change', (e) => {
                    const value = e.target.checked;
                    vscode.postMessage({
                        command: 'updateSetting',
                        settingName: 'hideNonIterativeFolders',
                        value: value
                    });
                });
            </script>
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