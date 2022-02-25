import { isEqual } from "lodash";
import { useSelector } from "react-redux";
import { RootState } from "./root-state";

export const useRootSelector = <T>(selector: (state: RootState) => T) =>
  useSelector(selector, isEqual);
