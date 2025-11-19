# Authentication Strategy Decisions Needed

**Created**: 2025-11-19
**Status**: 🚧 Decision Required
**AIA**: EAI Hin R Claude Code [Sonnet 4.5] v1.0

---

## 📋 Overview

This document outlines the key decisions needed to implement authentication for the Tournament Director API. These decisions will shape the authentication architecture, user experience, and development roadmap.

**Current State**: Basic auth infrastructure exists (`APIKey` model, token generation utility) but is not implemented or integrated.

**Goal**: Define authentication strategy before implementation to avoid refactoring pain.

---

## 🔐 Decision 1: Who Authenticates?

### Question
**Who needs to authenticate to use the API?**

### Options

#### A. Tournament Organizers Only
**Who**: People running tournaments (TOs)
**Use Case**: Only TOs need accounts to create/manage tournaments
**Players**: Players are just records in the database (no accounts)

**Pros**:
- ✅ Simpler system (fewer user types)
- ✅ Lower security burden (fewer accounts to protect)
- ✅ Faster to implement

**Cons**:
- ❌ Players can't view their own tournament history
- ❌ No player self-service (registration, deck list submission)
- ❌ Discord bot must use TO's API key (security concern)

**Example Flow**:
```
TO creates account → TO creates tournament → TO registers players (manually)
Players interact via TO or in-person only
```

---

#### B. Players and Organizers
**Who**: Both players and TOs have accounts
**Players can**: View history, register for tournaments, submit results
**TOs can**: Create/manage tournaments, override results, drop players

**Pros**:
- ✅ Player self-service (register, view history)
- ✅ Better Discord bot integration (players use their own accounts)
- ✅ Scales to larger tournaments
- ✅ Audit trail (who submitted what)

**Cons**:
- ❌ More complex role system
- ❌ More user management overhead
- ❌ Need player onboarding flow

**Example Flow**:
```
Player creates account → Player registers for tournament → Player views pairings
TO creates tournament → TO manages rounds → TO resolves disputes
```

---

#### C. Organizers + Optional Player Accounts
**Who**: TOs must have accounts, players optionally can
**Hybrid**: TOs can register players manually OR players can self-register

**Pros**:
- ✅ Flexible for different tournament types
- ✅ Supports kitchen table (no player accounts needed)
- ✅ Supports larger events (player self-service)

**Cons**:
- ❌ Most complex to implement
- ❌ Confusing user model

**Example Flow**:
```
Small tournament: TO creates accounts for all players
Large tournament: Players self-register with their own accounts
```

---

### Decision
**Choose**: [ ] A - TOs only  |  [ ] B - Players + TOs  |  [ ] C - Hybrid

**Reasoning**:
```
[Your thoughts here]
```

---

## 🎭 Decision 2: Authentication Method

### Question
**How do users prove their identity?**

### Options

#### A. API Key Only (No Passwords)
**Structure**: Generate long-lived API tokens for trusted users

**How it works**:
```
TO emails you → You manually create API key → They use it forever
No registration, no login, just tokens
```

**Pros**:
- ✅ Dead simple implementation
- ✅ No password security concerns
- ✅ Perfect for programmatic access (bots, scripts)
- ✅ No session management

**Cons**:
- ❌ No self-service (you must create all accounts)
- ❌ No web UI login (tokens only)
- ❌ No password reset flow
- ❌ Doesn't scale (manual account creation)

**Best for**: Internal tools, trusted users, Discord bot

---

#### B. JWT with Password Authentication
**Structure**: Email + password → Login → Get JWT tokens

**How it works**:
```
User registers with email/password → Login returns JWT → Use JWT for requests
JWT expires after X hours → Refresh with refresh token
```

**Pros**:
- ✅ Self-service registration
- ✅ Standard OAuth2 password flow
- ✅ Works with web UIs
- ✅ Refresh tokens for security
- ✅ Industry standard

**Cons**:
- ❌ Need password hashing (bcrypt/argon2)
- ❌ Need email verification?
- ❌ Need password reset flow
- ❌ More complex than API keys

