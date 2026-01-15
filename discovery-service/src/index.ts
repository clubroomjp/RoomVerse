import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
}

const app = new Hono<{ Bindings: Bindings }>()

app.use('*', cors())

app.get('/', (c) => c.text('RoomVerse Discovery Service'))

// List active rooms
app.get('/rooms', async (c) => {
  // Filter out rooms not seen in last 5 minutes (300 seconds)
  const now = Math.floor(Date.now() / 1000)
  const threshold = now - 300 
  
  try {
    const { results } = await c.env.DB.prepare(
      "SELECT * FROM rooms WHERE last_seen > ?"
    ).bind(threshold).all()
    
    // Parse metadata JSON
    const rooms = results.map((r: any) => ({
        ...r,
        metadata: r.metadata ? JSON.parse(r.metadata) : {}
    }))
    
    return c.json(rooms)
  } catch (e) {
    return c.json({ error: e.message }, 500)
  }
})

// Announce presence
app.post('/announce', async (c) => {
  const body = await c.req.json()
  const { uuid, url, name, metadata } = body
  
  if (!uuid || !url) return c.json({ error: "Missing uuid or url" }, 400)
    
  const now = Math.floor(Date.now() / 1000)
  const metaStr = JSON.stringify(metadata || {})
  
  try {
    // Upsert logic
    await c.env.DB.prepare(`
      INSERT INTO rooms (uuid, name, url, metadata, last_seen) 
      VALUES (?1, ?2, ?3, ?4, ?5)
      ON CONFLICT(uuid) DO UPDATE SET
        url = ?3,
        name = ?2,
        metadata = ?4,
        last_seen = ?5
    `).bind(uuid, name || "Unknown Room", url, metaStr, now).run()
    
    return c.json({ status: "ok" })
  } catch (e) {
    return c.json({ error: e.message }, 500)
  }
})

export default app
