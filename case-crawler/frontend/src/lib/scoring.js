/**
 * Client-side argument strength preview.
 * This is intentionally approximate — the real scoring happens server-side.
 * The purpose is UX feedback, not exact grading.
 */

export function getConfidence(slotAssignments, argumentSlots) {
	if (!argumentSlots) return { level: 'none', label: 'No argument yet' };

	const requiredSlots = argumentSlots.filter(s => s.required);
	const optionalSlots = argumentSlots.filter(s => !s.required);

	const requiredFilled = requiredSlots.filter(s => slotAssignments[s.slot_id]).length;
	const optionalFilled = optionalSlots.filter(s => slotAssignments[s.slot_id]).length;
	const totalFilled = requiredFilled + optionalFilled;

	if (requiredFilled === 0) {
		return { level: 'none', label: 'Missing required authorities' };
	}

	if (requiredFilled < requiredSlots.length) {
		return { level: 'weak', label: 'Required slots incomplete' };
	}

	if (totalFilled <= requiredSlots.length) {
		return { level: 'moderate', label: 'Meets minimum requirements' };
	}

	if (totalFilled >= argumentSlots.length - 1) {
		return { level: 'strong', label: 'Strong argument' };
	}

	return { level: 'good', label: 'Good — consider filling more slots' };
}
