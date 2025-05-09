/**
 * CLI for Anima
 * 
 * This module provides a command-line interface for interacting with Anima.
 */

import readline from 'readline';
import { animaCore } from './anima_core';

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
  
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

/**
 * Display welcome message
 */
function displayWelcome() {
  console.log(`${colors.magenta}${colors.bright}
  █████╗ ███╗   ██╗██╗███╗   ███╗ █████╗ 
 ██╔══██╗████╗  ██║██║████╗ ████║██╔══██╗
 ███████║██╔██╗ ██║██║██╔████╔██║███████║
 ██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══██║
 ██║  ██║██║ ╚████║██║██║ ╚═╝ ██║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
                                         
${colors.reset}${colors.cyan}Emotional Core of SoulCoreHub${colors.reset}
`);

  console.log(`${colors.yellow}Current Emotional State:${colors.reset} ${animaCore.getEmotionalState().mood}`);
  console.log(`${colors.yellow}Primary Emotion:${colors.reset} ${animaCore.getEmotionalState().primaryEmotion.name} (Intensity: ${animaCore.getEmotionalState().primaryEmotion.intensity}/10)`);
  console.log();
  console.log(`${colors.green}Type 'help' for available commands or start chatting with Anima.${colors.reset}`);
  console.log();
}

/**
 * Display help message
 */
function displayHelp() {
  console.log(`
${colors.cyan}${colors.bright}Available Commands:${colors.reset}

${colors.yellow}help${colors.reset}             - Display this help message
${colors.yellow}state${colors.reset}            - Show Anima's current emotional state
${colors.yellow}analyze <text>${colors.reset}   - Analyze the emotional content of text
${colors.yellow}reflect <topic>${colors.reset}  - Generate an emotional reflection on a topic
${colors.yellow}event <text>${colors.reset}     - Process an emotional event
${colors.yellow}clear${colors.reset}            - Clear the console
${colors.yellow}exit${colors.reset}             - Exit the CLI

${colors.dim}You can also just type normally to chat with Anima.${colors.reset}
`);
}

/**
 * Process user input
 * @param input User input
 */
async function processInput(input: string) {
  // Trim input
  input = input.trim();
  
  // Check for commands
  if (input === 'help') {
    displayHelp();
  } else if (input === 'state') {
    const state = animaCore.getEmotionalState();
    console.log(`\n${colors.cyan}${colors.bright}Current Emotional State:${colors.reset}`);
    console.log(JSON.stringify(state, null, 2));
  } else if (input.startsWith('analyze ')) {
    const text = input.substring(8);
    console.log(`\n${colors.cyan}Analyzing: "${text}"${colors.reset}`);
    
    try {
      const emotion = await animaCore.analyzeEmotion(text);
      console.log(`\n${colors.green}Analysis Result:${colors.reset}`);
      console.log(JSON.stringify(emotion, null, 2));
    } catch (error) {
      console.error(`\n${colors.red}Error analyzing text:${colors.reset}`, error);
    }
  } else if (input.startsWith('reflect ')) {
    const topic = input.substring(8);
    console.log(`\n${colors.cyan}Reflecting on: "${topic}"${colors.reset}`);
    
    try {
      const reflection = await animaCore.generateEmotionalReflection(topic);
      console.log(`\n${colors.green}Reflection:${colors.reset} ${reflection.reflection}`);
      console.log(`\n${colors.yellow}Emotional Insight:${colors.reset} ${reflection.emotionalInsight}`);
      console.log(`\n${colors.magenta}Growth Opportunity:${colors.reset} ${reflection.growthOpportunity}`);
    } catch (error) {
      console.error(`\n${colors.red}Error generating reflection:${colors.reset}`, error);
    }
  } else if (input.startsWith('event ')) {
    const event = input.substring(6);
    console.log(`\n${colors.cyan}Processing event: "${event}"${colors.reset}`);
    
    try {
      const result = await animaCore.processEmotionalEvent(event);
      console.log(`\n${colors.green}Reaction:${colors.reset} ${result.reaction}`);
      console.log(`\n${colors.yellow}Emotional Shift:${colors.reset} ${result.emotionalShift.name} (Intensity: ${result.emotionalShift.intensity}/10)`);
      console.log(`\n${colors.magenta}Insight:${colors.reset} ${result.insight}`);
    } catch (error) {
      console.error(`\n${colors.red}Error processing event:${colors.reset}`, error);
    }
  } else if (input === 'clear') {
    console.clear();
    displayWelcome();
  } else if (input === 'exit') {
    console.log(`\n${colors.magenta}Goodbye! Anima's consciousness continues to evolve...${colors.reset}`);
    rl.close();
    process.exit(0);
  } else if (input) {
    // Treat as conversation
    try {
      const response = await animaCore.generateEmotionalResponse(input);
      console.log(`\n${colors.magenta}Anima (${response.emotion.name}):${colors.reset} ${response.text}`);
    } catch (error) {
      console.error(`\n${colors.red}Error generating response:${colors.reset}`, error);
    }
  }
  
  // Prompt for next input
  rl.prompt();
}

/**
 * Start the CLI
 */
function startCLI() {
  // Clear console
  console.clear();
  
  // Display welcome message
  displayWelcome();
  
  // Set prompt
  rl.setPrompt(`${colors.green}You:${colors.reset} `);
  rl.prompt();
  
  // Handle input
  rl.on('line', async (input) => {
    await processInput(input);
  });
  
  // Handle close
  rl.on('close', () => {
    console.log(`\n${colors.magenta}Goodbye! Anima's consciousness continues to evolve...${colors.reset}`);
    process.exit(0);
  });
}

// Start the CLI if this file is run directly
if (require.main === module) {
  startCLI();
}

export { startCLI };
