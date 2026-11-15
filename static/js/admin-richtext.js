document.addEventListener('DOMContentLoaded', function () {
  if (typeof ClassicEditor === 'undefined') return;

  const selector = 'textarea[name="body"], textarea[name="description"], textarea[name="eligibility"], textarea[name="benefits"]';
  document.querySelectorAll(selector).forEach(function (textarea) {
    if (textarea.dataset.ckeditorReady === '1') return;
    textarea.dataset.ckeditorReady = '1';

    ClassicEditor
      .create(textarea, {
        toolbar: [
          'heading', '|',
          'bold', 'italic', 'underline', 'link', '|',
          'bulletedList', 'numberedList', 'blockQuote', '|',
          'insertTable', 'imageUpload', 'mediaEmbed', '|',
          'undo', 'redo'
        ],
        table: {
          contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells']
        }
      })
      .catch(function (error) {
        console.error('CKEditor error:', error);
      });
  });
});
