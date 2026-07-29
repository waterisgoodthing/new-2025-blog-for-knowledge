import { ManagePageHeader } from '../../components/manage-page-header'
import { CaptureContent } from './components/capture-content'

export default function ManageCapturePage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='学习采集'
        title='图片采集'
        description='可上传图片后识别，也可直接手工录入。识别失败不会阻止你手工补全并进入草稿审核。'
      />
      <CaptureContent />
    </div>
  )
}
