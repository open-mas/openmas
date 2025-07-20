# Session Storage

## Overview

The OpenMAS Session Storage system provides mechanisms for persisting session data across interactions. It offers multiple backend options with different performance characteristics and use cases while ensuring consistent access patterns regardless of the chosen backend.

## Storage Interface

All storage backends implement a common interface:

```python
class SessionStorage:
    """Abstract interface for session storage backends."""

    async def get(self, session_id):
        """Get a session by ID."""
        raise NotImplementedError()

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        raise NotImplementedError()

    async def delete(self, session_id):
        """Delete a session by ID."""
        raise NotImplementedError()

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        raise NotImplementedError()

    async def cleanup(self):
        """Clean up expired sessions."""
        raise NotImplementedError()
```

This interface ensures that session operations work consistently across all storage backends.

## Storage Backends

The session management system supports these storage backends:

### Memory Storage

Memory storage keeps session data in memory, suitable for development or ephemeral sessions.

#### Configuration

```yaml
sessions:
  storage:
    type: "memory"
    expiration: 3600  # in seconds
```

#### Characteristics

- **Performance**: Fastest, no I/O overhead
- **Persistence**: None (lost on restart)
- **Scalability**: Limited to single instance
- **Use Cases**: Development, testing, ephemeral interactions

#### Implementation Details

Memory storage uses an in-memory dictionary to store session data:

```python
class MemoryStorage(SessionStorage):
    """In-memory session storage."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.sessions = {}
        self.expiration = config.get("expiration", 3600)  # Default 1 hour

    async def get(self, session_id):
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Check if expired
        last_accessed = datetime.fromisoformat(session.get("last_accessed", session.get("created_at")))
        if (datetime.now() - last_accessed).total_seconds() > self.expiration:
            # Session expired
            await self.delete(session_id)
            return None

        return session

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        self.sessions[session_id] = session_data
        return True

    async def delete(self, session_id):
        """Delete a session by ID."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        if prefix:
            ids = [sid for sid in self.sessions.keys() if sid.startswith(prefix)]
        else:
            ids = list(self.sessions.keys())

        return ids[:limit]

    async def cleanup(self):
        """Clean up expired sessions."""
        now = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            last_accessed = datetime.fromisoformat(session.get("last_accessed", session.get("created_at")))
            if (now - last_accessed).total_seconds() > self.expiration:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.delete(session_id)

        return len(expired_sessions)
```

### File Storage

File storage persists sessions to the file system, suitable for simple persistence needs.

#### Configuration

```yaml
sessions:
  storage:
    type: "file"
    directory: "./sessions"
    format: "json"  # or pickle, yaml
    expiration: 86400  # in seconds
```

#### Characteristics

- **Performance**: Moderate, I/O bound
- **Persistence**: Durable across restarts
- **Scalability**: Limited to single server
- **Use Cases**: Single-server deployments, development

#### Implementation Details

File storage saves each session as a separate file:

```python
class FileStorage(SessionStorage):
    """File-based session storage."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.directory = config.get("directory", "./sessions")
        self.format = config.get("format", "json")
        self.expiration = config.get("expiration", 86400)  # Default 1 day

        # Ensure directory exists
        os.makedirs(self.directory, exist_ok=True)

    def _get_filename(self, session_id):
        """Get the filename for a session ID."""
        # Use a hash function to ensure safe filenames
        hashed = hashlib.md5(session_id.encode()).hexdigest()
        return os.path.join(self.directory, f"{hashed}.{self.format}")

    async def get(self, session_id):
        """Get a session by ID."""
        filename = self._get_filename(session_id)
        if not os.path.exists(filename):
            return None

        try:
            with open(filename, "r") as f:
                session = json.load(f)

            # Check if expired
            last_accessed = datetime.fromisoformat(session.get("last_accessed", session.get("created_at")))
            if (datetime.now() - last_accessed).total_seconds() > self.expiration:
                # Session expired
                await self.delete(session_id)
                return None

            return session
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        filename = self._get_filename(session_id)
        try:
            with open(filename, "w") as f:
                json.dump(session_data, f)
            return True
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False

    async def delete(self, session_id):
        """Delete a session by ID."""
        filename = self._get_filename(session_id)
        if os.path.exists(filename):
            try:
                os.remove(filename)
                return True
            except Exception as e:
                logger.error(f"Error deleting session {session_id}: {e}")
        return False

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        session_ids = []
        count = 0

        for filename in os.listdir(self.directory):
            if not filename.endswith(f".{self.format}"):
                continue

            if count >= limit:
                break

            try:
                with open(os.path.join(self.directory, filename), "r") as f:
                    session = json.load(f)

                session_id = session.get("id")
                if session_id and (not prefix or session_id.startswith(prefix)):
                    session_ids.append(session_id)
                    count += 1
            except Exception:
                continue

        return session_ids

    async def cleanup(self):
        """Clean up expired sessions."""
        now = datetime.now()
        expired_count = 0

        for filename in os.listdir(self.directory):
            if not filename.endswith(f".{self.format}"):
                continue

            try:
                with open(os.path.join(self.directory, filename), "r") as f:
                    session = json.load(f)

                last_accessed = datetime.fromisoformat(session.get("last_accessed", session.get("created_at")))
                if (now - last_accessed).total_seconds() > self.expiration:
                    os.remove(os.path.join(self.directory, filename))
                    expired_count += 1
            except Exception:
                continue

        return expired_count
```

