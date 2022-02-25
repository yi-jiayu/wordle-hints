import { LIMIT, NUM_LETTERS } from "app-constants";
import { RootState } from "app-domain/root-state";
import { forEach, map, range } from "lodash";
import React from "react";

export const selectHintQuery = ({
  hints: { status, values, activeId },
}: RootState) => {
  const fixedMap: Record<string, number> = {};
  const includeMap: Record<string, number[]> = {};
  const excludeMap = new Set<string>();

  range(LIMIT).forEach((i) => {
    const s = status[i];
    const v = values[i];

    if (v === "" || s === "unknown") return;
    switch (s) {
      case "exclude":
        excludeMap.add(v);
        break;
      case "actual":
        fixedMap[v] = (i % NUM_LETTERS) + 1;
        break;
      case "include":
        includeMap[v] ??= [];
        includeMap[v].push((i % NUM_LETTERS) + 1);
        break;
    }
  });

  const errorMap: Record<string, React.ReactNode> = {};
  forEach(fixedMap, (_, e) => {
    if (excludeMap.has(e)) {
      errorMap[e] = (
        <span>
          <b>{e}</b> is both excluded and included
        </span>
      );
    }
  });
  forEach(includeMap, (_, e) => {
    if (excludeMap.has(e)) {
      errorMap[e] = (
        <>
          <b>{e}</b> is both excluded and included
        </>
      );
    }
  });

  const errors = Object.values(errorMap);
  if (activeId === 0) {
    errors.push("No letters specified");
  }

  const fixed = map(fixedMap, (position, letter) => ({ letter, position }));
  const include = map(includeMap, (excludePosition, letter) => ({
    letter,
    excludePosition,
  }));
  const exclude = Array.from(excludeMap);

  return { fixed, include, exclude, errors };
};
