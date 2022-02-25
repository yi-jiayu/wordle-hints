import { applyMiddleware, createStore } from "redux";
import { composeWithDevTools } from "redux-devtools-extension";
import thunk from "redux-thunk";

import rootReducer from "./root-reducer";

const middleware = composeWithDevTools(applyMiddleware(thunk));
const store = createStore(rootReducer, middleware);
export default store;
