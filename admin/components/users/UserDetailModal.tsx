'use client';

import { UserResponse } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import { Dialog } from '@/components/ui/Dialog';
import { DirectMessage } from '@/components/users/DirectMessage';
import { formatDate } from '@/lib/utils';

interface UserDetailModalProps {
  user: UserResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export function UserDetailModal({
  user,
  isOpen,
  onClose,
}: UserDetailModalProps) {
  if (!user) return null;

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="User Details" size="lg">
      <div className="space-y-6 max-h-96 overflow-y-auto">
        {/* Profile Info */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Profile Information
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">ID</p>
              <p className="text-lg font-semibold">{user.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Full Name</p>
              <p className="text-lg font-semibold">{user.full_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="text-lg font-semibold">{user.email}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Role</p>
              <Badge variant={user.role === 'admin' ? 'admin' : 'user'}>
                {user.role}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">CEFR Level</p>
              <p className="text-lg font-semibold">{user.cefr_level}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Target Level</p>
              <p className="text-lg font-semibold">{user.target_level}</p>
            </div>
          </div>
        </div>

        {/* Status Info */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Status
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <Badge variant={user.is_active ? 'active' : 'blocked'}>
                {user.is_active ? 'Active' : 'Blocked'}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">AI Enabled</p>
              <Badge variant={user.ai_enabled ? 'on' : 'off'}>
                {user.ai_enabled ? 'ON' : 'OFF'}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email Verified</p>
              <Badge variant={user.is_verified ? 'active' : 'blocked'}>
                {user.is_verified ? 'Yes' : 'No'}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">Profile Completed</p>
              <Badge variant={user.profile_completed ? 'active' : 'blocked'}>
                {user.profile_completed ? 'Yes' : 'No'}
              </Badge>
            </div>
          </div>
        </div>

        {/* Telegram Info */}
        {(user.telegram_id || user.telegram_username) && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Telegram
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {user.telegram_id && (
                <div>
                  <p className="text-sm text-gray-600">Telegram ID</p>
                  <p className="text-lg font-semibold">{user.telegram_id}</p>
                </div>
              )}
              {user.telegram_username && (
                <div>
                  <p className="text-sm text-gray-600">Telegram Username</p>
                  <p className="text-lg font-semibold">@{user.telegram_username}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Activity
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Created At</p>
              <p className="text-lg font-semibold">
                {formatDate(user.created_at)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Last Login</p>
              <p className="text-lg font-semibold">
                {formatDate(user.last_login_at)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Updated At</p>
              <p className="text-lg font-semibold">
                {formatDate(user.updated_at)}
              </p>
            </div>
          </div>
        </div>

        {/* Direct Message */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Direct Message
          </h3>
          <DirectMessage
            telegramId={user.telegram_id}
            userName={user.full_name}
          />
        </div>
      </div>
    </Dialog>
  );
}
