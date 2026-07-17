import { FutureCapabilityPage } from '../components/future-capability-page'

export default function ManageJobsPage() {
  return (
    <FutureCapabilityPage
      eyebrow='系统'
      title='处理记录'
      description='这里目前没有后台任务能力。'
      sections={[
        {
          title: '队列状态',
          description: '未来会展示排队、运行、失败和完成状态。',
          items: ['不轮询 job API', '不展示假任务', '不启动 worker'],
        },
        {
          title: '任务类型',
          description: '未来可承载 OCR、Capture、AI 和附件派生处理。',
          items: ['OCR 后置', 'Capture Router 后置', '附件派生处理后置'],
        },
        {
          title: '重试与错误',
          description: '未来会记录错误、重试次数和人工处理入口。',
          items: ['重试按钮未启用', '错误日志未持久化', '没有后台调度'],
        },
      ]}
      disabledActions={['启动任务', '重试任务', '取消任务', '轮询队列', '创建 worker']}
    />
  )
}
