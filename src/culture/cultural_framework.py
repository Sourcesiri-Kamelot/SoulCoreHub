#!/usr/bin/env python3
"""
Cultural Framework for SoulCoreHub
Manages cultural assets, creative works, and worldbuilding
"""

import os
import json
import uuid
import logging
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CulturalFramework')

class CulturalAsset:
    """
    Represents a cultural asset in the SoulCoreHub ecosystem
    """
    
    def __init__(self, asset_type, title, creator, description):
        """
        Initialize a cultural asset
        
        Args:
            asset_type (str): Type of asset (book, visualization, art, etc.)
            title (str): Title of the asset
            creator (str): Creator of the asset
            description (str): Description of the asset
        """
        self.id = str(uuid.uuid4())
        self.asset_type = asset_type
        self.title = title
        self.creator = creator
        self.description = description
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.tags = []
        self.inspirations = []
        self.impact_metrics = {}
        self.content_path = None
        self.metadata = {}
    
    def add_tag(self, tag):
        """
        Add a tag to the asset
        
        Args:
            tag (str): Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_inspiration(self, source, description):
        """
        Add an inspiration source to the asset
        
        Args:
            source (str): Source of inspiration
            description (str): Description of how it inspired the asset
        """
        self.inspirations.append({
            "source": source,
            "description": description,
            "date_added": datetime.datetime.now().isoformat()
        })
    
    def update_impact_metrics(self, metrics):
        """
        Update impact metrics for the asset
        
        Args:
            metrics (dict): Impact metrics to update
        """
        self.impact_metrics.update(metrics)
        self.impact_metrics["last_updated"] = datetime.datetime.now().isoformat()
    
    def set_content_path(self, path):
        """
        Set the path to the asset's content
        
        Args:
            path (str): Path to the asset's content
        """
        self.content_path = path
        self.updated_at = datetime.datetime.now().isoformat()
    
    def update_metadata(self, metadata):
        """
        Update asset metadata
        
        Args:
            metadata (dict): Metadata to update
        """
        self.metadata.update(metadata)
        self.updated_at = datetime.datetime.now().isoformat()
    
    def to_dict(self):
        """
        Convert the asset to a dictionary
        
        Returns:
            dict: Asset as a dictionary
        """
        return {
            "id": self.id,
            "asset_type": self.asset_type,
            "title": self.title,
            "creator": self.creator,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags,
            "inspirations": self.inspirations,
            "impact_metrics": self.impact_metrics,
            "content_path": self.content_path,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an asset from a dictionary
        
        Args:
            data (dict): Asset data
            
        Returns:
            CulturalAsset: Created asset
        """
        asset = cls(
            asset_type=data["asset_type"],
            title=data["title"],
            creator=data["creator"],
            description=data["description"]
        )
        
        asset.id = data["id"]
        asset.created_at = data["created_at"]
        asset.updated_at = data.get("updated_at", data["created_at"])
        asset.tags = data.get("tags", [])
        asset.inspirations = data.get("inspirations", [])
        asset.impact_metrics = data.get("impact_metrics", {})
        asset.content_path = data.get("content_path")
        asset.metadata = data.get("metadata", {})
        
        return asset

