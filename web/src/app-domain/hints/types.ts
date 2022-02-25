export type Store = {
  corpus: {
    selected: string;
    options: string[];
  };
  activeId: number;
  values: Record<number, string>;
  status: Record<number, BoxStatus>;
  hints: WordHint[];
  searchLimit?: number;
  loading: {
    corpus: LoadingState;
    hints: LoadingState;
  };
};

export type WordHint = {
  word: string;
  score: number;
};
