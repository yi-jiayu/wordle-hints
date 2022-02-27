import { API, notifyOnApiError } from "app-domain/api";
import { ThunkFunctionAsync } from "app-domain/types";
import * as A from "./actions";
import { selectHintQuery } from "./selectors";
import * as T from "./types";

const api = new API("hint");

export const fetchCorpus = (): ThunkFunctionAsync => async (dispatch) => {
  await api.Get<string[]>("corpus", {
    beforeRequest: () => dispatch(A.fetchHintsCorpus.request()),
    onSuccess: (data) => {
      if (data.length > 0) {
        dispatch(A.fetchHintsCorpus.success(data));
      } else {
        throw new Error("could not fetch any corpus from the api server");
      }
    },
    onError: (e) => {
      notifyOnApiError(e);
      dispatch(A.fetchHintsCorpus.failure());
    },
  });
};

export const fetchHints =
  (): ThunkFunctionAsync<boolean> => async (dispatch, getState) => {
    const state = getState();
    const corpus = state.hints.corpus.selected;
    const { query } = selectHintQuery(state);

    const { status } = await api.Post<T.WordHint[]>(
      "",
      { corpus, limit: state.hints.searchLimit, query },
      {
        beforeRequest: () => dispatch(A.fetchHints.request()),
        onSuccess: (data) => dispatch(A.fetchHints.success(data)),
        onError: (e) => {
          notifyOnApiError(e);
          dispatch(A.fetchHints.failure());
        },
      }
    );
    return status === 200;
  };
