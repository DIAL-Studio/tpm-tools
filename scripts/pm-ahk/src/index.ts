import { Command } from 'commander'
import { resolve, join, dirname, extname } from 'node:path'
import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { createServer } from 'node:http'
import { PmAhkDB } from './core/db'
import { startMcpServer } from './core/mcp-server'

const VERSION = '2.2.0'

const __dirname = dirname(fileURLToPath(import.meta.url))

const program = new Command()

program.name('pm-ahk').description('PM Agent Harness Kit — MCP server for PM workflows').version(VERSION)

program
  .command('serve')
  .description('Start the MCP server (stdio)')
  .option('--db <path>', 'Path to the SQLite database')
  .action(async (opts) => {
    const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
    process.stderr.write(`[pm-ahk] MCP server starting (stdio)\n`)
    try {
      const db = new PmAhkDB(dbPath)
      await startMcpServer(db)
    } catch (err) {
      process.stderr.write(`[pm-ahk] Fatal: ${err instanceof Error ? err.message : String(err)}\n`)
      process.exit(1)
    }
  })

program
  .command('status')
  .description('Show initiative backlog')
  .option('--db <path>', 'Path to the SQLite database')
  .option('--json', 'Output as JSON')
  .action(async (opts) => {
    const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
    const db = new PmAhkDB(dbPath)
    const initiatives = db.listInitiatives()
    if (opts.json) {
      console.log(JSON.stringify(initiatives, null, 2))
    } else {
      console.log('\n  PM Agent Harness Kit')
      console.log(`  ${'─'.repeat(50)}`)
      if (initiatives.length === 0) {
        console.log('  No initiatives yet.')
      } else {
        console.log(`  ${'ID'.padEnd(4)} ${'Status'.padEnd(14)} ${'Title'}`)
        console.log(`  ${'─'.repeat(4)} ${'─'.repeat(14)} ${'─'.repeat(30)}`)
        for (const i of initiatives) {
          console.log(`  ${String(i.id).padEnd(4)} ${i.status.padEnd(14)} ${i.title.slice(0, 40)}`)
        }
      }
      console.log()
    }
    db.close()
  })

program
  .command('initiative')
  .description('Manage initiatives')
  .addCommand(
    new Command('list')
      .description('List initiatives')
      .option('--db <path>')
      .option('--status <status>')
      .action(async (opts) => {
        const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
        const db = new PmAhkDB(dbPath)
        const initiatives = db.listInitiatives(opts.status)
        console.log(JSON.stringify(initiatives, null, 2))
        db.close()
      }),
  )
  .addCommand(
    new Command('add')
      .description('Add an initiative')
      .argument('<title>', 'Initiative title')
      .option('--db <path>')
      .action(async (title, opts) => {
        const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
        const db = new PmAhkDB(dbPath)
        const slug = title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').slice(0, 50)
        const initiative = db.createInitiative(slug, title)
        console.log(JSON.stringify(initiative))
        db.close()
      }),
  )
  .addCommand(
    new Command('done')
      .description('Mark initiative as done')
      .argument('<id>', 'Initiative ID or slug')
      .option('--db <path>')
      .action(async (id, opts) => {
        const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
        const db = new PmAhkDB(dbPath)
        const idNum = parseInt(id, 10)
        if (isNaN(idNum)) {
          console.error('ID must be a number')
          process.exit(1)
        }
        db.updateInitiativeStatus(idNum, 'done')
        console.log(JSON.stringify({ id: idNum, status: 'done' }))
        db.close()
      }),
  )

