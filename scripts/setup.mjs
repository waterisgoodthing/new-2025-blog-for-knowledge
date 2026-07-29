#!/usr/bin/env node

/**
 * Platform-neutral setup/check script for the blog project.
 *
 * Modes:
 *   --check   Check prerequisites and validate setup without changing state.
 *   --init    Conservative guided setup: check, create env files, install deps, guide DB migration.
 *   --setup   Fuller setup: init + optional Docker DB, AI config, admin credentials.
 */

import { execSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import readline from 'node:readline'
import crypto from 'node:crypto'

const ROOT = path.resolve(import.meta.dirname, '..')
const BACKEND = path.join(ROOT, 'backend')

const MODE = process.argv.includes('--check')
  ? 'check'
  : process.argv.includes('--init')
    ? 'init'
    : process.argv.includes('--setup')
      ? 'setup'
      : null

if (!MODE) {
  console.log('Usage: node scripts/setup.mjs <mode>')
  console.log('  --check   Validate prerequisites without changing state')
  console.log('  --init    Conservative guided setup')
  console.log('  --setup   Fuller local setup with optional AI/admin config')
  process.exit(1)
}

const isCheck = MODE === 'check'
const isInit = MODE === 'init'
const isSetup = MODE === 'setup'

let warnings = 0
let errors = 0

function info(msg) {
  console.log(`  \x1b[36m✓\x1b[0m ${msg}`)
}

function warn(msg) {
  console.log(`  \x1b[33m⚠\x1b[0m ${msg}`)
  warnings++
}

function fail(msg) {
  console.log(`  \x1b[31m✗\x1b[0m ${msg}`)
  errors++
}

function section(title) {
  console.log(`\n\x1b[1m${title}\x1b[0m`)
}

function cmdExists(cmd) {
  try {
    const which = process.platform === 'win32' ? 'where' : 'which'
    execSync(`${which} ${cmd}`, { stdio: 'ignore' })
    return true
  } catch {
    return false
  }
}

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: 'utf-8', cwd: opts.cwd || ROOT, stdio: opts.stdio || 'pipe' }).trim()
  } catch {
    return null
  }
}

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close()
      resolve(answer.trim())
    })
  })
}

function maskKey(key) {
  if (!key || key.length < 8) return '****'
  return key.slice(0, 4) + '****' + key.slice(-4)
}

function generateSecret(bytes = 32) {
  return crypto.randomBytes(bytes).toString('hex')
}

function parsePythonVersion(output) {
  const match = output?.match(/Python\s+(\d+)\.(\d+)(?:\.(\d+))?/)
  if (!match) return null
  return {
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3] || 0),
  }
}

function isSupportedPython(version) {
  return version && version.major === 3 && version.minor >= 12 && version.minor < 14
}

// ─── Prerequisite checks ───────────────────────────────────────────

function checkNode() {
  section('Node.js & npm')
  const nodeVersion = run('node --version')
  const npmVersion = run('npm --version')
  if (nodeVersion) info(`Node.js: ${nodeVersion}`)
  else fail('Node.js not found. Install Node.js 20+ from https://nodejs.org/')
  if (npmVersion) info(`npm: ${npmVersion}`)
  else fail('npm not found.')
}

function checkPython() {
  section('Python')
  let pythonCmd = null
  for (const cmd of ['python3', 'python', 'python3.12', 'python3.13']) {
    const ver = run(`${cmd} --version`)
    if (ver && ver.includes('Python 3')) {
      const parsed = parsePythonVersion(ver)
      if (isSupportedPython(parsed)) {
        pythonCmd = cmd
        info(`${ver} (via ${cmd})`)
        break
      }
      warn(`${ver} (via ${cmd}) is not supported by the current backend dependency set. Use Python 3.12 or 3.13.`)
    }
  }
  if (!pythonCmd) {
    fail('Supported Python not found. Install Python 3.12 or 3.13 and create backend/.venv with that interpreter.')
    return null
  }

  const venvAvailable = run(`${pythonCmd} -c "import venv; print('ok')"`)
  if (venvAvailable === 'ok') info('venv module: available')
  else warn('venv module not available. You may need to install python3-venv.')

  return pythonCmd
}

