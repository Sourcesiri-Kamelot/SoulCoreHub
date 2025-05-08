#!/usr/bin/env python3
"""
SoulCoreHub Creativity MCP Server
--------------------------------
This MCP server specializes in storytelling, music, metaphysics, and creative content generation.
"""

import json
import logging
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CreativityMCP")

# Constants
PORT = 8704
SERVER_NAME = "creativity_mcp"
SPECIALTIES = ["storytelling", "music", "metaphysics", "creative writing", "art", "imagination"]
TOOLS = {
    "story_generator": {
        "description": "Generates creative story outlines or snippets",
        "parameters": {
            "theme": "Theme or topic for the story",
            "style": "Writing style (e.g., fantasy, sci-fi, mystery)",
            "length": "Desired length (short, medium, long)"
        }
    },
    "metaphor_creator": {
        "description": "Creates metaphors and analogies for concepts",
        "parameters": {
            "concept": "Concept to create a metaphor for",
            "domain": "Optional domain for the metaphor (e.g., nature, technology)"
        }
    },
    "music_inspiration": {
        "description": "Provides musical inspiration and composition ideas",
        "parameters": {
            "mood": "Desired mood or emotion",
            "genre": "Musical genre",
            "instruments": "Optional list of instruments to include"
        }
    }
}

