# SearchBridge API

*Connect your local LLMs to the web*

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

SearchBridge is a lightweight, containerized API service that enables local LLMs and automation workflows to perform web searches.



## 🌟 Features

- **Multiple Search Engine Support**:
  - Google Custom Search (with API key)
  - DuckDuckGo (no API key required)
  - Bing Search (with API key)
- **Easy to Deploy**: Full Docker containerization
- **n8n Integration**: Ready-to-use with n8n workflows
- **Customizable Response Format**: Structured JSON responses
- **Rate Limiting & Caching**: Built-in protection and performance optimization
- **Comprehensive Documentation**: Interactive API docs with Swagger UI
- **Lightweight**: Minimal dependencies and efficient resource usage

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- API keys for search engines (Google/Bing) if using those engines

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/arashmok/search-bridge.git
   cd search-bridge
   ```

2. Create your environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file to add your API keys:
   ```
   SEARCH_GOOGLE_API_KEY=your_google_api_key_here
   SEARCH_GOOGLE_CX=your_google_search_engine_id_here
   SEARCH_BING_API_KEY=your_bing_api_key_here
   ```

4. Start the service:
   ```bash
   docker-compose up -d
   ```

5. The API is now running at http://localhost:8000

### API Usage

#### Basic Search Request (POST)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest advancements in AI",
    "engine": "google",
    "num_results": 5
  }'
```

#### Basic Search Request (GET)

```bash
curl "http://localhost:8000/search?query=latest%20advancements%20in%20AI&engine=google&num_results=5"
```

#### Response Format

```json
{
  "query": "latest advancements in AI",
  "results": [
    {
      "title": "Recent AI Breakthrough Shows Promise for...",
      "link": "https://example.com/ai-news/breakthrough",
      "snippet": "Researchers have developed a new approach to...",
      "source": "google",
      "position": 1,
      "additional_data": { ... }
    },
    ...
  ],
  "total_results": 5,
  "search_time": 0.897,
  "engine": "google"
}
```

## 🔧 Configuration

All configuration options are available through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_GOOGLE_API_KEY` | Google Custom Search API key | None |
| `SEARCH_GOOGLE_CX` | Google Custom Search engine ID | None |
| `SEARCH_BING_API_KEY` | Bing Search API key | None |
| `SEARCH_API_HOST` | Host to bind the API service | 0.0.0.0 |
| `SEARCH_API_PORT` | Port for the API service | 8000 |
| `SEARCH_LOG_LEVEL` | Logging level | INFO |
| `SEARCH_ENABLE_RATE_LIMIT` | Enable rate limiting | true |
| `SEARCH_RATE_LIMIT` | Max requests per hour | 100 |
| `SEARCH_ENABLE_CACHE` | Enable result caching | true |
| `SEARCH_CACHE_TTL` | Cache TTL in seconds | 3600 |

## 🔗 Integration with n8n

SearchBridge is designed to work seamlessly with n8n workflows:

1. Add an **HTTP Request** node in your n8n workflow
2. Configure it to call the SearchBridge API endpoint
3. Process the results and pass them to your local LLM node

See the [integration documentation](docs/n8n-integration.md) for complete workflow examples.

## 📊 Example n8n LLM Workflow

Here's a simple n8n workflow that:
1. Receives a question via webhook
2. Searches the web using SearchBridge
3. Passes search results to a local LLM
4. Returns the LLM's answer



## 🧩 Architecture

SearchBridge uses a clean, modular architecture:

- **FastAPI**: High-performance web framework
- **Search Engines**: Modular implementations for different providers
- **Configuration**: Environment-based settings with sensible defaults
- **Docker**: Containerization for easy deployment
- **Async Processing**: Non-blocking request handling

## 🛣️ Roadmap

- [ ] Add more search engines (Yandex, Qwant, etc.)
- [ ] Implement content extraction from search results
- [ ] Add authentication mechanism
- [ ] Support for specialized search types (news, images)
- [ ] Result filtering options
- [ ] Web UI for testing and monitoring

## 🔒 Security Considerations

- The API doesn't include authentication by default - consider adding API keys for production
- For production, deploy behind a reverse proxy with HTTPS
- Consider network-level restrictions (firewall rules, container networking)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [n8n](https://n8n.io/) - Workflow automation tool
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- [Bing Web Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)

</p>
