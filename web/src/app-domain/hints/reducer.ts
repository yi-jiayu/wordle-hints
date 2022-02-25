import { LIMIT } from "app-constants";
import AllActions from "app-domain/root-action";
import produce from "immer";
import { range, sortBy } from "lodash";
import { getType } from "typesafe-actions";

import * as A from "./actions";
import * as T from "./types";

const defaultState: T.Store = {
  corpus: {
    selected: "",
    options: [],
  },
  activeId: 0,
  values: range(LIMIT).reduce((acc, i) => ({ ...acc, [i]: "" }), {}),
  status: range(LIMIT).reduce((acc, i) => ({ ...acc, [i]: "unknown" }), {}),
  hints: [],
  searchLimit: undefined,
  loading: {
    corpus: "SUCCESS",
    hints: "SUCCESS",
  },
};

const reducer = (state = defaultState, action: AllActions) =>
  produce(state, (draft) => {
    switch (action.type) {
      case getType(A.fetchHintsCorpus.request):
        draft.loading.corpus = "REQUEST";
        draft.corpus.options = [];
        break;
      case getType(A.fetchHintsCorpus.failure):
        draft.loading.corpus = "FAILURE";
        break;
      case getType(A.fetchHintsCorpus.success):
        draft.loading.corpus = "SUCCESS";
        draft.corpus = {
          selected: "web2", // Hard code to always use web 2 first
          options: action.payload.sort(),
        };
        break;

      case getType(A.setBoxValue):
        if (state.activeId === LIMIT) return;

        const value = action.payload;
        if (value.match(/^[a-z]$/i)) {
          draft.values[state.activeId] = value;
          draft.status[state.activeId] = "exclude";
          draft.activeId++;
        }
        break;

      case getType(A.clearBoxValue): {
        const id = state.activeId;
        if (id === 0) return;

        draft.activeId--;
        draft.values[draft.activeId] = "";
        draft.status[draft.activeId] = "unknown";
        break;
      }

      case getType(A.toggleBoxStatus): {
        const id = action.payload;
        if (state.values[id] === "") {
          draft.status[id] = "unknown";
        } else {
          switch (state.status[id]) {
            case "unknown":
            case "include":
              draft.status[id] = "exclude";
              break;
            case "actual":
              draft.status[id] = "include";
              break;
            case "exclude":
              draft.status[id] = "actual";
              break;
          }
        }
        break;
      }

      case getType(A.fetchHints.request):
        draft.loading.hints = "REQUEST";
        draft.hints = [];
        break;

      case getType(A.fetchHints.failure):
        draft.loading.hints = "FAILURE";
        break;

      case getType(A.fetchHints.success):
        draft.loading.hints = "SUCCESS";
        draft.hints = sortBy(action.payload, (e) => -e.score);
        break;

      case getType(A.setCorpus):
        draft.corpus.selected = action.payload;
        break;

      case getType(A.setSearchLimit):
        draft.searchLimit = action.payload;
        break;
    }
  });

export default reducer;
