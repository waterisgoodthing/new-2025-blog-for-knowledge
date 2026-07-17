import { FutureCapabilityPage } from '../components/future-capability-page'

export default function ManageSettingsPage() {
  return (
    <FutureCapabilityPage
      eyebrow='系统'
      title='设置'
      description='这里还没有可以保存的设置项。'
      sections={[
        {
          title: 'AI / OCR',
          description: '未来会管理模型能力、OCR 引擎和安全开关。',
          items: ['模型配置暂未启用', 'OCR 引擎暂未启用', '不会保存 provider 设置'],
        },
        {
          title: 'Upload / Jobs',
          description: '未来会管理上传大小、处理任务和重试策略。',
          items: ['上传策略当前由后端常量控制', '任务队列暂未启用', '无保存请求'],
        },
        {
          title: 'Privacy',
          description: '未来会集中管理公开/私有默认值和导出策略。',
          items: ['公开附件 API 未启用', '私有学习数据默认受保护', '无配置写入'],
        },
      ]}
      disabledActions={['保存设置', '测试模型', '启用 OCR', '启动任务队列', '开放公开附件']}
    />
  )
}
