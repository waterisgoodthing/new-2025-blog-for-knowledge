import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageCapturePage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 6 · OCR/Capture Placeholder'
      title='Capture'
      description='OCR 与 Capture 尚未启用；附件上传仍由 Batch 5 私有附件页面负责。'
      futureScope='本批不上传文件、不读取 capture_items、不执行 OCR、不分类内容，也不会自动创建题目或错题草稿。'
    />
  )
}
