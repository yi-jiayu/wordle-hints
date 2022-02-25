import { NUM_LETTERS } from "app-constants";
import range from "lodash/range";
import React from "react";
import LetterBox from "./LetterBox";
import styles from "./styles.module.css";

type Props = {
  rowNum: number;
};

const LetterBoxRow = ({ rowNum }: Props) => (
  <div className={styles.letterBoxRow}>
    {range(NUM_LETTERS).map((i) => (
      <LetterBox key={i} boxId={rowNum * NUM_LETTERS + i} />
    ))}
  </div>
);

export default LetterBoxRow;
