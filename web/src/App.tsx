import { Row } from "antd";
import { HintsApi } from "app-domain/hints";
import AppSkeleton from "components/AppSkeleton";
import Keyboard from "components/Keyboard";
import LetterBoxGrid from "components/LetterBoxGrid";
import RightSideOptions from "components/RightSideOptions";
import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import HelpModal from "./components/HelpModal";

const App = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(HintsApi.fetchCorpus());
  }, [dispatch]);

  return (
    <AppSkeleton
      header={{ left: <HelpModal />, right: <RightSideOptions /> }}
      footer={<Keyboard />}
    >
      <Row justify="center">
        <LetterBoxGrid />
      </Row>
    </AppSkeleton>
  );
};

export default App;
