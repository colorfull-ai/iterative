// Get VS Code API
const vscode = acquireVsCodeApi();

let selectedProject = null;
let selectedWorkspaceFolder = null;

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    updateProjectsList();
    setupEventListeners();
});

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update active tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

function setupEventListeners() {
    // Project selection change
    const projectSelect = document.getElementById('projectSelect');
    projectSelect.addEventListener('change', (e) => {
        selectedProject = e.target.value;
        updateFolderStatus(selectedProject);
        updateButtonStates();
    });

    // Server start button
    document.getElementById('startServerBtn').addEventListener('click', () => {
        if (selectedProject) {
            startServer(selectedProject);
        }
    });

    // Open in editor button
    document.getElementById('openInEditorBtn').addEventListener('click', () => {
        if (selectedProject) {
            vscode.postMessage({
                command: 'openInEditor',
                projectPath: selectedProject
            });
        }
    });

    // Convert button
    const convertButton = document.getElementById('convertButton');
    if (convertButton) {
        convertButton.addEventListener('click', convertToIterative);
    }

    // Settings checkboxes
    const hideNonIterativeFoldersCheckbox = document.getElementById('hideNonIterativeFolders');
    if (hideNonIterativeFoldersCheckbox) {
        hideNonIterativeFoldersCheckbox.addEventListener('change', (e) => {
            vscode.postMessage({
                command: 'updateSetting',
                settingName: 'hideNonIterativeFolders',
                value: e.target.checked
            });
        });
    }

    // Other settings form elements
    document.querySelectorAll('.settings-form input:not(#hideNonIterativeFolders)').forEach(input => {
        input.addEventListener('change', (e) => {
            vscode.postMessage({
                command: 'updateSetting',
                settingName: e.target.id,
                value: e.target.type === 'checkbox' ? e.target.checked : e.target.value
            });
        });
    });
}

function updateProjectsList() {
    vscode.postMessage({
        command: 'getProjects'
    });
}

function updateFolderStatus(projectPath) {
    if (!projectPath) {
        resetFolderStatus();
        return;
    }

    const folders = ['api', 'service', 'models', 'actions'];
    folders.forEach(folder => {
        const statusCard = document.getElementById(`${folder}Status`);
        const indicator = statusCard.querySelector('.status-indicator');
        const statusText = statusCard.querySelector('.status-text');

        vscode.postMessage({
            command: 'checkFolder',
            projectPath,
            folderType: folder
        });
    });
}

function resetFolderStatus() {
    const folders = ['api', 'service', 'models', 'actions'];
    folders.forEach(folder => {
        const statusCard = document.getElementById(`${folder}Status`);
        const indicator = statusCard.querySelector('.status-indicator');
        const statusText = statusCard.querySelector('.status-text');

        indicator.className = 'status-indicator';
        statusText.textContent = 'Not Found';
    });
}

function updateButtonStates() {
    const startServerBtn = document.getElementById('startServerBtn');
    const openInEditorBtn = document.getElementById('openInEditorBtn');
    const convertButton = document.getElementById('convertButton');

    startServerBtn.disabled = !selectedProject;
    openInEditorBtn.disabled = !selectedProject;
    convertButton.style.display = selectedWorkspaceFolder && !isIterativeProject(selectedWorkspaceFolder) ? 'block' : 'none';
}

function isIterativeProject(folderPath) {
    // This will be checked by the extension
    return false;
}

// Handle messages from the extension
window.addEventListener('message', event => {
    const message = event.data;
    switch (message.command) {
        case 'projectsLoaded':
            updateWorkspaceInfo(message.workspaceFolders);
            updateProjectsDropdown(message.projects);
            break;
        case 'folderStatus':
            updateFolderStatusIndicator(message.folder, message.exists, message.isValid);
            break;
        case 'selectedFolderChanged':
            updateSelectedFolder(message.folder);
            break;
        case 'notification':
            showNotification(message.text, message.type);
            break;
    }
});

