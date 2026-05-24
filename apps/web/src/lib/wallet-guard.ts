import type { Eip1193Provider, EthereumRequestArguments } from '@/types/ethereum';

export type WalletGuardErrorCode =
  | 'NO_PROVIDER'
  | 'REQUEST_REJECTED'
  | 'UNSUPPORTED_METHOD'
  | 'UNKNOWN_ERROR';

export type WalletGuardError = {
  code: WalletGuardErrorCode;
  message: string;
};

export type WalletGuardResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: WalletGuardError };

function getProvider(): Eip1193Provider | null {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.ethereum ?? null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function mapProviderError(error: unknown): WalletGuardError {
  if (!isRecord(error)) {
    return {
      code: 'UNKNOWN_ERROR',
      message: 'Unknown wallet error.',
    };
  }

  const rawCode = error.code;
  const rawMessage = error.message;

  if (rawCode === 4001) {
    return {
      code: 'REQUEST_REJECTED',
      message: typeof rawMessage === 'string' ? rawMessage : 'Wallet request rejected by user.',
    };
  }

  if (rawCode === 4200) {
    return {
      code: 'UNSUPPORTED_METHOD',
      message: typeof rawMessage === 'string' ? rawMessage : 'Wallet method is not supported.',
    };
  }

  return {
    code: 'UNKNOWN_ERROR',
    message: typeof rawMessage === 'string' ? rawMessage : 'Wallet request failed.',
  };
}

export function hasWalletProvider(): boolean {
  return getProvider() !== null;
}

export function isMetaMaskProvider(): boolean {
  const provider = getProvider();
  return provider?.isMetaMask === true;
}

export async function safeEthereumRequest<T = unknown>(
  args: EthereumRequestArguments
): Promise<WalletGuardResult<T>> {
  const provider = getProvider();

  if (!provider) {
    return {
      ok: false,
      error: {
        code: 'NO_PROVIDER',
        message: 'No Ethereum wallet provider detected in this browser.',
      },
    };
  }

  try {
    const data = await provider.request<T>(args);
    return { ok: true, data };
  } catch (error) {
    return {
      ok: false,
      error: mapProviderError(error),
    };
  }
}

export async function safeConnectWallet(): Promise<WalletGuardResult<string[]>> {
  return safeEthereumRequest<string[]>({ method: 'eth_requestAccounts' });
}
