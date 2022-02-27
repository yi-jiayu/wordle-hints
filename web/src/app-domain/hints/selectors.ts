import { NUM_LETTERS, NUM_TRIES } from "app-constants";
import { RootState } from "app-domain/root-state";
import { range, reduce } from "lodash";
import * as T from "./types";

type WordHintQueryBuilder = {
  letter: string;
  positions: Set<number>; // fixed position
  exclude_positions: Set<number>; // letters not in these positions
  atLeast: number;
  atMost: number;
};

export const selectHintQuery = ({
  hints: { status, values, activeId },
}: RootState): { errors: string[]; query: T.WordHintQuery[] } => {
  const queryMap: Record<string, WordHintQueryBuilder> = {};
  range(NUM_TRIES).forEach((row) => {
    // for each row
    // count the number of letter occurrence to get the maximum number of occurrence of each letter
    // If there are 2 greens or 2 yellows, it means that the letter occurs at least 2 times
    // 1 green and 1 grey means at most one time

    const rowNum = row * NUM_LETTERS;
    if (status[rowNum] === "unknown" || values[rowNum] === "") return;

    UpdateQueryPayload(row, queryMap);
  });

  const errors = [];
  if (activeId === 0) {
    errors.push("No letters specified");
  }

  const query = Object.values(queryMap).map(
    ({ exclude_positions, positions, ...rest }) => ({
      ...rest,
      exclude_positions: Array.from(exclude_positions),
      positions: Array.from(positions),
    })
  );

  return { errors, query };

  function GetLetterLimitPerRow(row: number) {
    const letterStatusArray = range(NUM_LETTERS).reduce((acc, col) => {
      const i = row * NUM_LETTERS + col; // index
      const s = status[i];
      const v = values[i];

      if (!acc.hasOwnProperty(v)) {
        acc[v] = [s];
      } else {
        acc[v].push(s);
      }

      return acc;
    }, {} as Record<string, BoxStatus[]>);

    return reduce(
      letterStatusArray,
      (acc, statuses, letter) => {
        let inc = 0; // inclusive count
        let exc = 0; // exclusive count

        statuses.forEach((s) => {
          switch (s) {
            case "actual":
            case "include":
              inc += 1;
              break;
            case "exclude":
              exc += 1;
              break;
          }
        }); // letter count
        let atMost = 0; // by default, at most is purely exclusive. This means we exclude the letter

        if (inc > 0) {
          if (exc === 0) {
            // for example, if we choose letter 'S' and it has 2 greens (or yellows) and 0 gray, then we can have at most 5 'S'
            atMost = NUM_LETTERS;
          } else {
            // for example, if we choose letter 'S' and it has 2 greens (or yellows) and 1 gray, then we have at most 2 'S'
            atMost = inc;
          }
        }

        acc[letter] = { atLeast: inc, atMost };

        return acc;
      },
      {} as Record<string, { atLeast: number; atMost: number }>
    );
  }

  function UpdateQueryPayload(
    row: number,
    query: Record<string, WordHintQueryBuilder>
  ) {
    const letterCountMap = GetLetterLimitPerRow(row);

    range(NUM_LETTERS).forEach((col) => {
      const i = row * NUM_LETTERS + col; // index
      const pos = (i % NUM_LETTERS) + 1;
      const s = status[i];
      const v = values[i];

      const { atLeast, atMost } = letterCountMap[v];

      if (!query.hasOwnProperty(v)) {
        query[v] = {
          letter: v,
          positions: new Set<number>(),
          exclude_positions: new Set<number>(),
          atLeast,
          atMost,
        };
      } else {
        query[v].atMost = Math.min(query[v].atMost, atMost);
        query[v].atLeast = Math.max(query[v].atLeast, atLeast);
      }

      switch (s) {
        case "actual":
          query[v].positions.add(pos);
          break;
        case "include":
          query[v].exclude_positions.add(pos);
          break;
      }
    });
  }
};
