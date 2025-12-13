---
adr: 0003
title: Dual-Mode Analysis (AI + Keyword Fallback)
date: 2025-11-26
status: Accepted
---

# ADR-0003: Dual-Mode Analysis (AI + Keyword Fallback)

## Status

✅ **Accepted**

**Date**: 2025-11-26

## Context

The Claude Code Generator needs to analyze natural language project descriptions to:
- Determine project type (SaaS, API, mobile, hardware/IoT, data science)
- Extract technology stack (backend framework, frontend framework, database)
- Identify features (auth, payments, websockets, email)
- Generate accurate configuration for template selection

Challenges:
- Users may not have an Anthropic API key (offline use, privacy concerns, cost)
- API calls can fail due to network issues, rate limits, or service outages
- The tool should be usable without internet connectivity
- Analysis quality should gracefully degrade rather than fail completely
- Setup friction should be minimal - the tool should work immediately after installation

## Decision

We will implement a **dual-mode analysis strategy**: AI-powered analysis with automatic keyword-based fallback.

**Architecture**:
1. On initialization, check for `ANTHROPIC_API_KEY` environment variable
2. If API key exists: Use Claude API for intelligent, context-aware analysis
3. If API key missing: Use regex keyword matching for basic analysis
4. Both modes return the same `ProjectConfig` structure (Pydantic validated)

**Implementation**:
```python
if self.client:
    # Use Claude API for intelligent analysis
    config_dict = self._analyze_with_claude(description, project_name)
else:
    # Fallback to keyword-based analysis
    config_dict = self._analyze_with_keywords(description, project_name)
```

**Keyword Fallback Logic**:
- Project type detection: Pattern matching keywords (iot/sensor→hardware-iot, mobile/ios→mobile-app, etc.)
- Framework inference: Sensible defaults per project type (FastAPI for API services, React Native for mobile)
- Feature extraction: Keyword presence (auth→authentication, payment→payments)
- Name extraction: First 3 words of description if not provided

## Consequences

**Positive:**
- **Zero setup friction**: Tool works immediately without API key configuration
- **Graceful degradation**: Reduced intelligence instead of complete failure
- **Offline capability**: Works without internet connection
- **Cost-free option**: Users can avoid API costs if they prefer keyword matching
- **Privacy-friendly**: No data sent to external services when using fallback
- **Resilient to failures**: Network issues don't break the tool
- **Same interface**: Both modes return identical data structures (transparent to consumers)
- **Testable**: Keyword logic is deterministic and easy to unit test

**Negative:**
- **Reduced accuracy in fallback**: Keyword matching misses nuance and context
- **Maintenance burden**: Two code paths to maintain (AI + keyword logic)
- **Keyword brittleness**: Fallback relies on users including specific keywords
- **Default assumptions**: Fallback makes opinionated tech stack choices (e.g., FastAPI, PostgreSQL)
- **Limited feature detection**: Can only detect features explicitly mentioned with known keywords
- **No learning**: Keyword rules don't improve over time (unlike potential AI fine-tuning)

**Neutral:**
- **Fallback good enough**: For simple projects, keyword matching often produces acceptable results
- **User control**: Users can override detected values in interactive mode

## Alternatives Considered

### AI-Only (Require API Key)
- **Pros**:
  - Single code path to maintain
  - Highest quality analysis
  - Can understand complex, nuanced descriptions
  - Learns from examples in prompt
- **Cons**:
  - Tool unusable without API key
  - Setup friction for new users
  - Fails completely on network errors
  - Privacy concerns (sends data to Anthropic)
  - Ongoing costs for users
- **Why rejected**: Too much friction for first-time users. Many users may want to try the tool before committing to API costs.

### Keyword-Only (No AI)
- **Pros**:
  - No dependencies or setup
  - Deterministic and fast
  - Completely offline
  - No ongoing costs
  - Easy to test
- **Cons**:
  - Poor quality for complex projects
  - Can't understand context or nuance
  - Requires very specific keyword usage
  - Doesn't differentiate between "We need auth" and "We don't want auth"
  - Can't extract custom tech stacks
- **Why rejected**: Leaves significant value on the table. AI analysis provides substantially better results when available.

### Hybrid with Caching
- **Pros**:
  - Cache AI results to reduce API calls
  - Share analysis across similar projects
  - Reduce costs over time
- **Cons**:
  - Complex cache invalidation logic
  - Description variations wouldn't hit cache
  - Privacy concerns (storing user descriptions)
  - Still requires API key for first use
  - Doesn't solve offline use case
- **Why rejected**: Adds complexity without solving the core problems (offline use, no API key). Marginal cost savings don't justify cache infrastructure.

### User Prompt for Mode Selection
- **Pros**:
  - Explicit user control
  - Clear expectations about quality
- **Cons**:
  - Extra decision for every run
  - Confusing for new users
  - Most users won't understand the trade-off
- **Why rejected**: The automatic fallback is simpler and smarter. Users get the best available mode without thinking about it.

## References

- **File(s)**:
  - `src/generator/analyzer.py:77-102` - Dual-mode decision logic
  - `src/generator/analyzer.py:104-120` - Claude API analysis
  - `src/generator/analyzer.py:122-200` - Keyword fallback analysis
- **Related ADRs**: ADR-0006 (Pydantic Validation) - ensures both modes produce valid output
- **External Links**:
  - [Anthropic API Documentation](https://docs.anthropic.com/)
  - [Graceful Degradation Pattern](https://en.wikipedia.org/wiki/Fault_tolerance#Graceful_degradation)

## Notes

**When AI Mode is Better**:
- Complex project descriptions with context
- Custom or uncommon technology stacks
- Implicit requirements (understands "We need user management" → auth)
- Natural language variations

**When Keyword Fallback is Sufficient**:
- Simple projects with clear keywords ("FastAPI REST API", "React mobile app")
- Standard tech stacks (FastAPI, PostgreSQL, React)
- Users explicitly mention features ("authentication", "payments")
- Quick prototypes where accuracy isn't critical

**Future Improvements**:
- Could enhance keyword matching with more sophisticated NLP (spaCy, transformers)
- Could fine-tune Claude for project analysis to reduce API costs
- Could add user feedback loop to improve keyword patterns over time
