# Tournament Director API Specification

## Overview

RESTful API for tournament management supporting multiple TCG formats with focus on Magic: The Gathering Pauper tournaments.

**Base URL**: `https://api.tournament-director.com/v1`  
**Content Type**: `application/json`  
**Authentication**: Bearer token (JWT)

## Core Principles

- **RESTful**: Standard HTTP methods and status codes
- **Type Safe**: All inputs/outputs defined with Pydantic models  
- **Async**: Full async/await support
- **Paginated**: List endpoints support pagination
- **Filtered**: List endpoints support filtering
- **Documented**: Auto-generated OpenAPI/Swagger docs

## Authentication & Authorization

### Authentication Endpoints

```http
POST /auth/login
POST /auth/logout  
POST /auth/refresh
GET  /auth/me
```

### Authorization Levels
- **Public**: No auth required (read-only tournament data)
- **Player**: Authenticated player (register, view own data)
- **Organizer**: Tournament organizer (manage own tournaments)
- **Admin**: System administrator (manage all data)

## Player Management

### Endpoints

```http
GET    /players                    # List all players
POST   /players                    # Create player
GET    /players/{id}               # Get player by ID
PUT    /players/{id}               # Update player
DELETE /players/{id}               # Delete player
GET    /players/search?name={name} # Search by name
GET    /players/discord/{id}       # Get by Discord ID
```

