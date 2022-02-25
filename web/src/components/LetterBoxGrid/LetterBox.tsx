import { STATUS_COLORS } from "app-constants";
import { HintsAction as A } from "app-domain/hints";
import { useRootSelector } from "app-domain/hooks";
import React from "react";
import { useDispatch } from "react-redux";
import styles from "./styles.module.css";

type Props = {
  boxId: number;
};

const LetterBox = ({ boxId }: Props) => {
  const dispatch = useDispatch();
  const { value, status } = useRootSelector(
    ({ hints: { values, status } }) => ({
      value: values[boxId],
      status: status[boxId],
    })
  );

  return (
    <div
      className={styles.letterBoxContainer}
      onClick={() => {
        if (value !== "") {
          dispatch(A.toggleBoxStatus(boxId));
        }
      }}
    >
      <div
        className={styles.letterBox}
        style={{ backgroundColor: STATUS_COLORS[status] }}
      >
        {value}
      </div>
    </div>
  );
};

export default LetterBox;
