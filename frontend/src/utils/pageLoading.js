import { reactive } from 'vue'



export const pageLoading = reactive({
  count: 0,
  message: '',
})

export function startPageLoading(message = '') {
  pageLoading.count += 1
  pageLoading.message = message
}

export function endPageLoading() {
  pageLoading.count = Math.max(0, pageLoading.count - 1)
  if (pageLoading.count === 0) {
    pageLoading.message = ''
  }
}



export function isPageLoading() {

  return pageLoading.count > 0

}

