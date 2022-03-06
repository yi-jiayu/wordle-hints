import { HintsAction as A } from "app-domain/hints";
import React, { MutableRefObject } from "react";
import { useDispatch } from "react-redux";
import Keyboard from "react-simple-keyboard";
import "react-simple-keyboard/build/css/index.css";
import styles from "./styles.module.css";

type Props = {
  keyboardRef: MutableRefObject<typeof Keyboard>;
};

const KeyboardWrapper = ({ keyboardRef }: Props) => {
  const dispatch = useDispatch();
  const onKeyPress = (value: string): void => {
    if (value === "{bksp}") {
      dispatch(A.clearBoxValue());
    } else {
      value = value.toUpperCase();
      if (value.match(/^[A-Z]$/)) {
        dispatch(A.setBoxValue(value.toUpperCase()));
      }
    }
  };

  return (
    <div className={styles.keyboard}>
      <Keyboard
        keyboardRef={(r) => (keyboardRef.current = r)}
        onKeyPress={onKeyPress}
        layoutName="default"
        layout={{
          default: [
            "Q W E R T Y U I O P",
            "A S D F G H J K L",
            "Z X C V B N M {bksp}",
          ],
        }}
        display={{
          "{bksp}": "⌫",
        }}
        physicalKeyboardHighlight={true}
        physicalKeyboardHighlightPress={true}
        buttonTheme={[
          {
            class: styles.ctrlKeys,
            buttons: "{bksp}",
          },
          {
            class: styles.keyLeft,
            buttons: "A Z",
          },
          {
            class: styles.keyL,
            buttons: "L",
          },
        ]}
      />
    </div>
  );
};

export default KeyboardWrapper;