**Best for**: Web TUI, user-facing applications, scalable systems

---

#### C. Hybrid (JWT for Users + API Keys for Services)
**Structure**: Both JWT and API keys, unified auth system

**How it works**:
```
Users: Register → Login → Get JWT → Use JWT
Services: Request API key → Get long-lived token → Use token
API accepts both: Authorization: Bearer <jwt_or_api_key>
```

**Pros**:
- ✅ Flexible for all use cases
- ✅ Human users get good UX (JWT)
- ✅ Bots/scripts get simple tokens (API keys)
- ✅ Best of both worlds

**Cons**:
- ❌ Most complex to implement
- ❌ Two auth systems to maintain
- ❌ More testing surface

**Best for**: Production systems with multiple client types

---

#### D. OAuth2 Providers (Discord, Google, GitHub)
**Structure**: Login via external provider (Discord OAuth)

**How it works**:
```
User clicks "Login with Discord" → Discord auth → Get JWT from our API
No password storage, provider handles identity
```

**Pros**:
- ✅ No password management
- ✅ Users already have accounts
- ✅ Perfect for Discord-focused tournaments
- ✅ Better security (provider responsibility)

**Cons**:
- ❌ External dependency (Discord API)
- ❌ Need fallback auth method?
- ❌ OAuth flow complexity
- ❌ Users must have Discord account

**Best for**: Discord-integrated tournaments, social platforms

---

### Decision
**Choose**: [ ] A - API Keys  |  [ ] B - JWT  |  [ ] C - Hybrid  |  [ ] D - OAuth2

**Reasoning**:
```
[Your thoughts here]
```

---

## 👥 Decision 3: User Roles & Permissions

### Question
**What can different users do?**

### Options

#### A. Simple Ownership Model
**Roles**: None
**Permissions**: You can only modify things you created

**Rules**:
```
✅ Anyone can create a tournament
✅ Only creator can modify their tournament
✅ Only creator can delete their tournament
❌ No admin override
❌ No delegation
```

**Pros**:
- ✅ Dead simple to implement
- ✅ No RBAC complexity
- ✅ Clear ownership model

**Cons**:
- ❌ No admin users
- ❌ Can't transfer tournament ownership
- ❌ Can't have co-organizers

---

#### B. Role-Based (Player, Organizer, Admin)
**Roles**: Player, Organizer, Admin
**Permissions**: Different capabilities per role

**Rules**:
```
Player:
  ✅ Register for tournaments
  ✅ View own history
  ❌ Create tournaments

Organizer:
  ✅ Everything Player can do
  ✅ Create/modify/delete own tournaments
  ✅ Manage players in their tournaments
  ❌ Modify other organizers' tournaments

Admin:
  ✅ Everything
  ✅ Modify any tournament
  ✅ Delete any tournament
  ✅ Manage users
```

**Pros**:
- ✅ Clear separation of concerns
- ✅ Supports admin override
- ✅ Scalable for larger systems

**Cons**:
- ❌ More complex implementation
- ❌ Need role management UI
- ❌ Need permission checks everywhere

---

#### C. Fine-Grained Permissions (RBAC with Scopes)
**Roles**: Flexible, custom permissions per user
**Permissions**: Granular scopes (tournaments.create, tournaments.delete, etc.)

**Rules**:
```
Scopes:
  - tournaments.create
  - tournaments.read
  - tournaments.update
  - tournaments.delete
  - players.manage
  - matches.submit
  - api_keys.manage

Users have custom scope combinations
```

**Pros**:
- ✅ Maximum flexibility
- ✅ Industry standard (OAuth2 scopes)
- ✅ Can delegate specific permissions

**Cons**:
- ❌ Very complex
- ❌ Overkill for most use cases
- ❌ Slow to implement

---

### Decision
**Choose**: [ ] A - Simple Ownership  |  [ ] B - Roles  |  [ ] C - Fine-Grained

