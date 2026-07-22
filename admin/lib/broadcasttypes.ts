// lib/broadcastTypes.ts
//
// Bu fayl bot/services/broadcast_worker.py dagi job sxemasi bilan QAT'IY
// mos bo'lishi kerak. Ikkalasini o'zgartirsangiz, ikkalasini ham yangilang.

export type MediaType = "text" | "photo" | "video" | "document";

export interface BroadcastJobContent {
  content: string; // xabar matni (HTML formatlash bilan)
  message_type: MediaType;
  media_url: string | null;
}

export interface BroadcastJob {
  id: string; // broadcastId
  batch_number: number;
  user_ids: number[];
  content: BroadcastJobContent;
  progress_key: string; // `broadcast:${id}:progress`
}

export interface BroadcastProgress {
  status: "pending" | "sending" | "completed" | "failed";
  total: number;
  sent: number;
  failed: number;
}
