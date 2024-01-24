let surveyNumber = ''
const downloadPdf = (surveyId) => {
  const test = window.location.href.includes('test')
  const currentLocation = window.location.href
  const url = new URL('download-result', currentLocation)

  let fetchUrl
  if (test) {
    const idx = '{{ index }}'
    url.pathname = `/test/download/?result=${idx}`
  } else {
    url.pathname = '/download-result/'
    url.searchParams.append('id', surveyId)
  }
  btn = document.getElementById('loadingButton')
  btn.classList.add('loading')
  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network error')
      }
      return response.json()
    })
    .then(data => {
      surveyNumber = data.survey_number
      generatePDF(data.resp_data)
    })
    .catch(error => {
      btn = document.getElementById('loadingButton')
      btn.classList.remove('loading')
      console.error('There has been a problem with your fetch operation:', error)
    })
}
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = ('0' + (date.getMonth() + 1)).slice(-2)
  const day = ('0' + date.getDate()).slice(-2)
  const hours = ('0' + date.getHours()).slice(-2)
  const minutes = ('0' + date.getMinutes()).slice(-2)
  const seconds = ('0' + date.getSeconds()).slice(-2)
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}
const generatePDF = (htmlContent) => {
  const hiddenContainer = document.getElementById('hiddenContainer')
  hiddenContainer.innerHTML = htmlContent
  const downloaded_at = document.getElementById('downloaded_at')
  const formattedDate = formatDate(new Date())
  downloaded_at.innerHTML = '<strong>ХЭВЛЭСЭН ОГНОО:</strong> ' + formattedDate
  const jsPDF = window.jspdf.jsPDF
  const hiddenContent = document.getElementById('hiddenContainer')
  hiddenContent.style.display = 'block'
  const pdf = new jsPDF({
    format: 'a4',
    orientation: 'portrait'
  })
  html2canvas(hiddenContent, {
    scale: Math.min(2480 / hiddenContent.offsetWidth, 3508 / hiddenContent.offsetHeight)
  }).then((hiddenCanvas) => {
    const hiddenImgData = hiddenCanvas.toDataURL('image/png')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    const imgProps = pdf.getImageProperties(hiddenImgData)
    const pdfImageWidth = pdfWidth
    const pdfImageHeight = (imgProps.height * pdfImageWidth) / imgProps.width

    let heightLeft = pdfImageHeight
    let position = 0
    heightLeft -= pdfHeight
    pdf.addImage(hiddenImgData, 'PNG', 10, 10, pdfImageWidth - 20, pdfImageHeight)
    while (heightLeft >= 0) {
      position = heightLeft - pdfImageHeight
      pdf.addPage()
      pdf.addImage(hiddenCanvas, 'PNG', 10, position, pdfImageWidth - 20, pdfImageHeight)
      heightLeft -= pdfHeight
    }
    btn = document.getElementById('loadingButton')
    btn.classList.remove('loading')
    pdf.save(surveyNumber + '.pdf')
  })
}