### Player Model
```json
{
  "id": "uuid",
  "name": "string",
  "discord_id": "string?",
  "email": "string?", 
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Examples

**Create Player:**
```http
POST /players
{
  "name": "Alice Johnson",
  "discord_id": "alice#1234",
  "email": "alice@example.com"
}
```

**List Players:**
```http
GET /players?limit=20&offset=0&search=alice
```

## Venue Management

### Endpoints

```http
GET    /venues           # List all venues
POST   /venues           # Create venue  
GET    /venues/{id}      # Get venue by ID
PUT    /venues/{id}      # Update venue
DELETE /venues/{id}      # Delete venue
```

### Venue Model
```json
{
  "id": "uuid",
  "name": "string",
  "address": "string?",
  "description": "string?",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Format Management

### Endpoints

```http
GET    /formats                     # List all formats
POST   /formats                     # Create format
GET    /formats/{id}                # Get format by ID  
PUT    /formats/{id}                # Update format
DELETE /formats/{id}                # Delete format
GET    /formats/game/{system}       # List by game system
```

### Format Model
```json
{
  "id": "uuid",
  "name": "string",
  "game_system": "magic_the_gathering | pokemon | star_wars_unlimited | ...",
  "base_format": "constructed | limited | special",
  "sub_format": "string?",
  "card_pool": "string",
  "match_structure": "string?",
  "description": "string?",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Tournament Management

### Endpoints

```http
GET    /tournaments                    # List tournaments
POST   /tournaments                    # Create tournament
GET    /tournaments/{id}               # Get tournament
PUT    /tournaments/{id}               # Update tournament
DELETE /tournaments/{id}               # Delete tournament
GET    /tournaments/status/{status}    # Filter by status
GET    /tournaments/venue/{venue_id}   # Filter by venue
GET    /tournaments/format/{format_id} # Filter by format
GET    /tournaments/organizer/{user_id}# Filter by organizer
```

### Tournament Model
```json
{
  "id": "uuid",
  "name": "string",
  "status": "draft | registration_open | registration_closed | in_progress | completed | cancelled",
  "visibility": "public | private | unlisted",
  "registration": {
    "open_date": "datetime?",
    "close_date": "datetime?", 
    "max_players": "int?",
    "allow_to_override": "bool"
  },
  "format_id": "uuid",
  "venue_id": "uuid",
  "created_by": "uuid",
  "description": "string?",
  "start_date": "datetime?",
  "end_date": "datetime?",
  "registration_deadline": "datetime?",
  "auto_advance_rounds": "bool",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Tournament Status Flow
```
draft → registration_open → registration_closed → in_progress → completed
                ↓
            cancelled (from any state)
```

## Registration Management

### Endpoints

```http
GET    /tournaments/{id}/registrations           # List registrations
POST   /tournaments/{id}/registrations           # Register player
GET    /tournaments/{id}/registrations/{reg_id}  # Get registration
PUT    /tournaments/{id}/registrations/{reg_id}  # Update registration
DELETE /tournaments/{id}/registrations/{reg_id}  # Cancel registration
GET    /players/{id}/registrations               # Player's registrations
```

### Registration Model
```json
{
  "id": "uuid",
  "tournament_id": "uuid",
  "player_id": "uuid", 
  "sequence_id": "int",
  "status": "active | late_entry | dropped | disqualified",
  "registered_at": "datetime",
  "updated_at": "datetime"
}
```

## Tournament Structure Management

### Component Endpoints

```http
GET    /tournaments/{id}/components         # List components
POST   /tournaments/{id}/components         # Add component
GET    /tournaments/{id}/components/{c_id}  # Get component
PUT    /tournaments/{id}/components/{c_id}  # Update component  
DELETE /tournaments/{id}/components/{c_id}  # Delete component
```

### Component Model
```json
{
  "id": "uuid",
  "tournament_id": "uuid",
  "type": "swiss | single_elimination | double_elimination | round_robin",
  "name": "string",
  "sequence_order": "int",
  "config": {
    "rounds": "int?",
    "pairing_method": "string?",
    "cut_size": "int?",
    "reseed_rounds": "bool?"
  },
  "created_at": "datetime"
}
```

## Round Management

### Round Endpoints

```http
GET    /tournaments/{id}/rounds              # List all rounds
GET    /components/{id}/rounds               # List component rounds
POST   /components/{id}/rounds               # Create round
GET    /rounds/{id}                         # Get round
PUT    /rounds/{id}                         # Update round
DELETE /rounds/{id}                         # Delete round
```

### Round Model
```json
{
  "id": "uuid",
  "tournament_id": "uuid",
  "component_id": "uuid",
  "round_number": "int",
  "status": "pending | active | completed | cancelled",
  "time_limit_minutes": "int?",
  "scheduled_start": "datetime?",
  "scheduled_end": "datetime?",
  "auto_advance": "bool",
  "start_time": "datetime?",
  "end_time": "datetime?",
  "created_at": "datetime"
}
```

## Match Management

### Match Endpoints

```http
GET    /tournaments/{id}/matches       # Tournament matches
GET    /rounds/{id}/matches            # Round matches  
GET    /components/{id}/matches        # Component matches
GET    /players/{id}/matches           # Player matches
POST   /rounds/{id}/matches            # Create match
GET    /matches/{id}                   # Get match
PUT    /matches/{id}                   # Update match (report result)
DELETE /matches/{id}                   # Delete match
```

### Match Model  
```json
{
  "id": "uuid",
  "tournament_id": "uuid",
  "component_id": "uuid", 
  "round_id": "uuid",
  "round_number": "int",
  "table_number": "int?",
  "player1_id": "uuid",
  "player2_id": "uuid?",
  "player1_wins": "int",
  "player2_wins": "int", 
  "draws": "int",
  "notes": "string?",
  "reported_at": "datetime?",
  "created_at": "datetime"
}
```

## Data Management

### Seed & Health Endpoints

```http
POST   /admin/seed                # Seed test data
DELETE /admin/clear               # Clear all data  
GET    /health                    # Health check
GET    /metrics                   # System metrics
```

## Pagination

List endpoints support pagination:

```http
GET /players?limit=20&offset=40
```

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 40,
  "has_next": true,
  "has_prev": true
}
```

## Filtering & Search

### Common Filters
- `?search=term` - Text search
- `?status=value` - Status filtering
- `?created_after=2024-01-01` - Date filtering  
- `?sort=field` - Sorting (`-field` for descending)

### Examples
```http
GET /tournaments?status=in_progress&format_id=uuid&sort=-created_at
GET /players?search=john&limit=10
GET /matches?player_id=uuid&tournament_id=uuid
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created  
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict (duplicate)
- `422` - Validation Error
- `500` - Internal Server Error

### Error Response Format
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input data",
    "details": {
      "field": "name",
      "issue": "must be at least 2 characters"
    }
  }
}
```

## Rate Limiting

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour  
- **Admin**: 5000 requests/hour

Rate limit headers included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhooks (Future)

For real-time updates to Discord bots and TUI clients:

```http
POST /webhooks/tournaments/{id}/subscribe
DELETE /webhooks/tournaments/{id}/unsubscribe
```

## OpenAPI Documentation

Interactive API documentation available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## SDK & Client Libraries (Future)

- Python SDK for TUI integration
- JavaScript SDK for web clients
- Discord.py integration helpers

## Implementation Priority

### Phase 1: Core API
1. ✅ Player management
2. ✅ Venue management  
3. ✅ Format management
4. ✅ Basic tournament CRUD

### Phase 2: Tournament Flow
1. Registration management
2. Component/round structure
3. Match creation and results
4. Tournament status management

### Phase 3: Advanced Features  
1. Authentication & authorization
2. **Auto-progression system** (scheduled rounds, registration deadlines)
3. Real-time updates
4. Advanced filtering/search
5. Webhook system

### Phase 4: Integration
1. Discord bot endpoints
2. TUI-specific endpoints  
3. Bulk operations
4. Data export/import

This specification provides a complete REST API that supports all tournament management workflows while maintaining clean separation between the API layer and our existing data layer.