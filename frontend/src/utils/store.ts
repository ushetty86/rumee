import create from 'zustand';

interface Note {
  _id: string;
  title: string;
  content: string;
  tags: string[];
  createdAt: string;
}

interface NoteStore {
  notes: Note[];
  setNotes: (notes: Note[]) => void;
  addNote: (note: Note) => void;
  removeNote: (id: string) => void;
}

export const useNoteStore = create<NoteStore>((set) => ({
  notes: [],
  setNotes: (notes) => set({ notes }),
  addNote: (note) => set((state) => ({ notes: [...state.notes, note] })),
  removeNote: (id) =>
    set((state) => ({
      notes: state.notes.filter((note) => note._id !== id),
    })),
}));

interface AppState {
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  selectedNote: string | null;
  setSelectedNote: (id: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
  selectedNote: null,
  setSelectedNote: (id) => set({ selectedNote: id }),
}));
