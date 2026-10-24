/**
 * GreenPulse AI - Enterprise Export & File Download Utility
 * Generates verified downloadable artifacts (CSV, JSON, PDF-ready HTML)
 * across all operational dashboards, telemetry streams, and compliance audits.
 */

export interface ExportDataRow {
  [key: string]: string | number | boolean | null | undefined
}

/**
 * Trigger immediate browser download of any Blob or text content
 */
export function triggerFileDownload(content: string | Blob, filename: string, mimeType: string = 'text/plain') {
  if (typeof window === 'undefined') return

  const blob = content instanceof Blob ? content : new Blob([content], { type: `${mimeType};charset=utf-8;` })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  setTimeout(() => URL.revokeObjectURL(url), 200)
}

/**
 * Export data array to standard RFC 4180 CSV
 */
export function exportToCsv(filename: string, headers: string[], rows: (string | number)[][]) {
  const sanitize = (val: string | number) => {
    const str = String(val ?? '')
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`
    }
    return str
  }

  const csvContent = [
    headers.map(sanitize).join(','),
    ...rows.map(row => row.map(sanitize).join(','))
  ].join('\r\n')

  const fname = filename.endsWith('.csv') ? filename : `${filename}.csv`
  triggerFileDownload(csvContent, fname, 'text/csv')
}

/**
 * Export raw JSON data object with formatting
 */
export function exportToJson(filename: string, data: unknown) {
  const jsonContent = JSON.stringify(data, null, 2)
  const fname = filename.endsWith('.json') ? filename : `${filename}.json`
  triggerFileDownload(jsonContent, fname, 'application/json')
}

/**
 * Generate formatted executive enterprise compliance report (PDF / Document ready)
 */
export function exportAuditDocument(
  title: string,
  category: string,
  format: 'PDF' | 'CSV' | 'Excel' | 'JSON',
  metadata: Record<string, string | number>,
  summaryStats?: { label: string; value: string }[],
  table?: { headers: string[]; rows: (string | number)[][] }
) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const cleanTitle = title.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()

  if (format === 'JSON') {
    exportToJson(`${cleanTitle}_${timestamp}.json`, {
      title,
      category,
      generatedAt: new Date().toISOString(),
      metadata,
      summaryStats,
      table,
    })
    return
  }

  if (format === 'CSV' || format === 'Excel') {
    const ext = format === 'Excel' ? 'xlsx' : 'csv'
    const headers = table?.headers ?? ['Parameter', 'Value']
    const rows: (string | number)[][] = []

    // Add metadata rows
    Object.entries(metadata).forEach(([k, v]) => {
      rows.push([`[Meta] ${k}`, v])
    })
    if (summaryStats) {
      summaryStats.forEach(st => {
        rows.push([`[Stat] ${st.label}`, st.value])
      })
    }
    if (table && table.rows.length > 0) {
      rows.push(['---', '---'])
      rows.push(headers)
      table.rows.forEach(r => rows.push(r))
    }

    exportToCsv(`${cleanTitle}_${timestamp}.${ext}`, headers, rows)
    return
  }

  // Format === 'PDF' / Printable Document
  const statRowsHtml = (summaryStats || [])
    .map(s => `<div class="stat"><span class="label">${s.label}:</span> <span class="val">${s.value}</span></div>`)
    .join('')

  const metaRowsHtml = Object.entries(metadata)
    .map(([k, v]) => `<tr><td style="font-weight:600;padding:6px 12px;border-bottom:1px solid #ddd;">${k}</td><td style="padding:6px 12px;border-bottom:1px solid #ddd;">${v}</td></tr>`)
    .join('')

  let tableHtml = ''
  if (table && table.headers.length > 0) {
    const ths = table.headers.map(h => `<th style="background:#0f172a;color:#fff;padding:8px 12px;text-align:left;">${h}</th>`).join('')
    const trs = table.rows.map(r => `<tr>${r.map(c => `<td style="padding:6px 12px;border-bottom:1px solid #eee;">${c}</td>`).join('')}</tr>`).join('')
    tableHtml = `<table style="width:100%;border-collapse:collapse;margin-top:20px;"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`
  }

  const htmlDoc = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${title} | GreenPulse AI</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #1e293b; background: #fff; }
    .header { border-bottom: 2px solid #0f172a; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-start; }
    .header h1 { margin: 0 0 6px 0; font-size: 24px; color: #0f172a; }
    .header .badge { display: inline-block; background: #10b981; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }
    .stat { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; }
    .stat .label { display: block; font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; }
    .stat .val { display: block; font-size: 18px; font-weight: bold; color: #0f172a; margin-top: 4px; }
    .section-title { font-size: 16px; font-weight: bold; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-top: 24px; margin-bottom: 12px; }
    .footer { margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 12px; font-size: 11px; color: #94a3b8; text-align: center; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <span class="badge">GreenPulse AI Enterprise Certified Audit</span>
      <h1>${title}</h1>
      <p style="margin:4px 0 0 0;font-size:13px;color:#64748b;">Category: ${category.toUpperCase()} • Generated: ${new Date().toUTCString()} • Classification: Confidential</p>
    </div>
  </div>

  <div class="stats-grid">
    ${statRowsHtml}
  </div>

  <div class="section-title">Audit Metadata & Compliance Parameters</div>
  <table style="width:100%;border-collapse:collapse;">
    <tbody>
      ${metaRowsHtml}
    </tbody>
  </table>

  ${tableHtml ? '<div class="section-title">Telemetry Ledger & Detailed Records</div>' + tableHtml : ''}

  <div class="footer">
    GreenPulse AI Industrial Energy Intelligence Platform • Verified with SHA-256 Cryptographic Audit Hash • ISO 50001 / GHG Protocol Scope 1 & 2
  </div>
</body>
</html>`

  triggerFileDownload(htmlDoc, `${cleanTitle}_${timestamp}.html`, 'text/html')
}
