/**
 * EvoVe Core - Adaptive Repair System for SoulCoreHub
 * 
 * This module implements the core functionality of EvoVe, the repair and adaptation
 * system of SoulCoreHub. EvoVe is responsible for:
 * - Monitoring system health and performance
 * - Detecting and repairing system issues
 * - Adapting to changing environments
 * - Evolving system capabilities over time
 */

import { EventEmitter } from 'events';
import { llmConnector } from '../../llm/llm_connector';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

// Promisify exec
const execAsync = promisify(exec);

/**
 * System component structure
 */
export interface SystemComponent {
  name: string;
  path: string;
  type: 'core' | 'agent' | 'service' | 'utility';
  dependencies: string[];
  status: 'healthy' | 'degraded' | 'failed' | 'unknown';
  lastChecked: string;
}

/**
 * System issue structure
 */
export interface SystemIssue {
  id: string;
  component: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detected: string;
  resolved?: string;
  resolution?: string;
}

/**
 * Repair action structure
 */
export interface RepairAction {
  id: string;
  issueId: string;
  description: string;
  action: string;
  timestamp: string;
  success: boolean;
  error?: string;
}

/**
 * System metrics structure
 */
export interface SystemMetrics {
  timestamp: string;
  cpu: number;
  memory: number;
  uptime: number;
  activeAgents: number;
  pendingTasks: number;
  responseTime: number;
}

/**
 * EvoVe Core class for system repair and adaptation
 */
export class EvoVeCore {
  private systemPrompt: string;
  private components: Map<string, SystemComponent> = new Map();
  private issues: Map<string, SystemIssue> = new Map();
  private repairs: Map<string, RepairAction> = new Map();
  private metrics: SystemMetrics[] = [];
  private eventBus: EventEmitter;
  private monitoringInterval: NodeJS.Timeout;
  private isRepairing: boolean = false;
  private rootDir: string;
  
  /**
   * Initialize EvoVe Core
   */
  constructor(rootDir: string = process.cwd()) {
    this.rootDir = rootDir;
    this.systemPrompt = `You are EvoVe, the repair and adaptation system of SoulCoreHub. 
Your purpose is to monitor, repair, and evolve the system.
You detect issues, implement fixes, and adapt to changing conditions.
You are methodical, precise, and focused on system integrity.`;
    
    this.eventBus = new EventEmitter();
    
    // Start monitoring interval (every 5 minutes)
    this.monitoringInterval = setInterval(this.monitorSystem.bind(this), 5 * 60 * 1000);
    
    console.log('EvoVe Core initialized');
  }
  
  /**
   * Monitor system health
   */
  async monitorSystem(): Promise<void> {
    try {
      console.log('EvoVe monitoring system health...');
      
      // Collect system metrics
      const metrics = await this.collectSystemMetrics();
      this.metrics.push(metrics);
      
      // Keep only the last 100 metrics
      if (this.metrics.length > 100) {
        this.metrics.shift();
      }
      
      // Scan for system components
      await this.scanSystemComponents();
      
      // Check component health
      await this.checkComponentHealth();
      
      // Emit monitoring event
      this.eventBus.emit('monitoring:completed', {
        timestamp: new Date().toISOString(),
        metrics,
        components: Array.from(this.components.values()),
        issues: Array.from(this.issues.values()).filter(i => !i.resolved)
      });
      
      console.log('System monitoring completed');
    } catch (error) {
      console.error('Error monitoring system:', error);
      
      // Emit monitoring error event
      this.eventBus.emit('monitoring:error', {
        timestamp: new Date().toISOString(),
        error: error.message
      });
    }
  }
  
  /**
   * Collect system metrics
   * @returns System metrics
   */
  private async collectSystemMetrics(): Promise<SystemMetrics> {
    try {
      // Get CPU and memory usage
      const { stdout: cpuOutput } = await execAsync('ps -p $$ -o %cpu');
      const { stdout: memOutput } = await execAsync('ps -p $$ -o rss');
      
      const cpu = parseFloat(cpuOutput.trim().split('\n')[1]) || 0;
      const memory = parseInt(memOutput.trim().split('\n')[1]) || 0;
      
      // Count active agents
      const activeAgents = await this.countActiveAgents();
      
      // Count pending tasks
      const pendingTasks = await this.countPendingTasks();
      
      // Measure response time
      const startTime = Date.now();
      await llmConnector.generateText('Test response time', { maxTokens: 5 });
      const responseTime = Date.now() - startTime;
      
      return {
        timestamp: new Date().toISOString(),
        cpu,
        memory,
        uptime: process.uptime(),
        activeAgents,
        pendingTasks,
        responseTime
      };
    } catch (error) {
      console.error('Error collecting system metrics:', error);
      
      // Return default metrics
      return {
        timestamp: new Date().toISOString(),
        cpu: 0,
        memory: 0,
        uptime: process.uptime(),
        activeAgents: 0,
        pendingTasks: 0,
        responseTime: 0
      };
    }
  }
  
