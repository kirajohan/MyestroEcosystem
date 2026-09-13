// lib/broadcastTypes.ts
//
// Bu fayl bot/services/broadcast_worker.py dagi job sxemasi bilan QAT'IY
// mos bo'lishi kerak. Ikkalasini o'zgartirsangiz, ikkalasini ham yangilang.

export type MediaType = "text" | "photo" | "video" | "document";

export type TargetMode = "all" | "manual" | "filter";

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
  broadcast_id?: string;
  title?: string;  // ✅ YANGI: qo'shildi
  status: "pending" | "queued" | "sending" | "completed" | "failed";
  total: number;
  sent: number;
  failed: number;
  created_at?: string;
}


export interface BroadcastCreatePayload {
  title: string;
  content: string;
  message_type: MediaType;
  file_id: string | null;
  target_mode: TargetMode;
  target_user_ids?: number[];
  target_filter?: {
    search?: string;
    role?: string;
    cefr_level?: string;
    lang?: string;
    is_active?: string;
  };
}

export interface BroadcastHistoryItem {
  broadcast_id: string;
  title: string;
  status: string;
  total: number;
  sent: number;
  failed: number;
  created_at: string;
}
