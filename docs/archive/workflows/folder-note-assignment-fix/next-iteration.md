# Next Iteration Decision

Date: 2026-06-13

## Decision

No new implementation requirement is opened from this task.

## Rationale

The original defect has been addressed in the code path:

- selected-folder note creation now has a frontend and backend `folder_id` contract;
- backend creation validates folder existence;
- the notes sidebar can refresh folder tree/count state after move operations.

The only residual item is browser acceptance evidence blocked by the in-app Browser URL policy. That remains a validation risk, not a new product requirement.

## Archive Criteria

Archive this workflow after one authenticated manual check confirms:

- selecting a folder and clicking "写笔记" opens `/write-note?folder_id=...`;
- saving the note places it in that folder;
- moving another note into the same folder refreshes the folder count/list state.