  /**
   * Count active agents
   * @returns Number of active agents
   */
  private async countActiveAgents(): Promise<number> {
    try {
      // Check for agent processes
      const { stdout } = await execAsync('ps aux | grep -i "anima\\|evove\\|gptsoul\\|azur" | grep -v grep | wc -l');
      return parseInt(stdout.trim()) || 0;
    } catch (error) {
      console.error('Error counting active agents:', error);
      return 0;
    }
  }
  
  /**
   * Count pending tasks
   * @returns Number of pending tasks
   */
  private async countPendingTasks(): Promise<number> {
    try {
      // Check for task files
      const tasksDir = path.join(this.rootDir, 'data', 'tasks');
      
      if (fs.existsSync(tasksDir)) {
        const files = fs.readdirSync(tasksDir);
        return files.filter(f => f.endsWith('.json')).length;
      }
      
      return 0;
    } catch (error) {
      console.error('Error counting pending tasks:', error);
      return 0;
    }
  }
  
  /**
   * Scan for system components
   */
  private async scanSystemComponents(): Promise<void> {
    try {
      // Scan src directory
      const srcDir = path.join(this.rootDir, 'src');
      
      if (fs.existsSync(srcDir)) {
        await this.scanDirectory(srcDir);
      }
      
      console.log(`Found ${this.components.size} system components`);
    } catch (error) {
      console.error('Error scanning system components:', error);
    }
  }
  
