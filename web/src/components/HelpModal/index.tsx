import { QuestionOutlined } from "@ant-design/icons";
import { Button, Divider, Modal, Typography } from "antd";
import React, { useState } from "react";
import ColorText from "./ColorText";

const { Title, Paragraph, Text } = Typography;

const HelpModal = () => {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <Button
        shape="circle"
        icon={<QuestionOutlined />}
        onClick={() => {
          setVisible(true);
        }}
      />
      <Modal visible={visible} onCancel={() => setVisible(false)} footer={null}>
        <Typography>
          <Title level={2}>Wordle Hints Help</Title>
          <Divider />
          <Title level={3} underline>
            Usage
          </Title>
          <Paragraph>
            The organization of the letters work in the same fashion as Wordle.
            Just type in the characters as you would into the boxes above.
          </Paragraph>
          <Paragraph>
            By default, when a letter is put in, it will have a{" "}
            <ColorText color="Gray" /> background. Tap on the background to
            toggle among <ColorText color="Yellow" /> and{" "}
            <ColorText color="Green" />. The colors have the following meaning:
          </Paragraph>
          <Paragraph>
            <ul>
              {[
                ["Gray", "Letter does not exist in word"],
                ["Yellow", "Letter exists but is not in correct location"],
                ["Green", "Letter exists and is in correct location"],
              ].map(([color, message]) => (
                <li key={color}>
                  <ColorText color={color as "Gray" | "Yellow" | "Green"} /> -{" "}
                  {message}
                </li>
              ))}
            </ul>
          </Paragraph>
          <Divider />
          <Title level={3} underline>
            Controls
          </Title>
          <Paragraph>
            If there are errors, the arrow button at the top right hand side
            will be{" "}
            <Text strong style={{ backgroundColor: "red", color: "white" }}>
              RED
            </Text>{" "}
            and will show a list of errors. Otherwise, clicking on the arrow
            button will fetch a list of hints.
          </Paragraph>
          <Paragraph>
            The settings button allow you to limit the number of hints and also
            to select the corpus to use.
          </Paragraph>
        </Typography>
      </Modal>
    </>
  );
};

export default HelpModal;
