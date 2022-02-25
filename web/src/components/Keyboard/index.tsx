import React, { useRef } from "react";
import KeyboardWrapper from "./KeyboardWrapper";
import styles from "./styles.module.css";

const Keyboard = () => {
  const keyboard = useRef(null as any);
  return (
    <div className={styles.keyboardContainer}>
      <KeyboardWrapper keyboardRef={keyboard} />
    </div>
  );
};

export default Keyboard;