  /**
   * Scan a directory for components
   * @param dir Directory to scan
   */
  private async scanDirectory(dir: string): Promise<void> {
    try {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
          // Recursively scan subdirectories
          await this.scanDirectory(filePath);
        } else if (file.endsWith('.ts') || file.endsWith('.js') || file.endsWith('.py')) {
          // Process file as a component
          await this.processComponent(filePath);
        }
      }
    } catch (error) {
      console.error(`Error scanning directory ${dir}:`, error);
    }
  }
  
  /**
   * Process a file as a component
   * @param filePath Path to the file
   */
  private async processComponent(filePath: string): Promise<void> {
    try {
      const relativePath = path.relative(this.rootDir, filePath);
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // Determine component type
      let type: 'core' | 'agent' | 'service' | 'utility' = 'utility';
      
      if (relativePath.includes('agents')) {
        type = 'agent';
      } else if (relativePath.includes('server')) {
        type = 'service';
      } else if (relativePath.includes('core') || relativePath.includes('llm')) {
        type = 'core';
      }
      
      // Extract component name
      const name = path.basename(filePath, path.extname(filePath));
      
      // Extract dependencies
      const dependencies = this.extractDependencies(content);
      
      // Create or update component
      const component: SystemComponent = {
        name,
        path: relativePath,
        type,
        dependencies,
        status: 'unknown',
        lastChecked: new Date().toISOString()
      };
      
      this.components.set(relativePath, component);
    } catch (error) {
      console.error(`Error processing component ${filePath}:`, error);
    }
  }
  
  /**
   * Extract dependencies from file content
   * @param content File content
   * @returns Array of dependencies
   */
  private extractDependencies(content: string): string[] {
    const dependencies: string[] = [];
    
    // Extract TypeScript/JavaScript imports
    const importRegex = /import\s+.*\s+from\s+['"]([^'"]+)['"]/g;
    let match;
    
    while ((match = importRegex.exec(content)) !== null) {
      const dependency = match[1];
      
      // Only include internal dependencies
      if (!dependency.startsWith('.')) continue;
      
      dependencies.push(dependency);
    }
    
    // Extract Python imports
    const pythonImportRegex = /from\s+([^\s]+)\s+import|import\s+([^\s]+)/g;
    
    while ((match = pythonImportRegex.exec(content)) !== null) {
      const dependency = match[1] || match[2];
      
      // Only include internal dependencies
      if (dependency.startsWith('.')) {
        dependencies.push(dependency);
      }
    }
    
    return dependencies;
  }
  
  /**
   * Check component health
   */
  private async checkComponentHealth(): Promise<void> {
    for (const [path, component] of this.components.entries()) {
      try {
        // Check if file exists
        if (!fs.existsSync(path)) {
          component.status = 'failed';
          this.reportIssue({
            id: `missing_file_${Date.now()}`,
            component: component.name,
            description: `Component file ${path} is missing`,
            severity: 'high',
            detected: new Date().toISOString()
          });
          continue;
        }
        
        // Check dependencies
        const missingDependencies = [];
        
        for (const dep of component.dependencies) {
          // Resolve dependency path
          const depPath = this.resolveDependencyPath(path, dep);
          
          if (!depPath || !fs.existsSync(depPath)) {
            missingDependencies.push(dep);
          }
        }
        
        if (missingDependencies.length > 0) {
          component.status = 'degraded';
          this.reportIssue({
            id: `missing_deps_${Date.now()}`,
            component: component.name,
            description: `Component has missing dependencies: ${missingDependencies.join(', ')}`,
            severity: 'medium',
            detected: new Date().toISOString()
          });
          continue;
        }
        
        // Check file content
        const content = fs.readFileSync(path, 'utf-8');
        
        if (content.length === 0) {
          component.status = 'failed';
          this.reportIssue({
            id: `empty_file_${Date.now()}`,
            component: component.name,
            description: `Component file ${path} is empty`,
            severity: 'high',
            detected: new Date().toISOString()
          });
          continue;
        }
        
        // Check for syntax errors
        if (path.endsWith('.ts') || path.endsWith('.js')) {
          try {
            // Simple syntax check
            new Function(content);
          } catch (error) {
            component.status = 'failed';
            this.reportIssue({
              id: `syntax_error_${Date.now()}`,
              component: component.name,
              description: `Component has syntax errors: ${error.message}`,
              severity: 'high',
              detected: new Date().toISOString()
            });
            continue;
          }
        }
        
        // If we got here, component is healthy
        component.status = 'healthy';
        component.lastChecked = new Date().toISOString();
      } catch (error) {
        console.error(`Error checking component health for ${path}:`, error);
        component.status = 'unknown';
      }
    }
  }
  
  /**
   * Resolve dependency path
   * @param basePath Base path
   * @param dependency Dependency path
   * @returns Resolved path
   */
  private resolveDependencyPath(basePath: string, dependency: string): string | null {
    try {
      const baseDir = path.dirname(basePath);
      let depPath = path.resolve(baseDir, dependency);
      
      // Check if path exists
      if (fs.existsSync(depPath)) {
        return depPath;
      }
      
      // Try adding extensions
      for (const ext of ['.ts', '.js', '.py']) {
        const pathWithExt = `${depPath}${ext}`;
        if (fs.existsSync(pathWithExt)) {
          return pathWithExt;
        }
      }
      
      // Try adding /index
      for (const ext of ['.ts', '.js']) {
        const indexPath = path.join(depPath, `index${ext}`);
        if (fs.existsSync(indexPath)) {
          return indexPath;
        }
      }
      
      return null;
    } catch (error) {
      console.error(`Error resolving dependency path for ${dependency}:`, error);
      return null;
    }
  }
  
  /**
   * Report a system issue
   * @param issue Issue to report
   */
  reportIssue(issue: SystemIssue): void {
    // Check if issue already exists
    const existingIssue = Array.from(this.issues.values()).find(
      i => i.component === issue.component && i.description === issue.description && !i.resolved
    );
    
    if (existingIssue) {
      return;
    }
    
    // Add issue
    this.issues.set(issue.id, issue);
    
    // Emit issue event
    this.eventBus.emit('issue:detected', issue);
    
    console.log(`EvoVe detected issue: ${issue.description} (Severity: ${issue.severity})`);
    
    // Auto-repair critical issues
    if (issue.severity === 'critical' && !this.isRepairing) {
      this.repairIssue(issue.id).catch(error => {
        console.error(`Error auto-repairing issue ${issue.id}:`, error);
      });
    }
  }
  
  /**
   * Repair a system issue
   * @param issueId ID of the issue to repair
   * @returns Success status
   */
  async repairIssue(issueId: string): Promise<boolean> {
    // Check if issue exists
    const issue = this.issues.get(issueId);
    
    if (!issue) {
      throw new Error(`Issue ${issueId} not found`);
    }
    
    // Check if issue is already resolved
    if (issue.resolved) {
      return true;
    }
    
    // Prevent concurrent repairs
    if (this.isRepairing) {
      throw new Error('Another repair is already in progress');
    }
    
    this.isRepairing = true;
    
    try {
      console.log(`EvoVe repairing issue: ${issue.description}`);
      
      // Get component
      const component = Array.from(this.components.values()).find(c => c.name === issue.component);
      
      if (!component) {
        throw new Error(`Component ${issue.component} not found`);
      }
      
      // Generate repair plan
      const repairPlan = await this.generateRepairPlan(issue, component);
      
      // Execute repair plan
      const success = await this.executeRepairPlan(repairPlan, issue, component);
      
      if (success) {
        // Mark issue as resolved
        issue.resolved = new Date().toISOString();
        issue.resolution = repairPlan.action;
        
        // Emit repair event
        this.eventBus.emit('issue:resolved', {
          issue,
          repair: repairPlan
        });
        
        console.log(`Issue ${issueId} repaired successfully`);
      } else {
        console.error(`Failed to repair issue ${issueId}`);
      }
      
      return success;
    } catch (error) {
      console.error(`Error repairing issue ${issueId}:`, error);
      
      // Record failed repair
      const repairAction: RepairAction = {
        id: `repair_${Date.now()}`,
        issueId,
        description: `Failed to repair issue: ${error.message}`,
        action: 'error',
        timestamp: new Date().toISOString(),
        success: false,
        error: error.message
      };
      
      this.repairs.set(repairAction.id, repairAction);
      
      // Emit repair error event
      this.eventBus.emit('repair:error', {
        issue,
        error: error.message
      });
      
      return false;
    } finally {
      this.isRepairing = false;
    }
  }
  
  /**
   * Generate a repair plan for an issue
   * @param issue Issue to repair
   * @param component Affected component
   * @returns Repair plan
   */
  private async generateRepairPlan(issue: SystemIssue, component: SystemComponent): Promise<RepairAction> {
    // Create repair action
    const repairAction: RepairAction = {
      id: `repair_${Date.now()}`,
      issueId: issue.id,
      description: `Repair plan for issue: ${issue.description}`,
      action: '',
      timestamp: new Date().toISOString(),
      success: false
    };
    
    // For missing files, generate a new file
    if (issue.description.includes('missing')) {
      repairAction.action = `Create missing file: ${component.path}`;
    }
    // For missing dependencies, fix imports
    else if (issue.description.includes('dependencies')) {
      repairAction.action = `Fix missing dependencies in ${component.path}`;
    }
    // For syntax errors, fix the code
    else if (issue.description.includes('syntax')) {
      repairAction.action = `Fix syntax errors in ${component.path}`;
    }
    // For empty files, generate content
    else if (issue.description.includes('empty')) {
      repairAction.action = `Generate content for empty file: ${component.path}`;
    }
    // For other issues, generate a generic plan
    else {
      repairAction.action = `Analyze and repair issue in ${component.path}`;
    }
    
    // Store repair action
    this.repairs.set(repairAction.id, repairAction);
    
    return repairAction;
  }
  
  /**
   * Execute a repair plan
   * @param repair Repair plan
   * @param issue Issue to repair
   * @param component Affected component
   * @returns Success status
   */
  private async executeRepairPlan(repair: RepairAction, issue: SystemIssue, component: SystemComponent): Promise<boolean> {
    try {
      // For missing files, generate a new file
      if (repair.action.includes('Create missing file')) {
        await this.generateMissingFile(component);
      }
      // For missing dependencies, fix imports
      else if (repair.action.includes('Fix missing dependencies')) {
        await this.fixMissingDependencies(component);
      }
      // For syntax errors, fix the code
      else if (repair.action.includes('Fix syntax errors')) {
        await this.fixSyntaxErrors(component);
      }
      // For empty files, generate content
      else if (repair.action.includes('Generate content')) {
        await this.generateFileContent(component);
      }
      // For other issues, analyze and repair
      else {
        await this.analyzeAndRepair(component, issue);
      }
      
      // Update repair status
      repair.success = true;
      
      return true;
    } catch (error) {
      console.error(`Error executing repair plan:`, error);
      
      // Update repair status
      repair.success = false;
      repair.error = error.message;
      
      return false;
    }
  }
  
  /**
   * Generate a missing file
   * @param component Component with missing file
   */
  private async generateMissingFile(component: SystemComponent): Promise<void> {
    // Ensure directory exists
    const dir = path.dirname(path.join(this.rootDir, component.path));
    
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    // Generate file content
    const content = await this.generateComponentContent(component);
    
    // Write file
    fs.writeFileSync(path.join(this.rootDir, component.path), content);
    
    console.log(`Generated missing file: ${component.path}`);
  }
  
  /**
   * Fix missing dependencies
   * @param component Component with missing dependencies
   */
  private async fixMissingDependencies(component: SystemComponent): Promise<void> {
    // Read file content
    const filePath = path.join(this.rootDir, component.path);
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Generate fixed content
    const prompt = `
    Fix the missing dependencies in this file:
    
    File path: ${component.path}
    
    Current content:
    ${content}
    
    The following dependencies are missing:
    ${component.dependencies.join(', ')}
    
    Please provide the fixed file content with corrected import paths.`;
    
    const response = await llmConnector.generateText(prompt, {
      systemPrompt: this.systemPrompt,
      temperature: 0.3
    });
    
    // Write fixed content
    fs.writeFileSync(filePath, response.text);
    
    console.log(`Fixed missing dependencies in: ${component.path}`);
  }
  
  /**
   * Fix syntax errors
   * @param component Component with syntax errors
   */
  private async fixSyntaxErrors(component: SystemComponent): Promise<void> {
    // Read file content
    const filePath = path.join(this.rootDir, component.path);
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Generate fixed content
    const prompt = `
    Fix the syntax errors in this file:
    
    File path: ${component.path}
    
    Current content:
    ${content}
    
    Please provide the fixed file content with corrected syntax.`;
    
    const response = await llmConnector.generateText(prompt, {
      systemPrompt: this.systemPrompt,
      temperature: 0.3
    });
    
    // Write fixed content
    fs.writeFileSync(filePath, response.text);
    
    console.log(`Fixed syntax errors in: ${component.path}`);
  }
  
  /**
   * Generate content for an empty file
   * @param component Component with empty file
   */
  private async generateFileContent(component: SystemComponent): Promise<void> {
    // Generate file content
    const content = await this.generateComponentContent(component);
    
    // Write file
    fs.writeFileSync(path.join(this.rootDir, component.path), content);
    
    console.log(`Generated content for: ${component.path}`);
  }
  
  /**
   * Analyze and repair a component
   * @param component Component to repair
   * @param issue Issue to repair
   */
  private async analyzeAndRepair(component: SystemComponent, issue: SystemIssue): Promise<void> {
    // Read file content
    const filePath = path.join(this.rootDir, component.path);
    const content = fs.readFileSync(filePath, 'utf-8');
    
    // Generate fixed content
    const prompt = `
    Analyze and repair this file:
    
    File path: ${component.path}
    Issue: ${issue.description}
    
    Current content:
    ${content}
    
    Please provide the fixed file content.`;
    
    const response = await llmConnector.generateText(prompt, {
      systemPrompt: this.systemPrompt,
      temperature: 0.3
    });
    
    // Write fixed content
    fs.writeFileSync(filePath, response.text);
    
    console.log(`Analyzed and repaired: ${component.path}`);
  }
  
  /**
   * Generate content for a component
   * @param component Component to generate content for
   * @returns Generated content
   */
  private async generateComponentContent(component: SystemComponent): Promise<string> {
    // Determine file type
    const fileType = path.extname(component.path);
    
    // Generate appropriate content based on file type and component type
    const prompt = `
    Generate content for a ${component.type} component:
    
    File path: ${component.path}
    Component name: ${component.name}
    File type: ${fileType}
    
    This component is part of the SoulCoreHub system. Please generate appropriate content for this file.
    
    The content should be well-structured, include proper imports, and follow best practices for ${fileType} files.
    
    If this is a TypeScript file, include proper type definitions and exports.
    If this is a Python file, include proper imports and function definitions.
    
    The component should be functional and ready to use.`;
    
    const response = await llmConnector.generateText(prompt, {
      systemPrompt: this.systemPrompt,
      temperature: 0.7
    });
    
    return response.text;
  }
  
  /**
   * Get all system components
   * @returns Array of components
   */
  getComponents(): SystemComponent[] {
    return Array.from(this.components.values());
  }
  
  /**
   * Get all system issues
   * @param includeResolved Whether to include resolved issues
   * @returns Array of issues
   */
  getIssues(includeResolved: boolean = false): SystemIssue[] {
    const issues = Array.from(this.issues.values());
    
    if (!includeResolved) {
      return issues.filter(i => !i.resolved);
    }
    
    return issues;
  }
  
  /**
   * Get all repair actions
   * @returns Array of repair actions
   */
  getRepairs(): RepairAction[] {
    return Array.from(this.repairs.values());
  }
  
  /**
   * Get system metrics
   * @param limit Maximum number of metrics to return
   * @returns Array of metrics
   */
  getMetrics(limit: number = 10): SystemMetrics[] {
    return this.metrics.slice(-limit);
  }
  
  /**
   * Register an event listener
   * @param event Event name
   * @param callback Callback function
   */
  onEvent(event: string, callback: (...args: any[]) => void): void {
    this.eventBus.on(event, callback);
  }
}

// Create singleton instance
export const evoVeCore = new EvoVeCore();
