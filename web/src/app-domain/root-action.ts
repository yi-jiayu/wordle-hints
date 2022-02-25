import { ActionType } from "typesafe-actions";
import { HintsAction } from "./hints";

type AllActions = ActionType<typeof HintsAction>;

export default AllActions;
