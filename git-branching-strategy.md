# Release Strategy

Defining a release strategy is important for a team to be able to achieve continuous delivery.

A release strategy will include definition and alignment on the following:
* GitHub branch strategy
* Environment strategy
* JIRA ticket strategy

This document is focused on the GitHub branching and environment strategy.

-----
### Goal: A branching strategy that allows us to achieve continuous delivery

```mermaid
---
title: "Larger releases"
---
gitGraph
    commit
    branch release/paypal-integration
    checkout release/paypal-integration
    branch CC-1
    branch CC-2
    checkout CC-1
    commit id: "Add PayPal Gateway"
    commit
    checkout CC-2
    commit
    commit
    commit
    checkout release/paypal-integration
    merge CC-1
    merge CC-2
    checkout main
    merge release/paypal-integration tag: "10.6.0"
```
```mermaid
---
title: "Smaller releases"
---
gitGraph
    commit
    branch release/add-paypal-gateway
    checkout release/add-paypal-gateway
    commit
    commit
    checkout main
    merge release/add-paypal-gateway tag: "10.7.0"
```
```mermaid
gitGraph
    commit
    branch hotfix/fix-gateway
    checkout hotfix/fix-gateway
    commit
    checkout main
    merge hotfix/fix-gateway tag: "10.7.1"
```



## Environment branches (disadvantages)
* By having a branch dedicated for all development work defeats the purpose of continuous delivery
* Forget get take dev or qa to production - so you have functionality that is not in production
* Environment specific code, configureation and other drift

### Need the following
* Less intermediate environments
  * Less environments encourages team to use shared environment optimally
* Remove branches for environments
  * By avoiding branches for environments we focus on production and moving new features forward.
* Create JIRA tickets as deployable units 

### Important notes
* Anything in master is deployable and ready for production
* To work on something new, create branch off of master
* Need to continue to merge/rebase from master and make sure envs are up-to-date
* If the team is overwhelmed with testing there is not enough automation
* Automation is key to continuous delivery

```mermaid
---
title: "Current Branching Strategy"
---
flowchart LR
    A[Branch] --> B[Dev]
    B --> C[QA]
    C --> D[Sandbox]
    D --> E[PreProd]
    E --> F[Prod]
```

```mermaid
---
title: "Ideal Future Branching and Environment Strategy"
---
flowchart LR
    A[ReleaseBranch]
    A --> B[TestingEnv]
    A --> C[Prod]
%%    A --> D[TestingEnv]
%%    A --> E[TestingEnv]
%%    E --> F[Prod]
%%    D --> F
%%    C --> F
```

-----
Influenced by current experience and observation. A lot of references and agreement with the [following article](https://sairamkrish.medium.com/git-branching-strategy-for-true-continuous-delivery-eade4435b57e)
