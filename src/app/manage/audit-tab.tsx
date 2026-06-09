'use client'

import { useState, useEffect, useCallback } from 'react'
import dayjs from 'dayjs'
import { EmptyState } from '@/components/empty-state'

interface AuditLogItem {
  id: string
  auth_level: string | null
  action: string
  entity_type: string | null
  entity_id: string | null
  before: any
  after: any
  ip: string | null
  created_at: string | null
}

const ACTION_LABELS: Record<string, string> = {
  login: '登录',
  logout: '登出',
  create: '创建',
  update: '更新',
  delete: '删除',
  move: '移动',
  merge: '合并',
  rename: '重命名',
  revoke: '撤销',
  sync: '同步',
  ai_call: 'AI 调用',
}

const ENTITY_LABELS: Record<string, string> = {
  note: '笔记',
  blog: '博客',
  mistake: '错题',
  folder: '文件夹',
  tag: '标签',
  session: '会话',
  music: '音乐',
  setting: '设置',
}

export function AuditTab() {
  const [logs, setLogs] = useState<AuditLogItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/audit?page=${page}&size=50`, { credentials: 'include' })
      if (res.ok) {
        const data = await res.json()
        setLogs(data.items || [])
        setTotal(data.total || 0)
      }
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div>
      <div className='mb-4 flex items-center justify-between'>
        <p className='text-sm text-gray-500'>记录管理操作的安全审计日志</p>
        <button
          onClick={load}
          className='rounded-lg bg-white/60 px-3 py-1.5 text-sm text-gray-600 hover:bg-white/80'
        >
          刷新
        </button>
      </div>

      {loading ? (
        <div className='py-20 text-center text-gray-400'>加载中...</div>
      ) : logs.length === 0 ? (
        <div className='py-20'>
          <EmptyState variant='no-content' title='暂无操作记录' description='管理操作会在这里显示' />
        </div>
      ) : (
        <>
          <div className='overflow-x-auto rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
            <table className='w-full text-sm'>
              <thead>
                <tr className='border-b border-white/20 text-left text-xs text-gray-500'>
                  <th className='p-3'>时间</th>
                  <th className='p-3'>操作</th>
                  <th className='p-3'>对象</th>
                  <th className='p-3'>认证</th>
                  <th className='p-3'>IP</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className='border-b border-white/10 hover:bg-white/40'>
                    <td className='whitespace-nowrap p-3 text-xs text-gray-500'>
                      {log.created_at ? dayjs(log.created_at).format('MM-DD HH:mm:ss') : '-'}
                    </td>
                    <td className='p-3'>
                      <span className='rounded bg-blue-500/10 px-2 py-0.5 text-xs text-blue-600'>
                        {ACTION_LABELS[log.action] || log.action}
                      </span>
                    </td>
                    <td className='max-w-[200px] truncate p-3 text-xs text-gray-600'>
                      {log.entity_type ? (
                        <span>
                          {ENTITY_LABELS[log.entity_type] || log.entity_type}
                          {log.entity_id && <span className='ml-1 text-gray-400'>#{log.entity_id.slice(0, 8)}</span>}
                        </span>
                      ) : '-'}
                    </td>
                    <td className='p-3'>
                      <span className={`rounded-full px-2 py-0.5 text-xs ${
                        log.auth_level === 'passkey' ? 'bg-green-500/10 text-green-600' :
                        log.auth_level === 'password' ? 'bg-yellow-500/10 text-yellow-600' :
                        'bg-gray-100 text-gray-500'
                      }`}>
                        {log.auth_level || 'system'}
                      </span>
                    </td>
                    <td className='p-3 text-xs text-gray-400'>{log.ip || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {total > 50 && (
            <div className='mt-4 flex justify-center gap-2'>
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
              >
                上一页
              </button>
              <span className='px-3 py-1 text-sm text-gray-500'>{page} / {Math.ceil(total / 50)}</span>
              <button
                disabled={page >= Math.ceil(total / 50)}
                onClick={() => setPage(p => p + 1)}
                className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