### Database Storage

Database storage persists sessions to a database, ideal for production environments.

#### Configuration

```yaml
sessions:
  storage:
    type: "database"
    connection_string: "${DB_CONNECTION_STRING}"
    table_name: "agent_sessions"
    expiration: 604800  # in seconds (7 days)
```

#### Characteristics

- **Performance**: Good, depends on database
- **Persistence**: Highly durable
- **Scalability**: Excellent, supports distributed deployments
- **Use Cases**: Production, multi-server deployments

#### Implementation Details

Database storage uses an SQL or NoSQL database:

```python
class DatabaseStorage(SessionStorage):
    """Database-based session storage."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.connection_string = config.get("connection_string")
        self.table_name = config.get("table_name", "agent_sessions")
        self.expiration = config.get("expiration", 604800)  # Default 7 days

        # Set up database connection
        self.db = self._setup_database()

    def _setup_database(self):
        """Set up database connection."""
        # Implementation depends on the database type
        # This is a simplified example using SQLAlchemy
        from sqlalchemy import create_engine, Table, Column, String, JSON, MetaData

        engine = create_engine(self.connection_string)
        metadata = MetaData()

        # Define sessions table
        sessions_table = Table(
            self.table_name,
            metadata,
            Column("session_id", String, primary_key=True),
            Column("data", JSON),
            Column("created_at", String),
            Column("last_accessed", String)
        )

        # Create table if it doesn't exist
        metadata.create_all(engine)

        return engine

    async def get(self, session_id):
        """Get a session by ID."""
        # Implementation using SQLAlchemy
        from sqlalchemy import text

        query = text(f"SELECT data FROM {self.table_name} WHERE session_id = :session_id")

        with self.db.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            row = result.fetchone()

            if not row:
                return None

            session = row[0]

            # Check if expired
            last_accessed = datetime.fromisoformat(session.get("last_accessed", session.get("created_at")))
            if (datetime.now() - last_accessed).total_seconds() > self.expiration:
                # Session expired
                await self.delete(session_id)
                return None

            return session

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        # Implementation using SQLAlchemy
        from sqlalchemy import text

        now = datetime.now().isoformat()

        upsert_query = text(f"""
            INSERT INTO {self.table_name} (session_id, data, created_at, last_accessed)
            VALUES (:session_id, :data, :created_at, :last_accessed)
            ON CONFLICT (session_id) DO UPDATE
            SET data = :data, last_accessed = :last_accessed
        """)

        with self.db.connect() as conn:
            conn.execute(upsert_query, {
                "session_id": session_id,
                "data": session_data,
                "created_at": session_data.get("created_at", now),
                "last_accessed": now
            })
            conn.commit()

        return True

    async def delete(self, session_id):
        """Delete a session by ID."""
        # Implementation using SQLAlchemy
        from sqlalchemy import text

        delete_query = text(f"DELETE FROM {self.table_name} WHERE session_id = :session_id")

        with self.db.connect() as conn:
            conn.execute(delete_query, {"session_id": session_id})
            conn.commit()

        return True

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        # Implementation using SQLAlchemy
        from sqlalchemy import text

        if prefix:
            query = text(f"SELECT session_id FROM {self.table_name} WHERE session_id LIKE :prefix LIMIT :limit")
            params = {"prefix": f"{prefix}%", "limit": limit}
        else:
            query = text(f"SELECT session_id FROM {self.table_name} LIMIT :limit")
            params = {"limit": limit}

        with self.db.connect() as conn:
            result = conn.execute(query, params)
            return [row[0] for row in result]

    async def cleanup(self):
        """Clean up expired sessions."""
        # Implementation using SQLAlchemy
        from sqlalchemy import text

        now = datetime.now()
        expiration_threshold = (now - timedelta(seconds=self.expiration)).isoformat()

        cleanup_query = text(f"""
            DELETE FROM {self.table_name}
            WHERE last_accessed < :threshold
        """)

        with self.db.connect() as conn:
            result = conn.execute(cleanup_query, {"threshold": expiration_threshold})
            conn.commit()

            return result.rowcount
```