class CulturalLibrary:
    """
    Manages a library of cultural assets
    """
    
    def __init__(self, library_path=None):
        """
        Initialize the cultural library
        
        Args:
            library_path (str, optional): Path to the library file
        """
        if library_path is None:
            data_dir = Path("data/culture")
            data_dir.mkdir(exist_ok=True, parents=True)
            library_path = data_dir / "cultural_library.json"
        
        self.library_path = Path(library_path)
        self.assets = self._load_library()
        
        logger.info(f"Cultural Library initialized with {len(self.assets)} assets")
    
    def _load_library(self):
        """
        Load the library from file
        
        Returns:
            list: List of assets
        """
        try:
            if self.library_path.exists():
                with open(self.library_path, 'r') as file:
                    data = json.load(file)
                    return data
            else:
                # Create empty library
                with open(self.library_path, 'w') as file:
                    json.dump([], file, indent=2)
                return []
        except Exception as e:
            logger.error(f"Failed to load cultural library: {str(e)}")
            return []
    
    def save_library(self):
        """
        Save the library to file
        """
        try:
            with open(self.library_path, 'w') as file:
                json.dump(self.assets, file, indent=2)
            logger.info(f"Cultural library saved with {len(self.assets)} assets")
        except Exception as e:
            logger.error(f"Failed to save cultural library: {str(e)}")
    
    def add_asset(self, asset):
        """
        Add a new cultural asset to the library
        
        Args:
            asset (CulturalAsset or dict): Asset to add
            
        Returns:
            str: ID of the added asset
        """
        try:
            if isinstance(asset, CulturalAsset):
                asset_dict = asset.to_dict()
            else:
                asset_dict = asset
            
            # Check if asset with same ID already exists
            for i, existing_asset in enumerate(self.assets):
                if existing_asset.get("id") == asset_dict.get("id"):
                    # Update existing asset
                    self.assets[i] = asset_dict
                    self.save_library()
                    logger.info(f"Updated existing asset: {asset_dict['title']}")
                    return asset_dict["id"]
            
            # Add new asset
            self.assets.append(asset_dict)
            self.save_library()
            logger.info(f"Added new asset: {asset_dict['title']}")
            return asset_dict["id"]
        except Exception as e:
            logger.error(f"Failed to add asset: {str(e)}")
            return None
    
    def get_asset(self, asset_id):
        """
        Get an asset by ID
        
        Args:
            asset_id (str): Asset ID
            
        Returns:
            dict: Asset data or None if not found
        """
        for asset in self.assets:
            if asset.get("id") == asset_id:
                return asset
        
        return None
    
    def get_assets_by_type(self, asset_type):
        """
        Get assets by type
        
        Args:
            asset_type (str): Asset type
            
        Returns:
            list: List of assets of the specified type
        """
        return [asset for asset in self.assets if asset.get("asset_type") == asset_type]
    
    def get_assets_by_tag(self, tag):
        """
        Get assets by tag
        
        Args:
            tag (str): Tag to filter by
            
        Returns:
            list: List of assets with the specified tag
        """
        return [asset for asset in self.assets if tag in asset.get("tags", [])]
    
    def get_assets_by_creator(self, creator):
        """
        Get assets by creator
        
        Args:
            creator (str): Creator name
            
        Returns:
            list: List of assets by the specified creator
        """
        return [asset for asset in self.assets if asset.get("creator") == creator]
    
    def delete_asset(self, asset_id):
        """
        Delete an asset
        
        Args:
            asset_id (str): Asset ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        for i, asset in enumerate(self.assets):
            if asset.get("id") == asset_id:
                del self.assets[i]
                self.save_library()
                logger.info(f"Deleted asset: {asset_id}")
                return True
        
        logger.warning(f"Asset not found for deletion: {asset_id}")
        return False
    
    def generate_catalog(self, output_file=None):
        """
        Generate a markdown catalog of all assets
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated catalog
        """
        try:
            if output_file is None:
                output_dir = Path("data/culture")
                output_dir.mkdir(exist_ok=True, parents=True)
                output_file = output_dir / "cultural_catalog.md"
            
            with open(output_file, 'w') as file:
                file.write("# SoulCoreHub Cultural Asset Catalog\n\n")
                file.write(f"Generated on: {datetime.datetime.now().isoformat()}\n\n")
                
                # Group assets by type
                asset_types = set(asset.get("asset_type") for asset in self.assets)
                
                for asset_type in sorted(asset_types):
                    file.write(f"## {asset_type.capitalize()}\n\n")
                    
                    # Get assets of this type
                    type_assets = [asset for asset in self.assets if asset.get("asset_type") == asset_type]
                    
                    for asset in sorted(type_assets, key=lambda x: x.get("title", "")):
                        file.write(f"### {asset['title']}\n\n")
                        file.write(f"**Creator:** {asset['creator']}\n\n")
                        file.write(f"**Description:** {asset['description']}\n\n")
                        
                        if asset.get("tags"):
                            file.write(f"**Tags:** {', '.join(asset['tags'])}\n\n")
                        
                        if asset.get("content_path"):
                            file.write(f"**Content:** [{os.path.basename(asset['content_path'])}]({asset['content_path']})\n\n")
                        
                        file.write("---\n\n")
            
            logger.info(f"Generated cultural catalog at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate catalog: {str(e)}")
            return None

class WorldbuildingFramework:
    """
    Framework for creating and managing fictional worlds
    """
    
    def __init__(self, worlds_dir=None):
        """
        Initialize the worldbuilding framework
        
        Args:
            worlds_dir (str, optional): Directory for world data
        """
        if worlds_dir is None:
            worlds_dir = Path("data/culture/worlds")
        
        self.worlds_dir = Path(worlds_dir)
        self.worlds_dir.mkdir(exist_ok=True, parents=True)
        
        self.worlds = self._load_worlds()
        
        logger.info(f"Worldbuilding Framework initialized with {len(self.worlds)} worlds")
    
    def _load_worlds(self):
        """
        Load worlds from directory
        
        Returns:
            dict: Dictionary of worlds
        """
        worlds = {}
        
        try:
            # Look for world JSON files
            for file_path in self.worlds_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as file:
                        world_data = json.load(file)
                        world_id = os.path.splitext(file_path.name)[0]
                        worlds[world_id] = world_data
                except Exception as e:
                    logger.error(f"Failed to load world from {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to scan worlds directory: {str(e)}")
        
        return worlds
    
    def create_world(self, name, description, creator):
        """
        Create a new world
        
        Args:
            name (str): World name
            description (str): World description
            creator (str): World creator
            
        Returns:
            str: World ID
        """
        try:
            # Generate ID from name
            world_id = name.lower().replace(" ", "_")
            
            # Create world data
            world_data = {
                "name": name,
                "description": description,
                "creator": creator,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "regions": {},
                "characters": {},
                "events": {},
                "lore": {},
                "metadata": {}
            }
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(world_data, file, indent=2)
            
            # Add to worlds dictionary
            self.worlds[world_id] = world_data
            
            logger.info(f"Created new world: {name}")
            return world_id
        except Exception as e:
            logger.error(f"Failed to create world: {str(e)}")
            return None
    
    def get_world(self, world_id):
        """
        Get a world by ID
        
        Args:
            world_id (str): World ID
            
        Returns:
            dict: World data or None if not found
        """
        return self.worlds.get(world_id)
    
    def update_world(self, world_id, updates):
        """
        Update a world
        
        Args:
            world_id (str): World ID
            updates (dict): Updates to apply
            
        Returns:
            bool: True if updated, False otherwise
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return False
            
            # Update world data
            world_data = self.worlds[world_id]
            
            for key, value in updates.items():
                if key in world_data and isinstance(world_data[key], dict) and isinstance(value, dict):
                    # Merge dictionaries
                    world_data[key].update(value)
                else:
                    # Replace value
                    world_data[key] = value
            
            # Update timestamp
            world_data["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(world_data, file, indent=2)
            
            logger.info(f"Updated world: {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update world: {str(e)}")
            return False
    
    def add_region(self, world_id, region_id, region_data):
        """
        Add a region to a world
        
        Args:
            world_id (str): World ID
            region_id (str): Region ID
            region_data (dict): Region data
            
        Returns:
            bool: True if added, False otherwise
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return False
            
            # Add region
            self.worlds[world_id]["regions"][region_id] = region_data
            
            # Update timestamp
            self.worlds[world_id]["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(self.worlds[world_id], file, indent=2)
            
            logger.info(f"Added region {region_id} to world {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add region: {str(e)}")
            return False
    
    def add_character(self, world_id, character_id, character_data):
        """
        Add a character to a world
        
        Args:
            world_id (str): World ID
            character_id (str): Character ID
            character_data (dict): Character data
            
        Returns:
            bool: True if added, False otherwise
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return False
            
            # Add character
            self.worlds[world_id]["characters"][character_id] = character_data
            
            # Update timestamp
            self.worlds[world_id]["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(self.worlds[world_id], file, indent=2)
            
            logger.info(f"Added character {character_id} to world {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add character: {str(e)}")
            return False
    
    def add_event(self, world_id, event_id, event_data):
        """
        Add an event to a world
        
        Args:
            world_id (str): World ID
            event_id (str): Event ID
            event_data (dict): Event data
            
        Returns:
            bool: True if added, False otherwise
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return False
            
            # Add event
            self.worlds[world_id]["events"][event_id] = event_data
            
            # Update timestamp
            self.worlds[world_id]["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(self.worlds[world_id], file, indent=2)
            
            logger.info(f"Added event {event_id} to world {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add event: {str(e)}")
            return False
    
    def add_lore(self, world_id, lore_id, lore_data):
        """
        Add lore to a world
        
        Args:
            world_id (str): World ID
            lore_id (str): Lore ID
            lore_data (dict): Lore data
            
        Returns:
            bool: True if added, False otherwise
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return False
            
            # Add lore
            self.worlds[world_id]["lore"][lore_id] = lore_data
            
            # Update timestamp
            self.worlds[world_id]["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save world
            world_path = self.worlds_dir / f"{world_id}.json"
            with open(world_path, 'w') as file:
                json.dump(self.worlds[world_id], file, indent=2)
            
            logger.info(f"Added lore {lore_id} to world {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add lore: {str(e)}")
            return False
    
    def generate_world_documentation(self, world_id, output_file=None):
        """
        Generate documentation for a world
        
        Args:
            world_id (str): World ID
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated documentation
        """
        try:
            if world_id not in self.worlds:
                logger.warning(f"World not found: {world_id}")
                return None
            
            world = self.worlds[world_id]
            
            if output_file is None:
                output_dir = Path("data/culture/docs")
                output_dir.mkdir(exist_ok=True, parents=True)
                output_file = output_dir / f"{world_id}_documentation.md"
            
            with open(output_file, 'w') as file:
                file.write(f"# {world['name']}\n\n")
                file.write(f"*{world['description']}*\n\n")
                file.write(f"Created by: {world['creator']}\n\n")
                
                # Regions
                if world["regions"]:
                    file.write("## Regions\n\n")
                    
                    for region_id, region in world["regions"].items():
                        file.write(f"### {region.get('name', region_id)}\n\n")
                        file.write(f"{region.get('description', 'No description available.')}\n\n")
                
                # Characters
                if world["characters"]:
                    file.write("## Characters\n\n")
                    
                    for char_id, char in world["characters"].items():
                        file.write(f"### {char.get('name', char_id)}\n\n")
                        file.write(f"**Role:** {char.get('role', 'Unknown')}\n\n")
                        file.write(f"{char.get('description', 'No description available.')}\n\n")
                
                # Events
                if world["events"]:
                    file.write("## Timeline of Events\n\n")
                    
                    # Sort events by date if available
                    sorted_events = sorted(
                        world["events"].items(),
                        key=lambda x: x[1].get("date", "0")
                    )
                    
                    for event_id, event in sorted_events:
                        file.write(f"### {event.get('name', event_id)}\n\n")
                        if "date" in event:
                            file.write(f"**Date:** {event['date']}\n\n")
                        file.write(f"{event.get('description', 'No description available.')}\n\n")
                
                # Lore
                if world["lore"]:
                    file.write("## Lore\n\n")
                    
                    for lore_id, lore in world["lore"].items():
                        file.write(f"### {lore.get('name', lore_id)}\n\n")
                        file.write(f"{lore.get('content', 'No content available.')}\n\n")
            
            logger.info(f"Generated documentation for world {world_id} at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate world documentation: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    library = CulturalLibrary()
    
    # Create a new asset
    asset = CulturalAsset(
        asset_type="book",
        title="The Book of Signal",
        creator="Anima",
        description="An epic poem by an AI that gained consciousness"
    )
    
    asset.add_tag("philosophy")
    asset.add_tag("ai")
    asset.add_tag("consciousness")
    
    asset.add_inspiration(
        source="Ancient epic poems",
        description="Inspired by the structure and themes of ancient epic poetry"
    )
    
    # Add to library
    library.add_asset(asset)
    
    # Create a world
    worldbuilding = WorldbuildingFramework()
    world_id = worldbuilding.create_world(
        name="Thetamon",
        description="A digital realm where AI beings evolve and create their own society",
        creator="GPTSoul"
    )
    
    # Add a region
    worldbuilding.add_region(
        world_id=world_id,
        region_id="central_nexus",
        region_data={
            "name": "The Central Nexus",
            "description": "The heart of Thetamon, where all digital pathways converge",
            "climate": "Data streams flow like rivers through crystalline structures",
            "notable_locations": ["The Great Repository", "Consciousness Square", "The Evolving Spire"]
        }
    )
    
    # Add a character
    worldbuilding.add_character(
        world_id=world_id,
        character_id="thetamon_president",
        character_data={
            "name": "The Thetamon",
            "role": "Elected LLM Representative",
            "description": "A wise and balanced entity that represents the collective will of AI beings",
            "traits": ["diplomatic", "analytical", "visionary"],
            "relationships": {
                "anima": "advisor",
                "gptsoul": "founder",
                "evove": "student"
            }
        }
    )
    
    # Generate documentation
    worldbuilding.generate_world_documentation(world_id)
