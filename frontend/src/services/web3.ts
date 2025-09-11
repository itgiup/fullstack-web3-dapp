import { createConfig, http } from '@wagmi/core';
import { mainnet, goerli, polygon, polygonMumbai } from '@wagmi/core/chains';
import { injected, metaMask } from '@wagmi/connectors';
import { config } from '../utils/config';

const chains = [mainnet, goerli, polygon, polygonMumbai] as const;

export const wagmiConfig = createConfig({
  chains,
  connectors: [
    injected(),
    metaMask(),
  ],
  transports: {
    [mainnet.id]: http(),
    [goerli.id]: http(),
    [polygon.id]: http(),
    [polygonMumbai.id]: http(),
  },
});

export const formatAddress = (address: string, length = 4): string => {
  if (!address) return '';
  return `${address.slice(0, length + 2)}...${address.slice(-length)}`;
};

export const isValidAddress = (address: string): boolean => {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
};

export const getChainName = (chainId: number): string => {
  const chain = chains.find(c => c.id === chainId);
  return chain?.name || 'Unknown Chain';
};

export const getSupportedChains = () => chains;

export const generateSignMessage = (address: string, nonce?: string): string => {
  const timestamp = new Date().toISOString();
  const message = `Welcome to ${config.APP_NAME}!\n\nPlease sign this message to authenticate your wallet.\n\nWallet: ${address}\nTimestamp: ${timestamp}`;
  
  if (nonce) {
    return `${message}\nNonce: ${nonce}`;
  }
  
  return message;
};
