const LOCALE = 'en-IN'

export function formatNumber(value: number, decimals = 0) {
  return new Intl.NumberFormat(LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

export function formatClockTime(date: Date, timeZone: string, withSeconds = false) {
  return new Intl.DateTimeFormat(LOCALE, {
    timeZone,
    hour: '2-digit',
    minute: '2-digit',
    second: withSeconds ? '2-digit' : undefined,
    hourCycle: 'h23',
  }).format(date)
}

export function formatShortDate(date: Date, timeZone: string) {
  return new Intl.DateTimeFormat('en-GB', {
    timeZone,
    weekday: 'short',
    day: '2-digit',
    month: 'short',
  }).format(date)
}

export function formatTimeOfDay(isoTimestamp: string, timeZone: string) {
  return formatClockTime(new Date(isoTimestamp), timeZone)
}

export function formatDateTimeStamp(isoTimestamp: string, timeZone: string) {
  const date = new Date(isoTimestamp)
  return `${formatShortDate(date, timeZone)}, ${formatClockTime(date, timeZone, true)}`
}

export function getGreeting(date: Date, timeZone: string) {
  const hour = Number(
    new Intl.DateTimeFormat('en-GB', {
      timeZone,
      hour: '2-digit',
      hourCycle: 'h23',
    }).format(date),
  )

  if (hour < 12) return 'Good Morning'
  if (hour < 17) return 'Good Afternoon'
  return 'Good Evening'
}