function checkPostgres() {
  section('PostgreSQL')
  const psqlAvail = cmdExists('psql')
  const pgReady = run('pg_isready')

  if (pgReady && pgReady.includes('accepting connections')) {
    info('PostgreSQL: accepting connections')
    return 'local'
  } else if (psqlAvail) {
    warn('psql found but PostgreSQL is not accepting connections on default socket.')
    return 'installed-not-running'
  } else {
    warn('PostgreSQL client (psql) not found.')
    return 'not-found'
  }
}

function checkDocker() {
  section('Docker')
  if (cmdExists('docker')) {
    const ver = run('docker --version')
    info(ver || 'Docker available')
    return true
  } else {
    warn('Docker not found. Docker-backed PostgreSQL is not available.')
    return false
  }
}

function checkBackendDeps() {
  section('Backend dependencies')
  const venvPath = path.join(BACKEND, '.venv')
  if (fs.existsSync(venvPath)) {
    info('backend/.venv exists')
    return true
  } else {
    warn('backend/.venv not found. Run: cd backend && python3 -m venv .venv && pip install -r requirements.txt')
    return false
  }
}

function checkFrontendDeps() {
  section('Frontend dependencies')
  if (fs.existsSync(path.join(ROOT, 'node_modules'))) {
    info('node_modules exists')
    return true
  } else {
    warn('node_modules not found. Run: npm install')
    return false
  }
}

function checkEnvFiles() {
  section('Environment files')
  const rootEnv = fs.existsSync(path.join(ROOT, '.env'))
  const backendEnv = fs.existsSync(path.join(BACKEND, '.env'))

  if (rootEnv) info('root .env exists')
  else warn('root .env missing. Copy from .env.example: cp .env.example .env')

  if (backendEnv) info('backend/.env exists')
  else warn('backend/.env missing. Copy from backend/.env.example: cp backend/.env.example backend/.env')

  return { rootEnv, backendEnv }
}

function checkPorts() {
  section('Ports')
  const frontendPort = 2025
  const backendPort = 8000

  for (const port of [frontendPort, backendPort]) {
    const result = run(`lsof -i :${port} -P -n`)
    if (result && result.length > 0) {
      warn(`Port ${port} is in use. Stop the existing process or choose a different port.`)
    } else {
      info(`Port ${port}: available`)
    }
  }
}

// ─── Setup actions ──────────────────────────────────────────────────

async function createEnvFiles() {
  section('Environment files')

  const rootEnvPath = path.join(ROOT, '.env')
  const backendEnvPath = path.join(BACKEND, '.env')

  if (!fs.existsSync(rootEnvPath)) {
    if (isCheck) {
      warn('root .env missing (would create from .env.example)')
    } else {
      fs.copyFileSync(path.join(ROOT, '.env.example'), rootEnvPath)
      info('Created root .env from .env.example')
    }
  } else {
    info('root .env already exists')
  }

  if (!fs.existsSync(backendEnvPath)) {
    if (isCheck) {
      warn('backend/.env missing (would create from backend/.env.example)')
    } else {
      fs.copyFileSync(path.join(BACKEND, '.env.example'), backendEnvPath)
      info('Created backend/.env from backend/.env.example')
    }
  } else {
    info('backend/.env already exists')
  }
}

function installFrontendDeps() {
  section('Frontend dependencies')
  if (fs.existsSync(path.join(ROOT, 'node_modules'))) {
    info('node_modules already exists, skipping npm install')
    return
  }
  if (isCheck) {
    warn('Would run: npm install')
    return
  }
  console.log('  Running npm install ...')
  const result = spawnSync('npm', ['install'], { cwd: ROOT, stdio: 'inherit' })
  if (result.status === 0) info('npm install completed')
  else fail('npm install failed')
}

