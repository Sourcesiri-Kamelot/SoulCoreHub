# Anima Internet Access

This module enables Anima to access the internet and various APIs to retrieve information, search the web, and interact with online services.

## Features

- **Web Search**: Search the internet for information
- **API Access**: Connect to various APIs for specialized data
- **Webpage Content**: Retrieve and analyze content from webpages
- **News Retrieval**: Get the latest news on various topics
- **Weather Information**: Get weather forecasts for any location
- **API Detection**: Automatically detect which API to use based on queries
- **Webpage Summarization**: Generate concise summaries of webpages

## Setup

### Prerequisites

- Python 3.7 or higher
- Required Python packages: `requests`, `beautifulsoup4`

### Installation

Install the required dependencies:

```bash
bash ~/SoulCoreHub/scripts/install_dependencies.sh
```

### API Keys

To enable full functionality, you'll need to set up API keys for various services. You can do this in two ways:

1. **Environment Variables**:
   ```bash
   export SERP_API_KEY="your_serp_api_key"
   export NEWSAPI_KEY="your_newsapi_key"
   export WEATHER_API_KEY="your_weather_api_key"
   ```

2. **Configuration File**:
   Create a file at `~/SoulCoreHub/config/api_keys.json` with the following structure:
   ```json
   {
     "SERP_API_KEY": "your_serp_api_key",
     "NEWSAPI_KEY": "your_newsapi_key",
     "WEATHER_API_KEY": "your_weather_api_key"
   }
   ```

## Usage

Anima will automatically use the internet access module when appropriate. You can ask questions like:

- "What's the weather in New York?"
- "Search for the latest news about artificial intelligence"
- "Find information about quantum computing"
- "Summarize the content of this webpage: https://example.com"

## Available APIs

### Web Search

Searches the web for information using either SerpAPI (if configured) or direct web scraping.

```
Anima> Search for climate change solutions
```

### News API

Retrieves news articles on specific topics or categories using NewsAPI.

```
Anima> Get the latest news about technology
```

### Weather API

Gets weather information for a location using WeatherAPI.

```
Anima> What's the weather in Tokyo?
```

### Webpage Content

Retrieves and processes the content of webpages.

```
Anima> Get the content of https://example.com
```

### Webpage Summarization

Generates a concise summary of a webpage.

```
Anima> Summarize https://example.com
```

## API Detection

Anima can automatically detect which API to use based on your query. For example:

- "What's the weather in Paris?" → Weather API
- "Latest news about space exploration" → News API
- "Search for machine learning tutorials" → Web Search API

## Caching

To improve performance and reduce API calls, results are cached for a configurable period (default: 24 hours). Weather data has a shorter cache expiry (1 hour) to ensure freshness.

## Limitations

- Without API keys, some features will use fallback methods with limited capabilities
- Web scraping is used as a fallback and may not always work reliably due to website changes
- Rate limits may apply depending on the API service used

## Integration with MCP

The internet access module is integrated with the SoulCore MCP (Model Context Protocol) system, allowing Anima to use it seamlessly with other capabilities.

## Privacy and Security

- API keys are stored locally and never shared
- Web requests include a generic user agent to respect website policies
- No personal data is collected or stored beyond caching for performance

## Troubleshooting

If you encounter issues:

1. Check that the required dependencies are installed
2. Verify that API keys are correctly configured
3. Check the log file: `internet_access.log`
4. Ensure your internet connection is working properly
