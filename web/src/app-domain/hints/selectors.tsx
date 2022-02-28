import { NUM_LETTERS, NUM_TRIES } from "app-constants";
import { RootState } from "app-domain/root-state";
import { range, reduce } from "lodash";
import React from "react";
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
}: RootState): { errors: React.ReactNode[]; query: T.WordHintQuery[] } => {
  const errors = [];
  if (activeId === 0) {
    errors.push("No letters specified");
  } else if (activeId % NUM_LETTERS > 0) {
    const diff = NUM_LETTERS - (activeId % NUM_LETTERS);
    errors.push(
      `Need ${diff} more letter${diff > 1 ? "s" : ""} to complete the word`
    );
  }

  if (errors.length > 0) {
    return { errors, query: [] };
  }

  const queryMap: Record<string, WordHintQueryBuilder> = {};
  range(NUM_TRIES).forEach((row) => {
    UpdateQueryPayload(row, queryMap);
  });

  const query = Object.values(queryMap).map(
    ({ exclude_positions, positions, ...rest }) => ({
      ...rest,
      exclude_positions: Array.from(exclude_positions),
      positions: Array.from(positions),
    })
  );

  return { query, errors: Validate(query) };

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

    // for each row
    // count the number of letter occurrence to get the maximum number of occurrence of each letter
    // If there are 2 greens or 2 yellows, it means that the letter occurs at least 2 times
    // 1 green and 1 grey means at most one time
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
      if (status[i] === "unknown" || values[i] === "") return;

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

  function Validate(query: T.WordHintQuery[]) {
    return query.reduce((errors, q) => {
      if (q.atLeast > q.atMost) {
        errors.push(
          <>
            Letter <b>{q.letter}</b> is ill-defined
          </>
        );
      }

      return errors;
    }, [] as React.ReactNode[]);
  }
};
