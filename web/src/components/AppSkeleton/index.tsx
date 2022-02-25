import { ContainerOutlined, MenuUnfoldOutlined, OrderedListOutlined, } from "@ant-design/icons";
import { Drawer, Layout, Menu } from "antd";
import React, { PropsWithChildren, useState } from "react";
import styles from "./styles.module.css";

const TITLE_TEXT = "WordleHints";

type Props = PropsWithChildren<{
  header: {
    left: React.ReactNode;
    right: React.ReactNode;
  };
  footer: React.ReactNode;
}>;

const AppSkeleton = ({ children, header, footer }: Props) => {
  const [collapsed, setCollapsed] = useState(true);
  const toggleCollapse = () => setCollapsed((v) => !v);

  return (
    <Layout>
      <div className={styles.header}>
        <div>
          <MenuUnfoldOutlined
            onClick={toggleCollapse}
            className={styles.headerIcon}
          />
          {header.left}
        </div>
        <div className={styles.title}>{TITLE_TEXT}</div>
        <div>{header.right}</div>
      </div>
      <Layout.Content className={styles.contentBody}>
        <Drawer
          title={<span>{TITLE_TEXT}</span>}
          headerStyle={{ borderBottomColor: "#656565" }}
          placement="left"
          width={500}
          visible={!collapsed}
          onClose={toggleCollapse}
        >
          <Menu mode="inline" defaultSelectedKeys={["Hints"]}>
            <Menu.Item
              key="Hints"
              icon={<OrderedListOutlined />}
              onClick={() => {
                toggleCollapse();
              }}
            >
              Hints
            </Menu.Item>
            <Menu.Item
              key="Documentation"
              icon={<ContainerOutlined />}
              onClick={() => {
                toggleCollapse();
              }}
            >
              Documentation
            </Menu.Item>
          </Menu>
        </Drawer>
        {children}
      </Layout.Content>
      <div className={styles.footer}>{footer}</div>
    </Layout>
  );
};

export default AppSkeleton;
