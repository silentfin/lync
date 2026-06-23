# Lync
A URL shortener built with FastAPI and PostgreSQL.

**Visit site: https://745368.xyz**

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves frontend |
| POST | `/` | Shorten a URL |
| GET | `/{short_code}` | Redirect to original URL |
| GET | `/{short_code}/stats` | Get click analytics |
| GET | `/api/links` | List all shortened URLs |

##  Getting Started
1. Clone the repository:
    ```bash
    git clone https://github.com/silentfin/lync.git
    cd lync
    ```

2. Create a `.env` file in the root directory:
    ```bash
    DATABASE_URL=your_postgresql_connection_string
    ```

3. Install dependencies:
    ```bash
    uv sync
    ```

4. Run in development mode:
    ```bash
    fastapi dev main.py
    ```

5. Run tests:
    ```bash
    pytest
    ```

## Roadmap
- [x] URL shortening with collision-resistant code generation
- [x] URL deduplication
- [x] Click tracking and analytics
- [x] SQL injection prevention with parameterized queries
- [x] pytest test suite
- [x] Deployment on Railway with custom domain
- [ ] Rate limiting to prevent abuse
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions
- [ ] API documentation with Swagger/OpenAPI
- [ ] Make it beautiful

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
