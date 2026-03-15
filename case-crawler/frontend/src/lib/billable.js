/**
 * Billable hours display helpers.
 */

export function formatHours(hours) {
	if (hours <= 0) return '0.00';
	return hours.toFixed(2);
}

export function hoursColor(hours, total) {
	const fraction = hours / total;
	if (fraction > 0.5) return 'var(--color-success)';
	if (fraction > 0.25) return 'var(--color-warning)';
	return 'var(--color-danger)';
}

export function hoursFraction(hours, total) {
	if (total <= 0) return 0;
	return Math.max(0, Math.min(1, hours / total));
}
