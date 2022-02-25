import { SettingOutlined } from "@ant-design/icons";
import { Button, Form, Modal, Select, Skeleton } from "antd";
import { HintsAction as A } from "app-domain/hints";
import { useRootSelector } from "app-domain/hooks";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

const { Option } = Select;

const useSettingState = () =>
  useRootSelector(({ hints: { corpus, loading } }) => ({
    ...corpus,
    loading: loading.corpus === "REQUEST",
  }));

const SettingsModal = () => {
  const dispatch = useDispatch();

  const [visible, setVisible] = useState(false);
  const { selected, options, loading } = useSettingState();

  return (
    <div>
      <Button
        shape="circle"
        icon={<SettingOutlined />}
        onClick={() => setVisible(true)}
      />
      <Modal
        visible={visible}
        title="Settings"
        onCancel={() => setVisible(false)}
        footer={null}
      >
        <Skeleton loading={loading} active={true}>
          <Form
            labelCol={{ span: 4 }}
            wrapperCol={{ span: 20 }}
            layout="horizontal"
          >
            <Form.Item label="Corpus">
              <Select
                showSearch={true}
                onChange={(x) => dispatch(A.setCorpus(x))}
                filterOption={(input, option) => {
                  if (!option || !option.value) return true;
                  const value = option.value as string;
                  return value.toLowerCase().indexOf(input.toLowerCase()) >= 0;
                }}
                value={selected}
              >
                {options.map((e, i) => (
                  <Option key={i} value={e}>
                    {e}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item label="Word Limit">
              <Select
                onChange={(x) =>
                  dispatch(
                    A.setSearchLimit(x === "ALL" ? undefined : parseInt(x))
                  )
                }
                value="ALL"
              >
                <Option value="ALL">All</Option>
                {[10, 20, 50, 100].map((e) => (
                  <Option key={e} value={e}>
                    {e}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        </Skeleton>
      </Modal>
    </div>
  );
};

export default SettingsModal;
