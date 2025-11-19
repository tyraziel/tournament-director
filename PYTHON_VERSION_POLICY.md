# Python Version Support Policy

**Tournament Director** follows a pragmatic Python version support policy based on official Python release schedules, package ecosystem compatibility, and practical CI/CD considerations.

## Current Supported Versions

As of **November 2025**, we support the following Python versions in our CI/CD pipeline:

| Version | Release Date | End of Life | Status | CI Support |
|---------|--------------|-------------|--------|------------|
| **3.10** | Oct 2021 | Oct 2026 | Security fixes only | ✅ Supported |
| **3.11** | Oct 2022 | Oct 2027 | Security fixes only | ✅ Supported |
| **3.12** | Oct 2023 | Oct 2028 | Security fixes only | ✅ Supported |
| 3.13 | Oct 2024 | Oct 2029 | Bugfix | ❌ Not yet supported |
| 3.14 | Oct 2025 | Oct 2030 | Pre-release (alpha) | ❌ Not supported |

## Version Selection Rationale

### Why Python 3.10, 3.11, and 3.12?

1. **EOL Coverage**: All three versions have 1-6 years of security support remaining
2. **Package Compatibility**: Pre-built binary wheels available for all our C-extension dependencies:
   - `asyncpg` (PostgreSQL async driver)
   - `greenlet` (SQLAlchemy async support)
   - `aiosqlite`, `aiomysql` (database drivers)
3. **Production Readiness**: All are in "security fixes only" phase, indicating stable, production-ready releases
4. **CI Efficiency**: Fast installation without compilation overhead
5. **Broad Compatibility**: Covers most production environments and deployment targets

### Why NOT Python 3.13?

**Temporarily excluded** due to package ecosystem maturity:

- **Missing Binary Wheels**: `asyncpg` and `greenlet` lack pre-built wheels for 3.13
- **CI Build Time**: Requires compiling C extensions from source (~2-5 minutes overhead per job)
- **Build Dependencies**: Needs `build-essential`, `python3-dev`, `libpq-dev` (already installed, but adds complexity)
- **Limited Adoption**: Few production environments run 3.13 yet

**Plan**: Re-evaluate in Q2 2025 when package maintainers publish 3.13 wheels.

### Why NOT Python 3.14?

**Not production-ready**:

- **Pre-release Status**: Currently in alpha/beta (as of November 2025)
- **API Instability**: Subject to breaking changes before stable release
- **No Binary Wheels**: No packages have built wheels yet
- **CI Overhead**: Would significantly increase build times
- **No Practical Value**: Not recommended for production use

**Plan**: Add to CI matrix 6+ months after stable release (estimated mid-2026).

## Python Version Support Lifecycle

Python follows a **5-year support lifecycle** for each major version:

### Support Phases

1. **Pre-release** (6-12 months): Alpha/Beta releases, API unstable
2. **Bugfix** (1.5 years): Full support, regular bugfix releases every 1-2 months
3. **Security** (3.5 years): Security-only fixes, irregular source-only releases
4. **End of Life (EOL)**: No further updates

### Our Policy

We support Python versions that are:
- ✅ In "Bugfix" or "Security" phase
- ✅ Have pre-built wheels for critical C dependencies
- ✅ Are widely deployed in production environments
- ❌ Exclude pre-release versions (alpha/beta)
- ❌ Exclude EOL versions

## Dependency Requirements

All supported Python versions must have **pre-built binary wheels** for:

### Critical C Extensions
- `asyncpg==0.29.0` - PostgreSQL async driver
- `greenlet==3.0.3` - SQLAlchemy async support

### Other C Extensions (with fallback)
- `aiosqlite==0.20.0` - SQLite async driver (builds quickly if needed)
- `aiomysql==0.2.0` - MySQL/MariaDB driver

**Rationale**: Without pre-built wheels, CI build times increase from ~30 seconds to 3-5 minutes per job, and requires additional system dependencies (`build-essential`, `python3-dev`, `libpq-dev`).

## CI/CD Pipeline Configuration

### Current Configuration (`.github/workflows/ci.yml`)

```yaml
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ["3.10", "3.11", "3.12"]
```

### Required System Dependencies

All CI jobs install these packages to support C extension compilation (if needed):

```bash
sudo apt-get install -y build-essential python3-dev libpq-dev
```

- **build-essential**: GCC, g++, make
- **python3-dev**: Python headers for C extensions
- **libpq-dev**: PostgreSQL client library headers (for `asyncpg`)

## Version Addition Criteria

Before adding a new Python version to the CI matrix, verify:

1. **EOL Status**: Version must be in "Bugfix" or "Security" phase
2. **Wheel Availability**: Check PyPI for pre-built wheels:
   ```bash
   pip download --only-binary :all: --python-version 3.X asyncpg greenlet
   ```
3. **CI Build Time**: Test installation time on GitHub Actions
4. **Production Adoption**: Check if major deployment platforms support it
5. **Breaking Changes**: Review release notes for backward incompatibilities

## Version Removal Criteria

Remove Python versions when:

1. **EOL Reached**: Version reaches official end of life
2. **Security Risk**: Critical vulnerabilities without patches
3. **Ecosystem Drop**: Major dependencies drop support
4. **CI Overhead**: Version causes disproportionate CI slowdowns

## Testing Recommendations

### Local Development

Use **Python 3.11 or 3.12** for local development:
- Most stable
- Best IDE/tooling support
- Fastest CI feedback loop

### Production Deployment

**Recommended**: Python 3.11 or 3.12
- Proven stability in production
- Long-term security support (6-7 years remaining)
- Excellent performance improvements over 3.10

## Version Update Schedule

We review Python version support **quarterly**:

- **Q1 (January)**: Review post-Python 3.X.0 releases (October cycle)
- **Q2 (April)**: Check for EOL warnings and wheel availability
- **Q3 (July)**: Mid-year package ecosystem assessment
- **Q4 (October)**: Plan for next Python major release (annual cycle)

## References

- **Official Python Release Schedule**: https://peps.python.org/pep-0602/
- **Python Version Status**: https://devguide.python.org/versions/
- **End of Life Tracker**: https://endoflife.date/python
- **Package Index**: https://pypi.org/

---

## Historical Changes

### 2025-01-15 (Initial Policy)
- **Added**: Python 3.10, 3.11, 3.12
- **Excluded**: Python 3.13 (no binary wheels for `asyncpg`, `greenlet`)
- **Excluded**: Python 3.14 (pre-release)

---

**Last Updated**: 2025-01-15
**Next Review**: 2025-04-01 (Q2 Review)
**AIA**: EAI Hin R Claude Code [Sonnet 4.5] v1.0

---

*This document is maintained by the development team and updated quarterly based on Python release schedules and package ecosystem compatibility.*
