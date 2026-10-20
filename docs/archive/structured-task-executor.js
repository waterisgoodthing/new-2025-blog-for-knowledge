export const meta = {
  name: 'structured-task-executor',
  description: 'Execute structured workflow tasks from docs/workflows/ folders',
  whenToUse: 'When a workflow folder contains requirements.md, design.md, tasks.md and needs execution',
  phases: [
    { title: 'Parse', detail: 'Load workflow files and extract structure' },
    { title: 'Plan', detail: 'Analyze requirements and create execution plan' },
    { title: 'Execute', detail: 'Run uncompleted tasks following design boundaries' },
    { title: 'Validate', detail: 'Verify results against requirements' },
  ],
}

// Schema for workflow structure
const WORKFLOW_STRUCTURE = {
  type: 'object',
  properties: {
    goal: { type: 'string' },
    touchedDomains: { type: 'array', items: { type: 'string' } },
    requirements: { type: 'array', items: { type: 'string' } },
    designScope: { type: 'string' },
    changeBoundary: { type: 'array', items: { type: 'string' } },
    tasks: { type: 'array', items: {
      type: 'object',
      properties: {
        id: { type: 'string' },
        description: { type: 'string' },
        completed: { type: 'boolean' },
        dependencies: { type: 'array', items: { type: 'string' } }
      }
    }},
    validationChecks: { type: 'array', items: { type: 'string' } }
  }
}

const TASK_SCHEMA = {
  type: 'object',
  properties: {
    tasksCompleted: { type: 'number' },
    tasksPending: { type: 'number' },
    blockers: { type: 'array', items: { type: 'string' } },
    nextActions: { type: 'array', items: { type: 'string' } }
  }
}

// Main workflow execution
phase('Parse')
log('Loading workflow structure from: ' + (args.workflowPath || 'unknown'))

const workflowPath = args.workflowPath || 'docs/workflows/github-open-source-selection-report'

// Parse workflow files
const structure = await agent(
  `Read and parse the workflow structure from ${workflowPath}:

1. Read README.md, requirements.md, design.md, tasks.md
2. Extract:
   - Goal and touched domains from README
   - All numbered requirements
   - Design scope, method, change boundaries, and decision gates
   - All tasks with their completion status ([x] or [ ])
   - Any approval boundaries or constraints
3. Identify which tasks are complete and which are pending
4. Note any validation criteria mentioned

Return structured data about this workflow.`,
  {
    schema: WORKFLOW_STRUCTURE,
    phase: 'Parse',
    label: 'Parse workflow structure'
  }
)

if (!structure) {
  log('Failed to parse workflow structure')
  return { error: 'Could not parse workflow files' }
}

log(`Found workflow: ${structure.goal}`)
log(`Requirements: ${structure.requirements?.length || 0}`)
log(`Tasks: ${structure.tasks?.length || 0}`)

phase('Plan')

// Analyze what needs to be done
const pendingTasks = structure.tasks?.filter(t => !t.completed) || []
const completedTasks = structure.tasks?.filter(t => t.completed) || []

log(`Completed: ${completedTasks.length}, Pending: ${pendingTasks.length}`)

if (pendingTasks.length === 0) {
  log('All tasks are complete. Moving to validation phase.')
  phase('Validate')

  const validation = await agent(
    `Validate the completed workflow at ${workflowPath}:

1. Check if validation.md exists and review its contents
2. Verify all requirements from requirements.md are addressed
3. Confirm all tasks in tasks.md are marked complete
4. Check if final deliverables mentioned in README exist
5. Identify any gaps or unverified claims

Requirements to check:
${structure.requirements?.join('\n') || 'None'}

Return validation results.`,
    {
      phase: 'Validate',
      label: 'Validate completed workflow',
      effort: 'low'
    }
  )

  log('Validation complete')
  return {
    status: 'complete',
    workflowPath,
    goal: structure.goal,
    completedTasks: completedTasks.length,
    validation
  }
}

// Create execution plan for pending tasks
const executionPlan = await agent(
  `Create an execution plan for pending tasks in ${workflowPath}:

Workflow Goal: ${structure.goal}

Design Boundaries:
${structure.changeBoundary?.join('\n') || 'None specified'}

Pending Tasks:
${pendingTasks.map((t, i) => `${i + 1}. ${t.id}: ${t.description}`).join('\n')}

Requirements:
${structure.requirements?.slice(0, 10).join('\n') || 'None'}

Analyze:
1. Which tasks can be executed safely within the design boundaries?
2. What are the dependencies between tasks?
3. Are there any blockers or risks?
4. What's the recommended execution order?

Return the analysis.`,
  {
    schema: TASK_SCHEMA,
    phase: 'Plan',
    label: 'Create execution plan'
  }
)

log(`Execution plan: ${executionPlan?.nextActions?.length || 0} next actions identified`)

phase('Execute')

// Execute pending tasks in order
const results = await pipeline(
  pendingTasks.slice(0, 3), // Process up to 3 tasks

  // Stage 1: Analyze task requirements
  async (task) => {
    const analysis = await agent(
      `Analyze task execution requirements:

Task: ${task.id}
Description: ${task.description}

Workflow boundaries:
${structure.changeBoundary?.join('\n') || 'None'}

Requirements context:
${structure.requirements?.slice(0, 5).join('\n') || 'None'}

Determine:
1. What files need to be read?
2. What files might be created or modified?
3. Is this within the approved change boundary?
4. What verification is needed after execution?

Return the task analysis.`,
      {
        phase: 'Execute',
        label: `Analyze ${task.id}`,
        effort: 'low'
      }
    )

    return { task, analysis }
  },

  // Stage 2: Execute the task
  async ({ task, analysis }) => {
    if (!analysis) {
      log(`Skipping ${task.id} - analysis failed`)
      return { task, executed: false, reason: 'analysis_failed' }
    }

    const execution = await agent(
      `Execute task ${task.id}:

Description: ${task.description}

Analysis: ${JSON.stringify(analysis)}

Workflow: ${workflowPath}

Instructions:
1. Follow the design boundaries strictly
2. Read necessary files
3. Perform the required work
4. Document what was done
5. Update tasks.md to mark this task complete if successful

Return execution results.`,
      {
        phase: 'Execute',
        label: `Execute ${task.id}`,
        effort: 'medium'
      }
    )

    return { task, executed: true, result: execution }
  }
)

const executedCount = results.filter(r => r?.executed).length
log(`Executed ${executedCount} of ${pendingTasks.length} pending tasks`)

phase('Validate')

// Final validation
const finalValidation = await agent(
  `Perform final validation of workflow execution:

Workflow: ${workflowPath}
Goal: ${structure.goal}

Check:
1. Review updated tasks.md - are executed tasks marked complete?
2. Were any files created or modified outside the change boundary?
3. Are there any new blockers or issues?
4. What tasks remain pending?
5. Should validation.md be updated?

Return validation summary.`,
  {
    phase: 'Validate',
    label: 'Final validation',
    effort: 'low'
  }
)

return {
  status: 'executed',
  workflowPath,
  goal: structure.goal,
  totalTasks: structure.tasks?.length || 0,
  completedBefore: completedTasks.length,
  executed: executedCount,
  pendingRemaining: pendingTasks.length - executedCount,
  validation: finalValidation
}
