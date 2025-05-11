import React, { useState, useEffect, useRef } from 'react';
import '../styles/Terminal.css';

interface TerminalProps {
  initialCommand?: string;
  onCommandExecute?: (command: string) => Promise<string>;
}

const Terminal: React.FC<TerminalProps> = ({ initialCommand = '', onCommandExecute }) => {
  const [history, setHistory] = useState<string[]>([]);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [currentCommand, setCurrentCommand] = useState(initialCommand);
  const [isProcessing, setIsProcessing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Terminal welcome message
  useEffect(() => {
    setHistory([
      'SoulCoreHub Terminal v1.0.0',
      'Type "help" for available commands',
      ''
    ]);
  }, []);

  // Auto-scroll to bottom when history changes
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input when terminal is clicked
  const focusInput = () => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Handle command execution
  const executeCommand = async (command: string) => {
    if (!command.trim()) return;

    // Add command to history
    setHistory(prev => [...prev, `$ ${command}`]);
    setCommandHistory(prev => [command, ...prev.slice(0, 49)]);
    setHistoryIndex(-1);
    setCurrentCommand('');
    setIsProcessing(true);

    try {
      let response: string;

      // Built-in commands
      if (command === 'clear') {
        setHistory([]);
        setIsProcessing(false);
        return;
      } else if (command === 'help') {
        response = [
          'Available commands:',
          '  help          - Show this help message',
          '  clear         - Clear the terminal',
          '  agent <name>  - Interact with an agent',
          '  status        - Show system status',
          '  version       - Show version information',
          '  exit          - Exit the terminal'
        ].join('\n');
      } else if (command === 'version') {
        response = 'SoulCoreHub v1.0.0';
      } else if (command === 'exit') {
        response = 'Closing terminal...';
        setTimeout(() => {
          window.close();
        }, 1000);
      } else if (onCommandExecute) {
        // Custom command handler
        response = await onCommandExecute(command);
      } else {
        response = `Command not found: ${command}`;
      }

      // Add response to history
      setHistory(prev => [...prev, response, '']);
    } catch (error) {
      setHistory(prev => [...prev, `Error: ${error instanceof Error ? error.message : String(error)}`, '']);
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle key press events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      executeCommand(currentCommand);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
        setHistoryIndex(newIndex);
        setCurrentCommand(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setCurrentCommand(commandHistory[newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCurrentCommand('');
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // Implement command auto-completion here
    }
  };

  return (
    <div className="terminal" onClick={focusInput} ref={terminalRef}>
      <div className="terminal-header">
        <div className="terminal-buttons">
          <div className="terminal-button close"></div>
          <div className="terminal-button minimize"></div>
          <div className="terminal-button maximize"></div>
        </div>
        <div className="terminal-title">SoulCoreHub Terminal</div>
      </div>
      <div className="terminal-content">
        {history.map((line, index) => (
          <div key={index} className="terminal-line">
            {line}
          </div>
        ))}
        <div className="terminal-input-line">
          <span className="terminal-prompt">$</span>
          <input
            ref={inputRef}
            type="text"
            className="terminal-input"
            value={currentCommand}
            onChange={(e) => setCurrentCommand(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
            disabled={isProcessing}
          />
          {isProcessing && <div className="terminal-spinner"></div>}
        </div>
      </div>
    </div>
  );
};

export default Terminal;
