export type ManageCapabilityState = 'active' | 'deferred'

export const manageCapabilityStates = {
  drafts: 'active',
  capture: 'deferred',
  ai: 'deferred',
  aiRuns: 'deferred',
  search: 'deferred',
  analytics: 'deferred',
  jobs: 'deferred',
} as const satisfies Record<string, ManageCapabilityState>
