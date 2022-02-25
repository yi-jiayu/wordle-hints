import { NUM_TRIES } from "app-constants";
import { HintsAction as A } from "app-domain/hints";
import range from "lodash/range";
import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import LetterBoxRow from "./LetterBoxRow";
import styles from "./styles.module.css";

// Handler is used to manage operations
const LetterBoxGrid = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    window.addEventListener("keydown", ({ code }) => {
      if (code.startsWith("Key") && code.length === 4) {
        const letter = code[3].toUpperCase();
        if (!letter.match(/[A-Z]/)) {
          return;
        } else {
          dispatch(A.setBoxValue(letter));
        }
      } else if (code === "Backspace") {
        dispatch(A.clearBoxValue());
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={styles.letterBoxGrid}>
      {range(NUM_TRIES).map((rn) => (
        <LetterBoxRow key={rn} rowNum={rn} />
      ))}
    </div>
  );
};

export default LetterBoxGrid;
