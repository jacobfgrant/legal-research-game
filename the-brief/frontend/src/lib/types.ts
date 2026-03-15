export interface DialogueLine {
	character: string;
	line: string;
}

export interface CharacterInfo {
	name: string;
	title: string;
}

export interface ResolvedChoice {
	label: string;
	index: number;
}

export interface ResolvedScene {
	id: string;
	act: string;
	text: string;
	dialogue: DialogueLine[] | null;
	choices: ResolvedChoice[] | null;
	character_info: Record<string, CharacterInfo>;
}

export interface ResearchItem {
	id: string;
	name: string;
	description: string;
	type: string;
	jurisdiction: string | null;
}

export interface GameState {
	save_id: string;
	current_chapter: string;
	current_scene: string;
	research_found: string[];
	relationships: Record<string, number>;
	career: Record<string, number>;
}

export interface SaveSummary {
	save_id: string;
	current_chapter: string;
	current_scene: string;
	updated_at: string;
}

export interface NewGameResponse {
	save_id: string;
	scene: ResolvedScene;
}

export interface ChapterSummary {
	id: string;
	title: string;
	description: string;
}
