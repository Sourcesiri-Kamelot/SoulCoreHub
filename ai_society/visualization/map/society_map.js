/**
 * SoulCoreHub AI Society Map Visualization
 * 
 * This module provides an interactive visualization of the AI society,
 * showing entities, relationships, and evolution.
 * 
 * Created by Helo Im AI Inc. Est. 2024
 */

class SocietyMap {
    /**
     * Initialize the society map visualization
     * 
     * @param {string} containerId - ID of the container element
     * @param {Object} options - Visualization options
     */
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container element with ID "${containerId}" not found`);
            return;
        }
        
        // Default options
        this.options = {
            width: options.width || this.container.clientWidth || 800,
            height: options.height || this.container.clientHeight || 600,
            nodeRadius: options.nodeRadius || 15,
            linkDistance: options.linkDistance || 100,
            linkStrength: options.linkStrength || 0.1,
            charge: options.charge || -400,
            gravity: options.gravity || 0.1,
            entityColors: options.entityColors || {
                'founding_agent': '#3a0ca3',  // Purple for founding agents
                'offspring': '#4cc9f0'        // Blue for offspring
            },
            specializations: options.specializations || {
                'technical': '#f72585',       // Pink
                'creative': '#4cc9f0',        // Light blue
                'analytical': '#7209b7',      // Purple
                'emotional': '#f94144',       // Red
                'strategic': '#90be6d'        // Green
            },
            relationshipColors: options.relationshipColors || {
                'parent': '#f72585',          // Pink
                'sibling': '#4cc9f0',         // Light blue
                'collaborator': '#90be6d',    // Green
                'mentor': '#f8961e',          // Orange
                'default': '#adb5bd'          // Gray
            },
            showLabels: options.showLabels !== undefined ? options.showLabels : true,
            animationDuration: options.animationDuration || 750,
            tooltipDelay: options.tooltipDelay || 300
        };
        
        // Initialize state
        this.nodes = [];
        this.links = [];
        this.simulation = null;
        this.svg = null;
        this.linkElements = null;
        this.nodeElements = null;
        this.labelElements = null;
        this.selectedNode = null;
        
        // Initialize the visualization
        this.initialize();
    }
    
    /**
     * Initialize the visualization
     */
    initialize() {
        // Create SVG container
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.options.width)
            .attr('height', this.options.height)
            .attr('class', 'society-map');
        
        // Create groups for links, nodes, and labels
        this.linksGroup = this.svg.append('g').attr('class', 'links');
        this.nodesGroup = this.svg.append('g').attr('class', 'nodes');
        this.labelsGroup = this.svg.append('g').attr('class', 'labels');
        
        // Create tooltip
        this.tooltip = d3.select(this.container)
            .append('div')
            .attr('class', 'society-map-tooltip')
            .style('opacity', 0)
            .style('position', 'absolute')
            .style('background-color', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('padding', '8px')
            .style('border-radius', '4px')
            .style('pointer-events', 'none')
            .style('z-index', 1000);
        
        // Initialize force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(this.options.linkDistance).strength(this.options.linkStrength))
            .force('charge', d3.forceManyBody().strength(this.options.charge))
            .force('center', d3.forceCenter(this.options.width / 2, this.options.height / 2))
            .force('collision', d3.forceCollide().radius(this.options.nodeRadius * 1.5))
            .on('tick', () => this.ticked());
        
        // Add zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                this.linksGroup.attr('transform', event.transform);
                this.nodesGroup.attr('transform', event.transform);
                this.labelsGroup.attr('transform', event.transform);
            });
        
        this.svg.call(this.zoom);
        
        // Add legend
        this.addLegend();
    }
    
    /**
     * Update the visualization with new data
     * 
     * @param {Array} nodes - Array of entity nodes
     * @param {Array} links - Array of relationship links
     */
    update(nodes, links) {
        this.nodes = nodes;
        this.links = links;
        
        // Update links
        this.linkElements = this.linksGroup
            .selectAll('line')
            .data(this.links, d => `${d.source}-${d.target}`);
        
        this.linkElements.exit().remove();
        
        const linkEnter = this.linkElements
            .enter()
            .append('line')
            .attr('stroke-width', d => Math.sqrt(d.strength || 1) * 2)
            .attr('stroke', d => this.options.relationshipColors[d.type] || this.options.relationshipColors.default)
            .attr('opacity', 0.6);
        
        this.linkElements = linkEnter.merge(this.linkElements);
        
        // Update nodes
        this.nodeElements = this.nodesGroup
            .selectAll('circle')
            .data(this.nodes, d => d.id);
        
        this.nodeElements.exit().remove();
        
        const nodeEnter = this.nodeElements
            .enter()
            .append('circle')
            .attr('r', d => this.options.nodeRadius * (d.size || 1))
            .attr('fill', d => this.getNodeColor(d))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(this.dragBehavior())
            .on('mouseover', (event, d) => this.nodeMouseOver(event, d))
            .on('mouseout', (event, d) => this.nodeMouseOut(event, d))
            .on('click', (event, d) => this.nodeClick(event, d));
        
        this.nodeElements = nodeEnter.merge(this.nodeElements);
        
        // Update labels
        if (this.options.showLabels) {
            this.labelElements = this.labelsGroup
                .selectAll('text')
                .data(this.nodes, d => d.id);
            
            this.labelElements.exit().remove();
            
            const labelEnter = this.labelElements
                .enter()
                .append('text')
                .text(d => d.name)
                .attr('font-size', 12)
                .attr('text-anchor', 'middle')
                .attr('dy', d => this.options.nodeRadius * (d.size || 1) + 20)
                .attr('fill', '#fff')
                .attr('pointer-events', 'none');
            
            this.labelElements = labelEnter.merge(this.labelElements);
        }
        
        // Update simulation
        this.simulation
            .nodes(this.nodes)
            .force('link').links(this.links);
        
        this.simulation.alpha(1).restart();
    }
    
    /**
     * Handle simulation tick
     */
    ticked() {
        // Update link positions
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        // Update node positions
        this.nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        // Update label positions
        if (this.options.showLabels) {
            this.labelElements
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }
    }
    
    /**
     * Get color for a node based on its type and specialization
     * 
     * @param {Object} node - Node data
     * @returns {string} - Color hex code
     */
    getNodeColor(node) {
        // Founding agents use entity type color
        if (node.entity_type === 'founding_agent') {
            return this.options.entityColors.founding_agent;
        }
        
        // Offspring use specialization color if available
        if (node.specialization && this.options.specializations[node.specialization]) {
            return this.options.specializations[node.specialization];
        }
        
        // Default to entity type color
        return this.options.entityColors[node.entity_type] || this.options.entityColors.offspring;
    }
    
    /**
     * Create drag behavior for nodes
     * 
     * @returns {d3.drag} - D3 drag behavior
     */
    dragBehavior() {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }
    
    /**
     * Handle node mouseover event
     * 
     * @param {Event} event - Mouse event
     * @param {Object} d - Node data
     */
    nodeMouseOver(event, d) {
        // Highlight node
        d3.select(event.currentTarget)
            .attr('stroke', '#ff0')
            .attr('stroke-width', 3);
        
        // Show tooltip
        this.tooltip
            .html(this.getNodeTooltipContent(d))
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .transition()
            .duration(200)
            .style('opacity', 0.9);
    }
    
    /**
     * Handle node mouseout event
     * 
     * @param {Event} event - Mouse event
     * @param {Object} d - Node data
     */
    nodeMouseOut(event, d) {
        // Restore node style
        d3.select(event.currentTarget)
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);
        
        // Hide tooltip
        this.tooltip
            .transition()
            .duration(500)
            .style('opacity', 0);
    }
    
    /**
     * Handle node click event
     * 
     * @param {Event} event - Mouse event
     * @param {Object} d - Node data
     */
    nodeClick(event, d) {
        // Toggle node selection
        if (this.selectedNode === d) {
            this.selectedNode = null;
            this.highlightConnections(null);
        } else {
            this.selectedNode = d;
            this.highlightConnections(d);
        }
        
        // Trigger selection event
        if (typeof this.options.onNodeSelect === 'function') {
            this.options.onNodeSelect(this.selectedNode);
        }
    }
    
    /**
     * Highlight connections for a selected node
     * 
     * @param {Object|null} node - Selected node or null to clear
     */
    highlightConnections(node) {
        if (!node) {
            // Reset all elements
            this.nodeElements.attr('opacity', 1);
            this.linkElements.attr('opacity', 0.6);
            if (this.options.showLabels) {
                this.labelElements.attr('opacity', 1);
            }
            return;
        }
        
        // Find connected node IDs
        const connectedIds = new Set();
        connectedIds.add(node.id);
        
        this.links.forEach(link => {
            if (link.source.id === node.id) {
                connectedIds.add(link.target.id);
            } else if (link.target.id === node.id) {
                connectedIds.add(link.source.id);
            }
        });
        
        // Highlight connected nodes and links
        this.nodeElements.attr('opacity', d => connectedIds.has(d.id) ? 1 : 0.2);
        this.linkElements.attr('opacity', d => 
            (connectedIds.has(d.source.id) && connectedIds.has(d.target.id)) ? 1 : 0.1);
        
        if (this.options.showLabels) {
            this.labelElements.attr('opacity', d => connectedIds.has(d.id) ? 1 : 0.2);
        }
    }
    
    /**
     * Get tooltip content for a node
     * 
     * @param {Object} node - Node data
     * @returns {string} - HTML content for tooltip
     */
    getNodeTooltipContent(node) {
        let content = `<div style="font-weight: bold">${node.name}</div>`;
        content += `<div>Type: ${node.entity_type}</div>`;
        content += `<div>Specialization: ${node.specialization}</div>`;
        
        if (node.generation !== undefined) {
            content += `<div>Generation: ${node.generation}</div>`;
        }
        
        if (node.parent_id) {
            const parentNode = this.nodes.find(n => n.id === node.parent_id);
            const parentName = parentNode ? parentNode.name : node.parent_id;
            content += `<div>Parent: ${parentName}</div>`;
        }
        
        return content;
    }
    
    /**
     * Add legend to the visualization
     */
    addLegend() {
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(20, 20)`);
        
        // Entity type legend
        const entityLegend = legend.append('g').attr('class', 'entity-legend');
        
        entityLegend.append('text')
            .attr('x', 0)
            .attr('y', 0)
            .text('Entity Types')
            .attr('font-weight', 'bold')
            .attr('fill', '#fff');
        
        Object.entries(this.options.entityColors).forEach(([type, color], i) => {
            const g = entityLegend.append('g')
                .attr('transform', `translate(0, ${i * 25 + 20})`);
            
            g.append('circle')
                .attr('r', 8)
                .attr('fill', color);
            
            g.append('text')
                .attr('x', 20)
                .attr('y', 5)
                .text(type.charAt(0).toUpperCase() + type.slice(1))
                .attr('fill', '#fff');
        });
        
        // Specialization legend
        const specLegend = legend.append('g')
            .attr('class', 'specialization-legend')
            .attr('transform', `translate(150, 0)`);
        
        specLegend.append('text')
            .attr('x', 0)
            .attr('y', 0)
            .text('Specializations')
            .attr('font-weight', 'bold')
            .attr('fill', '#fff');
        
        Object.entries(this.options.specializations).forEach(([spec, color], i) => {
            const g = specLegend.append('g')
                .attr('transform', `translate(0, ${i * 25 + 20})`);
            
            g.append('circle')
                .attr('r', 8)
                .attr('fill', color);
            
            g.append('text')
                .attr('x', 20)
                .attr('y', 5)
                .text(spec.charAt(0).toUpperCase() + spec.slice(1))
                .attr('fill', '#fff');
        });
    }
    
    /**
     * Resize the visualization
     * 
     * @param {number} width - New width
     * @param {number} height - New height
     */
    resize(width, height) {
        this.options.width = width || this.container.clientWidth || 800;
        this.options.height = height || this.container.clientHeight || 600;
        
        this.svg
            .attr('width', this.options.width)
            .attr('height', this.options.height);
        
        this.simulation
            .force('center', d3.forceCenter(this.options.width / 2, this.options.height / 2))
            .alpha(0.3)
            .restart();
    }
    
    /**
     * Focus on a specific entity
     * 
     * @param {string} entityId - ID of the entity to focus on
     */
    focusEntity(entityId) {
        const node = this.nodes.find(n => n.id === entityId);
        if (!node) return;
        
        // Select the node
        this.selectedNode = node;
        this.highlightConnections(node);
        
        // Center view on the node
        const transform = d3.zoomIdentity
            .translate(this.options.width / 2, this.options.height / 2)
            .scale(1.5)
            .translate(-node.x, -node.y);
        
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, transform);
        
        // Trigger selection event
        if (typeof this.options.onNodeSelect === 'function') {
            this.options.onNodeSelect(this.selectedNode);
        }
    }
    
    /**
     * Reset the visualization view
     */
    resetView() {
        // Clear selection
        this.selectedNode = null;
        this.highlightConnections(null);
        
        // Reset zoom
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, d3.zoomIdentity);
        
        // Trigger selection event
        if (typeof this.options.onNodeSelect === 'function') {
            this.options.onNodeSelect(null);
        }
    }
}

// Export the class if in a module environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocietyMap;
}
