import { SendOutlined } from "@ant-design/icons";
import { Button, List, Modal, Skeleton, Table } from "antd";
import { HintsApi } from "app-domain/hints";
import { selectHintQuery } from "app-domain/hints/selectors";
import { useRootSelector } from "app-domain/hooks";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

const useHintState = () =>
  useRootSelector((state) => {
    const { errors } = selectHintQuery(state);
    const { hints } = state;

    const loading = hints.loading.hints === "REQUEST";
    const hasErrors = errors.length > 0;

    return { loading, hasErrors };
  });

const ResultTable = () => {
  const hints = useRootSelector((s) => s.hints.hints);
  const columns = [
    { title: "Word", dataIndex: "word" },
    { title: "Score", dataIndex: "score" },
  ];

  return (
    <Table columns={columns} dataSource={hints} size="small" rowKey="word" />
  );
};

const ErrorList = () => {
  const { errors } = useRootSelector(selectHintQuery);

  return (
    <List
      header={<h4>Errors</h4>}
      bordered
      dataSource={errors}
      renderItem={(msg) => <List.Item>{msg}</List.Item>}
    />
  );
};

const ResultsModal = () => {
  const dispatch = useDispatch();
  const [visible, setVisible] = useState(false);
  const { loading, hasErrors } = useHintState();

  return (
    <div>
      <Button
        shape="circle"
        style={{ color: hasErrors ? "#b01010" : undefined }}
        icon={<SendOutlined />}
        onClick={async () => {
          if (hasErrors) {
            setVisible(true); // show error message straightaway
          } else if (await dispatch(HintsApi.fetchHints())) {
            setVisible(true); // wait for hints to be retrieved before showing
          }
        }}
      />
      <Modal
        visible={visible}
        title="Results"
        onCancel={() => setVisible(false)}
        footer={null}
      >
        <Skeleton
          active={true}
          loading={loading}
          title={true}
          paragraph={{
            rows: 10,
          }}
        >
          {hasErrors ? <ErrorList /> : <ResultTable />}
        </Skeleton>
      </Modal>
    </div>
  );
};

export default ResultsModal;
