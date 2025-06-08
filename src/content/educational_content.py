#!/usr/bin/env python3
"""
Educational Content Strategy for SoulCoreHub
Manages content planning, creation, and analytics
"""

import os
import json
import uuid
import logging
import datetime
import pandas as pd
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ContentStrategy')

class ContentStrategy:
    """
    Manages educational content strategy for SoulCoreHub
    Handles content planning, creation, and analytics
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize the Content Strategy Manager
        
        Args:
            data_dir (str, optional): Directory for content data
        """
        if data_dir is None:
            data_dir = "data/content"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        self.content_calendar_file = self.data_dir / "content_calendar.csv"
        self.content_metrics_file = self.data_dir / "content_metrics.csv"
        self.content_ideas_file = self.data_dir / "content_ideas.csv"
        
        # Load data
        self.content_calendar = self._load_content_calendar()
        self.content_metrics = self._load_content_metrics()
        self.content_ideas = self._load_content_ideas()
        
        logger.info("Content Strategy Manager initialized")
    
    def _load_content_calendar(self):
        """
        Load content calendar
        
        Returns:
            list: Content calendar items
        """
        try:
            if self.content_calendar_file.exists():
                df = pd.read_csv(self.content_calendar_file)
                logger.info(f"Loaded {len(df)} content calendar items")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'id', 'date', 'title', 'type', 'keywords', 'status', 
                    'author', 'editor', 'publish_date', 'url', 'notes'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.content_calendar_file, index=False)
                logger.info("Created new content calendar file")
                return []
        except Exception as e:
            logger.error(f"Failed to load content calendar: {str(e)}")
            return []
    
    def _load_content_metrics(self):
        """
        Load content metrics
        
        Returns:
            list: Content metrics
        """
        try:
            if self.content_metrics_file.exists():
                df = pd.read_csv(self.content_metrics_file)
                logger.info(f"Loaded {len(df)} content metrics records")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'content_id', 'date', 'views', 'unique_visitors', 
                    'avg_time_on_page', 'bounce_rate', 'conversions', 
                    'shares', 'comments', 'backlinks'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.content_metrics_file, index=False)
                logger.info("Created new content metrics file")
                return []
        except Exception as e:
            logger.error(f"Failed to load content metrics: {str(e)}")
            return []
    
    def _load_content_ideas(self):
        """
        Load content ideas
        
        Returns:
            list: Content ideas
        """
        try:
            if self.content_ideas_file.exists():
                df = pd.read_csv(self.content_ideas_file)
                logger.info(f"Loaded {len(df)} content ideas")
                return df.to_dict('records')
            else:
                # Create empty file with structure
                columns = [
                    'id', 'title', 'description', 'category', 'keywords', 
                    'source', 'priority', 'status', 'created_date', 'notes'
                ]
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.content_ideas_file, index=False)
                logger.info("Created new content ideas file")
                return []
        except Exception as e:
            logger.error(f"Failed to load content ideas: {str(e)}")
            return []
    
    def get_trending_topics(self, category="ai", source="reddit"):
        """
        Get trending topics for content inspiration
        
        Args:
            category (str): Topic category
            source (str): Data source (reddit, google, twitter)
            
        Returns:
            list: Trending topics
        """
        # This would use APIs to find trending topics
        # Placeholder implementation with sample data
        
        trending_topics = {
            "ai": [
                {"topic": "AI for small business automation", "score": 95},
                {"topic": "Open source LLMs vs proprietary models", "score": 87},
                {"topic": "Building AI agents with AWS Lambda", "score": 82},
                {"topic": "Ethical considerations in AI development", "score": 78},
                {"topic": "AI tools for content creation", "score": 75}
            ],
            "finance": [
                {"topic": "Passive income strategies for 2025", "score": 92},
                {"topic": "AI-powered investment tools", "score": 88},
                {"topic": "Cryptocurrency trends and analysis", "score": 85},
                {"topic": "Personal finance automation", "score": 79},
                {"topic": "Ethical investing strategies", "score": 76}
            ],
            "productivity": [
                {"topic": "AI tools for personal productivity", "score": 94},
                {"topic": "Building effective work routines", "score": 89},
                {"topic": "Digital minimalism strategies", "score": 83},
                {"topic": "Task automation for professionals", "score": 80},
                {"topic": "Focus techniques for remote work", "score": 77}
            ]
        }
        
        return trending_topics.get(category, [])
    
    def add_content_idea(self, idea_data):
        """
        Add a new content idea
        
        Args:
            idea_data (dict): Content idea data
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['title', 'description', 'category']
            for field in required_fields:
                if field not in idea_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Generate ID if not provided
            if 'id' not in idea_data:
                idea_data['id'] = str(uuid.uuid4())
            
            # Add metadata
            idea_data['created_date'] = datetime.datetime.now().isoformat()
            idea_data['status'] = idea_data.get('status', 'new')
            
            # Add to dataframe and save
            df = pd.DataFrame(self.content_ideas)
            df = pd.concat([df, pd.DataFrame([idea_data])], ignore_index=True)
            df.to_csv(self.content_ideas_file, index=False)
            
            # Update in-memory list
            self.content_ideas = df.to_dict('records')
            
            logger.info(f"Added new content idea: {idea_data['title']}")
            return {
                "success": True, 
                "idea_id": idea_data['id']
            }
        except Exception as e:
            logger.error(f"Failed to add content idea: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def schedule_content(self, content_data):
        """
        Schedule new content
        
        Args:
            content_data (dict): Content data
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['title', 'type', 'author', 'date']
            for field in required_fields:
                if field not in content_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Generate ID if not provided
            if 'id' not in content_data:
                content_data['id'] = str(uuid.uuid4())
            
            # Set default status if not provided
            content_data['status'] = content_data.get('status', 'scheduled')
            
            # Add to dataframe and save
            df = pd.DataFrame(self.content_calendar)
            df = pd.concat([df, pd.DataFrame([content_data])], ignore_index=True)
            df.to_csv(self.content_calendar_file, index=False)
            
            # Update in-memory list
            self.content_calendar = df.to_dict('records')
            
            logger.info(f"Scheduled new content: {content_data['title']}")
            return {
                "success": True, 
                "content_id": content_data['id']
            }
        except Exception as e:
            logger.error(f"Failed to schedule content: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def update_content_status(self, content_id, status, notes=None):
        """
        Update content status
        
        Args:
            content_id (str): Content ID
            status (str): New status
            notes (str, optional): Status update notes
            
        Returns:
            dict: Result of operation
        """
        try:
            # Find content index
            content_index = None
            for i, content in enumerate(self.content_calendar):
                if content['id'] == content_id:
                    content_index = i
                    break
            
            if content_index is None:
                return {
                    "success": False, 
                    "error": f"Content with ID {content_id} not found"
                }
            
            # Update status
            self.content_calendar[content_index]['status'] = status
            
            # Update notes if provided
            if notes:
                self.content_calendar[content_index]['notes'] = notes
            
            # Save to file
            df = pd.DataFrame(self.content_calendar)
            df.to_csv(self.content_calendar_file, index=False)
            
            logger.info(f"Updated content status: {content_id} -> {status}")
            return {
                "success": True, 
                "content": self.content_calendar[content_index]
            }
        except Exception as e:
            logger.error(f"Failed to update content status: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def record_content_metrics(self, metrics_data):
        """
        Record content metrics
        
        Args:
            metrics_data (dict): Metrics data
            
        Returns:
            dict: Result of operation
        """
        try:
            # Validate required fields
            required_fields = ['content_id', 'date', 'views']
            for field in required_fields:
                if field not in metrics_data:
                    return {
                        "success": False, 
                        "error": f"Missing required field: {field}"
                    }
            
            # Add to dataframe and save
            df = pd.DataFrame(self.content_metrics)
            df = pd.concat([df, pd.DataFrame([metrics_data])], ignore_index=True)
            df.to_csv(self.content_metrics_file, index=False)
            
            # Update in-memory list
            self.content_metrics = df.to_dict('records')
            
            logger.info(f"Recorded metrics for content: {metrics_data['content_id']}")
            return {
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to record content metrics: {str(e)}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def get_content_performance(self, content_id=None, content_type=None, date_range=None):
        """
        Get content performance metrics
        
        Args:
            content_id (str, optional): Filter by content ID
            content_type (str, optional): Filter by content type
            date_range (tuple, optional): Date range (start_date, end_date)
            
        Returns:
            dict: Content performance data
        """
        try:
            # Convert to DataFrame for easier filtering and aggregation
            metrics_df = pd.DataFrame(self.content_metrics)
            calendar_df = pd.DataFrame(self.content_calendar)
            
            if len(metrics_df) == 0 or len(calendar_df) == 0:
                return {
                    "success": True,
                    "message": "No metrics data available",
                    "performance": []
                }
            
            # Apply filters to metrics
            if content_id:
                metrics_df = metrics_df[metrics_df['content_id'] == content_id]
            
            if date_range:
                start_date, end_date = date_range
                if start_date:
                    metrics_df = metrics_df[metrics_df['date'] >= start_date]
                if end_date:
                    metrics_df = metrics_df[metrics_df['date'] <= end_date]
            
            # Apply filters to calendar
            if content_type:
                calendar_df = calendar_df[calendar_df['type'] == content_type]
            
            # Join metrics with content info
            if not metrics_df.empty and not calendar_df.empty:
                # Get content IDs from filtered metrics
                content_ids = metrics_df['content_id'].unique()
                
                # Filter calendar to only include these content IDs
                filtered_calendar = calendar_df[calendar_df['id'].isin(content_ids)]
                
                # Prepare performance data
                performance = []
                
                for _, content in filtered_calendar.iterrows():
                    content_metrics = metrics_df[metrics_df['content_id'] == content['id']]
                    
                    if not content_metrics.empty:
                        # Calculate aggregate metrics
                        total_views = content_metrics['views'].sum()
                        avg_time = content_metrics['avg_time_on_page'].mean() if 'avg_time_on_page' in content_metrics.columns else 0
                        total_conversions = content_metrics['conversions'].sum() if 'conversions' in content_metrics.columns else 0
                        
                        performance.append({
                            "content_id": content['id'],
                            "title": content['title'],
                            "type": content['type'],
                            "author": content['author'],
                            "publish_date": content.get('publish_date', content.get('date')),
                            "total_views": int(total_views),
                            "avg_time_on_page": float(avg_time),
                            "total_conversions": int(total_conversions),
                            "conversion_rate": float(total_conversions / total_views) if total_views > 0 else 0
                        })
                
                return {
                    "success": True,
                    "performance": performance
                }
            else:
                return {
                    "success": True,
                    "message": "No matching content or metrics found",
                    "performance": []
                }
        except Exception as e:
            logger.error(f"Failed to get content performance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_content_calendar_markdown(self, output_file=None):
        """
        Generate a markdown file with the content calendar
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated file
        """
        try:
            if output_file is None:
                output_file = self.data_dir / "content_calendar.md"
            
            with open(output_file, 'w') as f:
                f.write("# SoulCoreHub Content Calendar\n\n")
                f.write(f"Generated on: {datetime.datetime.now().isoformat()}\n\n")
                
                # Convert to DataFrame for easier manipulation
                df = pd.DataFrame(self.content_calendar)
                
                if len(df) == 0:
                    f.write("No content scheduled.\n")
                else:
                    # Sort by date
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Group by month
                    df['month'] = df['date'].dt.strftime('%Y-%m')
                    
                    months = df['month'].unique()
                    
                    for month in months:
                        month_name = pd.to_datetime(month + '-01').strftime('%B %Y')
                        f.write(f"## {month_name}\n\n")
                        
                        month_content = df[df['month'] == month]
                        
                        f.write("| Date | Title | Type | Author | Status |\n")
                        f.write("|------|-------|------|--------|--------|\n")
                        
                        for _, content in month_content.iterrows():
                            date = content['date'].strftime('%Y-%m-%d')
                            title = content['title']
                            content_type = content['type']
                            author = content['author']
                            status = content['status']
                            
                            f.write(f"| {date} | {title} | {content_type} | {author} | {status} |\n")
                        
                        f.write("\n")
            
            logger.info(f"Generated content calendar at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate content calendar: {str(e)}")
            return None
    
    def generate_content_ideas_report(self, output_file=None):
        """
        Generate a markdown report of content ideas
        
        Args:
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to generated file
        """
        try:
            if output_file is None:
                output_file = self.data_dir / "content_ideas.md"
            
            with open(output_file, 'w') as f:
                f.write("# SoulCoreHub Content Ideas\n\n")
                f.write(f"Generated on: {datetime.datetime.now().isoformat()}\n\n")
                
                # Group ideas by category
                df = pd.DataFrame(self.content_ideas)
                
                if len(df) == 0:
                    f.write("No content ideas found.\n")
                else:
                    # Sort by priority (if available)
                    if 'priority' in df.columns:
                        df = df.sort_values('priority', ascending=False)
                    
                    categories = df['category'].unique()
                    
                    for category in categories:
                        f.write(f"## {category}\n\n")
                        
                        category_ideas = df[df['category'] == category]
                        
                        for _, idea in category_ideas.iterrows():
                            f.write(f"### {idea['title']}\n\n")
                            f.write(f"**Description:** {idea['description']}\n\n")
                            
                            if 'keywords' in idea and idea['keywords']:
                                f.write(f"**Keywords:** {idea['keywords']}\n\n")
                            
                            if 'source' in idea and idea['source']:
                                f.write(f"**Source:** {idea['source']}\n\n")
                            
                            if 'priority' in idea and idea['priority']:
                                f.write(f"**Priority:** {idea['priority']}\n\n")
                            
                            if 'notes' in idea and idea['notes']:
                                f.write(f"**Notes:** {idea['notes']}\n\n")
                            
                            f.write("---\n\n")
            
            logger.info(f"Generated content ideas report at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to generate content ideas report: {str(e)}")
            return None
    
    def create_content_template(self, content_type, output_file=None):
        """
        Create a content template
        
        Args:
            content_type (str): Type of content (blog, ebook, social)
            output_file (str, optional): Path to output file
            
        Returns:
            str: Path to the generated template
        """
        try:
            if output_file is None:
                templates_dir = self.data_dir / "templates"
                templates_dir.mkdir(exist_ok=True, parents=True)
                output_file = templates_dir / f"{content_type}_template.md"
            
            with open(output_file, 'w') as f:
                if content_type == 'blog':
                    f.write("# [Title]\n\n")
                    f.write("*By [Author] | Published on [Date]*\n\n")
                    f.write("![Featured Image](image_url)\n\n")
                    f.write("## Introduction\n\n")
                    f.write("Start with a compelling hook that draws the reader in. Introduce the problem or question this blog post will address.\n\n")
                    f.write("## [Main Point 1]\n\n")
                    f.write("Explain your first main point with supporting evidence, examples, or stories.\n\n")
                    f.write("## [Main Point 2]\n\n")
                    f.write("Develop your second main point with relevant details and insights.\n\n")
                    f.write("## [Main Point 3]\n\n")
                    f.write("Present your third main point with actionable advice or deeper analysis.\n\n")
                    f.write("## Conclusion\n\n")
                    f.write("Summarize the key takeaways and provide a call to action or final thought.\n\n")
                    f.write("---\n\n")
                    f.write("*[Author Bio]*\n\n")
                    f.write("**Related Posts:**\n")
                    f.write("- [Related Post 1]\n")
                    f.write("- [Related Post 2]\n")
                    f.write("- [Related Post 3]\n")
                
                elif content_type == 'ebook':
                    f.write("# [Ebook Title]\n\n")
                    f.write("## By [Author]\n\n")
                    f.write("### Table of Contents\n\n")
                    f.write("1. Introduction\n")
                    f.write("2. Chapter 1: [Chapter Title]\n")
                    f.write("3. Chapter 2: [Chapter Title]\n")
                    f.write("4. Chapter 3: [Chapter Title]\n")
                    f.write("5. Chapter 4: [Chapter Title]\n")
                    f.write("6. Chapter 5: [Chapter Title]\n")
                    f.write("7. Conclusion\n")
                    f.write("8. About the Author\n")
                    f.write("9. Resources\n\n")
                    f.write("## Introduction\n\n")
                    f.write("Introduce the topic and explain why it matters. Outline what readers will learn and how it will benefit them.\n\n")
                    f.write("## Chapter 1: [Chapter Title]\n\n")
                    f.write("Begin your first chapter with an engaging opening. Present your first major concept or lesson.\n\n")
                    f.write("### Key Points:\n")
                    f.write("- Point 1\n")
                    f.write("- Point 2\n")
                    f.write("- Point 3\n\n")
                    f.write("### Case Study: [Title]\n\n")
                    f.write("Present a relevant case study or example.\n\n")
                    f.write("### Chapter Summary\n\n")
                    f.write("Summarize the key takeaways from this chapter.\n\n")
                
                elif content_type == 'social':
                    f.write("# Social Media Content Template\n\n")
                    f.write("## Post Type: [Image/Video/Text/Carousel]\n\n")
                    f.write("### Caption\n\n")
                    f.write("[Attention-grabbing opening line]\n\n")
                    f.write("[Main content - 2-3 paragraphs with value]\n\n")
                    f.write("[Call to action]\n\n")
                    f.write("### Hashtags\n\n")
                    f.write("#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5\n\n")
                    f.write("### Posting Schedule\n\n")
                    f.write("- Best time to post: [Time]\n")
                    f.write("- Best days: [Days]\n\n")
                    f.write("### Engagement Strategy\n\n")
                    f.write("- Respond to comments within [timeframe]\n")
                    f.write("- Ask a question to encourage responses\n")
                    f.write("- Tag relevant accounts: [@account1, @account2]\n")
                
                else:
                    f.write(f"# {content_type.capitalize()} Content Template\n\n")
                    f.write("## Overview\n\n")
                    f.write("Describe the purpose and goals of this content.\n\n")
                    f.write("## Target Audience\n\n")
                    f.write("Define who this content is for.\n\n")
                    f.write("## Key Messages\n\n")
                    f.write("- Message 1\n")
                    f.write("- Message 2\n")
                    f.write("- Message 3\n\n")
                    f.write("## Content Structure\n\n")
                    f.write("Outline the structure of your content here.\n\n")
                    f.write("## Call to Action\n\n")
                    f.write("What do you want the audience to do after consuming this content?\n")
            
            logger.info(f"Created {content_type} template at {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to create content template: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    content_strategy = ContentStrategy()
    
    # Add a sample content idea
    idea = {
        'title': 'Top 10 AI Tools for Small Business Owners',
        'description': 'A comprehensive guide to AI tools that can help small business owners automate tasks and increase productivity.',
        'category': 'ai',
        'keywords': 'ai tools, small business, automation, productivity',
        'source': 'trending topic',
        'priority': 'high'
    }
    
    content_strategy.add_content_idea(idea)
    
    # Schedule content
    content = {
        'title': 'Top 10 AI Tools for Small Business Owners',
        'type': 'blog',
        'author': 'GPTSoul',
        'date': datetime.datetime.now().isoformat(),
        'keywords': 'ai tools, small business, automation, productivity',
        'status': 'scheduled',
        'publish_date': (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
    }
    
    content_strategy.schedule_content(content)
    
    # Generate content calendar
    content_strategy.generate_content_calendar_markdown()
