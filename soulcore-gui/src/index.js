const { contextBridge, ipcRenderer } = require('electron');

// This exposes Node.js command access to the frontend safely
contextBridge.exposeInMainWorld('electronAPI', {
  runCommand: (cmd) => ipcRenderer.invoke('run-command', cmd)
});
