import { ManagePageHeader } from '../../components/manage-page-header'
import { CaptureWorkspace } from './components/capture-workspace'

export default function ManageCapturePage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 8 · 图片错题采集'
        title='图片采集'
        description='用于图片错题采集，生成私有错题草稿。上传错题图片，OCR 识别文字，AI 生成草稿，人工确认后转为错题草稿。'
      />
      <CaptureWorkspace />
    </div>
  )
}
