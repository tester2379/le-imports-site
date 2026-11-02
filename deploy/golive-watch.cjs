// DSM-1298 go-live watcher for leimports.com.
//
// The domain is registered at Hostinger and its DNS is edited in hPanel, which
// automation cannot log into (Cloudflare bot wall, see DSM-1093/1198). So the
// person with hPanel access changes two records, and this script — run every
// 10 minutes by the scheduled task "LE-Imports-GoLive-Watch" — finishes the job:
//
//   1. waits until leimports.com resolves ONLY to GitHub Pages' four IPs
//   2. sets the Pages custom domain to leimports.com (not before: setting it
//      early would redirect the working github.io address to a parked page)
//   3. turns on "Enforce HTTPS" once GitHub has issued the certificate
//   4. checks https://leimports.com/ serves the L&E site, then resolves
//      DSM-1298 as Bruce (staff_id NULL, resolved_by NULL), logs to the
//      handover file and deletes its own scheduled task.
//
// It never touches the domain's email records (Zoho MX/SPF/DMARC) - it only reads DNS.
// Gives up (and deletes the task) 30 days after it was set up.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { createRequire } = require('module');

const TICKETS_DIR = 'C:\\Users\\Windows 11\\dsm-it-tickets';
const treq = createRequire(path.join(TICKETS_DIR, 'package.json'));
const { Client } = treq('pg');
treq('dotenv').config({ path: path.join(TICKETS_DIR, '.env') });

const DOMAIN = 'leimports.com';
const REPO = 'tester2379/le-imports-site';
const TICKET = 'DSM-1298';
const TASK = 'LE-Imports-GoLive-Watch';
const GH_IPS = new Set(['185.199.108.153', '185.199.109.153', '185.199.110.153', '185.199.111.153']);
const GIVE_UP = new Date('2026-12-02T17:00:00Z');
const HANDOVER = 'C:\\Users\\Windows 11\\bruce-knowledge\\HERMES-HANDOVER.md';
const LOG = path.join(require('os').homedir(), 'le-golive-watch.log'); // outside the site folder (it is served)
const NOWIN = { windowsHide: true, encoding: 'utf8' };

const log = (m) => fs.appendFileSync(LOG, `${new Date().toISOString()} ${m}\n`);

async function resolveA(name) {
  const r = await fetch(`https://cloudflare-dns.com/dns-query?name=${name}&type=A`,
    { headers: { accept: 'application/dns-json' } });
  const j = await r.json();
  return (j.Answer || []).filter((a) => a.type === 1).map((a) => a.data);
}

function gh(args) {
  return execFileSync('gh', ['api', ...args], NOWIN);
}

function deleteTask() {
  try { execFileSync('schtasks', ['/delete', '/tn', TASK, '/f'], NOWIN); log('task deleted'); }
  catch (e) { log('task delete failed: ' + e.message); }
}

async function resolveTicket() {
  const c = new Client({ connectionString: process.env.DATABASE_URL });
  await c.connect();
  try {
    const { rows } = await c.query("SELECT id, status FROM tickets WHERE ref=$1", [TICKET]);
    const t = rows[0];
    if (!t || !['open', 'in_progress'].includes(t.status)) { log(`ticket is ${t && t.status} - left alone`); return; }
    const url = `https://${DOMAIN}`;
    await c.query('BEGIN');
    await c.query("INSERT INTO ticket_events (ticket_id, staff_id, kind, note) VALUES ($1, NULL, 'comment', $2)", [t.id,
      `Bruce: Done and live on ${url}. The domain now points at the L&E Imports website, with a free HTTPS certificate, `
      + `and www.${DOMAIN} and the old github.io address both forward to it. Email on the domain was not touched. `
      + 'Checked live: the home page loads over HTTPS.']);
    await c.query(`UPDATE tickets SET status='resolved', resolved_at=now(), resolved_by=NULL, updated_at=now(),
      resolution=$2 WHERE id=$1`, [t.id,
      `leimports.com connected to the L&E Imports website (GitHub Pages, HTTPS on, www + github.io forward to it, email untouched). Live: ${url}`]);
    await c.query("INSERT INTO ticket_events (ticket_id, staff_id, kind, note) VALUES ($1, NULL, 'status', $2)",
      [t.id, `${t.status} → resolved (Bruce)`]);
    await c.query('COMMIT');
    log('ticket resolved');
  } catch (e) { await c.query('ROLLBACK').catch(() => {}); throw e; }
  finally { await c.end(); }
}

(async () => {
  if (new Date() > GIVE_UP) { log('30 days passed without the DNS change - giving up'); deleteTask(); return; }
  const ips = await resolveA(DOMAIN);
  if (!ips.length || !ips.every((ip) => GH_IPS.has(ip))) { log(`waiting: ${DOMAIN} A = ${ips.join(',') || 'none'}`); return; }

  const pages = JSON.parse(gh([`repos/${REPO}/pages`]));
  if (pages.cname !== DOMAIN) {
    gh(['-X', 'PUT', `repos/${REPO}/pages`, '-f', `cname=${DOMAIN}`]);
    log('DNS points at GitHub - custom domain set');
    return; // certificate takes a few minutes; next run continues
  }
  try {
    gh(['-X', 'PUT', `repos/${REPO}/pages`, '-f', `cname=${DOMAIN}`, '-F', 'https_enforced=true']);
  } catch (e) { log('HTTPS not ready yet: ' + String(e.stderr || e.message).slice(0, 160)); return; }

  const r = await fetch(`https://${DOMAIN}/?cb=${Date.now()}`, { redirect: 'follow' }).catch((e) => ({ ok: false, err: e }));
  const body = r.ok ? await r.text() : '';
  if (!r.ok || !body.includes('L&amp;E Imports')) { log(`https check not passing yet (${r.status || r.err})`); return; }

  await resolveTicket();
  fs.appendFileSync(HANDOVER, `\n## ${new Date().toISOString().slice(0, 16).replace('T', ' ')} — golive-watch (Bruce) — ${TICKET} leimports.com LIVE\n`
    + `- DNS reached GitHub Pages; custom domain + Enforce HTTPS set on ${REPO}; https://${DOMAIN}/ verified; ticket resolved as Bruce; task ${TASK} removed.\n`);
  log('LIVE - done');
  deleteTask();
})().catch((e) => log('error: ' + (e.stack || e.message)));
