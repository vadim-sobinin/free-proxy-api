# free-proxy-api

REST API service for managing free proxies. Fork of [free-proxy](https://github.com/jundymek/free-proxy).

## What's Added

- **REST API endpoints** to get proxies easily
- **Docker** for quick deployment
- **docker-compose** to use with other services
- **Interactive API docs** at `/docs`

## Quick Start

### Using Docker Compose

```bash
docker-compose up -d
curl http://localhost:8000/health
```

### Using Docker

```bash
docker build -t free-proxy-api .
docker run -d -p 8000:8000 free-proxy-api
```

### From Docker Hub

```bash
docker pull vadimsobinin/free-proxy-api:latest
docker run -d -p 8000:8000 vadimsobinin/free-proxy-api:latest
```

## API Endpoints

### Get Single Proxy

```bash
curl "http://localhost:8000/proxy?country=US"
```

Response:

```json
{
  "proxy": "http://113.160.218.14:8888",
  "schema": "http",
  "country": "US"
}
```

### Get Proxy Config (for requests/Playwright)

```bash
curl "http://localhost:8000/proxy/config?country=US"
```

Response:

```json
{
  "proxy_url": "http://113.160.218.14:8888",
  "requests": { "http": "http://113.160.218.14:8888" },
  "playwright": { "server": "http://113.160.218.14:8888" }
}
```

### Get Proxy List

```bash
curl "http://localhost:8000/proxies?country=US&limit=5"
```

Response:

```json
{
  "proxies": ["http://1.1.1.1:8888", "http://2.2.2.2:8080"],
  "count": 2,
  "country": "US"
}
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

## Query Parameters

| Name        | Type   | Default | Description                         |
| ----------- | ------ | ------- | ----------------------------------- |
| `country`   | string | -       | Country code (US, GB, RU, KZ, etc.) |
| `timeout`   | float  | 1.0     | Proxy check timeout in seconds      |
| `random`    | bool   | false   | Randomize selection                 |
| `anonymous` | bool   | false   | Only anonymous proxies              |
| `elite`     | bool   | false   | Only elite proxies                  |
| `https`     | bool   | false   | Only HTTPS proxies                  |
| `google`    | bool   | null    | Google compatible only              |
| `limit`     | int    | 10      | Max results (1-100) for `/proxies`  |

## Usage with Other Services

### Python Example

```python
import requests

# Get proxy config
response = requests.get('http://free-proxy-api:8000/proxy/config?country=US')
config = response.json()

# Use in requests
data = requests.get('https://example.com', proxies=config['requests'])
```

### Docker Compose Integration

```yaml
services:
  my-app:
    image: my-app:latest
    environment:
      PROXY_API: http://free-proxy-api:8000
    depends_on:
      - free-proxy-api

  free-proxy-api:
    image: vadimsobinin/free-proxy-api:latest
    ports:
      - '8000:8000'
```

## Image Size

Optimized Docker image: **~130MB**

## Environment Variables

```env
API_PORT=8000
```

## Interactive Docs

Open in browser after starting:

```
http://localhost:8000/docs
```

Test all endpoints directly in Swagger UI.

## Proxy Sources

- https://www.sslproxies.org/
- https://www.us-proxy.org/
- https://free-proxy-list.net/uk-proxy.html
- https://free-proxy-list.net/

## Links

- **GitHub Repository**: https://github.com/vadim-sobinin/free-proxy-api
- **Docker Hub**: https://hub.docker.com/r/vadimsobinin/free-proxy-api
- **Original Project**: https://github.com/jundymek/free-proxy

## License

MIT (inherited from [free-proxy](https://github.com/jundymek/free-proxy))

## Credits

Based on [free-proxy](https://github.com/jundymek/free-proxy) by [jundymek](https://github.com/jundymek)

Maintained by [vadim-sobinin](https://github.com/vadim-sobinin)
