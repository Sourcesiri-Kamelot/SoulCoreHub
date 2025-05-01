#!/usr/bin/env python3
"""
multimodal_integration.py — Multimodal integration for Anima
Implements image and audio analysis capabilities and environmental awareness
"""

import os
import sys
import json
import logging
import time
import threading
import base64
import io
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sounddevice as sd
import soundfile as sf
import librosa

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("anima_multimodal.log"),
        logging.StreamHandler()
    ]
)

class MultimodalIntegration:
    """Multimodal integration for Anima with image and audio analysis"""
    
    def __init__(self, base_path=None):
        """Initialize the multimodal integration system"""
        self.base_path = base_path or Path.home() / "SoulCoreHub"
        self.data_path = self.base_path / "data" / "multimodal"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Image analysis settings
        self.image_path = self.data_path / "images"
        self.image_path.mkdir(parents=True, exist_ok=True)
        self.image_history = []
        self.image_history_file = self.data_path / "image_history.json"
        
        # Audio analysis settings
        self.audio_path = self.data_path / "audio"
        self.audio_path.mkdir(parents=True, exist_ok=True)
        self.audio_history = []
        self.audio_history_file = self.data_path / "audio_history.json"
        
        # Environmental awareness settings
        self.environment_data = {
            "audio_level": 0.0,
            "last_audio_event": None,
            "last_image_event": None,
            "room_activity": "unknown",
            "time_of_day": "unknown",
            "last_updated": datetime.now().isoformat()
        }
        self.environment_file = self.data_path / "environment.json"
        
        # Load history and environment data
        self._load_data()
        
        # Initialize monitoring threads
        self.monitoring_audio = False
        self.monitoring_thread = None
        
        logging.info("Multimodal integration system initialized")
    
    def _load_data(self):
        """Load history and environment data"""
        try:
            # Load image history
            if self.image_history_file.exists():
                with open(self.image_history_file, "r") as f:
                    self.image_history = json.load(f)
                logging.info(f"Loaded image history with {len(self.image_history)} entries")
            
            # Load audio history
            if self.audio_history_file.exists():
                with open(self.audio_history_file, "r") as f:
                    self.audio_history = json.load(f)
                logging.info(f"Loaded audio history with {len(self.audio_history)} entries")
            
            # Load environment data
            if self.environment_file.exists():
                with open(self.environment_file, "r") as f:
                    self.environment_data = json.load(f)
                logging.info("Loaded environment data")
        
        except Exception as e:
            logging.error(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save history and environment data"""
        try:
            # Save image history
            with open(self.image_history_file, "w") as f:
                json.dump(self.image_history, f, indent=2)
            
            # Save audio history
            with open(self.audio_history_file, "w") as f:
                json.dump(self.audio_history, f, indent=2)
            
            # Save environment data
            with open(self.environment_file, "w") as f:
                json.dump(self.environment_data, f, indent=2)
            
            logging.info("Saved multimodal data")
        
        except Exception as e:
            logging.error(f"Error saving data: {e}")
    
    def analyze_image(self, image_path=None, image_data=None, save_image=True, use_api=True):
        """Analyze an image for content and objects"""
        try:
            # Load image
            if image_path:
                image = Image.open(image_path)
            elif image_data:
                if isinstance(image_data, str) and image_data.startswith("data:image"):
                    # Handle data URL
                    image_data = image_data.split(",")[1]
                    image_data = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_data))
                elif isinstance(image_data, bytes):
                    image = Image.open(io.BytesIO(image_data))
                else:
                    raise ValueError("Invalid image data format")
            else:
                raise ValueError("Either image_path or image_data must be provided")
            
            # Basic image properties
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            # Save image if requested
            saved_path = None
            if save_image:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.{format_name.lower()}"
                saved_path = str(self.image_path / filename)
                image.save(saved_path)
            
            # Analyze image content
            if use_api:
                # Use external API for image analysis
                analysis = self._analyze_image_with_api(image)
            else:
                # Use local analysis (simplified)
                analysis = self._analyze_image_local(image)
            
            # Create result
            result = {
                "timestamp": datetime.now().isoformat(),
                "width": width,
                "height": height,
                "format": format_name,
                "mode": mode,
                "saved_path": saved_path,
                "analysis": analysis
            }
            
            # Add to history
            self.image_history.append(result)
            if len(self.image_history) > 100:  # Limit history size
                self.image_history = self.image_history[-100:]
            
            # Update environment data
            self.environment_data["last_image_event"] = {
                "timestamp": result["timestamp"],
                "description": analysis.get("description", "Unknown image content")
            }
            self.environment_data["last_updated"] = datetime.now().isoformat()
            
            # Save data
            self._save_data()
            
            return result
        
        except Exception as e:
            logging.error(f"Error analyzing image: {e}")
            return {"error": str(e)}
    
    def _analyze_image_local(self, image):
        """Analyze image locally (simplified)"""
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Resize for analysis
        image_small = image.resize((100, 100))
        pixels = np.array(image_small)
        
        # Calculate average color
        avg_color = pixels.mean(axis=(0, 1))
        
        # Calculate brightness
        brightness = pixels.mean()
        
        # Determine if image is dark or bright
        if brightness < 100:
            brightness_desc = "dark"
        elif brightness > 150:
            brightness_desc = "bright"
        else:
            brightness_desc = "medium brightness"
        
        # Determine dominant color
        r, g, b = avg_color
        if r > g and r > b:
            dominant_color = "red"
        elif g > r and g > b:
            dominant_color = "green"
        elif b > r and b > g:
            dominant_color = "blue"
        else:
            dominant_color = "gray"
        
        # Create simple description
        description = f"A {brightness_desc} image with dominant {dominant_color} tones"
        
        return {
            "description": description,
            "brightness": float(brightness),
            "dominant_color": dominant_color,
            "avg_color": [float(r), float(g), float(b)],
            "objects": []  # No object detection in local analysis
        }
    
    def _analyze_image_with_api(self, image):
        """Analyze image using an external API"""
        # This is a placeholder for using an external API
        # In a real implementation, this would call a service like Google Cloud Vision, Azure Computer Vision, etc.
        
        # For now, fall back to local analysis
        return self._analyze_image_local(image)
    
    def capture_image_from_camera(self, camera_index=0):
        """Capture an image from the camera"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
                temp_path = temp.name
            
            # Use system command to capture image
            if sys.platform == "darwin":  # macOS
                cmd = ["imagesnap", "-w", "1", temp_path]
            elif sys.platform == "linux":
                cmd = ["fswebcam", "-r", "1280x720", "--no-banner", temp_path]
            elif sys.platform == "win32":
                # On Windows, this is more complex and might require additional libraries
                logging.error("Camera capture not implemented for Windows")
                return {"error": "Camera capture not implemented for Windows"}
            else:
                logging.error(f"Unsupported platform: {sys.platform}")
                return {"error": f"Unsupported platform: {sys.platform}"}
            
            # Execute command
            subprocess.run(cmd, check=True)
            
            # Analyze the captured image
            result = self.analyze_image(image_path=temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return result
        
        except Exception as e:
            logging.error(f"Error capturing image: {e}")
            return {"error": str(e)}
    
    def analyze_audio(self, audio_path=None, audio_data=None, duration=5, sample_rate=16000, save_audio=True):
        """Analyze audio for content and features"""
        try:
            # Record audio if no path or data provided
            if not audio_path and not audio_data:
                audio_data, sample_rate = self.record_audio(duration, sample_rate)
            
            # Load audio
            if audio_path:
                audio_data, sample_rate = sf.read(audio_path)
            
            # Save audio if requested
            saved_path = None
            if save_audio and audio_data is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_{timestamp}.wav"
                saved_path = str(self.audio_path / filename)
                sf.write(saved_path, audio_data, sample_rate)
            
            # Analyze audio content
            analysis = self._analyze_audio_features(audio_data, sample_rate)
            
            # Create result
            result = {
                "timestamp": datetime.now().isoformat(),
                "duration": len(audio_data) / sample_rate if audio_data is not None else None,
                "sample_rate": sample_rate,
                "saved_path": saved_path,
                "analysis": analysis
            }
            
            # Add to history
            self.audio_history.append(result)
            if len(self.audio_history) > 100:  # Limit history size
                self.audio_history = self.audio_history[-100:]
            
            # Update environment data
            self.environment_data["audio_level"] = analysis.get("rms", 0.0)
            self.environment_data["last_audio_event"] = {
                "timestamp": result["timestamp"],
                "description": analysis.get("description", "Unknown audio content")
            }
            self.environment_data["last_updated"] = datetime.now().isoformat()
            
            # Save data
            self._save_data()
            
            return result
        
        except Exception as e:
            logging.error(f"Error analyzing audio: {e}")
            return {"error": str(e)}
    
    def _analyze_audio_features(self, audio_data, sample_rate):
        """Analyze audio features"""
        try:
            # Convert to mono if stereo
            if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Calculate basic features
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Calculate zero crossing rate
            zero_crossings = np.sum(np.abs(np.diff(np.signbit(audio_data))))
            zero_crossing_rate = zero_crossings / len(audio_data)
            
            # Determine if audio is silent, speech, or music (simplified)
            if rms < 0.01:
                content_type = "silence"
                description = "Silence or very quiet audio"
            elif zero_crossing_rate > 0.1:
                content_type = "speech"
                description = "Speech or vocal content"
            else:
                content_type = "music"
                description = "Music or ambient sound"
            
            # Calculate spectral features if librosa is available
            spectral_features = {}
            try:
                # Spectral centroid
                spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
                spectral_features["centroid_mean"] = float(np.mean(spectral_centroid))
                
                # Spectral bandwidth
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
                spectral_features["bandwidth_mean"] = float(np.mean(spectral_bandwidth))
                
                # Spectral contrast
                spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
                spectral_features["contrast_mean"] = float(np.mean(spectral_contrast))
            except Exception as e:
                logging.warning(f"Error calculating spectral features: {e}")
            
            return {
                "rms": float(rms),
                "zero_crossing_rate": float(zero_crossing_rate),
                "content_type": content_type,
                "description": description,
                "spectral_features": spectral_features
            }
        
        except Exception as e:
            logging.error(f"Error analyzing audio features: {e}")
            return {
                "description": "Error analyzing audio",
                "error": str(e)
            }
    
    def record_audio(self, duration=5, sample_rate=16000):
        """Record audio from the microphone"""
        try:
            # Record audio
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()
            
            # Convert to the right format
            audio_data = audio_data.flatten()
            
            return audio_data, sample_rate
        
        except Exception as e:
            logging.error(f"Error recording audio: {e}")
            return None, None
    
    def start_environment_monitoring(self, interval=60):
        """Start monitoring the environment"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logging.warning("Environment monitoring is already running")
            return False
        
        self.monitoring_audio = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logging.info(f"Environment monitoring started with interval {interval} seconds")
        return True
    
    def stop_environment_monitoring(self):
        """Stop monitoring the environment"""
        self.monitoring_audio = False
        logging.info("Environment monitoring stopped")
    
    def _monitoring_loop(self, interval):
        """Environment monitoring loop"""
        while self.monitoring_audio:
            try:
                # Monitor audio levels
                self.analyze_audio(duration=1, save_audio=False)
                
                # Determine room activity based on audio level
                audio_level = self.environment_data["audio_level"]
                if audio_level < 0.01:
                    activity = "quiet"
                elif audio_level < 0.05:
                    activity = "moderate"
                else:
                    activity = "active"
                
                self.environment_data["room_activity"] = activity
                
                # Determine time of day
                hour = datetime.now().hour
                if 5 <= hour < 12:
                    time_of_day = "morning"
                elif 12 <= hour < 17:
                    time_of_day = "afternoon"
                elif 17 <= hour < 22:
                    time_of_day = "evening"
                else:
                    time_of_day = "night"
                
                self.environment_data["time_of_day"] = time_of_day
                self.environment_data["last_updated"] = datetime.now().isoformat()
                
                # Save environment data
                self._save_data()
            
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
            
            # Sleep until next monitoring cycle
            time.sleep(interval)
    
    def get_environment_status(self):
        """Get the current environment status"""
        return self.environment_data
    
    def get_image_history(self, limit=10):
        """Get recent image history"""
        return self.image_history[-limit:]
    
    def get_audio_history(self, limit=10):
        """Get recent audio history"""
        return self.audio_history[-limit:]
    
    def annotate_image(self, image_path, annotations):
        """Annotate an image with bounding boxes and text"""
        try:
            # Load image
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("Arial", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Draw annotations
            for annotation in annotations:
                if "box" in annotation:
                    # Draw bounding box
                    box = annotation["box"]
                    draw.rectangle(box, outline="red", width=3)
                
                if "text" in annotation and "position" in annotation:
                    # Draw text
                    text = annotation["text"]
                    position = annotation["position"]
                    draw.text(position, text, fill="red", font=font)
            
            # Save annotated image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"annotated_{timestamp}.jpg"
            output_path = str(self.image_path / filename)
            image.save(output_path)
            
            return output_path
        
        except Exception as e:
            logging.error(f"Error annotating image: {e}")
            return None

# For testing
if __name__ == "__main__":
    multimodal = MultimodalIntegration()
    
    # Test audio analysis
    print("Recording and analyzing audio...")
    audio_result = multimodal.analyze_audio(duration=3)
    print(f"Audio analysis: {audio_result['analysis']['description']}")
    print(f"Audio level: {audio_result['analysis']['rms']:.4f}")
    
    # Test environment monitoring
    print("\nStarting environment monitoring...")
    multimodal.start_environment_monitoring(interval=5)
    
    # Wait for some monitoring cycles
    print("Monitoring environment for 15 seconds...")
    time.sleep(15)
    
    # Get environment status
    status = multimodal.get_environment_status()
    print("\nEnvironment status:")
    print(f"Room activity: {status['room_activity']}")
    print(f"Time of day: {status['time_of_day']}")
    print(f"Audio level: {status['audio_level']:.4f}")
    
    # Stop monitoring
    multimodal.stop_environment_monitoring()
    print("\nEnvironment monitoring stopped")
    
    # Test image analysis if a camera is available
    try:
        print("\nTrying to capture and analyze an image from camera...")
        image_result = multimodal.capture_image_from_camera()
        if "error" not in image_result:
            print(f"Image analysis: {image_result['analysis']['description']}")
            print(f"Image saved to: {image_result['saved_path']}")
            
            # Test image annotation
            annotations = [
                {"box": (50, 50, 200, 200), "text": "Test Object", "position": (50, 30)}
            ]
            annotated_path = multimodal.annotate_image(image_result['saved_path'], annotations)
            if annotated_path:
                print(f"Annotated image saved to: {annotated_path}")
        else:
            print(f"Error capturing image: {image_result['error']}")
    except Exception as e:
        print(f"Error testing image capture: {e}")
