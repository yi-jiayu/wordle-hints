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
  partition: number;
  frequency: number;
};

export type WordHintQuery = {
  letter: string;
  positions: number[]; // fixed position
  exclude_positions: number[]; // letters not in these positions
  atLeast: number;
  atMost: number;
};