program
  .command('dashboard')
  .description('Start the dashboard web server')
  .option('--port <port>', 'HTTP port', '3000')
  .option('--db <path>', 'Path to the SQLite database')
  .option('--no-open', 'Do not open browser')
  .action(async (opts) => {
    const dbPath = opts.db ?? resolve(process.cwd(), '.harness', 'harness.db')
    const port = parseInt(opts.port, 10)
    const db = new PmAhkDB(dbPath)
    const candidates = [
      resolve(__dirname, '..', '..', '..', 'dashboard', 'dist'),
      resolve(__dirname, '..', '..', 'dashboard', 'dist'),
      resolve(__dirname, '..', '..', 'pm-ahk-dashboard'),
    ]
    const staticDir = candidates.find((d) => existsSync(join(d, 'index.html')))
    if (!staticDir) {
      console.error('Dashboard not found. Run: bash install.sh --with-mcp')
      process.exit(1)
    }

    const MIME: Record<string, string> = {
      '.html': 'text/html; charset=utf-8',
      '.js': 'application/javascript; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.json': 'application/json; charset=utf-8',
      '.svg': 'image/svg+xml',
      '.png': 'image/png',
      '.ico': 'image/x-icon',
      '.woff': 'font/woff',
      '.woff2': 'font/woff2',
      '.ttf': 'font/ttf',
    }

    function statusToAhk(s: string): string {
      if (s === 'pending') return 'pending'
      if (s === 'blocked') return 'blocked'
      if (s === 'done' || s === 'approved') return 'done'
      return 'in_progress' // discovery, strategy, spec, review
    }

    const server = createServer((req, res) => {
      res.setHeader('Access-Control-Allow-Origin', '*')
      const url = new URL(req.url ?? '/', `http://${req.headers.host}`)
      const path = url.pathname

      // ── API: GET /api/stats ─────────────────────────────────────────────
      if (req.method === 'GET' && path === '/api/stats') {
        const initiatives = db.listInitiatives()
        const byStatus: Record<string, number> = { pending: 0, in_progress: 0, done: 0, blocked: 0 }
        for (const i of initiatives) {
          const s = statusToAhk(i.status)
          byStatus[s] = (byStatus[s] ?? 0) + 1
        }
        const allActions = initiatives.flatMap((i) => db.getActionsForInitiative(i.id))
        const totalActions = allActions.length
        const totalFiles = allActions.reduce((sum, a) => sum + 1, 0) // approximate
        const uniqueTools = 0 // not tracked per-action in our model
        const activeAgents = new Set(allActions.map((a) => a.agent)).size
        json(res, { byStatus, totalActions, totalFiles, uniqueTools, activeAgents })
        return
      }

      // ── API: GET /api/tasks ─────────────────────────────────────────────
      if (req.method === 'GET' && path === '/api/tasks') {
        const includeArchived = url.searchParams.get('includeArchived') === 'true'
        let initiatives = db.listInitiatives()
        if (!includeArchived) initiatives = initiatives.filter((i) => !i.archived_at)
        const result = initiatives.map((i) => ({
          id: i.id,
          slug: i.slug,
          title: i.title,
          description: i.description,
          status: statusToAhk(i.status),
          assigned_to: null as string | null,
          created_at: i.created_at,
          started_at: null as string | null,
          completed_at: i.status === 'done' || i.status === 'approved' ? i.updated_at : null,
          archived_at: i.archived_at,
          acceptance_total: db.listCriteria(i.id).length,
          acceptance_met: db.listCriteria(i.id).filter((c) => c.met).length,
        }))
        json(res, result)
        return
      }

      // ── API: GET /api/tasks/:id ─────────────────────────────────────────
      const taskMatch = path.match(/^\/api\/tasks\/(\d+)$/)
      if (req.method === 'GET' && taskMatch) {
        const id = parseInt(taskMatch[1], 10)
        const initiative = db.getInitiative(id)
        if (!initiative) { res.writeHead(404); res.end('{}'); return }
        const actions = db.getActionsForInitiative(id)
        const criteria = db.listCriteria(id)
        json(res, {
          id: initiative.id,
          slug: initiative.slug,
          title: initiative.title,
          description: initiative.description,
          status: statusToAhk(initiative.status),
          assigned_to: null,
          created_at: initiative.created_at,
          started_at: null,
          completed_at: initiative.status === 'done' || initiative.status === 'approved' ? initiative.updated_at : null,
          archived_at: initiative.archived_at,
          acceptance_total: criteria.length,
          acceptance_met: criteria.filter((c) => c.met).length,
          acceptance: criteria.map((c) => ({ id: c.id, task_id: initiative.id, criterion: c.criterion, met: c.met })),
          actions: actions.map((a) => ({
            id: String(a.id),
            task_id: initiative.id,
            agent: a.agent,
            status: a.status,
            created_at: a.created_at,
            completed_at: a.completed_at,
            summary: a.summary,
            sections: [{ id: a.id, action_id: String(a.id), section_type: 'result', content: a.content, created_at: a.created_at }],
            files: [],
            tools: [],
          })),
        })
        return
      }

      // ── API: PATCH /api/tasks/:id (update) ──────────────────────────────
      const taskUpdateMatch = path.match(/^\/api\/tasks\/(\d+)$/)
      if (req.method === 'PATCH' && taskUpdateMatch) {
        const id = parseInt(taskUpdateMatch[1], 10)
        let body = ''
        req.on('data', (c) => body += c)
        req.on('end', () => {
          const data = JSON.parse(body)
          if (data.title !== undefined || data.description !== undefined) {
            db.editInitiative(id, data.title, data.description)
          }
          const initiative = db.getInitiative(id)
          json(res, initiative ?? {})
        })
        return
      }

      // ── API: PATCH /api/tasks/:id/archive ───────────────────────────────
      const archiveMatch = path.match(/^\/api\/tasks\/(\d+)\/archive$/)
      if (req.method === 'PATCH' && archiveMatch) {
        const id = parseInt(archiveMatch[1], 10)
        db.archiveInitiative(id)
        json(res, { id, archived: true })
        return
      }

      // ── API: PATCH /api/tasks/:id/unarchive ─────────────────────────────
      const unarchiveMatch = path.match(/^\/api\/tasks\/(\d+)\/unarchive$/)
      if (req.method === 'PATCH' && unarchiveMatch) {
        const id = parseInt(unarchiveMatch[1], 10)
        db.unarchiveInitiative(id)
        json(res, { id, unarchived: true })
        return
      }

      // ── API: GET /api/tools/top ─────────────────────────────────────────
      if (req.method === 'GET' && path === '/api/tools/top') {
        json(res, [])
        return
      }

      // ── API: GET /api/tools/recent ──────────────────────────────────────
      if (req.method === 'GET' && path === '/api/tools/recent') {
        json(res, [])
        return
      }

      // ── API: GET /api/files/top ─────────────────────────────────────────
      if (req.method === 'GET' && path === '/api/files/top') {
        json(res, [])
        return
      }

      // ── API: GET /api/files/recent ──────────────────────────────────────
      if (req.method === 'GET' && path === '/api/files/recent') {
        json(res, [])
        return
      }

      // ── API: GET /api/agents/stats ──────────────────────────────────────
      if (req.method === 'GET' && path === '/api/agents/stats') {
        const initiatives = db.listInitiatives()
        const agentMap = new Map<string, { actions_total: number; actions_done: number; actions_blocked: number; tasks_worked: number; files_touched: number }>()
        for (const i of initiatives) {
          const actions = db.getActionsForInitiative(i.id)
          const seen = new Set<string>()
          for (const a of actions) {
            let e = agentMap.get(a.agent)
            if (!e) { e = { actions_total: 0, actions_done: 0, actions_blocked: 0, tasks_worked: 0, files_touched: 0 }; agentMap.set(a.agent, e) }
            e.actions_total++
            if (a.status === 'completed') e.actions_done++
            if (a.status === 'blocked') e.actions_blocked++
            if (!seen.has(a.agent)) { seen.add(a.agent); e.tasks_worked++ }
          }
        }
        json(res, Array.from(agentMap.entries()).map(([agent, s]) => ({ agent, ...s })))
        return
      }

      // ── API: GET /api/timeline ──────────────────────────────────────────
      if (req.method === 'GET' && path === '/api/timeline') {
        const initiatives = db.listInitiatives().slice(0, 50)
        const entries = initiatives.flatMap((i) =>
          db.getActionsForInitiative(i.id).map((a) => ({
            id: a.id,
            task_id: i.id,
            task_title: i.title,
            task_slug: i.slug,
            agent: a.agent,
            status: a.status,
            summary: a.summary,
            created_at: a.created_at,
          }))
        ).sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 50)
        json(res, entries)
        return
      }

      // ── Static SPA ──────────────────────────────────────────────────────
      const filePath = path === '/' ? join(staticDir, 'index.html') : join(staticDir, path)
      if (existsSync(filePath)) {
        const ext = extname(filePath)
        res.writeHead(200, { 'Content-Type': MIME[ext] ?? 'application/octet-stream' })
        res.end(readFileSync(filePath))
        return
      }
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' })
      res.end(readFileSync(join(staticDir, 'index.html')))
    })

    function json(res: import('node:http').ServerResponse, data: unknown): void {
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify(data))
    }

    server.listen(port, () => {
      console.log(`Dashboard: http://localhost:${port}`)
      if (opts.open !== false) {
        import('node:child_process').then((cp) => cp.exec(`open "http://localhost:${port}"`))
      }
    })
  })

program.parse(process.argv)