function updateWorkspaceInfo(workspaceFolders) {
    const currentWorkspace = document.getElementById('currentWorkspace');
    if (workspaceFolders && workspaceFolders.length > 0) {
        currentWorkspace.textContent = workspaceFolders[0].name;
    }
}

function updateSelectedFolder(folder) {
    const selectedFolderElement = document.getElementById('selectedFolder');
    selectedFolderElement.textContent = folder ? folder.name : 'No folder selected';
    selectedWorkspaceFolder = folder ? folder.path : null;
    updateButtonStates();
}

function updateProjectsDropdown(projects) {
    const select = document.getElementById('projectSelect');
    select.innerHTML = '<option value="">Select an Iterative Project</option>';
    
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.path;
        option.textContent = project.name;
        select.appendChild(option);
    });

    if (selectedProject) {
        select.value = selectedProject;
        updateFolderStatus(selectedProject);
    }
}

function updateFolderStatusIndicator(folder, exists, isValid) {
    const statusCard = document.getElementById(`${folder}Status`);
    const indicator = statusCard.querySelector('.status-indicator');
    const statusText = statusCard.querySelector('.status-text');

    indicator.className = 'status-indicator';
    if (exists) {
        indicator.classList.add(isValid ? 'found' : 'missing');
        statusText.textContent = isValid ? 'Valid' : 'Invalid';
    } else {
        indicator.classList.add('missing');
        statusText.textContent = 'Not Found';
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function convertToIterative() {
    if (!selectedWorkspaceFolder) {
        showNotification('Please select a folder to convert', 'error');
        return;
    }

    vscode.postMessage({
        command: 'convertToIterative',
        folderPath: selectedWorkspaceFolder
    });
}

function startServer(projectPath) {
    vscode.postMessage({
        command: 'startServer',
        projectPath: projectPath
    });
}

function addFolder(folderType) {
    if (!selectedProject) {
        showNotification('Please select a project first', 'error');
        return;
    }

    vscode.postMessage({
        command: 'addFolder',
        folderType: folderType,
        projectPath: selectedProject
    });
}

function displayWorkspaceFolders(folders) {
    const foldersList = document.getElementById('workspaceFoldersList');
    foldersList.innerHTML = '';

    folders.forEach(folder => {
        const folderElement = document.createElement('div');
        folderElement.className = `folder-card${folder.isIterative ? ' iterative' : ''}`;
        folderElement.onclick = () => {
            selectedWorkspaceFolder = folder.path;
            document.querySelectorAll('.folder-card').forEach(el => {
                el.classList.remove('selected');
            });
            folderElement.classList.add('selected');
            
            // Show/hide convert notice
            const convertNotice = document.getElementById('convertNotice');
            convertNotice.style.display = folder.isIterative ? 'none' : 'block';
        };

        folderElement.innerHTML = `
            <h3>${folder.name}</h3>
            <p>${folder.path}</p>
            ${folder.isIterative ? '<span class="folder-status">Iterative Project</span>' : ''}
        `;

        foldersList.appendChild(folderElement);
    });
}

function displayProjects(projects) {
    const projectsList = document.getElementById('projectsList');
    projectsList.innerHTML = '';

    projects.forEach(project => {
        const projectElement = document.createElement('div');
        projectElement.className = 'project-item';
        projectElement.onclick = () => {
            selectedProject = project.path;
            document.querySelectorAll('.project-item').forEach(el => {
                el.classList.remove('selected');
            });
            projectElement.classList.add('selected');
        };

        const foldersHtml = project.folders
            .filter(folder => folder !== '.iterative')
            .map(folder => {
                const isValid = folder !== 'api' || project.hasValidApiRouter;
                return `<span class="folder-tag${isValid ? '' : ' invalid'}">${folder}</span>`;
            })
            .join('');

        projectElement.innerHTML = `
            <h3>${project.name}</h3>
            <div class="project-folders">
                ${foldersHtml}
            </div>
            <div class="project-actions">
                <button onclick="startServer('${project.path}')">Start Server</button>
            </div>
        `;

        projectsList.appendChild(projectElement);
    });
} 