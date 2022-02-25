import React from "react";
import ResultsModal from "./ResultsModal";
import SettingsModal from "./SettingsModal";
import styles from "./styles.module.css";

const RightSideOptions = () => (
  <div className={styles.container}>
    <SettingsModal />
    <ResultsModal />
  </div>
);

export default RightSideOptions;
