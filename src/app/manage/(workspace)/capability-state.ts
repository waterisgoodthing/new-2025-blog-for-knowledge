export type ManageCapabilityState = 'active' | 'deferred'

export const manageCapabilityStates = {
  drafts: 'active',
  capture: 'active',
  ai: 'active',
  aiRuns: 'active',
  search: 'deferred',
  analytics: 'active',
  jobs: 'active',
} as const satisfies Record<string, ManageCapabilityState>
