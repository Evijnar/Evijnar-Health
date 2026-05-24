export {};

type EthereumRequestParams = readonly unknown[] | Record<string, unknown>;

export interface EthereumRequestArguments {
  method: string;
  params?: EthereumRequestParams;
}

export interface Eip1193Provider {
  request<T = unknown>(args: EthereumRequestArguments): Promise<T>;
  isMetaMask?: boolean;
  on?(event: string, listener: (...args: unknown[]) => void): void;
  removeListener?(event: string, listener: (...args: unknown[]) => void): void;
}

declare global {
  interface Window {
    ethereum?: Eip1193Provider;
  }
}
