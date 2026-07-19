import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageCapturePage() {
  return (
    <ManagePlaceholderPage
      batch='工具 · 后续能力'
      title='图片采集'
      description='当前版本未启用图片识别与自动采集流程，附件仍通过资料管理上传。'
      futureScope='现有 Capture 基础设施不会在此页面自动启用；不读取 capture_items、不执行 OCR，也不自动创建题目或错题草稿。'
    />
  )
}