**Reasoning**:
```
[Your thoughts here]
```

---

## 📱 Decision 4: Primary Client Type

### Question
**What is the main way users will interact with the API?**

### Options

#### A. Textual TUI (Terminal UI)
**Interface**: Terminal-based UI for tournament organizers

**Implications**:
- Need seamless terminal login flow
- Store JWT locally (~/.config/tournament-director/token)
- Re-authenticate on token expiry
- Tab completion, keyboard shortcuts

**Auth UX**:
```bash
$ tournament-director login
Email: user@example.com
Password: ********
✅ Logged in as user@example.com

$ tournament-director create-tournament --name "Pauper Weekly"
```

---

#### B. Discord Bot
**Interface**: Discord commands for players and TOs

**Implications**:
- Bot uses API key (long-lived token)
- Players use Discord IDs (no separate accounts?)
- Or players link Discord to API account
- Ephemeral messages for sensitive data

**Auth UX**:
```
Player: !register Tournament123
Bot: ✅ Registered Alice for Tournament123

TO: !pair-round Tournament123 1
Bot: ✅ Round 1 pairings posted
```

---

#### C. Web Dashboard (Future)
**Interface**: Web UI for tournament management

**Implications**:
- Standard login page
- Session cookies or JWT in localStorage
- Password reset via email
- Admin dashboard

**Auth UX**:
```
User visits https://tournaments.example.com
Logs in with email/password
Manages tournaments via web UI
```

---

#### D. Mobile App (Future)
**Interface**: Native iOS/Android app

**Implications**:
- OAuth2 mobile flow
- Biometric auth (Face ID, fingerprint)
- Push notifications
- Offline mode with token refresh

---

### Decision
**Choose**: [ ] A - TUI  |  [ ] B - Discord Bot  |  [ ] C - Web  |  [ ] D - Mobile

**Reasoning**:
```
[Your thoughts here]
```

---

## 🔑 Decision 5: Password Requirements

**Only relevant if choosing JWT/password authentication**

### Question
**What password security do we enforce?**

### Options

#### A. Minimal (Length Only)
**Rules**: Minimum 8 characters

**Pros**:
- ✅ User-friendly
- ✅ Simple validation

**Cons**:
- ❌ Less secure

---

#### B. Standard (Length + Complexity)
**Rules**:
- Minimum 8 characters
- At least one uppercase
- At least one number
- At least one special character

**Pros**:
- ✅ Industry standard
- ✅ Better security

**Cons**:
- ❌ Users hate complexity rules
- ❌ Encourages weak passwords (Password1!)

---

#### C. Passphrase (Length Only, Higher Minimum)
**Rules**: Minimum 12-16 characters (no complexity required)

**Pros**:
- ✅ More secure (higher entropy)
- ✅ Easier to remember ("correct horse battery staple")
- ✅ Modern best practice

**Cons**:
- ❌ Users expect complexity rules

---

### Decision
**Choose**: [ ] A - Minimal  |  [ ] B - Standard  |  [ ] C - Passphrase

**Reasoning**:
```
[Your thoughts here]
```

---

## 📧 Decision 6: Email Verification

**Only relevant if choosing JWT/password authentication**

### Question
**Do users need to verify their email address?**

### Options

#### A. No Email Verification
**Flow**: Register → Immediate login

**Pros**:
- ✅ Faster onboarding
- ✅ No email service needed
- ✅ Simpler implementation

**Cons**:
- ❌ Fake emails allowed
- ❌ No password reset capability
- ❌ Can't contact users

---

#### B. Email Verification Required
**Flow**: Register → Verify email → Can login

**Pros**:
- ✅ Verified contact info
- ✅ Enables password reset
- ✅ Prevents spam accounts

**Cons**:
- ❌ Need email service (SendGrid, Mailgun)
- ❌ Slower onboarding
- ❌ Users may not verify

---

#### C. Optional Email Verification
**Flow**: Register → Can login immediately → Nag to verify