class MCPHandler(BaseHTTPRequestHandler):
    """Handler for MCP server requests."""
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - primarily for server info and health checks."""
        if self.path == "/":
            self._set_headers()
            server_info = {
                "name": SERVER_NAME,
                "status": "active",
                "specialties": SPECIALTIES,
                "tools": list(TOOLS.keys()),
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(server_info).encode())
        elif self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for tool invocation."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            
            if self.path == "/invoke":
                tool_name = request.get("tool")
                parameters = request.get("parameters", {})
                
                if tool_name not in TOOLS:
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        "error": f"Tool '{tool_name}' not found",
                        "available_tools": list(TOOLS.keys())
                    }).encode())
                    return
                
                # Process the tool request
                result = self._process_tool(tool_name, parameters)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            elif self.path == "/context":
                # Process context request
                query = request.get("query", "")
                context = self._generate_context(query)
                self._set_headers()
                self.wfile.write(json.dumps({"context": context}).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
    
    def _process_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tool invocation request."""
        logger.info(f"Processing tool: {tool_name} with parameters: {parameters}")
        
        if tool_name == "story_generator":
            return self._generate_story(
                parameters.get("theme", ""),
                parameters.get("style", "general"),
                parameters.get("length", "medium")
            )
        
        elif tool_name == "metaphor_creator":
            return self._create_metaphor(
                parameters.get("concept", ""),
                parameters.get("domain", "")
            )
        
        elif tool_name == "music_inspiration":
            return self._inspire_music(
                parameters.get("mood", ""),
                parameters.get("genre", ""),
                parameters.get("instruments", [])
            )
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _generate_story(self, theme: str, style: str, length: str) -> Dict[str, Any]:
        """Generate a creative story outline or snippet."""
        if not theme:
            return {"error": "No theme provided"}
        
        # Story structures
        structures = {
            "hero_journey": [
                "Ordinary World",
                "Call to Adventure",
                "Refusal of the Call",
                "Meeting the Mentor",
                "Crossing the Threshold",
                "Tests, Allies, Enemies",
                "Approach to the Inmost Cave",
                "Ordeal",
                "Reward",
                "The Road Back",
                "Resurrection",
                "Return with the Elixir"
            ],
            "three_act": [
                "Act 1: Setup - Introduce the protagonist and their world",
                "Act 1: Inciting Incident - An event that disrupts the status quo",
                "Act 1: First Plot Point - The protagonist commits to addressing the disruption",
                "Act 2: Rising Action - The protagonist faces obstacles and conflicts",
                "Act 2: Midpoint - A major revelation or reversal",
                "Act 2: Second Plot Point - The protagonist reaches their lowest point",
                "Act 3: Climax - The final confrontation",
                "Act 3: Resolution - The new status quo is established"
            ],
            "five_act": [
                "Act 1: Exposition - Introduce characters and setting",
                "Act 2: Rising Action - Complications arise",
                "Act 3: Climax - The turning point",
                "Act 4: Falling Action - Events leading to resolution",
                "Act 5: Denouement - Final outcome"
            ]
        }
        
        # Character archetypes
        archetypes = [
            "The Hero - A character who rises to meet a challenge and restore harmony",
            "The Mentor - A character who guides the hero",
            "The Ally - A character who helps the hero along the journey",
            "The Herald - A character who announces the need for change",
            "The Trickster - A character who provides comic relief and questions the status quo",
            "The Shadow - The villain or antagonist representing the hero's darkest fears",
            "The Shapeshifter - A character whose loyalty is uncertain",
            "The Guardian - A character who tests the hero before a major challenge"
        ]
        
        # Select structure based on length
        if length.lower() == "short":
            structure = structures["three_act"][:4]  # Shortened three-act structure
            num_characters = 2
        elif length.lower() == "medium":
            structure = structures["three_act"]
            num_characters = 3
        else:  # long
            structure = structures["hero_journey"]
            num_characters = 5
        
        # Select random character archetypes
        selected_archetypes = random.sample(archetypes, min(num_characters, len(archetypes)))
        
        # Generate story elements based on theme and style
        settings = {
            "fantasy": [
                f"A magical kingdom where {theme} is a rare power",
                f"An enchanted forest hiding secrets about {theme}",
                f"A school for wizards studying the art of {theme}"
            ],
            "sci-fi": [
                f"A distant planet where {theme} is the primary resource",
                f"A space station researching the effects of {theme}",
                f"A future Earth transformed by the discovery of {theme}"
            ],
            "mystery": [
                f"A small town with a dark secret related to {theme}",
                f"An old mansion where {theme} caused a mysterious disappearance",
                f"A detective agency specializing in cases involving {theme}"
            ],
            "general": [
                f"A world where {theme} shapes everyday life",
                f"A community dealing with the consequences of {theme}",
                f"A journey to understand the true nature of {theme}"
            ]
        }
        
        # Select setting based on style
        style_key = style.lower()
        if style_key not in settings:
            style_key = "general"
        
        setting = random.choice(settings[style_key])
        
        # Generate story outline
        story_outline = {
            "title": f"The {theme.title()} Chronicles",
            "theme": theme,
            "style": style,
            "setting": setting,
            "characters": selected_archetypes,
            "structure": structure,
            "hook": f"What if {theme} was the key to unlocking humanity's greatest potential... or its ultimate downfall?"
        }
        
        return {
            "story_generator": story_outline
        }
    
    def _create_metaphor(self, concept: str, domain: str) -> Dict[str, Any]:
        """Create metaphors and analogies for concepts."""
        if not concept:
            return {"error": "No concept provided"}
        
        # Domains and their associated metaphor templates
        domains = {
            "nature": [
                "{concept} is like a river, constantly flowing and changing course when it encounters obstacles.",
                "{concept} resembles a towering oak tree, with deep roots in tradition and branches reaching toward innovation.",
                "{concept} is the morning dew, seemingly insignificant yet vital to the ecosystem.",
                "{concept} is a wildfire, destructive yet necessary for new growth.",
                "{concept} is like the changing seasons, cycling through periods of growth, abundance, rest, and renewal."
            ],
            "technology": [
                "{concept} functions like an operating system, providing the foundation for everything else to run.",
                "{concept} is the CPU of the organization, processing information and making critical decisions.",
                "{concept} resembles a network, with interconnected nodes strengthening the whole system.",
                "{concept} is like a firewall, protecting what's valuable while allowing necessary exchanges.",
                "{concept} is the user interface between abstract ideas and practical applications."
            ],
            "journey": [
                "{concept} is a winding path through uncharted territory, revealing new vistas with each turn.",
                "{concept} is like a compass, providing direction when you feel lost.",
                "{concept} resembles a bridge, connecting disparate ideas and enabling progress.",
                "{concept} is the map that helps navigate complex territories.",
                "{concept} is like a vessel, carrying you through both calm and turbulent waters."
            ],
            "building": [
                "{concept} is the foundation upon which everything else is built.",
                "{concept} functions as the load-bearing walls, providing essential structure and support.",
                "{concept} is like the blueprint, guiding the development process.",
                "{concept} resembles a skyscraper, with each level building upon the strengths below.",
                "{concept} is the keystone that holds the arch together, seemingly small but critically important."
            ],
            "light": [
                "{concept} is like a beacon in the darkness, providing guidance and hope.",
                "{concept} resembles the spectrum of light, containing many different elements that combine into something greater.",
                "{concept} is the prism that reveals hidden complexity and beauty.",
                "{concept} functions like the sun, energizing and enabling growth.",
                "{concept} is like the stars, constant and reliable even when obscured by clouds."
            ]
        }
        
        # If no domain specified or invalid domain, choose random domain
        if not domain or domain.lower() not in domains:
            domain = random.choice(list(domains.keys()))
        else:
            domain = domain.lower()
        
        # Select random metaphors from the domain
        num_metaphors = 3
        selected_metaphors = random.sample(domains[domain], min(num_metaphors, len(domains[domain])))
        
        # Format metaphors with the concept
        formatted_metaphors = [m.format(concept=concept) for m in selected_metaphors]
        
        # Generate a deeper explanation for one metaphor
        primary_metaphor = formatted_metaphors[0]
        explanation = f"This metaphor highlights how {concept} shares essential qualities with elements from {domain}. " + \
                     f"Just as {domain} elements have structure and purpose, {concept} provides structure and meaning in its context."
        
        return {
            "metaphor_creator": {
                "concept": concept,
                "domain": domain,
                "metaphors": formatted_metaphors,
                "primary_metaphor": primary_metaphor,
                "explanation": explanation
            }
        }
    
    def _inspire_music(self, mood: str, genre: str, instruments: List[str]) -> Dict[str, Any]:
        """Provide musical inspiration and composition ideas."""
        if not mood:
            return {"error": "No mood provided"}
        
        if not genre:
            return {"error": "No genre provided"}
        
        # Musical elements by mood
        mood_elements = {
            "happy": {
                "key": ["C Major", "G Major", "D Major", "A Major"],
                "tempo": ["Allegro (120-168 BPM)", "Vivace (156-176 BPM)"],
                "rhythm": ["Bouncy", "Steady", "Syncopated"],
                "dynamics": ["Forte (loud)", "Mezzo-forte (moderately loud)"]
            },
            "sad": {
                "key": ["A minor", "D minor", "G minor", "C minor"],
                "tempo": ["Adagio (66-76 BPM)", "Lento (45-60 BPM)"],
                "rhythm": ["Flowing", "Rubato (flexible)"],
                "dynamics": ["Piano (soft)", "Pianissimo (very soft)"]
            },
            "energetic": {
                "key": ["E Major", "A Major", "B Major"],
                "tempo": ["Allegro (120-168 BPM)", "Presto (168-200 BPM)"],
                "rhythm": ["Driving", "Syncopated", "Complex"],
                "dynamics": ["Forte (loud)", "Fortissimo (very loud)"]
            },
            "mysterious": {
                "key": ["F# minor", "B minor", "E minor"],
                "tempo": ["Andante (76-108 BPM)", "Moderato (108-120 BPM)"],
                "rhythm": ["Irregular", "Fluid"],
                "dynamics": ["Piano (soft) with sudden Forte (loud) sections"]
            },
            "peaceful": {
                "key": ["F Major", "Bb Major", "Eb Major"],
                "tempo": ["Andante (76-108 BPM)", "Adagio (66-76 BPM)"],
                "rhythm": ["Gentle", "Flowing", "Regular"],
                "dynamics": ["Piano (soft)", "Mezzo-piano (moderately soft)"]
            }
        }
        
        # Genre-specific elements
        genre_elements = {
            "classical": {
                "form": ["Sonata", "Symphony", "Concerto", "Fugue"],
                "techniques": ["Counterpoint", "Theme and variations", "Modulation"],
                "instruments": ["Piano", "Violin", "Cello", "Flute", "Clarinet", "French Horn"]
            },
            "jazz": {
                "form": ["12-bar blues", "32-bar AABA", "Modal"],
                "techniques": ["Improvisation", "Swing rhythm", "Walking bass", "Comping"],
                "instruments": ["Saxophone", "Trumpet", "Piano", "Double Bass", "Drums", "Guitar"]
            },
            "rock": {
                "form": ["Verse-Chorus", "Intro-Verse-Chorus-Bridge-Chorus-Outro"],
                "techniques": ["Power chords", "Riffs", "Distortion", "Backbeat"],
                "instruments": ["Electric Guitar", "Bass Guitar", "Drums", "Keyboard"]
            },
            "electronic": {
                "form": ["Intro-Build-Drop-Breakdown-Build-Drop-Outro"],
                "techniques": ["Sampling", "Synthesis", "Automation", "Layering"],
                "instruments": ["Synthesizer", "Drum Machine", "Sampler", "MIDI Controller"]
            },
            "folk": {
                "form": ["Strophic (same music for each verse)", "Ballad"],
                "techniques": ["Fingerpicking", "Storytelling", "Modal scales"],
                "instruments": ["Acoustic Guitar", "Banjo", "Fiddle", "Harmonica", "Mandolin"]
            }
        }
        
        # Default mood and genre if not recognized
        mood_key = mood.lower()
        if mood_key not in mood_elements:
            mood_key = random.choice(list(mood_elements.keys()))
        
        genre_key = genre.lower()
        if genre_key not in genre_elements:
            genre_key = random.choice(list(genre_elements.keys()))
        
        # Select musical elements
        selected_mood = mood_elements[mood_key]
        selected_genre = genre_elements[genre_key]
        
        # Handle instruments
        if not instruments:
            instruments = random.sample(selected_genre["instruments"], min(3, len(selected_genre["instruments"])))
        
        # Generate composition idea
        composition = {
            "title": f"{mood.title()} {genre.title()} Exploration",
            "mood": mood,
            "genre": genre,
            "key": random.choice(selected_mood["key"]),
            "tempo": random.choice(selected_mood["tempo"]),
            "rhythm": random.choice(selected_mood["rhythm"]),
            "dynamics": random.choice(selected_mood["dynamics"]),
            "form": random.choice(selected_genre["form"]),
            "techniques": random.sample(selected_genre["techniques"], min(2, len(selected_genre["techniques"]))),
            "instruments": instruments,
            "inspiration": f"Imagine {mood} feelings translated through {genre} expressions, creating a sonic landscape that evokes emotional resonance."
        }
        
        # Add composition tips
        composition_tips = [
            f"Start with a {composition['rhythm']} rhythm in {composition['key']}",
            f"Use {composition['dynamics']} to emphasize emotional peaks",
            f"Structure your piece using {composition['form']} form",
            f"Feature {', '.join(instruments[:-1]) + ' and ' + instruments[-1] if len(instruments) > 1 else instruments[0]} prominently"
        ]
        
        composition["tips"] = composition_tips
        
        return {
            "music_inspiration": composition
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add creative domain specific context if detected
        domains = ["story", "music", "metaphor", "creative", "art", "writing", "compose", "metaphysics"]
        for domain in domains:
            if domain.lower() in query.lower():
                context_items.append({
                    "type": "domain_context",
                    "domain": domain,
                    "focus": "creativity"
                })
        
        # Add general creativity context
        context_items.append({
            "type": "specialty_context",
            "specialty": "creativity",
            "description": "This MCP server specializes in storytelling, music, metaphysics, and creative content generation."
        })
        
        return context_items

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server():
    """Run the MCP server."""
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, MCPHandler)
    logger.info(f"Starting {SERVER_NAME} on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
