import { AsyncStatePanel } from '@/components/async-state-panel'

export default function NotesLoading() {
  return <AsyncStatePanel status='loading' loadingLabel='正在加载笔记' />
}
