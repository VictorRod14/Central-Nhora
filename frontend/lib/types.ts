export interface Inbox { id: number; name: string; department?: string; display_name?: string }
export interface Agent { id: number; name: string; availability_status?: string }
export interface Label { id?: number; title: string; color?: string; description?: string }
export interface Contact { id: number; name: string; phone_number?: string; thumbnail?: string }
export interface MessageAttachment { id: number; file_type: string; data_url?: string; thumb_url?: string; file_size?: number }
export interface Message {
  id: number;
  content?: string;
  message_type: number | string;
  created_at: number;
  sender?: { name?: string };
  attachments?: MessageAttachment[];
}
export interface Conversation {
  id: number;
  status: string;
  inbox_id: number;
  unread_count: number;
  timestamp?: number;
  last_activity_at?: number;
  last_non_activity_message?: Message;
  labels?: string[];
  custom_attributes?: Record<string, string | number | boolean | null>;
  meta?: { sender?: Contact; assignee?: Agent; channel?: string };
}
