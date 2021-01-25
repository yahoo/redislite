# Changelog Messages

This directory contains changelog news fragment messages.  

Changelog messages are descriptions of changes for the end users of the package.  In
contrast to change messages for developers which go into the git commit log.

## Adding a new changelog message

In the git branch that contains the change, create a file in this directory named in the following format:

  {issuenum}.{changetype}.md

|            |      |
| ---------- | ---- |
| issuenum   | Is the issue or change number for the change.  This can be any valid string, and is frequently github issues or jira ticket number for the change. |
| changetype | Is the type of change, it can be one of the following: |
|            | - feature - A new feature |
|            | - bugfix - The change fixes a bug |
|            | - doc - The change is an improvement to the documentation |
|            | - removal - The changed involved removing code or features |
|            | - misc - Other kinds of changes |

The changes are automatically added to the changelog of the release that added the change document.
