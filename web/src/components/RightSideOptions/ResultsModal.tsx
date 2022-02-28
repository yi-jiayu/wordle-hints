import { SendOutlined, WarningTwoTone } from "@ant-design/icons";
import { Button, Modal, notification, Skeleton, Table } from "antd";
import { HintsApi } from "app-domain/hints";
import { selectHintQuery } from "app-domain/hints/selectors";
import { useRootSelector } from "app-domain/hooks";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

const useHintState = () =>
  useRootSelector((state) => {
    const { query, errors } = selectHintQuery(state);
    const { hints } = state;

    const loading = hints.loading.hints === "REQUEST";
    const hasErrors = errors.length > 0;

    return { loading, hasErrors, errors, query };
  });

const ResultTable = () => {
  const hints = useRootSelector((s) => s.hints.hints);
  const columns = [
    { title: "Word", dataIndex: "word" },
    {
      title: "Scores",
      children: [
        { title: "Partition", dataIndex: "partition" },
        { title: "Frequency", dataIndex: "frequency" },
      ],
    },
  ];

  return (
    <Table columns={columns} dataSource={hints} size="small" rowKey="word" />
  );
};

const ResultsModal = () => {
  const dispatch = useDispatch();
  const [visible, setVisible] = useState(false);
  const { loading, hasErrors, errors, query } = useHintState();

  return (
    <div>
      <Button
        shape="circle"
        style={{ color: hasErrors ? "#b01010" : undefined }}
        icon={<SendOutlined />}
        onClick={async () => {
          if (hasErrors) {
            notification.error({
              icon: <WarningTwoTone twoToneColor="#b01010" />,
              message: "Input Errors",
              description: (
                <ul style={{ listStyleType: "none", paddingLeft: 4 }}>
                  {errors.map((e, i) => (
                    <li key={i}>{e}</li>
                  ))}
                </ul>
              ),
              placement: "topRight",
              style: { marginLeft: 0 },
            });
          } else if (await dispatch(HintsApi.fetchHints(query))) {
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
          <ResultTable />
        </Skeleton>
      </Modal>
    </div>
  );
};

export default ResultsModal;
