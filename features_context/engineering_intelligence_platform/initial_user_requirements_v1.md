## Metrics

(Check LinearB metrics as well)

### 1. Delivery Metrics

#### Lead time for changes

Time from code committed to production.

Measures:
- Development efficiency
- CI/CD effectiveness
- Release bottlenecks

#### Deployment frequency

How often production deployments occur.

Measures:
- Release agility
- Batch size
- Team confidence

#### Change failure rate

Percentage of deployments causing incidents, rollbacks, hotfixes, etc.

Measures:
- Quality
- Risk

#### Mean time to restore

Time to recover after an incident.

Measures:
- Operational excellence
- Incident response effectiveness

### 2. Flow Metrics

#### Cycle time

Time from work starting to work completed.

Notes:
- Track P50, P75, P95. Tail latency is usually more revealing than averages.

#### Queue time

Time spent waiting.

Examples:
- Waiting for review
- Waiting for testing
- Waiting for approval

#### PR review time

Time between opening and first meaningful review.

#### Work in progress

Number of active items per engineer/team.


### 3. Reliability Metrics

#### Availability/ SLO attainment

Examples:
- Service uptime
- Error budget consumption

#### Incident metrics

Examples:
- Number of incidents
- Severity distribution
- Time to detection
- Time to mitigation

#### Escaped deffects

Bugs reaching customers.

Examples:
- Production defects per release
- Customer-reported bugs


### 4. Developer productivity signals

#### Time spent coding vs waiting

Examples:
- Coding time
- Review wait time
- CI wait time
- Environment wait time

#### Build and test performance

Examples:
- Build duration
- Test duration
- Flaky test rate

#### Developer friction

Examples:
- Failed builds
- Failed deployments
- Rework rate
- Context switches


### 5. Engineering economics

#### Engineering investment allocation

Examples:
- New features
- Reliability
- Technical debt
- Maintenance
- Support

#### Cost per delivered outcome

Examples:
- Cost per feature
- Cost per deployment
- Cost per customer request completed

### 6. AI Metrics

#### AI adoption

Examples:
- % engineers using AI tools
- Acceptance rate of suggestions

#### AI impact

Examples:
- Cycle time before vs after AI
- Review burden changes
- Defect rate changes

#### Human oversight

Exampels:
- Revert rate of AI-generated code
- Incident involvement

## Merics connections (drivers and outcomes, correlation analysis, etc.)


## Metric model (linking multiple sources data with metadata)


## Aggregation views (by release, by feature, by team member, etc.)