const url = window.location.href
const hasPath = url.includes('/survey/load/')
const queryParams = new URLSearchParams(window.location.search)

const hasQueryParam = queryParams.has('file_name')

if (hasPath && hasQueryParam) {
  const socketUrl = `ws://${window.location.hostname}:8001/ws/task/`

  const socket = new WebSocket(socketUrl)

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data !== null && data !== undefined && data.file_name !== null && data.file_name !== undefined) {
      const currentUrl = window.location.href
      const baseUrl = currentUrl.split('/survey/')[0]
      const newUrl = baseUrl + '/survey/result/?file_name=' + data.file_name
      window.location.href = newUrl
    }
  }
}
