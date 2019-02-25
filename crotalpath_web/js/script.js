$(document).ready(function () {
    $('#upload_input').on('change', function () {
        var fileList =  $('#file_list');
        $('#file_container').css('display', 'flex');
        $('#file_upload_btn span').text('Cambiar imagen');
        fileList.empty();

        var files = $(this)[0].files;
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            fileList.append(
                '<div class="card d-flex flex-column text-dark">' +
                ' <i class="card-body fas fa-image text-center"></i>' +
                ' <div class="card-footer">' + file.name + '</div>' +
                '</div>'
            );
        }
    });

    $('#upload_btn').on('click', function () {
        var mainContent = $('#main_content');
        mainContent.empty();

        mainContent.append(
            '<div class="fa-3x text-white">' +
            '  <i class="fas fa-spinner fa-spin"></i>' +
            '</div>'
        );

        setTimeout(function () {
            mainContent.empty();
            mainContent.append('<img src="./images/0002_pred.png"/>');
            mainContent.append('<h1 class="display-1">9926</h1>');
        }, 1000);
    })
});

function upload() {
    $('#upload_input').click()
}