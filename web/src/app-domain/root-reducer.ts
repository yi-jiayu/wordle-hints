import { combineReducers } from "redux";
import { RootState } from "./root-state";
import { HintsReducer } from "./hints";

export default combineReducers<RootState>({
  hints: HintsReducer,
});
