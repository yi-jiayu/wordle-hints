import { notification, Typography } from "antd";
import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosRequestHeaders,
  AxiosRequestTransformer,
  AxiosResponse,
  AxiosResponseTransformer,
} from "axios";
import camelCaseKeys from "camelcase-keys";
import { ReactNode } from "react";
import {
  BeforeRequestFunction,
  ErrorFunction,
  RequestConfig,
  SuccessFunction,
} from "./types";

const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8080`;

/*
 * HEADERS
 */

const isJson = (headers?: AxiosRequestHeaders) => {
  if (!headers) {
    return false;
  }

  for (const key of Object.keys(headers)) {
    if (key.toLowerCase() === "content-type") {
      const value = headers[key];
      if (typeof value === "string") {
        return value.toLowerCase().includes("application/json");
      }
    }
  }
  return false;
};

const CamelCaseKeysTransformer: AxiosRequestTransformer = (data, headers) => {
  if (!isJson(headers)) return data;

  if (typeof data === "object" && !(data instanceof FormData)) {
    if (Array.isArray(data) && typeof data[0] === "string") return data;
    return camelCaseKeys(data, { deep: true });
  }
  return data;
};

/*
 * Functions for handling intermediate operations during request
 */

function runFunctionHandlers(
  funcs?: BeforeRequestFunction | BeforeRequestFunction[]
) {
  if (funcs === undefined) return;

  if (typeof funcs === "function") {
    funcs();
  } else {
    funcs.forEach((f) => runFunctionHandlers(f));
  }
}

function runSuccessHandlers<R>(
  data: R,
  funcs?: SuccessFunction<R> | SuccessFunction<R>[]
) {
  if (funcs === undefined) return;

  if (typeof funcs === "function") {
    funcs(data);
  } else {
    funcs.forEach((f) => runSuccessHandlers(data, f));
  }
}

function runErrorHandlers(
  error: AxiosResponse,
  funcs?: ErrorFunction | ErrorFunction[]
) {
  if (funcs === undefined) return;

  if (typeof funcs === "function") {
    funcs(error);
  } else {
    funcs.forEach((f) => runErrorHandlers(error, f));
  }
}

function wrapErrorResponse(e?: AxiosResponse) {
  if (!e)
    // if server down, this would be empty
    return {
      status: 500,
      data: "Server is likely to be down",
      config: {},
      headers: {},
      request: {},
      statusText: "",
    };
  return e;
}

/*
 * API Class
 */

export class API {
  private client: AxiosInstance;

  constructor(section?: string, config?: AxiosRequestConfig) {
    section = (section || "").replace(/^\/*/, "").replace(/\/*$/, "");
    const {
      baseURL = `${BASE_URL}/api/${section}`,
      transformRequest = [
        ...(axios.defaults.transformRequest as AxiosRequestTransformer[]),
      ],
      transformResponse = [
        ...(axios.defaults.transformResponse as AxiosResponseTransformer[]),
        CamelCaseKeysTransformer,
      ],
      ...rest
    } = config || {};

    this.client = axios.create({
      baseURL,
      transformRequest,
      transformResponse,
      ...rest,
    });
  }

  async Get<R>(endpoint: string, config?: RequestConfig<R>) {
    return await this.execute<R>("GET", endpoint, undefined, config);
  }

  async Post<R>(endpoint: string, payload: any, config?: RequestConfig<R>) {
    return await this.execute<R>("POST", endpoint, payload, config);
  }

  async Put<R>(endpoint: string, payload: any, config?: RequestConfig<R>) {
    return await this.execute<R>("PUT", endpoint, payload, config);
  }

  async Delete<R>(endpoint: string, payload?: any, config?: RequestConfig<R>) {
    return await this.execute<R>("DELETE", endpoint, payload, config);
  }

  private async execute<R>(
    method: "GET" | "PUT" | "POST" | "DELETE",
    endpoint: string,
    payload?: any,
    config?: RequestConfig<R>
  ): Promise<AxiosResponse<R>> {
    const {
      onError = [],
      onSuccess = [],
      beforeRequest = [],
      afterResponse = [],
      returnErrorResponse = true,
      ...req
    } = config || {};

    runFunctionHandlers(beforeRequest);

    try {
      const result = await this.axiosCall<R>(method, endpoint, payload, req);

      runSuccessHandlers(result.data, onSuccess);
      return result;
    } catch (e) {
      const error = wrapErrorResponse((e as AxiosError).response);
      runErrorHandlers(error, onError);
      if (returnErrorResponse) return error;

      throw e;
    } finally {
      // Run after response function only if there are no errors
      runFunctionHandlers(afterResponse);
    }
  }

  private async axiosCall<R>(
    method: "GET" | "PUT" | "POST" | "DELETE",
    endpoint: string,
    payload: any,
    config: AxiosRequestConfig
  ): Promise<AxiosResponse<R>> {
    endpoint = endpoint.replace(/^\/*/, "");

    switch (method) {
      case "GET":
        return await this.client.get<R>(endpoint, config);
      case "PUT":
        return await this.client.put<R>(endpoint, payload, config);
      case "POST":
        return await this.client.post<R>(endpoint, payload, config);
      case "DELETE":
        if (payload) {
          config.data = payload;
          config.headers = { "content-type": "application/json" };
        }

        return await this.client.delete<R>(endpoint, config);
    }
  }
}

export const notifyOnApiError = (e: AxiosResponse) => {
  let content: ReactNode;
  if (e.status === 422) {
    const detail = e.data.detail as {
      loc: string[];
      msg: string;
    }[];

    content = (
      <ul>
        {detail.map(({ loc, msg }, i) => (
          <li key={i}>
            <b>{loc.join(" - ")}</b> - {msg}
          </li>
        ))}
      </ul>
    );
  } else {
    content = e.data;
  }

  console.log(e);
  notification.error({
    duration: 5,
    message: (
      <div>
        <Typography.Text strong>Status</Typography.Text>: {e.status}
        <br />
        <Typography.Paragraph>{content}</Typography.Paragraph>
      </div>
    ),
  });
};
