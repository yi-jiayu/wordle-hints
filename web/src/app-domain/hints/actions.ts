import { createAction, createAsyncAction } from "typesafe-actions";
import * as T from "./types";

export const fetchHintsCorpus = createAsyncAction(
  "HINTS_FETCH_CORPUS_REQUEST",
  "HINTS_FETCH_CORPUS_SUCCESS",
  "HINTS_FETCH_CORPUS_FAILURE"
)<void, string[], void>();

export const clearBoxValue = createAction("HINTS_CLEAR_BOX_VALUE")();

export const toggleBoxStatus = createAction(
  "HINTS_TOGGLE_BOX_STATUS"
)<number>();

export const setBoxValue = createAction("HINTS_SET_BOX_VALUE")<string>();

export const fetchHints = createAsyncAction(
  "HINTS_FETCH_REQUEST",
  "HINTS_FETCH_SUCCESS",
  "HINTS_FETCH_FAILURE"
)<void, T.WordHint[], void>();

export const setCorpus = createAction("HINTS_SET_CORPUS")<string>();

export const setSearchLimit = createAction("HINTS_SET_SEARCH_LIMIT")<
  number | undefined
>();
