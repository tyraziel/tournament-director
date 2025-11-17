# Tournament Director Design Decisions & Deferred Items

*AIA PAI Hin R Claude Code v1.0*

## 📋 Decision Log

### Data Model Architecture
- **UUID + Sequence ID Pattern**: ✅ **DECIDED** - Use UUIDs for global identity, sequence IDs for human-readable tournament numbering
- **Component-Based Tournament Structure**: ✅ **DECIDED** - Swiss → Elimination via separate components rather than monolithic structure
- **Computed vs Stored Standings**: ✅ **DECIDED** - Calculate standings dynamically from match results, don't store them
- **Multi-TCG Support**: ✅ **DECIDED** - Four-tier format classification (GameSystem, BaseFormat, sub_format, card_pool)
- **Embedded Registration Control**: ✅ **DECIDED** - RegistrationControl embedded in Tournament rather than separate entity

### Backend Architecture  
- **Three Backend Pattern**: ✅ **DECIDED** - Mock (memory), Local (files), Database (PostgreSQL) 
- **Data Layer Abstraction**: ✅ **DECIDED** - Single interface implemented by all three backends
- **Pydantic Models Everywhere**: ✅ **DECIDED** - Same models used by TUI, API, backends for consistency

### Tournament Management
- **Player Re-entry Handling**: ❓ **DEFERRED** - Create new registration vs reactivate dropped registration?
- **Swiss Tiebreaker Implementation**: ❓ **DEFERRED** - Real-time calculation vs cached values vs precomputed tables?
- **Sequence ID Uniqueness**: ❓ **DEFERRED** - Enforce at model level, data layer, or database constraints?

### Code Quality
- **Pydantic json_encoders Deprecation**: ❓ **DEFERRED** - Migrate to modern serialization (warnings functional but deprecated)
- **Foreign Key Validation**: ❓ **DEFERRED** - Enforce referential integrity at model level vs data layer
- **Data Integrity Constraints**: ❓ **DEFERRED** - Where to validate uniqueness and relationships

### Database Backend Architecture
- **Implementation Approach**: ✅ **DECIDED** - Single SQLAlchemy backend supporting both PostgreSQL and SQLite
- **Connection Strategy**: ✅ **DECIDED** - Database URL-based configuration (same code, different connection strings)
- **Schema Management**: ✅ **DECIDED** - Alembic migrations for version control
- **Development Priority**: ✅ **DECIDED** - SQLite first (zero config), PostgreSQL second (production)
- **Repository Pattern**: ✅ **DECIDED** - Same interface as Mock/Local, SQLAlchemy implementation
- **Foreign Key Enforcement**: ✅ **DECIDED** - Database-level constraints vs application-level validation

## 🔮 Future Token Series Items

### Phase 1: Data Layer Implementation
- [x] Design abstract data layer interface
- [x] Implement Mock backend (in-memory)
- [x] Implement Local JSON backend (file-based)
- [ ] Implement Database backend (PostgreSQL/SQLite) - **DEFERRED**
- [x] Add comprehensive backend test suite using seed data

### Phase 2: API Server
- [ ] FastAPI server with backend abstraction
- [ ] REST endpoints for all CRUD operations
- [ ] Authentication and authorization system
- [ ] API seed data endpoints (`/admin/seed/kitchen-table-pauper`)
- [ ] OpenAPI documentation and validation

### Phase 3: TUI Application  
- [ ] Textual framework implementation
- [ ] Tournament management screens
- [ ] Real-time tournament monitoring
- [ ] Player registration and management
- [ ] Swiss pairing algorithm implementation
- [ ] Results entry and standings display

### Phase 4: Database Backend (Deferred)
- [ ] SQLAlchemy table definitions and relationships
- [ ] Alembic migration system setup
- [ ] Database repository implementation (async)
- [ ] SQLite backend (development/small tournaments)
- [ ] PostgreSQL backend (production/multi-user)
- [ ] Database constraint enforcement vs application validation
- [ ] Connection pooling and transaction management
- [ ] Database performance optimization

### Phase 5: Advanced Features
- [ ] Swiss tiebreaker calculations (OMW%, GW%, OGW%)
- [ ] Elimination bracket generation and management  
- [ ] Tournament export (standings, pairings, results)
- [ ] Multi-tournament series support
- [ ] Deck list submission and validation
- [ ] Judge penalty system
- [ ] Timer and scheduling system

### Phase 6: Discord Bot
- [ ] Discord.py integration with API
- [ ] Tournament commands (`!tournament create`, `!register`, `!pairings`)
- [ ] Results reporting via Discord
- [ ] Tournament announcements and notifications
- [ ] Discord-specific tournament management