### Redis Storage

Redis storage uses Redis for high-performance, distributed session management.

#### Configuration

```yaml
sessions:
  storage:
    type: "redis"
    host: "${REDIS_HOST:-localhost}"
    port: "${REDIS_PORT:-6379}"
    db: 0
    prefix: "openmas:session:"
    expiration: 86400  # in seconds
```

#### Characteristics

- **Performance**: Excellent, in-memory with persistence
- **Persistence**: Configurable (RDB, AOF)
- **Scalability**: Excellent, supports clustering
- **Use Cases**: High-performance production, distributed deployments

#### Implementation Details

Redis storage uses Redis as a fast, distributed key-value store:

```python
class RedisStorage(SessionStorage):
    """Redis-based session storage."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6379)
        self.db = config.get("db", 0)
        self.prefix = config.get("prefix", "openmas:session:")
        self.expiration = config.get("expiration", 86400)  # Default 1 day

        # Set up Redis connection
        import redis
        self.redis = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            decode_responses=False
        )

    def _get_key(self, session_id):
        """Get the Redis key for a session ID."""
        return f"{self.prefix}{session_id}"

    async def get(self, session_id):
        """Get a session by ID."""
        key = self._get_key(session_id)
        data = self.redis.get(key)

        if not data:
            return None

        try:
            session = json.loads(data)

            # Update expiration
            self.redis.expire(key, self.expiration)

            return session
        except Exception as e:
            logger.error(f"Error deserializing session {session_id}: {e}")
            return None

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        key = self._get_key(session_id)
        try:
            data = json.dumps(session_data)
            self.redis.set(key, data, ex=self.expiration)
            return True
        except Exception as e:
            logger.error(f"Error serializing session {session_id}: {e}")
            return False

    async def delete(self, session_id):
        """Delete a session by ID."""
        key = self._get_key(session_id)
        result = self.redis.delete(key)
        return result > 0

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        search_pattern = f"{self.prefix}{prefix or ''}*"
        keys = self.redis.keys(search_pattern)

        # Extract session IDs from keys
        session_ids = []
        for key in keys[:limit]:
            key_str = key.decode("utf-8")
            session_id = key_str[len(self.prefix):]
            session_ids.append(session_id)

        return session_ids

    async def cleanup(self):
        """Clean up expired sessions."""
        # Redis automatically expires keys, so no manual cleanup is needed
        return 0
```

## Custom Storage Backends

The session storage system can be extended with custom storage backends by implementing the `SessionStorage` interface:

```python
class CustomStorage(SessionStorage):
    """Custom session storage backend."""

    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        # Custom initialization

    async def get(self, session_id):
        """Get a session by ID."""
        # Custom implementation

    async def set(self, session_id, session_data):
        """Store a session by ID."""
        # Custom implementation

    async def delete(self, session_id):
        """Delete a session by ID."""
        # Custom implementation

    async def list(self, prefix=None, limit=100):
        """List session IDs, optionally filtered by prefix."""
        # Custom implementation

    async def cleanup(self):
        """Clean up expired sessions."""
        # Custom implementation
```

Custom storage backends are registered in the unified configuration:

```yaml
sessions:
  storage:
    type: "custom"
    class: "my_package.storage.CustomStorage"
    # Custom configuration options
```

## Storage Feature Comparison

| Feature | Memory | File | Database | Redis |
|---------|--------|------|----------|-------|
| Performance | Fastest | Moderate | Good | Excellent |
| Persistence | None | File-based | High | Configurable |
| Distributed | No | No | Yes | Yes |
| Auto-expiration | Manual | Manual | Manual | Automatic |
| Query Support | Basic | Basic | Advanced | Basic |
| Scalability | Low | Low | High | High |
| Complexity | Low | Low | High | Medium |

## Best Practices

1. **Development Environment**: Use Memory or File storage for simplicity
2. **Single-Server Production**: Use File or Redis storage for good performance
3. **Multi-Server Production**: Use Database or Redis storage for distribution
4. **High-Performance Needs**: Use Redis storage for optimal performance
5. **Complex Queries**: Use Database storage for advanced query capabilities

## Integration with Observability

The session storage system integrates with the OpenMAS observability system:

```yaml
sessions:
  storage:
    type: "redis"
    # Redis configuration

  analytics:
    enabled: true
    tracking_level: "standard"
    metrics:
      - "storage_operation_time"
      - "storage_operation_count"
      - "storage_size"
```

This integration provides visibility into storage performance and usage.
