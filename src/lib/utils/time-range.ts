import dayjs from 'dayjs';

/**
 * Returns a human-friendly time range bucket for a given timestamp:
 * - Today, Yesterday, This week, This month, Earlier this year, Last year, Older
 *
 * Accepts seconds or milliseconds (auto-normalizes), Date, or numeric string.
 */
export function getTimeRange(input: number | string | Date): string {
  let d: dayjs.Dayjs;

  if (input instanceof Date) {
    d = dayjs(input);
  } else if (typeof input === 'string') {
    const n = Number(input);
    if (!Number.isNaN(n)) {
      // normalize seconds to ms when value is likely in seconds
      d = dayjs(n < 1e12 ? n * 1000 : n);
    } else {
      // fallback to dayjs string parsing
      d = dayjs(input);
    }
  } else {
    // number
    const ms = input < 1e12 ? input * 1000 : input;
    d = dayjs(ms);
  }

  const now = dayjs();

  if (d.isSame(now, 'day')) return 'Today';
  if (d.isSame(now.subtract(1, 'day'), 'day')) return 'Yesterday';
import dayjs from 'dayjs';

/**
 * Returns a human-friendly time range bucket for a given timestamp:
 * - Today, Yesterday, This week, This month, Earlier this year, Last year, Older
 *
 * Accepts seconds or milliseconds (auto-normalizes), Date, or numeric string.
 */
export function getTimeRange(input: number | string | Date): string {
  let d: dayjs.Dayjs;

  if (input instanceof Date) {
    d = dayjs(input);
  } else if (typeof input === 'string') {
    const n = Number(input);
    if (!Number.isNaN(n)) {
      // normalize seconds to ms when value is likely in seconds
      d = dayjs(n < 1e12 ? n * 1000 : n);
    } else {
      // fallback to dayjs string parsing
      d = dayjs(input);
    }
  } else {
    // number
    const ms = input < 1e12 ? input * 1000 : input;
    d = dayjs(ms);
  }

  const now = dayjs();

  if (d.isSame(now, 'day')) return 'Today';
  if (d.isSame(now.subtract(1, 'day'), 'day')) return 'Yesterday';

  // Start of this week (Sunday as start) without relying on week plugin
  const startOfThisWeek = now.startOf('day').subtract(now.day(), 'day');
  if (d.isAfter(startOfThisWeek)) return 'This week';

  const startOfThisMonth = now.startOf('month');
  if (d.isAfter(startOfThisMonth)) return 'This month';

  const startOfThisYear = now.startOf('year');
  if (d.isAfter(startOfThisYear)) return 'Earlier this year';

  if (d.isAfter(startOfThisYear.subtract(1, 'year'))) return 'Last year';

  return 'Older';
}
  // Calculate start of this week without relying on dayjs week plugin (Sunday as start)
  const startOfThisWeek = now.startOf('day').subtract(now.day(), 'day');
  if (d.isAfter(startOfThisWeek)) return 'This week';

  const startOfThisMonth = now.startOf('month');
  if (d.isAfter(startOfThisMonth)) return 'This month';

  const startOfThisYear = now.startOf('year');
  if (d.isAfter(startOfThisYear)) return 'Earlier this year';

  if (d.isAfter(startOfThisYear.subtract(1, 'year'))) return 'Last year';

  return 'Older';
}
