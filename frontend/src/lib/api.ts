/**
 * API 客户端配置
 * 这个文件封装了所有与后端 FastAPI 服务的通信
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

/**
 * 通用的 fetch 封装函数
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `API Error: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`API Request Failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * 数据类型定义
 */
export interface UserNote {
  note_url: string;
  note_id?: string;
  title?: string;
}

export interface UserNotesResponse {
  success: boolean;
  message: string;
  data: UserNote[];
}

export interface NoteComment {
  commenter_id: string;
  commenter_name: string;
  comment_content: string;
  published_time: number;
  likes_on_comment: number;
}

export interface NoteDetail {
  channel_id: string;
  content_id: string;
  content_type: string;
  content_title: string;
  likes: number;
  shares: number;
  views: number;
  published_time: string | Date;
  collected_number: number;
  comments: NoteComment[];
  description: string;
  tags: string[];
  note_url: string;
  last_updated: string | Date;
}

export interface NoteDetailResponse {
  success: boolean;
  message: string;
  data: NoteDetail;
}

export interface UserInfo {
  user_id: string;
  user_name: string;
  red_id?: string;
  fans?: string | number;
  note_count?: number;
  is_verified?: boolean;
  avatar?: string;
  description?: string;
}

export interface UserDetailResponse {
  success: boolean;
  message: string;
  data: UserInfo;
}

/**
 * API 方法集合
 */
export const xhsApi = {
  /**
   * 获取用户笔记列表
   * @param userUrl 用户主页 URL (例如: https://www.xiaohongshu.com/user/profile/xxx)
   */
  async getUserNotes(userUrl: string): Promise<UserNotesResponse> {
    const encodedUrl = encodeURIComponent(userUrl);
    return apiFetch<UserNotesResponse>(`/user/notes?user_url=${encodedUrl}`);
  },

  /**
   * 获取笔记详情
   * @param noteUrl 笔记 URL (例如: https://www.xiaohongshu.com/explore/xxx)
   */
  async getNoteInfo(noteUrl: string): Promise<NoteDetailResponse> {
    const encodedUrl = encodeURIComponent(noteUrl);
    return apiFetch<NoteDetailResponse>(`/note/info?note_url=${encodedUrl}`);
  },

  /**
   * 获取用户笔记列表（从路由）
   * @param userUrl 用户主页 URL
   */
  async getUserNoteList(userUrl: string): Promise<UserNotesResponse> {
    const encodedUrl = encodeURIComponent(userUrl);
    return apiFetch<UserNotesResponse>(`/user/note_list?user_url=${encodedUrl}`);
  },

  /**
   * 获取用户详细信息
   * @param userUrl 用户主页 URL
   */
  async getUserDetail(userUrl: string): Promise<UserDetailResponse> {
    const encodedUrl = encodeURIComponent(userUrl);
    return apiFetch<UserDetailResponse>(`/user/detail_info?user_url=${encodedUrl}`);
  },

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string }> {
    return apiFetch<{ status: string }>('/health');
  },
};

/**
 * 错误处理工具
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 导出 API 基础 URL，方便其他地方使用
 */
export { API_BASE_URL };
