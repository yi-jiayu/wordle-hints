import React from "react";
import { STATUS_COLORS } from "../../app-constants";
import { Typography } from "antd";

type Props = {
  color: "Gray" | "Yellow" | "Green";
};

const backgroundColor = (color: Props["color"]) => {
  switch (color) {
    case "Green":
      return STATUS_COLORS.actual;
    case "Gray":
      return STATUS_COLORS.exclude;
    case "Yellow":
      return STATUS_COLORS.include;
  }
};

const ColorText = ({ color }: Props) => (
  <Typography.Text
    strong
    style={{ backgroundColor: backgroundColor(color), color: "white" }}
  >
    {color}
  </Typography.Text>
);

export default ColorText;