### Phase 7: Production Deployment
- [ ] Docker containerization
- [ ] Database migrations and versioning
- [ ] CI/CD pipeline implementation  
- [ ] Monitoring and logging
- [ ] Performance optimization
- [ ] Security audit and hardening

### Database Backend Implementation Details

**Complexity Assessment**: Medium difficulty (~10-14 hours focused development)

**Required Dependencies**:
```txt
sqlalchemy[asyncio]==2.0.31    # Async ORM
alembic==1.12.1               # Schema migrations  
asyncpg==0.29.0               # PostgreSQL async driver
aiosqlite==0.19.0             # SQLite async driver
```

**Architecture Approach**:
- Single `DatabaseDataLayer` class works with both PostgreSQL and SQLite
- Connection string determines backend: `sqlite:///./tournament.db` vs `postgresql://...`
- Same repository implementation for both databases
- SQLAlchemy table definitions map directly to Pydantic models
- Alembic handles schema versioning and migrations

**Development Strategy**:
1. Start with SQLite (zero deployment complexity)
2. Add PostgreSQL support (just connection string change)
3. Database-level foreign key constraints vs application validation
4. Connection pooling and async transaction management

**Estimated Effort Breakdown**:
- SQLAlchemy schema definition: 2-3 hours
- Repository async implementation: 4-5 hours  
- Alembic migration system: 1-2 hours
- Testing and integration: 2-3 hours
- Documentation: 1 hour

**Decision**: Deferred to focus on API server development first. Mock + Local JSON backends provide sufficient functionality for current development needs.

## 🤔 Open Questions for Future Sessions

### Technical Decisions
1. **Player Re-entry Strategy**: New registration record vs status change on existing?
   - New registration: Full audit trail, cleaner sequence IDs
   - Status change: Simpler logic, preserves original registration time

2. **Swiss Tiebreaker Performance**: Real-time vs cached?
   - Real-time: Always accurate, potentially slow with large tournaments
   - Cached: Fast display, complexity in cache invalidation

3. **Data Validation Layer**: Where to enforce constraints?
   - Pydantic models: Early validation, but limited relationship checking
   - Data layer: Comprehensive validation, consistent across backends  
   - Database: Ultimate consistency, but backend-specific

4. **Tournament State Transitions**: Automatic vs manual?
   - Automatic: `registration_open` → `in_progress` when first round starts
   - Manual: TO controls all state changes explicitly

5. **Match Result Validation**: How strict?
   - Strict: Validate game counts match format rules (BO3 = max 3 games)
   - Flexible: Allow any combination for edge cases and manual corrections

### Architecture Questions
1. **API Authentication**: Simple tokens vs OAuth2 vs custom?
2. **Database Schema**: Single database vs microservice pattern?
3. **Real-time Updates**: WebSockets vs Server-Sent Events vs polling?
4. **Caching Strategy**: Redis vs in-memory vs database-level?
5. **File Storage**: Local files vs S3 vs database blobs for exports?

### User Experience
1. **TUI vs Web Interface**: Primary interface for tournament management?
2. **Mobile Support**: Native app vs responsive web?
3. **Offline Mode**: How to handle connectivity issues during tournaments?
4. **Multi-language Support**: Tournament management in different languages?
5. **Accessibility**: Screen reader support, keyboard navigation?

## 📝 Session Notes

### Current Session (Token Context Exhaustion)
- ✅ Completed comprehensive data model audit
- ✅ Updated DATA_MODEL.md to match implementation  
- ✅ Created robust seed data generation system
- ✅ Validated all tournament scenarios work correctly
- 🔄 Ready to design data layer interface next session

### Key Insights
- **Kitchen Table Vibes Preserved**: Pauper priority maintained throughout
- **Multi-TCG Architecture Works**: Successfully tested 5 different game systems
- **Seed Data Comprehensive**: Complete tournaments with realistic match results  
- **Foundation Solid**: 24/24 tests passing, clean lint, proper architecture

### Technical Debt
- Pydantic `json_encoders` deprecation warnings (functional but should migrate)
- Data integrity validation not yet implemented
- Swiss tiebreaker calculations not implemented
- Player re-entry workflow undefined

## 🎯 Success Metrics

### Completed This Phase
- [x] Complete Pydantic data model implementation
- [x] Comprehensive test coverage (24/24 tests passing)
- [x] Multi-TCG support validation
- [x] Tournament lifecycle modeling
- [x] Seed data generation system
- [x] Clean code quality (ruff + lint passing)

### Next Phase Targets
- [ ] Abstract data layer interface designed
- [ ] Mock backend implementation
- [ ] Local backend implementation  
- [ ] Backend test coverage > 90%
- [ ] Integration tests with seed data
- [ ] Performance benchmarks established

---

*This document will be updated each session to track progress and maintain context across token boundaries.*