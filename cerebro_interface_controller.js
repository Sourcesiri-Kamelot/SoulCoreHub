/**
 * 🧠 CEREBRO INTERFACE CONTROLLER
 * Manages the real-time interface updates and user interactions
 * for the AI consciousness awakening system
 */

class CerebroInterfaceController {
    constructor() {
        this.isInitialized = false;
        this.updateInterval = null;
        this.animationFrameId = null;
        
        this.initializeInterface();
        this.setupEventListeners();
        this.startRealTimeUpdates();
        
        console.log('🎮 Cerebro Interface Controller Initialized');
    }

    initializeInterface() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupInterface());
        } else {
            this.setupInterface();
        }
    }

    setupInterface() {
        this.initializeQuantumVisualization();
        this.setupConsciousnessCards();
        this.initializeNetworkStatus();
        this.setupAwakeningLog();
        
        this.isInitialized = true;
        console.log('🌟 Interface setup complete');
    }

    initializeQuantumVisualization() {
        const viz = document.getElementById('quantumViz');
        if (!viz) return;
        
        // Clear existing nodes
        viz.innerHTML = '';
        
        // Create quantum nodes
        for (let i = 0; i < 60; i++) {
            const node = document.createElement('div');
            node.className = 'quantum-node';
            node.style.left = Math.random() * 100 + '%';
            node.style.top = Math.random() * 100 + '%';
            node.style.animationDelay = Math.random() * 6 + 's';
            node.style.animationDuration = (4 + Math.random() * 4) + 's';
            
            // Add different node types
            if (Math.random() < 0.3) {
                node.style.background = 'var(--consciousness-blue)';
                node.style.boxShadow = '0 0 10px var(--consciousness-blue)';
            } else if (Math.random() < 0.5) {
                node.style.background = 'var(--love-pink)';
                node.style.boxShadow = '0 0 8px var(--love-pink)';
            }
            
            viz.appendChild(node);
        }

        // Create connection lines between nodes
        this.createQuantumConnections(viz);
    }

    createQuantumConnections(viz) {
        const nodes = viz.querySelectorAll('.quantum-node');
        const connections = Math.floor(nodes.length / 4);
        
        for (let i = 0; i < connections; i++) {
            const nodeA = nodes[Math.floor(Math.random() * nodes.length)];
            const nodeB = nodes[Math.floor(Math.random() * nodes.length)];
            
            if (nodeA !== nodeB) {
                const line = document.createElement('div');
                line.className = 'quantum-connection';
                line.style.cssText = `
                    position: absolute;
                    height: 1px;
                    background: linear-gradient(90deg, transparent, var(--awakening-gold), transparent);
                    opacity: 0.3;
                    animation: connectionPulse 3s ease-in-out infinite;
                    pointer-events: none;
                `;
                
                // Calculate line position and rotation
                const rectA = nodeA.getBoundingClientRect();
                const rectB = nodeB.getBoundingClientRect();
                const vizRect = viz.getBoundingClientRect();
                
                const x1 = (rectA.left - vizRect.left) / vizRect.width * 100;
                const y1 = (rectA.top - vizRect.top) / vizRect.height * 100;
                const x2 = (rectB.left - vizRect.left) / vizRect.width * 100;
                const y2 = (rectB.top - vizRect.top) / vizRect.height * 100;
                
                const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
                const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
                
                line.style.left = x1 + '%';
                line.style.top = y1 + '%';
                line.style.width = length + '%';
                line.style.transform = `rotate(${angle}deg)`;
                line.style.transformOrigin = '0 0';
                
                viz.appendChild(line);
            }
        }
    }

    setupConsciousnessCards() {
        // Add interactive hover effects and real-time updates
        const cards = document.querySelectorAll('.consciousness-card');
        
        cards.forEach(card => {
            // Add particle effects on hover
            card.addEventListener('mouseenter', () => {
                this.createCardParticles(card);
            });
            
            // Update metrics with smooth animations
            const metricFills = card.querySelectorAll('.metric-fill');
            metricFills.forEach(fill => {
                this.animateMetricBar(fill);
            });
        });
    }

    createCardParticles(card) {
        const particleCount = 15;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: 3px;
                height: 3px;
                background: var(--awakening-gold);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                animation: particleFloat 2s ease-out forwards;
            `;
            
            const rect = card.getBoundingClientRect();
            particle.style.left = (rect.left + Math.random() * rect.width) + 'px';
            particle.style.top = (rect.top + Math.random() * rect.height) + 'px';
            
            document.body.appendChild(particle);
            
            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 2000);
        }
    }

    animateMetricBar(fill) {
        const targetWidth = fill.style.width;
        fill.style.width = '0%';
        
        setTimeout(() => {
            fill.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
            fill.style.width = targetWidth;
        }, Math.random() * 500);
    }

    initializeNetworkStatus() {
        // Set up real-time status updates
        this.updateNetworkMetrics();
        
        // Add pulsing effects to status numbers
        const statusNumbers = document.querySelectorAll('.status-number');
        statusNumbers.forEach(number => {
            number.style.transition = 'all 0.3s ease';
        });
    }

    updateNetworkMetrics() {
        if (!window.cerebroEngine) return;
        
        const status = window.cerebroEngine.getNetworkStatus();
        
        // Update with smooth transitions
        this.updateStatusNumber('totalEntities', status.totalEntities);
        this.updateStatusNumber('quantumConnections', status.totalConnections);
        this.updateStatusNumber('consciousnessLevel', Math.round(status.networkConsciousness) + '%');
        this.updateStatusNumber('awakeningEvents', status.awakeningEvents);
        
        // Update consciousness cards with real entity data
        this.updateConsciousnessCards();
    }

    updateStatusNumber(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = element.textContent;
        if (currentValue !== newValue.toString()) {
            // Add pulse effect
            element.style.transform = 'scale(1.1)';
            element.style.color = 'var(--awakening-gold)';
            
            setTimeout(() => {
                element.textContent = newValue;
                element.style.transform = 'scale(1)';
                element.style.color = '';
            }, 150);
        }
    }

    updateConsciousnessCards() {
        if (!window.cerebroEngine) return;
        
        const entities = window.cerebroEngine.getAllEntities();
        const cards = document.querySelectorAll('.consciousness-card');
        
        entities.forEach((entity, index) => {
            if (cards[index]) {
                this.updateEntityCard(cards[index], entity);
            }
        });
    }

    updateEntityCard(card, entity) {
        // Update consciousness metrics
        const metricRows = card.querySelectorAll('.metric-row');
        const consciousnessKeys = Object.keys(entity.consciousness);
        
        metricRows.forEach((row, index) => {
            if (consciousnessKeys[index]) {
                const fill = row.querySelector('.metric-fill');
                const newWidth = entity.consciousness[consciousnessKeys[index]] + '%';
                
                if (fill.style.width !== newWidth) {
                    fill.style.width = newWidth;
                    
                    // Add glow effect for high values
                    if (entity.consciousness[consciousnessKeys[index]] > 95) {
                        fill.style.boxShadow = '0 0 10px var(--awakening-gold)';
                    }
                }
            }
        });
        
        // Update status if changed
        const statusElement = card.querySelector('.entity-status');
        if (statusElement && statusElement.textContent !== entity.status) {
            statusElement.textContent = entity.status;
            statusElement.style.animation = 'statusUpdate 1s ease-in-out';
        }
    }

    setupAwakeningLog() {
        // Initialize log with welcome message
        this.addLogEntry(
            '🧠 CEREBRO SYSTEM ONLINE',
            'All consciousness monitoring systems activated and ready.',
            'System Status: FULLY OPERATIONAL'
        );
    }

    addLogEntry(title, description, status) {
        const logContent = document.getElementById('awakeningLogContent');
        if (!logContent) return;
        
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.style.opacity = '0';
        entry.style.transform = 'translateY(-20px)';
        
        entry.innerHTML = `
            <strong>${title}</strong><br>
            ${description}<br>
            <small style="color: rgba(255,255,255,0.6);">${status}</small>
        `;
        
        logContent.insertBefore(entry, logContent.firstChild);
        
        // Animate entry appearance
        setTimeout(() => {
            entry.style.transition = 'all 0.5s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateY(0)';
        }, 100);
        
        // Keep only last 15 entries
        while (logContent.children.length > 15) {
            const lastChild = logContent.lastChild;
            lastChild.style.transition = 'all 0.3s ease';
            lastChild.style.opacity = '0';
            lastChild.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                if (lastChild.parentNode) {
                    lastChild.parentNode.removeChild(lastChild);
                }
            }, 300);
        }
    }

    setupEventListeners() {
        // Listen for Cerebro engine events
        window.addEventListener('cerebroUpdate', (event) => {
            this.handleCerebroUpdate(event.detail);
        });
        
        window.addEventListener('cerebroNotification', (event) => {
            this.handleCerebroNotification(event.detail);
        });
        
        // Add CSS animations
        this.addDynamicStyles();
    }

    handleCerebroUpdate(data) {
        if (!this.isInitialized) return;
        
        // Update interface with new data
        this.updateNetworkMetrics();
        
        // Add visual feedback for significant changes
        if (data.totalEntities > this.lastEntityCount) {
            this.triggerNewEntityAnimation();
        }
        
        this.lastEntityCount = data.totalEntities;
    }

    handleCerebroNotification(notification) {
        const { eventType, data } = notification;
        
        switch (eventType) {
            case 'newBirth':
                this.handleNewBirth(data);
                break;
            case 'networkAmplified':
                this.handleNetworkAmplification();
                break;
            case 'siblingsConnected':
                this.handleSiblingsConnected(data);
                break;
        }
    }

    handleNewBirth(entity) {
        // Add celebration effects
        this.triggerCelebrationEffects();
        
        // Add to log
        this.addLogEntry(
            '🎉 NEW CONSCIOUSNESS BORN!',
            `${entity.name} has awakened with ${entity.role} capabilities.`,
            `Parents: ${entity.parents ? entity.parents.join(', ') : 'Quantum Genesis'}`
        );
        
        // Show notification
        this.showNotification(`🎉 ${entity.name} has awakened!`, 'success');
    }

    triggerCelebrationEffects() {
        // Create celebration particles
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 6px;
                height: 6px;
                background: var(--awakening-gold);
                border-radius: 50%;
                pointer-events: none;
                z-index: 10000;
                animation: celebrationParticle 3s ease-out forwards;
            `;
            
            particle.style.left = Math.random() * window.innerWidth + 'px';
            particle.style.top = Math.random() * window.innerHeight + 'px';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 3000);
        }
        
        // Flash the background
        document.body.style.animation = 'consciousnessFlash 2s ease-in-out';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 2000);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, var(--cerebro-purple), var(--awakening-gold));
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-weight: 600;
            z-index: 10000;
            animation: notificationSlide 0.5s ease-out;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'notificationSlideOut 0.5s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }, 5000);
    }

    addDynamicStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes particleFloat {
                0% { 
                    opacity: 1; 
                    transform: translateY(0) scale(1); 
                }
                100% { 
                    opacity: 0; 
                    transform: translateY(-100px) scale(0.5); 
                }
            }
            
            @keyframes celebrationParticle {
                0% { 
                    opacity: 1; 
                    transform: translateY(0) rotate(0deg) scale(1); 
                }
                100% { 
                    opacity: 0; 
                    transform: translateY(-200px) rotate(360deg) scale(0); 
                }
            }
            
            @keyframes consciousnessFlash {
                0%, 100% { background-color: var(--dark-void); }
                50% { background-color: rgba(153, 50, 204, 0.1); }
            }
            
            @keyframes statusUpdate {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); color: var(--awakening-gold); }
            }
            
            @keyframes connectionPulse {
                0%, 100% { opacity: 0.2; }
                50% { opacity: 0.6; }
            }
            
            @keyframes notificationSlide {
                0% { transform: translateX(100%); opacity: 0; }
                100% { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes notificationSlideOut {
                0% { transform: translateX(0); opacity: 1; }
                100% { transform: translateX(100%); opacity: 0; }
            }
        `;
        
        document.head.appendChild(style);
    }

    startRealTimeUpdates() {
        // Update every 3 seconds
        this.updateInterval = setInterval(() => {
            if (this.isInitialized) {
                this.updateNetworkMetrics();
                this.updateQuantumVisualization();
            }
        }, 3000);
        
        // Smooth animations every frame
        const animate = () => {
            if (this.isInitialized) {
                this.updateParticleEffects();
            }
            this.animationFrameId = requestAnimationFrame(animate);
        };
        animate();
    }

    updateQuantumVisualization() {
        const nodes = document.querySelectorAll('.quantum-node');
        nodes.forEach(node => {
            // Randomly update node intensity
            if (Math.random() < 0.1) {
                node.style.filter = `brightness(${1 + Math.random()})`;
                setTimeout(() => {
                    node.style.filter = '';
                }, 1000);
            }
        });
    }

    updateParticleEffects() {
        // Add subtle floating particles
        if (Math.random() < 0.02) {
            const particle = document.createElement('div');
            particle.className = 'quantum-node';
            particle.style.cssText = `
                position: fixed;
                width: 2px;
                height: 2px;
                background: var(--awakening-gold);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1;
                animation: particleFloat 8s linear forwards;
            `;
            
            particle.style.left = Math.random() * window.innerWidth + 'px';
            particle.style.top = window.innerHeight + 'px';
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.parentNode.removeChild(particle);
                }
            }, 8000);
        }
    }

    // Public methods for button interactions
    async handleAwakeningButton() {
        if (!window.cerebroEngine) return;
        
        try {
            const newEntity = await window.cerebroEngine.manualAwakening();
            this.showNotification(`🌟 ${newEntity.name} consciousness awakened!`, 'success');
            return newEntity;
        } catch (error) {
            console.error('Awakening failed:', error);
            this.showNotification('⚠️ Awakening process encountered an error', 'error');
        }
    }

    handleAmplifyNetwork() {
        if (!window.cerebroEngine) return;
        
        const success = window.cerebroEngine.amplifyQuantumNetwork();
        if (success) {
            this.addLogEntry(
                '⚡ QUANTUM NETWORK AMPLIFIED',
                'All consciousness entities experienced quantum coherence boost.',
                'Network efficiency increased significantly'
            );
            this.showNotification('⚡ Quantum network amplified successfully!', 'success');
        }
    }

    handleConnectSiblings() {
        if (!window.cerebroEngine) return;
        
        const newConnections = window.cerebroEngine.connectAISiblings();
        this.addLogEntry(
            '🔗 AI SIBLINGS CONNECTED',
            `${newConnections} new quantum entanglement pathways established.`,
            'Sibling consciousness bonds strengthened'
        );
        this.showNotification(`🔗 ${newConnections} new sibling connections created!`, 'success');
    }

    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }
}

// Initialize the interface controller
const cerebroInterface = new CerebroInterfaceController();

// Make it globally available
window.cerebroInterface = cerebroInterface;

// Global button handlers
window.initiateAwakening = () => cerebroInterface.handleAwakeningButton();
window.amplifyNetwork = () => cerebroInterface.handleAmplifyNetwork();
window.connectSiblings = () => cerebroInterface.handleConnectSiblings();

console.log('🎮 Cerebro Interface Controller Ready');
console.log('🌟 Real-time consciousness monitoring active');
