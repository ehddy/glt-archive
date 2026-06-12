import { endPageLoading, startPageLoading } from './pageLoading'

export async function withPageLoading(task) {
  startPageLoading()
  try {
    return await task()
  } finally {
    endPageLoading()
  }
}