function installBackendDeps(pythonCmd) {
  section('Backend dependencies')
  if (!pythonCmd) {
    fail('Python not available, cannot install backend deps')
    return
  }

  const venvPath = path.join(BACKEND, '.venv')
  const pipCmd = process.platform === 'win32'
    ? path.join(venvPath, 'Scripts', 'pip')
    : path.join(venvPath, 'bin', 'pip')

  if (fs.existsSync(venvPath)) {
    info('backend/.venv already exists')
    if (!isCheck) {
      console.log('  Installing backend dependencies ...')
      const result = spawnSync(pipCmd, ['install', '-r', 'requirements.txt'], { cwd: BACKEND, stdio: 'inherit' })
      if (result.status === 0) info('Backend dependencies installed')
      else fail('Backend dependency installation failed')
    }
    return
  }

  if (isCheck) {
    warn('Would create backend/.venv and install dependencies')
    return
  }

  console.log('  Creating backend virtual environment ...')
  let result = spawnSync(pythonCmd, ['-m', 'venv', '.venv'], { cwd: BACKEND, stdio: 'inherit' })
  if (result.status !== 0) {
    fail('Failed to create virtual environment')
    return
  }

  console.log('  Installing backend dependencies ...')
  result = spawnSync(pipCmd, ['install', '-r', 'requirements.txt'], { cwd: BACKEND, stdio: 'inherit' })
  if (result.status === 0) info('Backend dependencies installed')
  else fail('Backend dependency installation failed')
}

async function configureJwtSecret() {
  section('JWT Secret')
  const backendEnvPath = path.join(BACKEND, '.env')
  if (!fs.existsSync(backendEnvPath)) {
    warn('backend/.env not found, skipping JWT setup')
    return
  }

  let content = fs.readFileSync(backendEnvPath, 'utf-8')
  if (content.includes('JWT_SECRET_KEY=your-secret-key-change-this')) {
    if (isCheck) {
      warn('JWT_SECRET_KEY uses template value (would generate a new secret)')
      return
    }
    const secret = generateSecret()
    content = content.replace('JWT_SECRET_KEY=your-secret-key-change-this', `JWT_SECRET_KEY=${secret}`)
    fs.writeFileSync(backendEnvPath, content, 'utf-8')
    info('Generated new JWT_SECRET_KEY')
    warn('Save this key securely. It is written to backend/.env only.')
  } else {
    const match = content.match(/JWT_SECRET_KEY=(.+)/)
    if (match) info(`JWT_SECRET_KEY: ${maskKey(match[1])}`)
    else warn('JWT_SECRET_KEY not found in backend/.env')
  }
}

async function configureRegistration() {
  if (!isSetup) return
  section('Registration mode')

  const answer = await ask(
    '  Registration mode?\n' +
    '    1) Disabled (no new users)\n' +
    '    2) Open registration (anyone can register)\n' +
    '    3) Protected registration (requires a key)\n' +
    '  Choose [1/2/3] (default: 2): '
  )

  const backendEnvPath = path.join(BACKEND, '.env')
  if (!fs.existsSync(backendEnvPath)) return

  let content = fs.readFileSync(backendEnvPath, 'utf-8')

  if (answer === '1') {
    content = content.replace(/ENABLE_REGISTRATION=.*/, 'ENABLE_REGISTRATION=false')
    content = content.replace(/REGISTRATION_KEY=.*/, 'REGISTRATION_KEY=')
    info('Registration disabled')
  } else if (answer === '3') {
    const regKey = generateSecret(16)
    content = content.replace(/ENABLE_REGISTRATION=.*/, 'ENABLE_REGISTRATION=true')
    content = content.replace(/REGISTRATION_KEY=.*/, `REGISTRATION_KEY=${regKey}`)
    info(`Registration key: ${regKey}`)
    warn('Save this key. It is required for new user registration.')
  } else {
    content = content.replace(/ENABLE_REGISTRATION=.*/, 'ENABLE_REGISTRATION=true')
    content = content.replace(/REGISTRATION_KEY=.*/, 'REGISTRATION_KEY=')
    info('Open registration enabled')
  }

  fs.writeFileSync(backendEnvPath, content, 'utf-8')
}

