import useSWR from "swr";
import {
  getContextPack,
  getWeakPoints,
  type ContextPackRequest,
  type ContextPackResponse,
  type WeakPointsResponse,
} from "@/lib/api/knowledge";

export function useContextPack(request: ContextPackRequest | null) {
  const key = request
    ? `/api/knowledge/context-pack?${JSON.stringify(request)}`
    : null;

  return useSWR<ContextPackResponse>(
    key,
    () => (request ? getContextPack(request) : Promise.resolve(null as unknown as ContextPackResponse)),
    { revalidateOnFocus: false }
  );
}

export function useWeakPoints(days: number = 30) {
  return useSWR<WeakPointsResponse>(
    `/api/knowledge/weak-points?days=${days}`,
    () => getWeakPoints(days),
    { revalidateOnFocus: false }
  );
}
