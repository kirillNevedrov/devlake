Metrics:

Level 1:

DORA:
- lead time for changes
- deployment frequency
- change failure rate
- mean time to restore

- planning accuracy? (https://linearb.io/resources/quickstart-guide-planning-accuracy)

- cycle time

Level 2:

Workflow:
- developer friction
    - failed builds
    - failed deployments
    - rework rate (after MR review by EM, after feature review by PM) (https://linearb.io/resources/quickstart-guide-rework)
- build and test performance
    - build duration
    - test duration
- time spent coding vs waiting
    - coding time
    - review wait time
    - CI wait time
    - environment wait time
- engineering investment allocation
    - new features
    - reliability
    - technical debt
    - maintenance
    - support
- work in progress

Quality:
- SLO attainment
- incident metrics
    - Number of incidents
    - Severity distribution
    - Time to detection
    - Time to mitigation
- escaped deffects
    - Production defects per release
    - Customer-reported bugs

_______________________

Linking data:

(in addition to metadat we can detect links by analything content of tasks, commits, MRs, etc.)
    - https://linearb.helpdocs.io/article/80cg9o0dhu-pulse-naming-conventions
        - https://linearb.helpdocs.io/article/j9toje81cb-jira-based-coding-time
    - https://linearb.helpdocs.io/article/vnw2fw6226-set-up-release-detection-method
    - https://linearb.helpdocs.io/article/5h6n4re0t9-api-deployment
    - https://linearb.helpdocs.io/article/jig0z5m1oz-git-activity

metadata we add (enforced on each service level):

Clickup task:
[- task id]
[- developer id]
- feature id

Git commit:
[- commit id]
[- developer id]
- clickup task id

Gitlab MR:
[- MR id]
- developer id
- reviewer id
- feature id

Release:
[- release id]
- inluded features ids

AWS ECR:
- release id

Sentry:
- release id

Issue:
- feature-id (on resolution linked to feature caused the issue)

______________________________-

Linked reports view:

1. planning accuracy/ lead time for changes / deployment frequency
    - list of releases
        - list of features

    - rework rate (global, per release, per feature, per engeneer)
    - review wait time (global, per release, per feature, per engeneer)
    - active MRs (global, per release, per feature, per engeneer)
    - WIP per engeneer
    - incident metrics


2. change failure rate / incident metrics
    - list of releases
        - list of features

    - deployment frequency (global, per release)
    - MR review time (global, per release, per feature, per engeneer)
    - Tech design time
    - QA time
    - Test coverage
    - Static types coverage
    - inividual incedents grouped by relase, feature
    - PlanB quality metrics (https://linearb.helpdocs.io/category/hhc8s9rrd7-quality-metrics)
        - review depth (review comments per review comparing to average)
        - MR size

4. cycle time
    - list of releases
        - list of features

    - coding time (global, per release, per feature, per engeneer)
    - review wait time (global, per release, per feature, per engeneer)
    - CI wait time (global, per release, per feature, per engeneer)
    - environment wait time (global, per release, per feature, per engeneer)
    - rework rate (global, per release, per feature, per engeneer)

______________________

As the result we:
- detect issues with DORA metrics
- identify source of issues with drilldown driver metrics
- discuss with responsible team mebers according to RACI how to prevent in future
- track records on team members reponsible for issues?
______________

Refernces:
- https://linearb.io/resources/apex-framework
- https://getdx.com/report/dx-core-4
    - https://getdx.com/research/the-one-number-you-need-to-increase-roi-per-engineer/
    - https://getdx.com/research/conceptual-framework-for-developer-experience/