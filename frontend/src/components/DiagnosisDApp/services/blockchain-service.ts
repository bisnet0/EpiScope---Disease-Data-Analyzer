import { ethers } from "ethers";
import { INPUT_BOX_ADDRESS, DAPP_ADDRESS, INPUTBOX_ABI } from "../utils/constants";
import { type HistoryItem } from "../types";

export const sendDiagnosisToCartesi = async (
  item: HistoryItem, 
  signer: any, 
  walletAddress: string
) => {
  // 💡 ENVIO DIRETO (Garante o Hash no Ganache)
  const tx = await signer.sendTransaction({
    to: DAPP_ADDRESS, // Pode ser qualquer endereço, o Ganache aceita
    value: 0,
    data: ethers.hexlify(ethers.toUtf8Bytes(JSON.stringify({
      id: item.id,
      type: item.type,
      result: item.result
    })))
  });

  const receipt = await tx.wait();
  return receipt.hash; // Esse hash vai para o seu Postgres!
};