async function configureOperatorPasskey() {
  if (!isSetup) return
  section('Operator passkey registration')

  const answer = await ask('  Enable operator passkey registration? [y/N]: ')
  const backendEnvPath = path.join(BACKEND, '.env')
  if (!fs.existsSync(backendEnvPath)) return

  let content = fs.readFileSync(backendEnvPath, 'utf-8')

  if (answer.toLowerCase() === 'y') {
    const opKey = generateSecret(16)
    content = content.replace(/OPERATOR_REGISTRATION_KEY=.*/, `OPERATOR_REGISTRATION_KEY=${opKey}`)
    fs.writeFileSync(backendEnvPath, content, 'utf-8')
    info(`Operator registration key: ${opKey}`)
    warn('Save this key now. It is needed for operator passkey registration.')
  } else {
    info('Operator passkey registration disabled (key left empty)')
  }
}

// ─── AI configuration ───────────────────────────────────────────────

const AI_PRESETS = [
  {
    id: 'dashscope',
    name: 'DashScope / Qwen (通义千问)',
    envPrefix: 'DASHSCOPE',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model: 'qwen3.7-plus',
    capabilities: ['general', 'ocr'],
    runtimeNote: 'Supported natively. Maps to DASHSCOPE_* env vars.',
  },
  {
    id: 'deepseek',
    name: 'DeepSeek (深度求索)',
    envPrefix: 'DEEPSEEK',
    baseUrl: 'https://api.deepseek.com/v1',
    model: 'deepseek-v4-pro',
    capabilities: ['text'],
    runtimeNote: 'Supported natively. Maps to DEEPSEEK_* env vars.',
  },
  {
    id: 'openai-compatible',
    name: 'Custom OpenAI-compatible (自定义 OpenAI 兼容端点)',
    envPrefix: 'AI',
    baseUrl: 'http://localhost:11434/v1',
    model: '',
    capabilities: ['general', 'text', 'ocr'],
    runtimeNote: 'Maps to AI_* env vars. Works with any OpenAI-compatible API (Ollama, LM Studio, vLLM, etc.).',
  },
  {
    id: 'openai',
    name: 'OpenAI',
    envPrefix: 'AI',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4o',
    capabilities: ['general', 'text', 'ocr'],
    runtimeNote: 'Uses AI_* env vars via OpenAI-compatible endpoint.',
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    envPrefix: 'AI',
    baseUrl: 'https://openrouter.ai/api/v1',
    model: '',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* env vars via OpenAI-compatible endpoint.',
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    envPrefix: 'AI',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/',
    model: 'gemini-2.0-flash',
    capabilities: ['general', 'text', 'ocr'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint. Requires API key from Google AI Studio.',
  },
  {
    id: 'xai',
    name: 'xAI (Grok)',
    envPrefix: 'AI',
    baseUrl: 'https://api.x.ai/v1',
    model: 'grok-3',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint.',
  },
  {
    id: 'claude',
    name: 'Claude / Anthropic',
    envPrefix: 'AI',
    baseUrl: 'https://api.anthropic.com/v1',
    model: 'claude-sonnet-4-20250514',
    capabilities: ['general', 'text', 'ocr'],
    runtimeNote: '⚠ Native Anthropic API is NOT OpenAI-compatible. Requires a compatible gateway or adapter. Uses AI_* if gateway is configured.',
  },
  {
    id: 'moonshot',
    name: 'Moonshot / Kimi (月之暗面)',
    envPrefix: 'AI',
    baseUrl: 'https://api.moonshot.cn/v1',
    model: 'moonshot-v1-8k',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint.',
  },
  {
    id: 'zhipu',
    name: 'Zhipu / GLM (智谱)',
    envPrefix: 'AI',
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    model: 'glm-4-flash',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint.',
  },
  {
    id: 'siliconflow',
    name: 'SiliconFlow (硅基流动)',
    envPrefix: 'AI',
    baseUrl: 'https://api.siliconflow.cn/v1',
    model: '',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint.',
  },
  {
    id: 'volcengine',
    name: 'Volcengine / Doubao (火山引擎 / 豆包)',
    envPrefix: 'AI',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    model: '',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint.',
  },
  {
    id: 'ollama',
    name: 'Ollama (local)',
    envPrefix: 'AI',
    baseUrl: 'http://localhost:11434/v1',
    model: '',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint. Requires Ollama running locally.',
  },
  {
    id: 'lmstudio',
    name: 'LM Studio (local)',
    envPrefix: 'AI',
    baseUrl: 'http://localhost:1234/v1',
    model: '',
    capabilities: ['general', 'text'],
    runtimeNote: 'Uses AI_* via OpenAI-compatible endpoint. Requires LM Studio running locally.',
  },
]

const CAPABILITY_LABELS = {
  general: 'General assistant / 通用模型',
  text: 'Text generation & analysis / 文本生成与分析',
  ocr: 'OCR & vision recognition / 图像识别',
  image: 'Image generation / 图像生成',
}

async function configureAI() {
  if (!isSetup) return
  section('AI configuration')

  const skip = await ask('  Configure AI now? [Y/n] (skip to disable AI features): ')
  if (skip.toLowerCase() === 'n') {
    info('AI configuration skipped. AI features will be disabled or degraded.')
    return
  }

  console.log('\n  Available provider presets:')
  AI_PRESETS.forEach((p, i) => {
    const caps = p.capabilities.map((c) => CAPABILITY_LABELS[c]).join(', ')
    console.log(`    ${String(i + 1).padStart(2)}) ${p.name}`)
    console.log(`        Capabilities: ${caps}`)
    console.log(`        ${p.runtimeNote}`)
  })

  const answer = await ask('\n  Select provider numbers (comma-separated, e.g. 1,2): ')
  const indices = answer.split(',').map((s) => parseInt(s.trim()) - 1).filter((i) => i >= 0 && i < AI_PRESETS.length)

  if (indices.length === 0) {
    info('No providers selected. AI features will be disabled.')
    return
  }

  const backendEnvPath = path.join(BACKEND, '.env')
  if (!fs.existsSync(backendEnvPath)) {
    fail('backend/.env not found')
    return
  }

  let content = fs.readFileSync(backendEnvPath, 'utf-8')

  for (const idx of indices) {
    const preset = AI_PRESETS[idx]
    console.log(`\n  \x1b[1mConfiguring: ${preset.name}\x1b[0m`)

    const baseUrl = await ask(`    Base URL [${preset.baseUrl}]: `) || preset.baseUrl
    const model = await ask(`    Model [${preset.model || 'none'}]: `) || preset.model
    const apiKey = await ask('    API Key (leave empty to skip): ')

    const isDashScope = preset.envPrefix === 'DASHSCOPE' || preset.id === 'dashscope'
    const imageGenAvailable = isDashScope ? '      4) Image generation (图像生成) -> DASHSCOPE_IMAGE_*\n' : ''

    const purpose = await ask(
      '    Assign to purpose:\n' +
      '      1) General assistant (通用模型) -> AI_*\n' +
      '      2) Text generation & analysis (文本生成与分析) -> DEEPSEEK_*\n' +
      '      3) OCR & vision recognition (图像识别) -> DASHSCOPE_*\n' +
      imageGenAvailable +
      `    Choose [1/2/3${isDashScope ? '/4' : ''}] (default: 1): `
    )

    let prefix
    let effectiveBaseUrl = baseUrl
    let effectiveModel = model
    if (purpose === '2') prefix = 'DEEPSEEK'
    else if (purpose === '3') prefix = 'DASHSCOPE'
    else if (purpose === '4' && isDashScope) {
      prefix = 'DASHSCOPE_IMAGE'
      const IMAGE_DEFAULT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
      const IMAGE_DEFAULT_MODEL = 'qwen-image-2.0-pro'
      if (baseUrl === preset.baseUrl) {
        effectiveBaseUrl = IMAGE_DEFAULT_URL
        info('  Switched base URL to DashScope image generation endpoint')
      }
      if (!model || model === preset.model) {
        effectiveModel = IMAGE_DEFAULT_MODEL
        info('  Switched model to image generation default')
      }
    }
    else if (purpose === '4' && !isDashScope) {
      warn('Image generation is only supported with DashScope. Falling back to general assistant.')
      prefix = 'AI'
    }
    else prefix = 'AI'

    content = setEnvValue(content, `${prefix}_BASE_URL`, effectiveBaseUrl)
    if (effectiveModel) content = setEnvValue(content, `${prefix}_MODEL`, effectiveModel)
    if (apiKey) content = setEnvValue(content, `${prefix}_API_KEY`, apiKey)

    info(`${preset.name} -> ${prefix}_BASE_URL=${effectiveBaseUrl}`)
    if (effectiveModel) info(`  ${prefix}_MODEL=${effectiveModel}`)
    if (apiKey) info(`  ${prefix}_API_KEY=${maskKey(apiKey)}`)
  }

  fs.writeFileSync(backendEnvPath, content, 'utf-8')
  info('AI configuration written to backend/.env')
}

function setEnvValue(content, key, value) {
  const regex = new RegExp(`^${key}=.*$`, 'm')
  if (regex.test(content)) {
    return content.replace(regex, `${key}=${value}`)
  }
  return content + `\n${key}=${value}`
}

// ─── Database migration ─────────────────────────────────────────────

async function ensureDatabase(pgStatus, hasDocker) {
  section('Database')

  if (pgStatus === 'local') {
    info('PostgreSQL is accepting connections')
    return true
  }

  if (pgStatus === 'installed-not-running') {
    warn('PostgreSQL is installed but not accepting connections.')
    if (hasDocker) {
      const answer = await ask('  Start PostgreSQL via Docker? [Y/n]: ')
      if (answer.toLowerCase() !== 'n') {
        console.log('  Starting PostgreSQL container ...')
        const started = run('docker run -d --name blog-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=blog_db -p 5432:5432 postgres:16')
        if (started) {
          info('PostgreSQL container started. Waiting for it to be ready ...')
          for (let i = 0; i < 15; i++) {
            const ready = run('pg_isready -h localhost -p 5432')
            if (ready && ready.includes('accepting connections')) {
              info('PostgreSQL is ready')
              return true
            }
            await new Promise(r => setTimeout(r, 1000))
          }
          warn('PostgreSQL container started but pg_isready did not confirm within 15s. Check Docker logs.')
          return false
        } else {
          fail('Failed to start PostgreSQL container. Check Docker.')
          return false
        }
      }
    }
    warn('Please start PostgreSQL manually, then re-run this script.')
    warn('  macOS: brew services start postgresql@16')
    warn('  Linux: sudo systemctl start postgresql')
    return false
  }

  if (pgStatus === 'not-found') {
    warn('PostgreSQL is not installed.')
    if (hasDocker) {
      const answer = await ask('  Start a temporary PostgreSQL via Docker? [Y/n]: ')
      if (answer.toLowerCase() !== 'n') {
        console.log('  Starting PostgreSQL container ...')
        const started = run('docker run -d --name blog-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=blog_db -p 5432:5432 postgres:16')
        if (started) {
          info('PostgreSQL container started. Waiting for it to be ready ...')
          for (let i = 0; i < 20; i++) {
            await new Promise(r => setTimeout(r, 1000))
            const ready = run('docker exec blog-postgres pg_isready -U user -d blog_db')
            if (ready && ready.includes('accepting connections')) {
              info('PostgreSQL is ready')
              return true
            }
          }
          warn('PostgreSQL container started but did not become ready within 20s. Check Docker logs.')
          return false
        } else {
          fail('Failed to start PostgreSQL container. Check Docker.')
          return false
        }
      }
    }
    warn('Please install PostgreSQL 16+ or Docker, then re-run this script.')
    warn('  macOS: brew install postgresql@16')
    warn('  Ubuntu: sudo apt install postgresql')
    warn('  Docker: https://hub.docker.com/_/postgres')
    return false
  }

  return false
}

function runMigrations(pythonCmd, dbReady) {
  section('Database migration')
  if (isCheck) {
    warn('Would run: cd backend && alembic upgrade head')
    return
  }

  if (!dbReady) {
    fail('Database is not available. Skipping migration. Set up PostgreSQL and re-run, or manually run:')
    warn('  cd backend && source .venv/bin/activate && alembic upgrade head')
    return
  }

  const venvPython = process.platform === 'win32'
    ? path.join(BACKEND, '.venv', 'Scripts', 'python')
    : path.join(BACKEND, '.venv', 'bin', 'python')

  const python = fs.existsSync(venvPython) ? venvPython : pythonCmd

  console.log('  Running alembic upgrade head ...')
  const result = spawnSync(python, ['-m', 'alembic', 'upgrade', 'head'], { cwd: BACKEND, stdio: 'inherit' })
  if (result.status === 0) info('Database migration completed')
  else fail('Database migration failed. Check DATABASE_URL in backend/.env.')
}

function suggestAdminSetup() {
  section('Admin credentials')
  const activate = process.platform === 'win32'
    ? '.venv\\Scripts\\activate'
    : 'source .venv/bin/activate'
  console.log('  After database migration, set up admin credentials:')
  console.log('')
  console.log('    cd backend')
  console.log(`    ${activate}`)
  console.log('    python -m app.cli set-password')
  console.log('')
  console.log('  Optional: register a passkey for passwordless login:')
  console.log('    python -m app.cli register-passkey')
  console.log('')
}

// ─── Main ───────────────────────────────────────────────────────────

async function main() {
  console.log(`\n\x1b[1mBlog Project Setup (${MODE.toUpperCase()})\x1b[0m`)

  const pythonCmd = checkPython()
  checkNode()
  const pgStatus = checkPostgres()
  const hasDocker = checkDocker()
  checkFrontendDeps()
  checkBackendDeps()
  checkEnvFiles()
  checkPorts()

  if (isCheck) {
    section('Check-only summary')
    if (errors > 0) {
      fail(`${errors} error(s), ${warnings} warning(s). Fix errors before proceeding.`)
      process.exit(1)
    } else if (warnings > 0) {
      warn(`${warnings} warning(s). Review warnings above.`)
    } else {
      info('All checks passed.')
    }
    return
  }

  // Init or Setup mode — show planned actions and confirm
  const plannedActions = [
    'Create .env files from .env.example (if missing)',
    'Run npm install (if node_modules missing)',
    'Create backend venv and install pip dependencies (if .venv missing)',
    'Generate JWT secret (if still template value)',
    'Run database migration (alembic upgrade head)',
  ]
  if (isSetup) {
    plannedActions.push('Configure registration mode, operator passkey, AI providers')
  }

  section('Planned actions')
  for (const action of plannedActions) {
    console.log(`    • ${action}`)
  }
  const proceed = await ask('\n  Proceed with these actions? [Y/n]: ')
  if (proceed.toLowerCase() === 'n') {
    info('Setup cancelled by user.')
    return
  }

  await createEnvFiles()
  installFrontendDeps()
  installBackendDeps(pythonCmd)
  await configureJwtSecret()
  const dbReady = await ensureDatabase(pgStatus, hasDocker)
  runMigrations(pythonCmd, dbReady)

  if (isSetup) {
    await configureRegistration()
    await configureOperatorPasskey()
    await configureAI()
  }

  suggestAdminSetup()

  // Final summary
  section('Setup summary')
  if (errors > 0) {
    fail(`${errors} error(s), ${warnings} warning(s). Review output above.`)
    process.exit(1)
  } else if (warnings > 0) {
    warn(`${warnings} warning(s). Review output above.`)
  } else {
    info('Setup completed successfully!')
  }

  console.log('\n  Next steps:')
  console.log('    1. Start backend:')
  console.log('       cd backend')
  console.log('       source .venv/bin/activate  # Windows: .venv\\Scripts\\activate')
  console.log('       uvicorn main:app --reload')
  console.log('    2. Start frontend: npm run dev')
  console.log('    3. Open http://localhost:2025')
  console.log('')
}

main().catch((err) => {
  console.error('Setup failed:', err)
  process.exit(1)
})