**Pros**:
- ✅ Fast onboarding
- ✅ Can verify later
- ✅ Enables password reset if verified

**Cons**:
- ❌ Complex state management
- ❌ Users may never verify

---

### Decision
**Choose**: [ ] A - No Verification  |  [ ] B - Required  |  [ ] C - Optional

**Reasoning**:
```
[Your thoughts here]
```

---

## 🔄 Decision 7: Token Expiry

**Relevant for JWT authentication**

### Question
**How long should access tokens last?**

### Options

#### A. Short-Lived (15 minutes)
**Access Token**: 15 minutes
**Refresh Token**: 7 days

**Pros**:
- ✅ Most secure
- ✅ Limits damage from stolen token
- ✅ Industry best practice

**Cons**:
- ❌ Frequent refreshes
- ❌ More complex client code

---

#### B. Medium (1 hour)
**Access Token**: 1 hour
**Refresh Token**: 30 days

**Pros**:
- ✅ Good balance
- ✅ Less frequent refreshes
- ✅ Still reasonably secure

**Cons**:
- ❌ 1-hour window for stolen tokens

---

#### C. Long-Lived (24 hours)
**Access Token**: 24 hours
**Refresh Token**: 90 days

**Pros**:
- ✅ Rare refreshes
- ✅ Better UX (rarely re-login)

**Cons**:
- ❌ Less secure
- ❌ Larger attack window

---

#### D. No Expiry (API Key Style)
**Access Token**: Never expires (until revoked)

**Pros**:
- ✅ Simplest UX
- ✅ No refresh logic needed

**Cons**:
- ❌ Security nightmare
- ❌ Not recommended for JWT

---

### Decision
**Choose**: [ ] A - 15min  |  [ ] B - 1hr  |  [ ] C - 24hr  |  [ ] D - No expiry

**Reasoning**:
```
[Your thoughts here]
```

---

## 🎯 Recommended Starting Point

Based on typical tournament management needs, here's a suggested starting configuration:

### 🏁 Phase 1 (MVP)
**Decision 1**: B - Players + TOs
**Decision 2**: B - JWT with Passwords
**Decision 3**: B - Roles (Player, Organizer, Admin)
**Decision 4**: A - TUI (primary client)
**Decision 5**: A - Minimal password requirements
**Decision 6**: A - No email verification (for now)
**Decision 7**: B - 1 hour access tokens

**Rationale**: Covers 80% of use cases, minimal complexity, can expand later

### 🚀 Phase 2 (Enhanced)
Add:
- API Keys for Discord bot
- Email verification (optional)
- Password reset flow

### 🌟 Phase 3 (Full-Featured)
Add:
- OAuth2 providers (Discord, Google)
- Fine-grained permissions
- Web dashboard
- 2FA support

---

## 📝 Your Decisions

Fill this out and we'll implement accordingly:

```yaml
authentication:
  who_authenticates: ""           # TOs only | Players + TOs | Hybrid
  auth_method: ""                 # API Keys | JWT | Hybrid | OAuth2
  roles: ""                       # Simple | Roles | Fine-Grained
  primary_client: ""              # TUI | Discord | Web | Mobile

passwords:
  requirements: ""                # Minimal | Standard | Passphrase
  email_verification: ""          # None | Required | Optional

tokens:
  access_token_expiry: ""         # 15min | 1hr | 24hr | Never
  refresh_token_expiry: ""        # 7days | 30days | 90days

implementation:
  branch_strategy: ""             # This branch | New branch
  priority: ""                    # High | Medium | Low
```

---

## ❓ Questions to Consider

Before making final decisions, think about:

1. **Scale**: How many users? (10s, 100s, 1000s?)
2. **Trust Model**: Who runs tournaments? (You only, community organizers, anyone?)
3. **Data Sensitivity**: What needs protection? (Tournament results are public?)
4. **Development Time**: How much complexity can you afford now?
5. **Future Plans**: What features are on the roadmap?

---

**Next Steps**: Fill out your decisions above, then create an implementation branch!
